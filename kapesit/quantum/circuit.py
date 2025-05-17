from typing import List, Optional, Union
import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.quantum_info import Statevector
from qiskit.providers.aer import AerSimulator

class QuantumEngine:
    def __init__(self, num_qubits: int = 2):
        self.num_qubits = num_qubits
        self.qr = QuantumRegister(num_qubits, 'q')
        self.cr = ClassicalRegister(num_qubits, 'c')
        self.circuit = QuantumCircuit(self.qr, self.cr)
        self.simulator = AerSimulator()
    
    def apply_hadamard(self, qubit: int) -> None:
        self.circuit.h(qubit)
    
    def apply_cnot(self, control: int, target: int) -> None:
        self.circuit.cx(control, target)
    
    def apply_phase(self, qubit: int, phase: float) -> None:
        self.circuit.p(phase, qubit)
    
    def measure_all(self) -> None:
        self.circuit.measure(self.qr, self.cr)
    
    def get_statevector(self) -> Statevector:
        return Statevector.from_instruction(self.circuit)
    
    def run_simulation(self, shots: int = 1000) -> dict:
        job = self.simulator.run(self.circuit, shots=shots)
        result = job.result()
        return result.get_counts()
    
    def reset(self) -> None:
        self.circuit = QuantumCircuit(self.qr, self.cr)
    
    def visualize(self) -> None:
        print(self.circuit)
    
    def get_entanglement(self) -> float:
        state = self.get_statevector()
        return np.abs(state.data[0]) ** 2
    
    def create_bell_state(self) -> None:
        self.reset()
        self.apply_hadamard(0)
        self.apply_cnot(0, 1)
    
    def create_ghz_state(self) -> None:
        self.reset()
        self.apply_hadamard(0)
        for i in range(self.num_qubits - 1):
            self.apply_cnot(i, i + 1) 