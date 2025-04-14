import asyncio
import websockets
import json
from typing import Dict, Any, Optional, Callable
from .protocol import Message, Protocol, MessageType
from ..utils.error_handling import KAPESITError, ErrorSeverity
from ..utils.config_manager import config_manager

class CommunicationClient:
    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.session_id: Optional[str] = None
        self.message_handlers: Dict[MessageType, Callable] = {}
        self.connected = False
        self.reconnect_task = None
        
    async def connect(self):
        try:
            self.websocket = await websockets.connect(f"ws://{self.host}:{self.port}")
            self.connected = True
            self.reconnect_task = asyncio.create_task(self._reconnect_loop())
            await self._start_message_loop()
        except Exception as e:
            raise KAPESITError(
                f"Connection failed: {str(e)}",
                severity=ErrorSeverity.ERROR,
                component="COMMUNICATION_CLIENT"
            )
    
    async def disconnect(self):
        try:
            if self.reconnect_task:
                self.reconnect_task.cancel()
            if self.websocket:
                await self.websocket.close()
            self.connected = False
        except Exception as e:
            raise KAPESITError(
                f"Disconnection failed: {str(e)}",
                severity=ErrorSeverity.ERROR,
                component="COMMUNICATION_CLIENT"
            )
    
    async def _reconnect_loop(self):
        while True:
            try:
                if not self.connected:
                    await self.connect()
                await asyncio.sleep(5)
            except Exception as e:
                raise KAPESITError(
                    f"Reconnect loop failed: {str(e)}",
                    severity=ErrorSeverity.ERROR,
                    component="COMMUNICATION_CLIENT"
                )
    
    async def _start_message_loop(self):
        try:
            while self.connected and self.websocket:
                try:
                    message = await self.websocket.recv()
                    await self._handle_message(message)
                except websockets.exceptions.ConnectionClosed:
                    self.connected = False
                    break
        except Exception as e:
            raise KAPESITError(
                f"Message loop failed: {str(e)}",
                severity=ErrorSeverity.ERROR,
                component="COMMUNICATION_CLIENT"
            )
    
    async def _handle_message(self, message: str):
        try:
            data = json.loads(message)
            msg = Message.from_dict(data)
            
            if msg.type in self.message_handlers:
                await self.message_handlers[msg.type](msg)
        except Exception as e:
            raise KAPESITError(
                f"Message handling failed: {str(e)}",
                severity=ErrorSeverity.ERROR,
                component="COMMUNICATION_CLIENT"
            )
    
    def register_handler(self, message_type: MessageType, handler: Callable):
        self.message_handlers[message_type] = handler
    
    async def send_message(self, message: Message):
        try:
            if not self.connected or not self.websocket:
                raise ValueError("Not connected")
                
            await self.websocket.send(json.dumps(message.to_dict()))
        except Exception as e:
            raise KAPESITError(
                f"Message sending failed: {str(e)}",
                severity=ErrorSeverity.ERROR,
                component="COMMUNICATION_CLIENT"
            )
    
    async def send_command(self, command: str, args: Dict[str, Any]):
        message = Protocol.create_command(command, args)
        await self.send_message(message)
    
    async def send_data(self, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None):
        message = Protocol.create_data(data, metadata)
        await self.send_message(message)
    
    async def send_stream(self, data: Dict[str, Any], stream_id: str):
        message = Protocol.create_stream(data, stream_id)
        await self.send_message(message)
    
    async def send_control(self, action: str, params: Dict[str, Any]):
        message = Protocol.create_control(action, params)
        await self.send_message(message)
    
    async def send_config(self, config: Dict[str, Any]):
        message = Protocol.create_config(config)
        await self.send_message(message)
    
    async def authenticate(self, token: str):
        message = Protocol.create_auth(token)
        await self.send_message(message)
    
    async def exchange_key(self, key: str):
        message = Protocol.create_key_exchange(key)
        await self.send_message(message) 