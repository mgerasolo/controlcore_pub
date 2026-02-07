"""
MQTT Service for ControlCore - Phase 2

Handles communication with IoT sensing/action nodes via MQTT.
Manages node discovery, status updates, sensor readings, and command dispatch.
"""

import os
import json
import logging
import threading
from datetime import datetime, timezone
from typing import Callable, Optional
from dataclasses import dataclass, field
import paho.mqtt.client as mqtt
import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)


@dataclass
class MQTTConfig:
    """MQTT broker configuration."""
    host: str = "localhost"
    port: int = 1883
    username: Optional[str] = None
    password: Optional[str] = None
    client_id: str = "controlcore-central"
    keepalive: int = 60
    # Topic prefixes
    base_topic: str = "controlcore"
    status_topic: str = "controlcore/+/status"
    sensor_topic: str = "controlcore/+/sensor/#"
    command_topic: str = "controlcore/{node_uuid}/command"
    emergency_topic: str = "controlcore/emergency/#"


@dataclass
class NodeMessage:
    """Parsed message from a node."""
    node_uuid: str
    message_type: str  # 'status', 'sensor', 'response', 'error'
    capability: Optional[str] = None
    value: Optional[dict] = None
    raw_payload: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class MQTTService:
    """
    MQTT service for node communication.

    Responsibilities:
    - Connect to MQTT broker
    - Subscribe to node topics
    - Parse and store sensor readings
    - Update node status
    - Dispatch commands to nodes
    - Handle emergency messages
    """

    def __init__(self, config: MQTTConfig, db_connection_string: str):
        self.config = config
        self.db_connection_string = db_connection_string
        self.client: Optional[mqtt.Client] = None
        self.connected = False
        self._message_handlers: list[Callable[[NodeMessage], None]] = []
        self._lock = threading.Lock()

    def connect(self) -> bool:
        """Connect to MQTT broker."""
        try:
            self.client = mqtt.Client(
                client_id=self.config.client_id,
                callback_api_version=mqtt.CallbackAPIVersion.VERSION2
            )

            # Set credentials if provided
            if self.config.username:
                self.client.username_pw_set(
                    self.config.username,
                    self.config.password
                )

            # Set callbacks
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            self.client.on_message = self._on_message

            # Connect
            self.client.connect(
                self.config.host,
                self.config.port,
                self.config.keepalive
            )

            # Start network loop in background thread
            self.client.loop_start()

            logger.info(f"MQTT connecting to {self.config.host}:{self.config.port}")
            return True

        except Exception as e:
            logger.error(f"MQTT connection failed: {e}")
            return False

    def disconnect(self):
        """Disconnect from MQTT broker."""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            self.connected = False
            logger.info("MQTT disconnected")

    def _on_connect(self, client, userdata, flags, reason_code, properties):
        """Callback when connected to broker."""
        if reason_code == 0:
            self.connected = True
            logger.info("MQTT connected successfully")

            # Subscribe to node topics
            self._subscribe_to_topics()
        else:
            logger.error(f"MQTT connection failed: {reason_code}")

    def _on_disconnect(self, client, userdata, flags, reason_code, properties):
        """Callback when disconnected from broker."""
        self.connected = False
        logger.warning(f"MQTT disconnected: {reason_code}")

    def _subscribe_to_topics(self):
        """Subscribe to all node topics."""
        topics = [
            (self.config.status_topic, 1),
            (self.config.sensor_topic, 1),
            (self.config.emergency_topic, 2),  # QoS 2 for emergency
        ]

        for topic, qos in topics:
            self.client.subscribe(topic, qos)
            logger.info(f"Subscribed to: {topic}")

    def _on_message(self, client, userdata, msg):
        """Callback when message received."""
        try:
            topic_parts = msg.topic.split("/")
            payload = msg.payload.decode("utf-8")

            logger.debug(f"MQTT message: {msg.topic} = {payload[:100]}")

            # Parse message based on topic structure
            # controlcore/{node_uuid}/{type}/{capability}
            if len(topic_parts) < 3:
                return

            node_uuid = topic_parts[1]
            msg_type = topic_parts[2]
            capability = topic_parts[3] if len(topic_parts) > 3 else None

            # Handle emergency messages specially
            if msg_type == "emergency":
                self._handle_emergency(topic_parts, payload)
                return

            # Parse payload as JSON
            try:
                value = json.loads(payload)
            except json.JSONDecodeError:
                value = {"raw": payload}

            message = NodeMessage(
                node_uuid=node_uuid,
                message_type=msg_type,
                capability=capability,
                value=value,
                raw_payload=payload
            )

            # Process message
            self._process_message(message)

            # Notify handlers
            for handler in self._message_handlers:
                try:
                    handler(message)
                except Exception as e:
                    logger.error(f"Message handler error: {e}")

        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}")

    def _process_message(self, message: NodeMessage):
        """Process incoming message and update database."""
        conn = psycopg2.connect(self.db_connection_string)

        try:
            with conn.cursor() as cur:
                if message.message_type == "status":
                    self._update_node_status(cur, message)
                elif message.message_type == "sensor":
                    self._store_sensor_reading(cur, message)
                elif message.message_type == "response":
                    self._update_action_response(cur, message)

                conn.commit()

        except Exception as e:
            logger.error(f"Database error processing message: {e}")
            conn.rollback()
        finally:
            conn.close()

    def _update_node_status(self, cur, message: NodeMessage):
        """Update node status from heartbeat/status message."""
        status = message.value.get("status", "online")
        battery = message.value.get("battery_voltage")
        firmware = message.value.get("firmware_version")

        cur.execute("""
            INSERT INTO nodes (uuid, friendly_name, node_type, status, last_seen,
                             last_heartbeat, battery_voltage, firmware_version)
            VALUES (%s, %s, 'hybrid', %s, NOW(), NOW(), %s, %s)
            ON CONFLICT (uuid) DO UPDATE SET
                status = EXCLUDED.status,
                last_seen = NOW(),
                last_heartbeat = NOW(),
                battery_voltage = COALESCE(EXCLUDED.battery_voltage, nodes.battery_voltage),
                firmware_version = COALESCE(EXCLUDED.firmware_version, nodes.firmware_version)
        """, (message.node_uuid, f"Node-{message.node_uuid[:8]}",
              status, battery, firmware))

        logger.debug(f"Updated node status: {message.node_uuid} = {status}")

    def _store_sensor_reading(self, cur, message: NodeMessage):
        """Store sensor reading in database."""
        # Ensure node exists
        cur.execute("""
            INSERT INTO nodes (uuid, friendly_name, node_type, status, last_seen)
            VALUES (%s, %s, 'sensor', 'online', NOW())
            ON CONFLICT (uuid) DO UPDATE SET
                last_seen = NOW(),
                status = 'online'
        """, (message.node_uuid, f"Node-{message.node_uuid[:8]}"))

        # Store reading
        cur.execute("""
            INSERT INTO sensor_readings (node_uuid, capability_name, value, raw_value)
            VALUES (%s, %s, %s, %s)
        """, (message.node_uuid, message.capability,
              json.dumps(message.value), message.raw_payload))

        logger.debug(f"Stored sensor reading: {message.node_uuid}/{message.capability}")

    def _update_action_response(self, cur, message: NodeMessage):
        """Update action log with node response."""
        action_id = message.value.get("action_id")
        status = message.value.get("status", "confirmed")

        if action_id:
            cur.execute("""
                UPDATE action_log
                SET execution_status = %s,
                    execution_result = %s,
                    completed_at = NOW()
                WHERE id = %s
            """, (status, json.dumps(message.value), action_id))

            logger.info(f"Action {action_id} completed: {status}")

    def _handle_emergency(self, topic_parts: list, payload: str):
        """Handle emergency/E-stop messages."""
        try:
            data = json.loads(payload)
            level = data.get("level", "all")
            target = data.get("target")
            reason = data.get("reason", "Emergency stop triggered")

            logger.critical(f"EMERGENCY: level={level}, target={target}, reason={reason}")

            # Log to database
            conn = psycopg2.connect(self.db_connection_string)
            try:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO action_log
                        (initiated_by, action, parameters, safety_notes, execution_status)
                        VALUES ('emergency', 'e_stop', %s, %s, 'executed')
                    """, (json.dumps(data), reason))
                    conn.commit()
            finally:
                conn.close()

            # TODO: Broadcast stop to all affected nodes

        except Exception as e:
            logger.error(f"Error handling emergency: {e}")

    def send_command(self, node_uuid: str, action: str, parameters: dict = None,
                     action_id: int = None) -> bool:
        """
        Send command to a node.

        Args:
            node_uuid: Target node UUID
            action: Action to perform (e.g., 'valve_on', 'set_temperature')
            parameters: Action parameters
            action_id: Reference to action_log entry

        Returns:
            True if message was published successfully
        """
        if not self.connected:
            logger.error("Cannot send command: MQTT not connected")
            return False

        topic = self.config.command_topic.format(node_uuid=node_uuid)
        payload = {
            "action": action,
            "parameters": parameters or {},
            "action_id": action_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        try:
            result = self.client.publish(topic, json.dumps(payload), qos=1)

            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"Command sent: {node_uuid} -> {action}")
                return True
            else:
                logger.error(f"Failed to send command: {result.rc}")
                return False

        except Exception as e:
            logger.error(f"Error sending command: {e}")
            return False

    def send_emergency_stop(self, level: str = "all", target: str = None,
                           reason: str = "Manual emergency stop"):
        """
        Broadcast emergency stop message.

        Args:
            level: 'all', 'zone', or 'node'
            target: Zone or node to target (if level != 'all')
            reason: Reason for emergency stop
        """
        topic = f"{self.config.base_topic}/emergency/stop"
        payload = {
            "level": level,
            "target": target,
            "reason": reason,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        # Use QoS 2 for guaranteed delivery
        self.client.publish(topic, json.dumps(payload), qos=2)
        logger.critical(f"Emergency stop broadcast: {level} - {reason}")

    def add_message_handler(self, handler: Callable[[NodeMessage], None]):
        """Add a callback for incoming messages."""
        self._message_handlers.append(handler)

    def get_node_status(self, node_uuid: str) -> Optional[dict]:
        """Get current status of a node from database."""
        conn = psycopg2.connect(self.db_connection_string)
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT uuid, friendly_name, node_type, status, last_seen,
                           battery_voltage, firmware_version, metadata
                    FROM nodes WHERE uuid = %s
                """, (node_uuid,))
                return cur.fetchone()
        finally:
            conn.close()

    def get_all_nodes(self) -> list[dict]:
        """Get all registered nodes."""
        conn = psycopg2.connect(self.db_connection_string)
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT uuid, friendly_name, node_type, status, last_seen,
                           battery_voltage, firmware_version
                    FROM nodes
                    ORDER BY last_seen DESC NULLS LAST
                """)
                return cur.fetchall()
        finally:
            conn.close()

    def get_node_capabilities(self, node_uuid: str) -> list[dict]:
        """Get capabilities of a specific node."""
        conn = psycopg2.connect(self.db_connection_string)
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT capability_type, name, display_name, unit,
                           data_type, constraints, description
                    FROM node_capabilities
                    WHERE node_uuid = %s
                """, (node_uuid,))
                return cur.fetchall()
        finally:
            conn.close()


def create_mqtt_service() -> MQTTService:
    """Factory function to create MQTT service from environment."""
    from dotenv import load_dotenv
    load_dotenv()

    config = MQTTConfig(
        host=os.getenv("MQTT_HOST", "localhost"),
        port=int(os.getenv("MQTT_PORT", "1883")),
        username=os.getenv("MQTT_USERNAME"),
        password=os.getenv("MQTT_PASSWORD"),
        client_id=os.getenv("MQTT_CLIENT_ID", "controlcore-central"),
        base_topic=os.getenv("MQTT_TOPIC", "controlcore").rstrip("/#")
    )

    db_conn = (
        f"host={os.getenv('PG_HOST', 'localhost')} "
        f"port={os.getenv('PG_PORT', '5432')} "
        f"user={os.getenv('PG_USER', 'forecaster')} "
        f"password={os.getenv('PG_PASSWORD')} "
        f"dbname=forecaster"
    )

    return MQTTService(config, db_conn)
