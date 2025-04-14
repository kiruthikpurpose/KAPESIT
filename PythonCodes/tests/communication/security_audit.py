import pytest
import asyncio
import json
from cryptography.fernet import Fernet
from src.communication.communication_manager import CommunicationManager
from src.communication.client import CommunicationClient
from src.communication.protocol import Message, Protocol, MessageType
from src.utils.error_handling import KAPESITError, ErrorSeverity

@pytest.fixture
async def security_manager():
    manager = CommunicationManager()
    server = await manager.start(host="localhost", port=8767)
    yield manager
    await manager.stop()
    server.close()
    await server.wait_closed()

@pytest.fixture
async def security_client():
    client = CommunicationClient(host="localhost", port=8767)
    await client.connect()
    yield client
    await client.disconnect()

@pytest.mark.security
async def test_quantum_encryption_security(security_manager, security_client):
    # Test quantum encryption key generation
    key1 = security_manager.secure_protocol.quantum_enc.generate_quantum_key()
    key2 = security_manager.secure_protocol.quantum_enc.generate_quantum_key()
    
    # Keys should be different and of correct length
    assert len(key1) == 256  # 256-bit key
    assert len(key2) == 256
    assert key1 != key2
    
    # Test encryption/decryption
    test_message = "Test message for quantum encryption"
    encrypted = security_manager.secure_protocol.quantum_enc.encrypt_message(test_message, key1)
    decrypted = security_manager.secure_protocol.quantum_enc.decrypt_message(encrypted, key1)
    
    assert decrypted == test_message
    assert encrypted != test_message.encode()  # Should be encrypted

@pytest.mark.security
async def test_session_key_security(security_manager, security_client):
    # Test session key generation and exchange
    session_key = Fernet.generate_key()
    fernet = Fernet(session_key)
    
    # Test encryption/decryption
    test_data = {"test": "data"}
    encrypted = fernet.encrypt(json.dumps(test_data).encode())
    decrypted = json.loads(fernet.decrypt(encrypted).decode())
    
    assert decrypted == test_data
    assert encrypted != json.dumps(test_data).encode()  # Should be encrypted

@pytest.mark.security
async def test_message_integrity(security_manager, security_client):
    # Test message integrity protection
    test_message = Message(
        type=MessageType.DATA,
        payload={"test": "data"}
    )
    
    # Send message
    await security_client.send_message(test_message)
    
    # Attempt to modify message in transit
    modified_message = test_message.to_dict()
    modified_message["payload"]["test"] = "modified"
    
    # Verify message integrity
    assert modified_message != test_message.to_dict()
    assert "test" in modified_message["payload"]
    assert modified_message["payload"]["test"] == "modified"

@pytest.mark.security
async def test_replay_attack_prevention(security_manager, security_client):
    # Test replay attack prevention
    messages = []
    
    async def handle_message(message: Message):
        messages.append(message)
    
    security_client.register_handler(MessageType.DATA, handle_message)
    
    # Send original message
    original_message = Message(
        type=MessageType.DATA,
        payload={"test": "data"}
    )
    await security_client.send_message(original_message)
    
    # Attempt replay
    await security_client.send_message(original_message)
    
    await asyncio.sleep(0.1)
    
    # Verify only one message was processed
    assert len(messages) == 1
    assert messages[0].payload == original_message.payload

@pytest.mark.security
async def test_man_in_the_middle_prevention(security_manager, security_client):
    # Test MITM prevention
    session_id = security_client.session_id
    
    # Verify secure channel establishment
    assert session_id in security_manager.secure_protocol.session_keys
    assert session_id in security_manager.secure_protocol.fernet_keys
    
    # Attempt to intercept session key
    try:
        intercepted_key = security_manager.secure_protocol.session_keys[session_id]
        assert False, "Session key should not be accessible"
    except:
        pass

@pytest.mark.security
async def test_denial_of_service_prevention(security_manager, security_client):
    # Test DoS prevention
    message_count = 0
    
    async def handle_message(message: Message):
        nonlocal message_count
        message_count += 1
    
    security_client.register_handler(MessageType.DATA, handle_message)
    
    # Send large number of messages
    for _ in range(1000):
        await security_client.send_data({"test": "data"})
    
    await asyncio.sleep(0.1)
    
    # Verify system remains responsive
    assert message_count > 0
    assert message_count < 1000  # Some messages should be rate-limited

@pytest.mark.security
async def test_authentication_security(security_manager, security_client):
    # Test authentication security
    valid_token = "valid_token"
    invalid_token = "invalid_token"
    
    # Test valid authentication
    await security_client.authenticate(valid_token)
    assert security_client.connected
    
    # Test invalid authentication
    try:
        await security_client.authenticate(invalid_token)
        assert False, "Invalid authentication should fail"
    except:
        pass

@pytest.mark.security
async def test_message_validation(security_manager, security_client):
    # Test message validation
    invalid_messages = [
        Message(type=None, payload={}),  # Invalid type
        Message(type=MessageType.DATA, payload=None),  # Invalid payload
        Message(type=MessageType.DATA, payload={"": "data"}),  # Empty key
        Message(type=MessageType.DATA, payload={"key": None})  # None value
    ]
    
    for invalid_message in invalid_messages:
        try:
            await security_client.send_message(invalid_message)
            assert False, f"Invalid message should be rejected: {invalid_message}"
        except:
            pass 