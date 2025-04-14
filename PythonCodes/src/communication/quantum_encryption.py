from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, execute, Aer
from qiskit.circuit.library import QFT
import numpy as np
from typing import Tuple, List
from ..utils.error_handling import KAPESITError, ErrorSeverity

class QuantumEncryption:
    def __init__(self, key_length: int = 256):
        self.key_length = key_length
        self.simulator = Aer.get_backend('qasm_simulator')
        
    def generate_quantum_key(self) -> List[int]:
        qr = QuantumRegister(self.key_length)
        cr = ClassicalRegister(self.key_length)
        circuit = QuantumCircuit(qr, cr)
        
        # Apply Hadamard gates to create superposition
        for i in range(self.key_length):
            circuit.h(qr[i])
            
        # Measure qubits
        circuit.measure(qr, cr)
        
        # Execute circuit
        job = execute(circuit, self.simulator, shots=1)
        result = job.result()
        counts = result.get_counts(circuit)
        
        # Convert measurement to binary key
        key = [int(bit) for bit in list(counts.keys())[0]]
        return key
    
    def encrypt_message(self, message: str, key: List[int]) -> bytes:
        try:
            message_bytes = message.encode('utf-8')
            encrypted = bytearray()
            
            for i, byte in enumerate(message_bytes):
                key_byte = key[i % len(key)]
                encrypted.append(byte ^ key_byte)
                
            return bytes(encrypted)
        except Exception as e:
            raise KAPESITError(
                f"Encryption failed: {str(e)}",
                severity=ErrorSeverity.ERROR,
                component="QUANTUM_ENCRYPTION"
            )
    
    def decrypt_message(self, encrypted: bytes, key: List[int]) -> str:
        try:
            decrypted = bytearray()
            
            for i, byte in enumerate(encrypted):
                key_byte = key[i % len(key)]
                decrypted.append(byte ^ key_byte)
                
            return decrypted.decode('utf-8')
        except Exception as e:
            raise KAPESITError(
                f"Decryption failed: {str(e)}",
                severity=ErrorSeverity.ERROR,
                component="QUANTUM_ENCRYPTION"
            )
    
    def create_entangled_pair(self) -> Tuple[QuantumCircuit, QuantumCircuit]:
        qr = QuantumRegister(2)
        circuit = QuantumCircuit(qr)
        
        # Create Bell state
        circuit.h(qr[0])
        circuit.cx(qr[0], qr[1])
        
        return circuit, circuit.copy() 