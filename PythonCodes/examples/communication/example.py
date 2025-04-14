import asyncio
import json
from src.communication.communication_manager import CommunicationManager
from src.communication.client import CommunicationClient
from src.communication.protocol import Message, Protocol, MessageType

async def server_example():
    # Create and start communication manager
    manager = CommunicationManager()
    server = await manager.start(host="localhost", port=8765)
    
    # Register message handlers
    async def handle_data(session_id: str, message: Message):
        print(f"Server received data: {message.payload}")
        # Echo back to client
        await manager.send_message(session_id, message)
    
    async def handle_command(session_id: str, message: Message):
        print(f"Server received command: {message.payload}")
        # Process command and send response
        response = Protocol.create_response(
            message.payload["command"],
            {"result": "success"}
        )
        await manager.send_message(session_id, response)
    
    manager.register_handler("data", handle_data)
    manager.register_handler("command", handle_command)
    
    try:
        # Keep server running
        await asyncio.Future()
    finally:
        await manager.stop()
        server.close()
        await server.wait_closed()

async def client_example():
    # Create and connect client
    client = CommunicationClient(host="localhost", port=8765)
    await client.connect()
    
    # Register message handlers
    async def handle_response(message: Message):
        print(f"Client received response: {message.payload}")
    
    async def handle_data(message: Message):
        print(f"Client received data: {message.payload}")
    
    client.register_handler(MessageType.RESPONSE, handle_response)
    client.register_handler(MessageType.DATA, handle_data)
    
    try:
        # Send various message types
        await client.send_data({"test": "data"})
        await client.send_command("test_command", {"arg": "value"})
        await client.send_control("start", {"param": "value"})
        await client.send_config({"setting": "value"})
        
        # Wait for responses
        await asyncio.sleep(1)
    finally:
        await client.disconnect()

async def quantum_encryption_example():
    # Create communication manager
    manager = CommunicationManager()
    
    # Generate quantum key
    key = manager.secure_protocol.quantum_enc.generate_quantum_key()
    print(f"Generated quantum key: {key[:10]}...")
    
    # Encrypt and decrypt message
    message = "Secret message"
    encrypted = manager.secure_protocol.quantum_enc.encrypt_message(message, key)
    decrypted = manager.secure_protocol.quantum_enc.decrypt_message(encrypted, key)
    
    print(f"Original message: {message}")
    print(f"Encrypted message: {encrypted[:20]}...")
    print(f"Decrypted message: {decrypted}")

async def message_queue_example():
    # Create communication manager
    manager = CommunicationManager()
    
    # Enqueue messages with different priorities
    await manager.message_queue.enqueue("session1", {"priority": "low"}, priority=0)
    await manager.message_queue.enqueue("session1", {"priority": "high"}, priority=1)
    
    # Process messages
    while message := await manager.message_queue.dequeue("session1"):
        print(f"Processed message: {message}")
    
    # Cleanup
    await manager.message_queue.stop()

async def main():
    # Run examples
    print("Running communication examples...")
    
    # Start server in background
    server_task = asyncio.create_task(server_example())
    
    # Run client example
    await client_example()
    
    # Run quantum encryption example
    await quantum_encryption_example()
    
    # Run message queue example
    await message_queue_example()
    
    # Cleanup
    server_task.cancel()
    try:
        await server_task
    except asyncio.CancelledError:
        pass

if __name__ == "__main__":
    asyncio.run(main()) 