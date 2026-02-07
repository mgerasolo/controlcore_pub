"""
Safety Rule Engine for ControlCore - Phase 2.4

Enforces safety constraints before actions are executed.
All AI-initiated actions MUST pass through safety checks.

Safety rule types:
- NEVER: Action is never allowed under these conditions
- ALWAYS: Action is always required under these conditions
- LIMIT: Action parameters must stay within limits
- REQUIRE: Condition must be met before action is allowed
"""

import os
import json
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)


class SafetyDecision(Enum):
    """Result of safety check."""
    APPROVED = "approved"           # Action can proceed
    DENIED = "denied"              # Action blocked by safety rule
    MODIFIED = "modified"          # Action allowed with modifications
    REQUIRES_CONFIRMATION = "requires_confirmation"  # Human approval needed


class RuleType(Enum):
    """Types of safety rules."""
    NEVER = "never"       # Never allow under conditions
    ALWAYS = "always"     # Always require under conditions
    LIMIT = "limit"       # Parameter must be within limits
    REQUIRE = "require"   # Prerequisite condition required


@dataclass
class SafetyCheckResult:
    """Result of a safety check."""
    decision: SafetyDecision
    rule_name: Optional[str] = None
    rule_id: Optional[int] = None
    original_action: str = ""
    original_params: dict = field(default_factory=dict)
    modified_params: Optional[dict] = None
    reason: str = ""
    checked_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class SafetyContext:
    """Current context for safety evaluation."""
    # Current sensor readings
    current_temperature: Optional[float] = None
    current_humidity: Optional[float] = None
    current_soil_moisture: Optional[float] = None
    current_wind_speed: Optional[float] = None

    # External conditions
    frost_warning: bool = False
    rain_expected: bool = False
    high_wind_warning: bool = False

    # Time-based context
    time_of_day: str = "unknown"  # morning, afternoon, evening, night
    is_daylight: bool = True

    # Recent history
    last_watering_minutes_ago: Optional[int] = None
    daily_watering_count: int = 0
    daily_watering_minutes: int = 0


class SafetyEngine:
    """
    Safety rule engine that enforces constraints on actions.

    All AI-initiated actions MUST be checked before execution.
    Human-initiated actions can optionally bypass (with logging).
    """

    def __init__(self, db_connection_string: str):
        self.db_connection_string = db_connection_string
        self._rules_cache: list[dict] = []
        self._cache_timestamp: Optional[datetime] = None
        self._cache_ttl_seconds = 60  # Refresh rules every minute

        # Built-in critical safety rules (cannot be disabled)
        self._builtin_rules = [
            {
                "name": "CRITICAL: No watering during freeze",
                "rule_type": "never",
                "priority": 1,
                "conditions": {"frost_warning": True},
                "action_constraint": {"action_pattern": "valve_on|irrigation|water", "result": "deny"},
                "reason": "Watering during freezing conditions can damage plants and equipment"
            },
            {
                "name": "CRITICAL: Max single watering duration",
                "rule_type": "limit",
                "priority": 2,
                "conditions": {"action_pattern": "valve_on|irrigation|water"},
                "action_constraint": {"parameter": "duration_minutes", "max": 60},
                "reason": "Single watering sessions limited to 60 minutes to prevent flooding"
            },
            {
                "name": "CRITICAL: Daily watering limit",
                "rule_type": "limit",
                "priority": 3,
                "conditions": {"action_pattern": "valve_on|irrigation|water"},
                "action_constraint": {"context": "daily_watering_minutes", "max": 180},
                "reason": "Daily watering limited to 3 hours total to conserve water"
            },
            {
                "name": "CRITICAL: Temperature set limits",
                "rule_type": "limit",
                "priority": 4,
                "conditions": {"action_pattern": "set_temperature|thermostat"},
                "action_constraint": {"parameter": "value", "min": 40, "max": 90},
                "reason": "Temperature settings must be between 40°F and 90°F"
            },
            {
                "name": "CRITICAL: No irrigation during high wind",
                "rule_type": "never",
                "priority": 5,
                "conditions": {"high_wind_warning": True},
                "action_constraint": {"action_pattern": "valve_on|irrigation|sprinkler", "result": "deny"},
                "reason": "Sprinkler irrigation ineffective during high winds"
            },
        ]

    def check_action(self, action: str, parameters: dict,
                     initiated_by: str, context: SafetyContext = None) -> SafetyCheckResult:
        """
        Check if an action passes safety rules.

        Args:
            action: The action being attempted (e.g., 'valve_on', 'set_temperature')
            parameters: Action parameters (e.g., {'duration_minutes': 15})
            initiated_by: Who initiated the action ('user', 'ai', 'schedule', 'rule')
            context: Current environmental context for evaluation

        Returns:
            SafetyCheckResult with decision and details
        """
        if context is None:
            context = self._get_current_context()

        logger.info(f"Safety check: {action} by {initiated_by}, params={parameters}")

        # Get all applicable rules (built-in + database)
        rules = self._get_applicable_rules(action)

        # Sort by priority (lower = higher priority)
        rules.sort(key=lambda r: r.get("priority", 100))

        # Check each rule
        for rule in rules:
            result = self._evaluate_rule(rule, action, parameters, context)

            if result.decision == SafetyDecision.DENIED:
                logger.warning(f"Action DENIED by rule '{rule['name']}': {result.reason}")
                return result

            if result.decision == SafetyDecision.MODIFIED:
                logger.info(f"Action MODIFIED by rule '{rule['name']}': {result.reason}")
                parameters = result.modified_params or parameters

            if result.decision == SafetyDecision.REQUIRES_CONFIRMATION:
                logger.info(f"Action requires confirmation: {result.reason}")
                return result

        # All rules passed
        return SafetyCheckResult(
            decision=SafetyDecision.APPROVED,
            original_action=action,
            original_params=parameters,
            reason="All safety checks passed"
        )

    def _get_applicable_rules(self, action: str) -> list[dict]:
        """Get all rules that might apply to this action."""
        rules = []

        # Add built-in rules
        rules.extend(self._builtin_rules)

        # Get database rules (cached)
        self._refresh_rules_cache_if_needed()
        rules.extend(self._rules_cache)

        return rules

    def _refresh_rules_cache_if_needed(self):
        """Refresh rules from database if cache is stale."""
        now = datetime.now(timezone.utc)

        if (self._cache_timestamp is None or
            (now - self._cache_timestamp).total_seconds() > self._cache_ttl_seconds):

            try:
                conn = psycopg2.connect(self.db_connection_string)
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("""
                        SELECT id, name, description, rule_type, priority, enabled,
                               conditions, action_constraint, applies_to
                        FROM safety_rules
                        WHERE enabled = true
                        ORDER BY priority ASC
                    """)
                    self._rules_cache = [dict(r) for r in cur.fetchall()]
                conn.close()
                self._cache_timestamp = now
                logger.debug(f"Refreshed safety rules cache: {len(self._rules_cache)} rules")
            except Exception as e:
                logger.error(f"Failed to refresh safety rules: {e}")
                # Keep using stale cache rather than failing

    def _evaluate_rule(self, rule: dict, action: str, parameters: dict,
                       context: SafetyContext) -> SafetyCheckResult:
        """Evaluate a single safety rule."""
        rule_type = rule.get("rule_type", "").lower()
        conditions = rule.get("conditions", {})
        constraint = rule.get("action_constraint", {})

        # Check if rule applies to this action
        action_pattern = constraint.get("action_pattern") or conditions.get("action_pattern")
        if action_pattern:
            import re
            if not re.search(action_pattern, action, re.IGNORECASE):
                return SafetyCheckResult(
                    decision=SafetyDecision.APPROVED,
                    original_action=action,
                    original_params=parameters,
                    reason="Rule does not apply to this action"
                )

        # Check conditions match current context
        if not self._conditions_match(conditions, context):
            return SafetyCheckResult(
                decision=SafetyDecision.APPROVED,
                rule_name=rule.get("name"),
                original_action=action,
                original_params=parameters,
                reason="Conditions not met, rule does not apply"
            )

        # Evaluate based on rule type
        if rule_type == "never":
            return SafetyCheckResult(
                decision=SafetyDecision.DENIED,
                rule_name=rule.get("name"),
                rule_id=rule.get("id"),
                original_action=action,
                original_params=parameters,
                reason=rule.get("reason", "Action denied by NEVER rule")
            )

        elif rule_type == "limit":
            return self._check_limit_rule(rule, action, parameters, context)

        elif rule_type == "require":
            # Check if required condition is met
            required = constraint.get("required_condition", {})
            if not self._conditions_match(required, context):
                return SafetyCheckResult(
                    decision=SafetyDecision.DENIED,
                    rule_name=rule.get("name"),
                    rule_id=rule.get("id"),
                    original_action=action,
                    original_params=parameters,
                    reason=rule.get("reason", "Required condition not met")
                )

        elif rule_type == "always":
            # This type is used for alerts/monitoring, not blocking
            pass

        return SafetyCheckResult(
            decision=SafetyDecision.APPROVED,
            rule_name=rule.get("name"),
            original_action=action,
            original_params=parameters,
            reason="Rule evaluated, action approved"
        )

    def _check_limit_rule(self, rule: dict, action: str, parameters: dict,
                          context: SafetyContext) -> SafetyCheckResult:
        """Check a LIMIT rule and potentially modify parameters."""
        constraint = rule.get("action_constraint", {})
        param_name = constraint.get("parameter")
        context_name = constraint.get("context")

        min_val = constraint.get("min")
        max_val = constraint.get("max")

        # Check parameter limit
        if param_name and param_name in parameters:
            value = parameters[param_name]
            modified = False
            new_value = value

            if min_val is not None and value < min_val:
                new_value = min_val
                modified = True
            if max_val is not None and value > max_val:
                new_value = max_val
                modified = True

            if modified:
                new_params = parameters.copy()
                new_params[param_name] = new_value
                return SafetyCheckResult(
                    decision=SafetyDecision.MODIFIED,
                    rule_name=rule.get("name"),
                    rule_id=rule.get("id"),
                    original_action=action,
                    original_params=parameters,
                    modified_params=new_params,
                    reason=f"{param_name} adjusted from {value} to {new_value} (limit: {min_val}-{max_val})"
                )

        # Check context limit
        if context_name:
            context_value = getattr(context, context_name, None)
            if context_value is not None and max_val is not None:
                if context_value >= max_val:
                    return SafetyCheckResult(
                        decision=SafetyDecision.DENIED,
                        rule_name=rule.get("name"),
                        rule_id=rule.get("id"),
                        original_action=action,
                        original_params=parameters,
                        reason=f"{context_name} ({context_value}) exceeds limit ({max_val})"
                    )

        return SafetyCheckResult(
            decision=SafetyDecision.APPROVED,
            rule_name=rule.get("name"),
            original_action=action,
            original_params=parameters,
            reason="Within limits"
        )

    def _conditions_match(self, conditions: dict, context: SafetyContext) -> bool:
        """Check if conditions match the current context."""
        if not conditions:
            return True

        for key, expected in conditions.items():
            if key == "action_pattern":
                continue  # Handled separately

            actual = getattr(context, key, None)
            if actual is None:
                continue  # Unknown context, don't fail

            if isinstance(expected, bool):
                if actual != expected:
                    return False
            elif isinstance(expected, dict):
                # Range check
                if "min" in expected and actual < expected["min"]:
                    return False
                if "max" in expected and actual > expected["max"]:
                    return False
            elif actual != expected:
                return False

        return True

    def _get_current_context(self) -> SafetyContext:
        """Get current environmental context from database."""
        context = SafetyContext()

        try:
            conn = psycopg2.connect(self.db_connection_string)
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Get recent sensor readings
                cur.execute("""
                    SELECT capability_name, value
                    FROM sensor_readings
                    WHERE timestamp > NOW() - INTERVAL '15 minutes'
                    ORDER BY timestamp DESC
                """)
                readings = cur.fetchall()

                for r in readings:
                    cap = r["capability_name"]
                    val = r["value"]
                    if isinstance(val, str):
                        val = json.loads(val)

                    if cap == "temperature" and isinstance(val, dict):
                        context.current_temperature = val.get("value")
                    elif cap == "humidity" and isinstance(val, dict):
                        context.current_humidity = val.get("value")
                    elif cap == "soil_moisture" and isinstance(val, dict):
                        context.current_soil_moisture = val.get("value")

                # Get daily watering stats
                cur.execute("""
                    SELECT COUNT(*) as count,
                           COALESCE(SUM((parameters->>'duration_minutes')::int), 0) as total_minutes
                    FROM action_log
                    WHERE action LIKE '%valve%' OR action LIKE '%water%'
                    AND timestamp > CURRENT_DATE
                    AND execution_status = 'confirmed'
                """)
                stats = cur.fetchone()
                if stats:
                    context.daily_watering_count = stats["count"]
                    context.daily_watering_minutes = stats["total_minutes"]

            conn.close()

        except Exception as e:
            logger.warning(f"Error getting safety context: {e}")

        # Determine time of day
        now = datetime.now()
        hour = now.hour
        if 5 <= hour < 12:
            context.time_of_day = "morning"
        elif 12 <= hour < 17:
            context.time_of_day = "afternoon"
        elif 17 <= hour < 21:
            context.time_of_day = "evening"
        else:
            context.time_of_day = "night"

        context.is_daylight = 6 <= hour < 20

        # Check for frost warning (temperature below 35°F)
        if context.current_temperature is not None:
            context.frost_warning = context.current_temperature < 35

        return context

    def log_safety_decision(self, result: SafetyCheckResult, action_id: Optional[int] = None):
        """Log a safety decision to the database."""
        try:
            conn = psycopg2.connect(self.db_connection_string)
            with conn.cursor() as cur:
                if action_id:
                    cur.execute("""
                        UPDATE action_log
                        SET safety_check_result = %s,
                            safety_notes = %s
                        WHERE id = %s
                    """, (result.decision.value, result.reason, action_id))
                conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to log safety decision: {e}")


def create_safety_engine() -> SafetyEngine:
    """Factory function to create safety engine from environment."""
    from dotenv import load_dotenv
    load_dotenv()

    db_conn = (
        f"host={os.getenv('PG_HOST', 'localhost')} "
        f"port={os.getenv('PG_PORT', '5432')} "
        f"user={os.getenv('PG_USER', 'forecaster')} "
        f"password={os.getenv('PG_PASSWORD')} "
        f"dbname=forecaster"
    )

    return SafetyEngine(db_conn)


# Example usage and testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    # Test with mock context
    context = SafetyContext(
        current_temperature=28.0,  # Below freezing!
        frost_warning=True,
        daily_watering_minutes=0
    )

    engine = SafetyEngine("host=localhost dbname=test")

    # Test 1: Watering during freeze (should DENY)
    result = engine.check_action(
        action="valve_on",
        parameters={"duration_minutes": 15},
        initiated_by="ai",
        context=context
    )
    print(f"Test 1 (freeze): {result.decision.value} - {result.reason}")

    # Test 2: Long watering duration (should MODIFY)
    context.frost_warning = False
    context.current_temperature = 75
    result = engine.check_action(
        action="valve_on",
        parameters={"duration_minutes": 120},  # Over 60 min limit
        initiated_by="ai",
        context=context
    )
    print(f"Test 2 (duration): {result.decision.value} - {result.reason}")
    if result.modified_params:
        print(f"  Modified to: {result.modified_params}")

    # Test 3: Normal watering (should APPROVE)
    result = engine.check_action(
        action="valve_on",
        parameters={"duration_minutes": 15},
        initiated_by="ai",
        context=context
    )
    print(f"Test 3 (normal): {result.decision.value} - {result.reason}")

    # Test 4: Temperature out of range (should MODIFY)
    result = engine.check_action(
        action="set_temperature",
        parameters={"value": 100},  # Over 90 limit
        initiated_by="ai",
        context=context
    )
    print(f"Test 4 (temp limit): {result.decision.value} - {result.reason}")
    if result.modified_params:
        print(f"  Modified to: {result.modified_params}")
