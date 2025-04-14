import asyncio
import pytest
import time
from src.communication.communication_manager import CommunicationManager
from src.communication.client import CommunicationClient
from src.communication.protocol import Message, Protocol, MessageType

@pytest.fixture
async def benchmark_manager():
    manager = CommunicationManager()
    server = await manager.start(host="localhost", port=8766)
    yield manager
    await manager.stop()
    server.close()
    await server.wait_closed()

@pytest.fixture
async def benchmark_client():
    client = CommunicationClient(host="localhost", port=8766)
    await client.connect()
    yield client
    await client.disconnect()

@pytest.mark.benchmark
async def test_message_latency(benchmark_manager, benchmark_client):
    # Test message round-trip latency
    latencies = []
    
    async def handle_message(message: Message):
        end_time = time.perf_counter()
        latencies.append(end_time - start_time)
    
    benchmark_client.register_handler(MessageType.DATA, handle_message)
    
    # Send 100 messages and measure latency
    for _ in range(100):
        start_time = time.perf_counter()
        await benchmark_client.send_data({"test": "data"})
        await asyncio.sleep(0.001)  # Small delay between messages
    
    await asyncio.sleep(0.5)  # Wait for all messages to be processed
    
    # Calculate statistics
    avg_latency = sum(latencies) / len(latencies)
    max_latency = max(latencies)
    min_latency = min(latencies)
    
    print(f"\nMessage Latency Statistics:")
    print(f"Average: {avg_latency * 1000:.2f}ms")
    print(f"Maximum: {max_latency * 1000:.2f}ms")
    print(f"Minimum: {min_latency * 1000:.2f}ms")
    
    assert avg_latency < 0.1  # Average latency should be less than 100ms

@pytest.mark.benchmark
async def test_message_throughput(benchmark_manager, benchmark_client):
    # Test message throughput
    message_count = 1000
    start_time = time.perf_counter()
    
    async def handle_message(message: Message):
        pass  # Just acknowledge receipt
    
    benchmark_client.register_handler(MessageType.DATA, handle_message)
    
    # Send messages as fast as possible
    for _ in range(message_count):
        await benchmark_client.send_data({"test": "data"})
    
    end_time = time.perf_counter()
    duration = end_time - start_time
    throughput = message_count / duration
    
    print(f"\nMessage Throughput:")
    print(f"Messages per second: {throughput:.2f}")
    print(f"Total duration: {duration:.2f}s")
    
    assert throughput > 100  # Should handle at least 100 messages per second

@pytest.mark.benchmark
async def test_concurrent_connections(benchmark_manager):
    # Test handling multiple concurrent connections
    client_count = 50
    clients = []
    messages_received = 0
    
    async def handle_message(message: Message):
        nonlocal messages_received
        messages_received += 1
    
    # Create and connect multiple clients
    for _ in range(client_count):
        client = CommunicationClient(host="localhost", port=8766)
        await client.connect()
        client.register_handler(MessageType.DATA, handle_message)
        clients.append(client)
    
    # Send messages from all clients
    start_time = time.perf_counter()
    for client in clients:
        for _ in range(10):
            await client.send_data({"test": "data"})
    
    await asyncio.sleep(1)  # Wait for messages to be processed
    end_time = time.perf_counter()
    
    # Cleanup
    for client in clients:
        await client.disconnect()
    
    duration = end_time - start_time
    total_messages = client_count * 10
    throughput = total_messages / duration
    
    print(f"\nConcurrent Connection Test:")
    print(f"Total messages sent: {total_messages}")
    print(f"Messages received: {messages_received}")
    print(f"Duration: {duration:.2f}s")
    print(f"Throughput: {throughput:.2f} messages/second")
    
    assert messages_received == total_messages  # All messages should be received
    assert throughput > 100  # Should handle at least 100 messages per second

@pytest.mark.benchmark
async def test_large_message_handling(benchmark_manager, benchmark_client):
    # Test handling of large messages
    message_sizes = [1, 10, 100, 1000]  # KB
    results = []
    
    async def handle_message(message: Message):
        pass  # Just acknowledge receipt
    
    benchmark_client.register_handler(MessageType.DATA, handle_message)
    
    for size_kb in message_sizes:
        # Create large message
        large_data = {"data": "x" * (size_kb * 1024)}
        
        # Measure send time
        start_time = time.perf_counter()
        await benchmark_client.send_data(large_data)
        await asyncio.sleep(0.1)  # Wait for message to be processed
        end_time = time.perf_counter()
        
        duration = end_time - start_time
        results.append((size_kb, duration))
        
        print(f"\nMessage Size: {size_kb}KB")
        print(f"Duration: {duration * 1000:.2f}ms")
        
        assert duration < 1.0  # Should handle large messages in under 1 second
    
    print("\nLarge Message Handling Summary:")
    for size_kb, duration in results:
        print(f"{size_kb}KB: {duration * 1000:.2f}ms") 