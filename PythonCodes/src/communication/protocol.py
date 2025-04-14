from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

class MessageType(Enum):
    # System messages
    HEARTBEAT = "heartbeat"
    ERROR = "error"
    STATUS = "status"
    
    # Command messages
    COMMAND = "command"
    RESPONSE = "response"
    
    # Data messages
    DATA = "data"
    STREAM = "stream"
    
    # Control messages
    CONTROL = "control"
    CONFIG = "config"
    
    # Security messages
    AUTH = "auth"
    KEY_EXCHANGE = "key_exchange"

@dataclass
class Message:
    type: MessageType
    payload: Dict[str, Any]
    timestamp: datetime = datetime.utcnow()
    priority: int = 0
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value,
            "payload": self.payload,
            "timestamp": self.timestamp.isoformat(),
            "priority": self.priority,
            "metadata": self.metadata or {}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        return cls(
            type=MessageType(data["type"]),
            payload=data["payload"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            priority=data.get("priority", 0),
            metadata=data.get("metadata")
        )

class Protocol:
    @staticmethod
    def create_heartbeat() -> Message:
        return Message(
            type=MessageType.HEARTBEAT,
            payload={"status": "alive"}
        )
    
    @staticmethod
    def create_error(error: str, code: int) -> Message:
        return Message(
            type=MessageType.ERROR,
            payload={"error": error, "code": code},
            priority=1
        )
    
    @staticmethod
    def create_command(command: str, args: Dict[str, Any]) -> Message:
        return Message(
            type=MessageType.COMMAND,
            payload={"command": command, "args": args}
        )
    
    @staticmethod
    def create_response(command: str, result: Any) -> Message:
        return Message(
            type=MessageType.RESPONSE,
            payload={"command": command, "result": result}
        )
    
    @staticmethod
    def create_data(data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> Message:
        return Message(
            type=MessageType.DATA,
            payload=data,
            metadata=metadata
        )
    
    @staticmethod
    def create_stream(data: Dict[str, Any], stream_id: str) -> Message:
        return Message(
            type=MessageType.STREAM,
            payload={"stream_id": stream_id, "data": data}
        )
    
    @staticmethod
    def create_control(action: str, params: Dict[str, Any]) -> Message:
        return Message(
            type=MessageType.CONTROL,
            payload={"action": action, "params": params}
        )
    
    @staticmethod
    def create_config(config: Dict[str, Any]) -> Message:
        return Message(
            type=MessageType.CONFIG,
            payload=config
        )
    
    @staticmethod
    def create_auth(token: str) -> Message:
        return Message(
            type=MessageType.AUTH,
            payload={"token": token}
        )
    
    @staticmethod
    def create_key_exchange(key: str) -> Message:
        return Message(
            type=MessageType.KEY_EXCHANGE,
            payload={"key": key}
        ) 