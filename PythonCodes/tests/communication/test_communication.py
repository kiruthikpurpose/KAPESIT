import asyncio
import pytest
from src.communication.communication_manager import CommunicationManager
from src.communication.client import CommunicationClient
from src.communication.protocol import Message, Protocol, MessageType
from src.utils.error_handling import KAPESITError, ErrorSeverity

@pytest.fixture
async def communication_manager():
    manager = CommunicationManager()
    server = await manager.start(host="localhost", port=8765)
    yield manager
    await manager.stop()
    server.close()
    await server.wait_closed()

@pytest.fixture
async def communication_client():
    client = CommunicationClient(host="localhost", port=8765)
    await client.connect()
    yield client
    await client.disconnect()

@pytest.mark.asyncio
async def test_secure_connection(communication_manager, communication_client):
    # Test connection establishment
    assert communication_client.connected
    
    # Test message exchange
    received_messages = []
    
    async def handle_message(message: Message):
        received_messages.append(message)
    
    communication_client.register_handler(MessageType.DATA, handle_message)
    
    test_data = {"test": "data"}
    await communication_client.send_data(test_data)
    
    await asyncio.sleep(0.1)  # Wait for message processing
    assert len(received_messages) == 1
    assert received_messages[0].payload == test_data

@pytest.mark.asyncio
async def test_message_queue(communication_manager, communication_client):
    # Test message queuing
    received_messages = []
    
    async def handle_message(message: Message):
        received_messages.append(message)
    
    communication_client.register_handler(MessageType.COMMAND, handle_message)
    
    # Send multiple commands
    commands = ["command1", "command2", "command3"]
    for cmd in commands:
        await communication_client.send_command(cmd, {"arg": "value"})
    
    await asyncio.sleep(0.1)  # Wait for message processing
    assert len(received_messages) == len(commands)
    assert all(msg.type == MessageType.COMMAND for msg in received_messages)

@pytest.mark.asyncio
async def test_error_handling(communication_manager, communication_client):
    # Test error handling
    received_errors = []
    
    async def handle_error(message: Message):
        received_errors.append(message)
    
    communication_client.register_handler(MessageType.ERROR, handle_error)
    
    # Send invalid message
    await communication_client.send_message(Message(
        type=MessageType.DATA,
        payload={"invalid": "data"}
    ))
    
    await asyncio.sleep(0.1)  # Wait for error processing
    assert len(received_errors) > 0
    assert all(msg.type == MessageType.ERROR for msg in received_errors)

@pytest.mark.asyncio
async def test_reconnection(communication_manager, communication_client):
    # Test reconnection
    assert communication_client.connected
    
    # Simulate connection loss
    await communication_client.disconnect()
    assert not communication_client.connected
    
    # Wait for reconnection
    await asyncio.sleep(6)  # Reconnect loop interval is 5 seconds
    assert communication_client.connected

@pytest.mark.asyncio
async def test_protocol_messages(communication_manager, communication_client):
    # Test all protocol message types
    received_messages = []
    
    async def handle_message(message: Message):
        received_messages.append(message)
    
    for msg_type in MessageType:
        communication_client.register_handler(msg_type, handle_message)
    
    # Send all message types
    await communication_client.send_command("test", {"arg": "value"})
    await communication_client.send_data({"test": "data"})
    await communication_client.send_stream({"test": "stream"}, "stream1")
    await communication_client.send_control("test_action", {"param": "value"})
    await communication_client.send_config({"setting": "value"})
    await communication_client.authenticate("test_token")
    await communication_client.exchange_key("test_key")
    
    await asyncio.sleep(0.1)  # Wait for message processing
    assert len(received_messages) == 7  # All message types sent

@pytest.mark.asyncio
async def test_priority_handling(communication_manager, communication_client):
    # Test message priority handling
    received_messages = []
    
    async def handle_message(message: Message):
        received_messages.append(message)
    
    communication_client.register_handler(MessageType.DATA, handle_message)
    
    # Send messages with different priorities
    await communication_client.send_message(Message(
        type=MessageType.DATA,
        payload={"priority": "low"},
        priority=0
    ))
    await communication_client.send_message(Message(
        type=MessageType.DATA,
        payload={"priority": "high"},
        priority=1
    ))
    
    await asyncio.sleep(0.1)  # Wait for message processing
    assert len(received_messages) == 2
    assert received_messages[0].priority == 1  # High priority first
    assert received_messages[1].priority == 0  # Low priority second 