import asyncio
from typing import Dict, Any, Optional, Callable
from .realtime_handler import RealtimeHandler
from .message_queue import MessageQueue
from .secure_protocol import SecureProtocol
from ..utils.error_handling import KAPESITError, ErrorSeverity
from ..utils.config_manager import config_manager

class CommunicationManager:
    def __init__(self):
        self.realtime_handler = RealtimeHandler()
        self.message_queue = MessageQueue()
        self.secure_protocol = SecureProtocol()
        self.message_handlers: Dict[str, Callable] = {}
        
    async def start(self, host: str = "localhost", port: int = 8765):
        try:
            # Start realtime server
            server = await self.realtime_handler.start_server(host, port)
            
            # Start message queue
            await self.message_queue.start()
            
            # Register default handlers
            self._register_default_handlers()
            
            return server
            
        except Exception as e:
            raise KAPESITError(
                f"Failed to start communication manager: {str(e)}",
                severity=ErrorSeverity.ERROR,
                component="COMMUNICATION_MANAGER"
            )
    
    async def stop(self):
        try:
            await self.message_queue.stop()
        except Exception as e:
            raise KAPESITError(
                f"Failed to stop communication manager: {str(e)}",
                severity=ErrorSeverity.ERROR,
                component="COMMUNICATION_MANAGER"
            )
    
    def _register_default_handlers(self):
        self.realtime_handler.register_handler("message", self._handle_realtime_message)
        self.realtime_handler.register_handler("queue", self._handle_queue_message)
    
    async def _handle_realtime_message(self, session_id: str, message: Dict[str, Any]):
        try:
            if "type" in message and message["type"] in self.message_handlers:
                await self.message_handlers[message["type"]](session_id, message)
        except Exception as e:
            raise KAPESITError(
                f"Realtime message handling failed: {str(e)}",
                severity=ErrorSeverity.ERROR,
                component="COMMUNICATION_MANAGER"
            )
    
    async def _handle_queue_message(self, session_id: str, message: Dict[str, Any]):
        try:
            await self.message_queue.enqueue(session_id, message)
        except Exception as e:
            raise KAPESITError(
                f"Queue message handling failed: {str(e)}",
                severity=ErrorSeverity.ERROR,
                component="COMMUNICATION_MANAGER"
            )
    
    def register_handler(self, message_type: str, handler: Callable):
        self.message_handlers[message_type] = handler
    
    async def send_message(self, session_id: str, message: Dict[str, Any], priority: int = 0):
        try:
            if session_id in self.realtime_handler.connections:
                await self.realtime_handler.broadcast(message)
            else:
                await self.message_queue.enqueue(session_id, message, priority)
        except Exception as e:
            raise KAPESITError(
                f"Message sending failed: {str(e)}",
                severity=ErrorSeverity.ERROR,
                component="COMMUNICATION_MANAGER"
            )
    
    async def process_queued_messages(self):
        try:
            for session_id in list(self.message_queue.queues.keys()):
                while message := await self.message_queue.dequeue(session_id):
                    if "type" in message and message["type"] in self.message_handlers:
                        await self.message_handlers[message["type"]](session_id, message)
        except Exception as e:
            raise KAPESITError(
                f"Queued message processing failed: {str(e)}",
                severity=ErrorSeverity.ERROR,
                component="COMMUNICATION_MANAGER"
            )
    
    def get_connection_stats(self) -> Dict[str, Any]:
        return {
            "active_connections": len(self.realtime_handler.connections),
            "queued_messages": self.message_queue.get_total_messages(),
            "message_types": list(self.message_handlers.keys())
        } 