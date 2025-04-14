import asyncio
import websockets
from typing import Dict, Set, Callable, Any
from .secure_protocol import SecureProtocol
from ..utils.error_handling import KAPESITError, ErrorSeverity
from ..utils.config_manager import config_manager

class RealtimeHandler:
    def __init__(self):
        self.secure_protocol = SecureProtocol()
        self.connections: Dict[str, websockets.WebSocketServerProtocol] = {}
        self.message_handlers: Dict[str, Set[Callable]] = {}
        self.heartbeat_task = None
        
    async def start_server(self, host: str = "localhost", port: int = 8765):
        try:
            self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
            server = await websockets.serve(self._handle_connection, host, port)
            return server
        except Exception as e:
            raise KAPESITError(
                f"Failed to start realtime server: {str(e)}",
                severity=ErrorSeverity.ERROR,
                component="REALTIME_HANDLER"
            )
    
    async def _handle_connection(self, websocket: websockets.WebSocketServerProtocol, path: str):
        try:
            session_id = await self.secure_protocol.establish_secure_channel(websocket)
            self.connections[session_id] = websocket
            
            try:
                async for message in websocket:
                    await self._process_message(session_id, message)
            except websockets.exceptions.ConnectionClosed:
                await self._handle_disconnection(session_id)
                
        except Exception as e:
            raise KAPESITError(
                f"Connection handling failed: {str(e)}",
                severity=ErrorSeverity.ERROR,
                component="REALTIME_HANDLER"
            )
    
    async def _process_message(self, session_id: str, message: bytes):
        try:
            decrypted = await self.secure_protocol.decrypt_message(session_id, message)
            message_type = decrypted.get("type")
            
            if message_type in self.message_handlers:
                for handler in self.message_handlers[message_type]:
                    await handler(session_id, decrypted)
                    
        except Exception as e:
            raise KAPESITError(
                f"Message processing failed: {str(e)}",
                severity=ErrorSeverity.ERROR,
                component="REALTIME_HANDLER"
            )
    
    async def _handle_disconnection(self, session_id: str):
        if session_id in self.connections:
            del self.connections[session_id]
        self.secure_protocol.close_session(session_id)
    
    async def _heartbeat_loop(self):
        while True:
            try:
                for session_id, websocket in self.connections.items():
                    try:
                        await websocket.ping()
                    except:
                        await self._handle_disconnection(session_id)
                await asyncio.sleep(30)
            except Exception as e:
                raise KAPESITError(
                    f"Heartbeat loop failed: {str(e)}",
                    severity=ErrorSeverity.ERROR,
                    component="REALTIME_HANDLER"
                )
    
    def register_handler(self, message_type: str, handler: Callable):
        if message_type not in self.message_handlers:
            self.message_handlers[message_type] = set()
        self.message_handlers[message_type].add(handler)
    
    async def broadcast(self, message: Dict[str, Any]):
        try:
            for session_id, websocket in self.connections.items():
                encrypted = await self.secure_protocol.encrypt_message(session_id, message)
                await websocket.send(encrypted)
        except Exception as e:
            raise KAPESITError(
                f"Broadcast failed: {str(e)}",
                severity=ErrorSeverity.ERROR,
                component="REALTIME_HANDLER"
            ) 