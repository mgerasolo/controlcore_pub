"""
Command Parser for ControlCore - Phase 2.3

Parses natural language into structured commands for IoT nodes.
Distinguishes between:
- Queries (asking for information)
- Actions (controlling devices)
- Control (system-level commands like E-stop)
"""

import os
import re
import json
import logging
import httpx
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# LiteLLM configuration
LITELLM_API_URL = os.getenv("LITELLM_API_URL", "http://10.0.0.27:2764/v1")
LITELLM_API_KEY = os.getenv("LITELLM_API_KEY", "sk-placeholder")
LITELLM_MODEL = os.getenv("LITELLM_COMMAND_MODEL", "jarvis-llama31")


class IntentType(Enum):
    """Types of user intents."""
    QUERY = "query"           # Asking for information (weather, sensor readings)
    ACTION = "action"         # Controlling a device (turn on valve, set temperature)
    CONTROL = "control"       # System control (E-stop, emergency, restart)
    UNKNOWN = "unknown"       # Can't determine intent


class ActionType(Enum):
    """Types of device actions."""
    ON = "on"
    OFF = "off"
    SET = "set"
    TOGGLE = "toggle"
    SCHEDULE = "schedule"
    CANCEL = "cancel"


@dataclass
class ParsedCommand:
    """Result of parsing a natural language command."""
    intent: IntentType
    original_text: str
    confidence: float = 0.0

    # For ACTION intent
    target_node: Optional[str] = None      # Node UUID or friendly name
    action_type: Optional[ActionType] = None
    capability: Optional[str] = None       # valve, temperature, moisture, etc.
    parameters: dict = field(default_factory=dict)

    # For CONTROL intent
    control_type: Optional[str] = None     # e_stop, restart, status
    scope: Optional[str] = None            # all, zone, node

    # For QUERY intent
    query_type: Optional[str] = None       # weather, sensor, node_status

    # Audit fields
    parsed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    parse_method: str = "unknown"          # pattern, llm, hybrid


# Pattern-based intent detection (fast, no LLM needed)
ACTION_PATTERNS = [
    # Turn on/off patterns
    (r"turn\s+(on|off)\s+(?:the\s+)?(.+)", "toggle_device"),
    (r"(enable|disable)\s+(?:the\s+)?(.+)", "toggle_device"),
    (r"(start|stop)\s+(?:the\s+)?(.+)", "toggle_device"),
    (r"(activate|deactivate)\s+(?:the\s+)?(.+)", "toggle_device"),
    (r"(open|close)\s+(?:the\s+)?(.+)", "toggle_device"),

    # Set value patterns
    (r"set\s+(?:the\s+)?(.+?)\s+to\s+(\d+\.?\d*)\s*(%|degrees?|°|f|c)?", "set_value"),
    (r"change\s+(?:the\s+)?(.+?)\s+to\s+(\d+\.?\d*)", "set_value"),

    # Duration patterns
    (r"(?:turn|run|water)\s+(?:the\s+)?(.+?)\s+for\s+(\d+)\s*(minutes?|mins?|hours?|hrs?|seconds?|secs?)", "timed_action"),
    (r"water\s+(?:the\s+)?(.+?)\s+for\s+(\d+)", "timed_action"),

    # Schedule patterns
    (r"schedule\s+(.+?)\s+(?:at|for)\s+(\d{1,2}:\d{2})", "schedule"),
    (r"(?:at|every)\s+(\d{1,2}:\d{2})\s+(.+)", "schedule"),
]

CONTROL_PATTERNS = [
    (r"(?:e-?stop|emergency\s*stop|kill|halt)", "e_stop"),
    (r"stop\s+(?:all|everything)", "e_stop"),
    (r"(?:restart|reboot)\s+(?:the\s+)?(.+)", "restart"),
    (r"(?:status|health)\s+(?:of\s+)?(?:the\s+)?(.+)", "status"),
    (r"list\s+(?:all\s+)?(?:nodes?|devices?)", "list_nodes"),
]

QUERY_PATTERNS = [
    (r"what(?:'s| is)\s+(?:the\s+)?(.+?)(?:\?|$)", "query"),
    (r"how\s+(?:much|many)\s+(.+?)(?:\?|$)", "query"),
    (r"when\s+(?:did|was)\s+(.+?)(?:\?|$)", "query"),
    (r"show\s+(?:me\s+)?(?:the\s+)?(.+)", "query"),
    (r"get\s+(?:the\s+)?(.+?)(?:\s+reading)?(?:\?|$)", "query"),
    (r"(?:weather|temperature|humidity|rain|precipitation)", "weather_query"),
]

# Capability keywords to node type mapping
CAPABILITY_KEYWORDS = {
    "valve": ["valve", "irrigation", "water", "sprinkler", "solenoid"],
    "temperature": ["temperature", "temp", "thermostat", "heat", "cool", "heating", "cooling"],
    "moisture": ["moisture", "soil", "humidity", "wet", "dry"],
    "light": ["light", "lamp", "led", "brightness"],
    "pump": ["pump", "pressure", "flow"],
    "fan": ["fan", "ventilation", "vent", "exhaust"],
}


class CommandParser:
    """
    Parses natural language into structured commands.

    Uses a hybrid approach:
    1. Pattern matching for common phrases (fast, no API calls)
    2. LLM fallback for complex or ambiguous commands
    """

    def __init__(self, use_llm_fallback: bool = True):
        self.use_llm_fallback = use_llm_fallback
        self._known_nodes: dict[str, dict] = {}  # Cache of known nodes

    def parse(self, text: str) -> ParsedCommand:
        """
        Parse natural language text into a structured command.

        Args:
            text: User's natural language input

        Returns:
            ParsedCommand with intent, targets, and parameters
        """
        text = text.strip()

        # Try pattern-based parsing first (fast)
        result = self._parse_with_patterns(text)

        if result.intent != IntentType.UNKNOWN and result.confidence >= 0.7:
            return result

        # Fall back to LLM for complex commands
        if self.use_llm_fallback:
            llm_result = self._parse_with_llm(text)

            # Prefer LLM result if more confident
            if llm_result.confidence > result.confidence:
                return llm_result

        return result

    def _parse_with_patterns(self, text: str) -> ParsedCommand:
        """Pattern-based parsing for common commands."""
        text_lower = text.lower()

        # Check for emergency/control commands first (highest priority)
        for pattern, control_type in CONTROL_PATTERNS:
            match = re.search(pattern, text_lower)
            if match:
                return self._build_control_command(text, match, control_type)

        # Check for action commands
        for pattern, action_type in ACTION_PATTERNS:
            match = re.search(pattern, text_lower)
            if match:
                return self._build_action_command(text, match, action_type)

        # Check for query commands
        for pattern, query_type in QUERY_PATTERNS:
            match = re.search(pattern, text_lower)
            if match:
                return ParsedCommand(
                    intent=IntentType.QUERY,
                    original_text=text,
                    confidence=0.8,
                    query_type=query_type,
                    parse_method="pattern"
                )

        # Couldn't determine intent
        return ParsedCommand(
            intent=IntentType.UNKNOWN,
            original_text=text,
            confidence=0.3,
            parse_method="pattern"
        )

    def _build_control_command(self, text: str, match, control_type: str) -> ParsedCommand:
        """Build a control command from pattern match."""
        cmd = ParsedCommand(
            intent=IntentType.CONTROL,
            original_text=text,
            confidence=0.95,
            control_type=control_type,
            parse_method="pattern"
        )

        if control_type == "e_stop":
            cmd.scope = "all"
        elif control_type in ("restart", "status") and match.lastindex >= 1:
            cmd.target_node = match.group(1).strip()
        elif control_type == "list_nodes":
            cmd.scope = "all"

        return cmd

    def _build_action_command(self, text: str, match, pattern_type: str) -> ParsedCommand:
        """Build an action command from pattern match."""
        cmd = ParsedCommand(
            intent=IntentType.ACTION,
            original_text=text,
            confidence=0.85,
            parse_method="pattern"
        )

        if pattern_type == "toggle_device":
            action_word = match.group(1).lower()
            target = match.group(2).strip()

            # Determine on/off based on action word
            if action_word in ("on", "enable", "start", "activate", "open"):
                cmd.action_type = ActionType.ON
            else:
                cmd.action_type = ActionType.OFF

            cmd.target_node = target
            cmd.capability = self._extract_capability(target)

        elif pattern_type == "set_value":
            target = match.group(1).strip()
            value = float(match.group(2))
            unit = match.group(3) if match.lastindex >= 3 else None

            cmd.action_type = ActionType.SET
            cmd.target_node = target
            cmd.capability = self._extract_capability(target)
            cmd.parameters = {"value": value}
            if unit:
                cmd.parameters["unit"] = unit.lower().rstrip('s')

        elif pattern_type == "timed_action":
            target = match.group(1).strip()
            duration = int(match.group(2))
            unit = match.group(3).lower() if match.lastindex >= 3 else "minutes"

            # Normalize duration to minutes
            if unit.startswith("hour") or unit.startswith("hr"):
                duration *= 60
            elif unit.startswith("sec"):
                duration = max(1, duration // 60)

            cmd.action_type = ActionType.ON
            cmd.target_node = target
            cmd.capability = self._extract_capability(target)
            cmd.parameters = {"duration_minutes": duration}

        elif pattern_type == "schedule":
            # Basic schedule parsing
            cmd.action_type = ActionType.SCHEDULE
            cmd.parameters = {"time": match.group(2) if match.lastindex >= 2 else match.group(1)}

        return cmd

    def _extract_capability(self, target: str) -> Optional[str]:
        """Extract capability type from target description."""
        target_lower = target.lower()

        for capability, keywords in CAPABILITY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in target_lower:
                    return capability

        return None

    def _parse_with_llm(self, text: str) -> ParsedCommand:
        """Use LLM for complex command parsing."""
        prompt = self._build_llm_prompt(text)

        try:
            response = self._call_llm(prompt)
            return self._parse_llm_response(text, response)
        except Exception as e:
            logger.error(f"LLM parsing failed: {e}")
            return ParsedCommand(
                intent=IntentType.UNKNOWN,
                original_text=text,
                confidence=0.2,
                parse_method="llm_failed"
            )

    def _build_llm_prompt(self, text: str) -> str:
        """Build prompt for LLM command parsing."""
        return f"""You are a command parser for an IoT control system. Parse the following user input and return a JSON object.

User input: "{text}"

Return JSON with these fields:
- intent: "query" (asking for information), "action" (controlling device), "control" (system command), or "unknown"
- confidence: 0.0 to 1.0
- target_node: device/node name if applicable (null if not)
- action_type: "on", "off", "set", "toggle", "schedule", or null
- capability: "valve", "temperature", "moisture", "light", "pump", "fan", or null
- parameters: object with values like {{"value": 72, "unit": "fahrenheit", "duration_minutes": 15}}
- control_type: "e_stop", "restart", "status", "list_nodes" or null

Only output valid JSON, no explanation."""

    def _call_llm(self, prompt: str) -> str:
        """Call LiteLLM API for command parsing."""
        import httpx

        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{LITELLM_API_URL}/chat/completions",
                headers={"Authorization": f"Bearer {LITELLM_API_KEY}"},
                json={
                    "model": LITELLM_MODEL,
                    "messages": [
                        {"role": "system", "content": "You are a precise command parser. Output only valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.1,
                    "max_tokens": 200
                }
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]

    def _parse_llm_response(self, original_text: str, response: str) -> ParsedCommand:
        """Parse LLM response into ParsedCommand."""
        try:
            # Extract JSON from response (may have markdown wrapping)
            json_match = re.search(r'\{[^{}]*\}', response, re.DOTALL)
            if not json_match:
                raise ValueError("No JSON found in response")

            data = json.loads(json_match.group())

            intent_str = data.get("intent", "unknown")
            intent = IntentType(intent_str) if intent_str in [i.value for i in IntentType] else IntentType.UNKNOWN

            action_str = data.get("action_type")
            action_type = ActionType(action_str) if action_str in [a.value for a in ActionType] else None

            return ParsedCommand(
                intent=intent,
                original_text=original_text,
                confidence=float(data.get("confidence", 0.7)),
                target_node=data.get("target_node"),
                action_type=action_type,
                capability=data.get("capability"),
                parameters=data.get("parameters", {}),
                control_type=data.get("control_type"),
                parse_method="llm"
            )

        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.warning(f"Failed to parse LLM response: {e}")
            return ParsedCommand(
                intent=IntentType.UNKNOWN,
                original_text=original_text,
                confidence=0.3,
                parse_method="llm_parse_error"
            )

    def register_known_node(self, uuid: str, info: dict):
        """Register a known node for better matching."""
        self._known_nodes[uuid] = info
        # Also index by friendly name
        if "friendly_name" in info:
            self._known_nodes[info["friendly_name"].lower()] = info

    def resolve_target_node(self, target: str) -> Optional[str]:
        """
        Resolve a target description to a node UUID.

        Args:
            target: Friendly name or partial match

        Returns:
            Node UUID if found, None otherwise
        """
        target_lower = target.lower()

        # Exact match
        if target_lower in self._known_nodes:
            node = self._known_nodes[target_lower]
            return node.get("uuid", target_lower)

        # Fuzzy match on friendly name
        for key, node in self._known_nodes.items():
            if isinstance(node, dict):
                friendly = node.get("friendly_name", "").lower()
                if target_lower in friendly or friendly in target_lower:
                    return node.get("uuid")

        return None


def create_command_parser(use_llm: bool = True) -> CommandParser:
    """Factory function to create a command parser."""
    return CommandParser(use_llm_fallback=use_llm)


# Example usage and testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    parser = CommandParser(use_llm_fallback=False)  # Pattern-only for testing

    test_commands = [
        "Turn on the main valve",
        "Turn off irrigation zone 3",
        "Set temperature to 72 degrees",
        "Water the garden for 15 minutes",
        "What's the current soil moisture?",
        "E-STOP!",
        "Stop everything",
        "How much rain fell yesterday?",
        "Schedule watering at 6:00",
        "List all nodes",
    ]

    for cmd in test_commands:
        result = parser.parse(cmd)
        print(f"\n'{cmd}'")
        print(f"  Intent: {result.intent.value}")
        print(f"  Confidence: {result.confidence:.2f}")
        if result.target_node:
            print(f"  Target: {result.target_node}")
        if result.action_type:
            print(f"  Action: {result.action_type.value}")
        if result.capability:
            print(f"  Capability: {result.capability}")
        if result.parameters:
            print(f"  Params: {result.parameters}")
        if result.control_type:
            print(f"  Control: {result.control_type}")
