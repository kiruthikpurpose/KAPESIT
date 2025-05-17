import numpy as np
from typing import Dict, List, Tuple, Optional, Union, Any, Callable
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.aqua.algorithms import VQE, QAOA
from qiskit.aqua.components.optimizers import COBYLA, SPSA, ADAM
from qiskit.aqua.components.variational_forms import RYRZ, RY
from qiskit.optimization import QuadraticProgram
from qiskit.optimization.algorithms import MinimumEigenOptimizer
from qiskit.optimization.converters import QuadraticProgramToQubo
from qiskit.optimization.applications import Maxcut, Tsp
from qiskit.aqua.operators import WeightedPauliOperator
from qiskit.aqua.algorithms import NumPyMinimumEigensolver

class QuantumOptimization:
    def __init__(self, num_qubits: int, num_layers: int = 3):
        if num_qubits <= 0:
            raise ValueError("Number of qubits must be positive")
        if num_layers <= 0:
            raise ValueError("Number of layers must be positive")
            
        self.num_qubits = num_qubits
        self.num_layers = num_layers
        self.optimizer = COBYLA(maxiter=1000)
        self.variational_form = RYRZ(num_qubits, depth=num_layers)
        self.initial_point = np.random.random(self.variational_form.num_parameters)
        self.circuit = QuantumCircuit(num_qubits)
        self._build_circuit()
        
        self.quadratic_program: Optional[QuadraticProgram] = None
        self.qubo: Optional[QuadraticProgram] = None
        self.operator: Optional[WeightedPauliOperator] = None
        self.optimizer_result: Optional[Any] = None
    
    def _build_circuit(self) -> None:
        for layer in range(self.num_layers):
            for qubit in range(self.num_qubits):
                self.circuit.ry(self.initial_point[2 * (layer * self.num_qubits + qubit)], qubit)
                self.circuit.rz(self.initial_point[2 * (layer * self.num_qubits + qubit) + 1], qubit)
            for qubit in range(self.num_qubits - 1):
                self.circuit.cx(qubit, qubit + 1)
    
    def set_quadratic_program(self, program: QuadraticProgram) -> None:
        if not isinstance(program, QuadraticProgram):
            raise TypeError("Program must be a QuadraticProgram")
            
        self.quadratic_program = program
        converter = QuadraticProgramToQubo()
        self.qubo = converter.convert(program)
        self.operator = self.qubo.to_ising()[0]
    
    def optimize_quadratic_program(self, use_exact: bool = False) -> Dict[str, Any]:
        if self.quadratic_program is None:
            raise ValueError("No quadratic program set")
            
        if use_exact:
            solver = NumPyMinimumEigensolver()
        else:
            solver = QAOA(optimizer=self.optimizer, p=self.num_layers)
        
        optimizer = MinimumEigenOptimizer(solver)
        self.optimizer_result = optimizer.solve(self.quadratic_program)
        
        return {
            "optimal_value": float(self.optimizer_result.fval),
            "optimal_solution": self.optimizer_result.x.tolist(),
            "status": self.optimizer_result.status
        }
    
    def solve_maxcut(self, graph: List[Tuple[int, int, float]]) -> Dict[str, Any]:
        if not isinstance(graph, list):
            raise TypeError("Graph must be a list of edges")
        if not all(isinstance(edge, tuple) and len(edge) == 3 for edge in graph):
            raise TypeError("Each edge must be a tuple of (node1, node2, weight)")
            
        maxcut = Maxcut(graph)
        self.quadratic_program = maxcut.to_quadratic_program()
        return self.optimize_quadratic_program()
    
    def solve_tsp(self, coordinates: List[Tuple[float, float]]) -> Dict[str, Any]:
        if not isinstance(coordinates, list):
            raise TypeError("Coordinates must be a list of points")
        if not all(isinstance(point, tuple) and len(point) == 2 for point in coordinates):
            raise TypeError("Each point must be a tuple of (x, y)")
            
        tsp = Tsp(coordinates)
        self.quadratic_program = tsp.to_quadratic_program()
        return self.optimize_quadratic_program()
    
    def optimize_custom_function(self, objective: Callable[[np.ndarray], float], 
                               constraints: Optional[List[Callable[[np.ndarray], float]]] = None,
                               bounds: Optional[List[Tuple[float, float]]] = None) -> Dict[str, Any]:
        if not callable(objective):
            raise TypeError("Objective must be a callable function")
        if constraints is not None and not all(callable(c) for c in constraints):
            raise TypeError("All constraints must be callable functions")
        if bounds is not None and not all(isinstance(b, tuple) and len(b) == 2 for b in bounds):
            raise TypeError("Bounds must be a list of (min, max) tuples")
            
        program = QuadraticProgram()
        
        for i in range(self.num_qubits):
            program.binary_var(f'x_{i}')
        
        if bounds is not None:
            for i, (min_val, max_val) in enumerate(bounds):
                program.linear_constraint(linear={f'x_{i}': 1}, sense='>=', rhs=min_val)
                program.linear_constraint(linear={f'x_{i}': 1}, sense='<=', rhs=max_val)
        
        if constraints is not None:
            for i, constraint in enumerate(constraints):
                program.quadratic_constraint(
                    quadratic={f'x_{j}': 1 for j in range(self.num_qubits)},
                    linear={},
                    sense='<=',
                    rhs=0,
                    name=f'constraint_{i}'
                )
        
        self.quadratic_program = program
        return self.optimize_quadratic_program()
    
    def get_optimal_value(self) -> float:
        if self.optimizer_result is None:
            raise ValueError("No optimization result available")
        return float(self.optimizer_result.fval)
    
    def get_optimal_solution(self) -> List[float]:
        if self.optimizer_result is None:
            raise ValueError("No optimization result available")
        return self.optimizer_result.x.tolist()
    
    def get_optimization_status(self) -> str:
        if self.optimizer_result is None:
            raise ValueError("No optimization result available")
        return str(self.optimizer_result.status)
    
    def get_operator(self) -> WeightedPauliOperator:
        if self.operator is None:
            raise ValueError("No operator available")
        return self.operator
    
    def get_qubo(self) -> QuadraticProgram:
        if self.qubo is None:
            raise ValueError("No QUBO available")
        return self.qubo
    
    def get_quadratic_program(self) -> QuadraticProgram:
        if self.quadratic_program is None:
            raise ValueError("No quadratic program available")
        return self.quadratic_program 