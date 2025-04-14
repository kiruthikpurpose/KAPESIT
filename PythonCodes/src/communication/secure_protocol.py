import asyncio
import websockets
import json
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
from .quantum_encryption import QuantumEncryption
from ..utils.error_handling import KAPESITError, ErrorSeverity
from ..utils.config_manager import config_manager

class SecureProtocol:
    def __init__(self):
        self.quantum_enc = QuantumEncryption()
        self.session_keys: Dict[str, bytes] = {}
        self.fernet_keys: Dict[str, Fernet] = {}
        
    async def establish_secure_channel(self, websocket: websockets.WebSocketServerProtocol) -> str:
        try:
            # Generate quantum key
            quantum_key = self.quantum_enc.generate_quantum_key()
            
            # Create session key
            session_key = Fernet.generate_key()
            fernet = Fernet(session_key)
            
            # Encrypt session key with quantum key
            encrypted_key = self.quantum_enc.encrypt_message(session_key.decode(), quantum_key)
            
            # Send encrypted session key
            await websocket.send(json.dumps({
                "type": "key_exchange",
                "key": encrypted_key.hex()
            }))
            
            # Store session information
            session_id = websocket.id
            self.session_keys[session_id] = session_key
            self.fernet_keys[session_id] = fernet
            
            return session_id
            
        except Exception as e:
            raise KAPESITError(
                f"Secure channel establishment failed: {str(e)}",
                severity=ErrorSeverity.ERROR,
                component="SECURE_PROTOCOL"
            )
    
    async def encrypt_message(self, session_id: str, message: Dict[str, Any]) -> bytes:
        try:
            if session_id not in self.fernet_keys:
                raise ValueError("Invalid session ID")
                
            fernet = self.fernet_keys[session_id]
            message_str = json.dumps(message)
            return fernet.encrypt(message_str.encode())
            
        except Exception as e:
            raise KAPESITError(
                f"Message encryption failed: {str(e)}",
                severity=ErrorSeverity.ERROR,
                component="SECURE_PROTOCOL"
            )
    
    async def decrypt_message(self, session_id: str, encrypted: bytes) -> Dict[str, Any]:
        try:
            if session_id not in self.fernet_keys:
                raise ValueError("Invalid session ID")
                
            fernet = self.fernet_keys[session_id]
            decrypted = fernet.decrypt(encrypted)
            return json.loads(decrypted.decode())
            
        except Exception as e:
            raise KAPESITError(
                f"Message decryption failed: {str(e)}",
                severity=ErrorSeverity.ERROR,
                component="SECURE_PROTOCOL"
            )
    
    def close_session(self, session_id: str) -> None:
        if session_id in self.session_keys:
            del self.session_keys[session_id]
        if session_id in self.fernet_keys:
            del self.fernet_keys[session_id] 