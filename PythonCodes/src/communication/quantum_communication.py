from typing import List, Tuple, Dict
import random
import math

class QuantumState:
    def __init__(self, qubit_count: int):
        self.qubit_count = qubit_count
        self.state = [complex(1.0, 0.0)] + [complex(0.0, 0.0)] * (2**qubit_count - 1)
        
    def apply_hadamard(self, qubit: int):
        h = 1/math.sqrt(2)
        for i in range(2**self.qubit_count):
            if i & (1 << qubit):
                self.state[i], self.state[i ^ (1 << qubit)] = \
                    h * (self.state[i ^ (1 << qubit)] - self.state[i]), \
                    h * (self.state[i ^ (1 << qubit)] + self.state[i])

class QuantumChannel:
    def __init__(self, noise_level: float = 0.01):
        self.noise_level = noise_level
        self.entangled_pairs = []
        
    def generate_bell_pair(self) -> Tuple[QuantumState, QuantumState]:
        alice_qubit = QuantumState(1)
        bob_qubit = QuantumState(1)
        
        alice_qubit.apply_hadamard(0)
        
        if random.random() > self.noise_level:
            bob_qubit.state = alice_qubit.state.copy()
        
        return alice_qubit, bob_qubit
    
    def measure_correlation(self, state1: QuantumState, 
                          state2: QuantumState) -> float:
        correlation = 0
        for i in range(len(state1.state)):
            correlation += abs(state1.state[i] * state2.state[i].conjugate())
        return correlation

class QuantumCommunicator:
    def __init__(self, error_correction: bool = True):
        self.channel = QuantumChannel()
        self.error_correction = error_correction
        self.key_buffer = []
        
    def generate_key(self, length: int) -> List[int]:
        key = []
        while len(key) < length:
            alice, bob = self.channel.generate_bell_pair()
            correlation = self.channel.measure_correlation(alice, bob)
            
            if correlation > 0.9:
                key.append(1 if random.random() > 0.5 else 0)
                
        return key
    
    def encode_message(self, message: str, key: List[int]) -> List[int]:
        encoded = []
        message_bits = ''.join(format(ord(c), '08b') for c in message)
        
        for i, bit in enumerate(message_bits):
            encoded.append(int(bit) ^ key[i % len(key)])
            
        return encoded