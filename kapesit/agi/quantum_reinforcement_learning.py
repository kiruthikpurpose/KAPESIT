import numpy as np
from typing import Dict, List, Tuple, Optional, Union, Any, Callable
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.aqua.algorithms import VQE
from qiskit.aqua.components.optimizers import COBYLA, SPSA, ADAM
from qiskit.aqua.components.variational_forms import RYRZ, RY
from qiskit.aqua.components.feature_maps import SecondOrderExpansion
from qiskit.aqua.operators import WeightedPauliOperator
from qiskit.aqua.algorithms import NumPyMinimumEigensolver

class QuantumReinforcementLearning:
    def __init__(self, num_qubits: int, num_layers: int = 3, learning_rate: float = 0.01,
                 discount_factor: float = 0.99, epsilon: float = 0.1):
        if num_qubits <= 0:
            raise ValueError("Number of qubits must be positive")
        if num_layers <= 0:
            raise ValueError("Number of layers must be positive")
        if not 0 < learning_rate <= 1:
            raise ValueError("Learning rate must be between 0 and 1")
        if not 0 < discount_factor <= 1:
            raise ValueError("Discount factor must be between 0 and 1")
        if not 0 <= epsilon <= 1:
            raise ValueError("Epsilon must be between 0 and 1")
            
        self.num_qubits = num_qubits
        self.num_layers = num_layers
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        
        self.optimizer = COBYLA(maxiter=1000)
        self.variational_form = RYRZ(num_qubits, depth=num_layers)
        self.feature_map = SecondOrderExpansion(feature_dimension=num_qubits, depth=2)
        self.initial_point = np.random.random(self.variational_form.num_parameters)
        self.circuit = QuantumCircuit(num_qubits)
        self._build_circuit()
        
        self.q_table: Dict[Tuple[int, ...], Dict[int, float]] = {}
        self.policy: Dict[Tuple[int, ...], int] = {}
        self.rewards: List[float] = []
        self.episodes: List[int] = []
        self.avg_rewards: List[float] = []
    
    def _build_circuit(self) -> None:
        for layer in range(self.num_layers):
            for qubit in range(self.num_qubits):
                self.circuit.ry(self.initial_point[2 * (layer * self.num_qubits + qubit)], qubit)
                self.circuit.rz(self.initial_point[2 * (layer * self.num_qubits + qubit) + 1], qubit)
            for qubit in range(self.num_qubits - 1):
                self.circuit.cx(qubit, qubit + 1)
    
    def get_action(self, state: Tuple[int, ...], available_actions: List[int]) -> int:
        if not isinstance(state, tuple):
            raise TypeError("State must be a tuple")
        if not isinstance(available_actions, list):
            raise TypeError("Available actions must be a list")
        if not all(isinstance(a, int) for a in available_actions):
            raise TypeError("All actions must be integers")
            
        if state not in self.q_table:
            self.q_table[state] = {action: 0.0 for action in available_actions}
        
        if np.random.random() < self.epsilon:
            return np.random.choice(available_actions)
        
        return max(self.q_table[state].items(), key=lambda x: x[1])[0]
    
    def update_q_value(self, state: Tuple[int, ...], action: int, reward: float,
                      next_state: Tuple[int, ...], next_available_actions: List[int]) -> None:
        if not isinstance(state, tuple):
            raise TypeError("State must be a tuple")
        if not isinstance(action, int):
            raise TypeError("Action must be an integer")
        if not isinstance(reward, (int, float)):
            raise TypeError("Reward must be a number")
        if not isinstance(next_state, tuple):
            raise TypeError("Next state must be a tuple")
        if not isinstance(next_available_actions, list):
            raise TypeError("Next available actions must be a list")
        if not all(isinstance(a, int) for a in next_available_actions):
            raise TypeError("All next available actions must be integers")
            
        if state not in self.q_table:
            self.q_table[state] = {}
        if action not in self.q_table[state]:
            self.q_table[state][action] = 0.0
            
        if next_state not in self.q_table:
            self.q_table[next_state] = {action: 0.0 for action in next_available_actions}
        
        next_max_q = max(self.q_table[next_state].values())
        current_q = self.q_table[state][action]
        
        new_q = current_q + self.learning_rate * (reward + self.discount_factor * next_max_q - current_q)
        self.q_table[state][action] = new_q
    
    def update_policy(self, state: Tuple[int, ...]) -> None:
        if not isinstance(state, tuple):
            raise TypeError("State must be a tuple")
            
        if state in self.q_table:
            self.policy[state] = max(self.q_table[state].items(), key=lambda x: x[1])[0]
    
    def train(self, num_episodes: int, env: Any, max_steps: int = 100) -> None:
        if num_episodes <= 0:
            raise ValueError("Number of episodes must be positive")
        if max_steps <= 0:
            raise ValueError("Maximum steps must be positive")
            
        for episode in range(num_episodes):
            state = env.reset()
            total_reward = 0
            
            for step in range(max_steps):
                available_actions = env.get_available_actions()
                action = self.get_action(state, available_actions)
                
                next_state, reward, done, _ = env.step(action)
                next_available_actions = env.get_available_actions()
                
                self.update_q_value(state, action, reward, next_state, next_available_actions)
                self.update_policy(state)
                
                total_reward += reward
                state = next_state
                
                if done:
                    break
            
            self.rewards.append(total_reward)
            self.episodes.append(episode)
            self.avg_rewards.append(np.mean(self.rewards[-100:]))
    
    def get_q_value(self, state: Tuple[int, ...], action: int) -> float:
        if not isinstance(state, tuple):
            raise TypeError("State must be a tuple")
        if not isinstance(action, int):
            raise TypeError("Action must be an integer")
            
        if state not in self.q_table or action not in self.q_table[state]:
            return 0.0
        
        return float(self.q_table[state][action])
    
    def get_policy(self, state: Tuple[int, ...]) -> int:
        if not isinstance(state, tuple):
            raise TypeError("State must be a tuple")
            
        if state not in self.policy:
            return 0
        
        return self.policy[state]
    
    def get_rewards(self) -> List[float]:
        return self.rewards
    
    def get_episodes(self) -> List[int]:
        return self.episodes
    
    def get_avg_rewards(self) -> List[float]:
        return self.avg_rewards
    
    def get_q_table(self) -> Dict[Tuple[int, ...], Dict[int, float]]:
        return self.q_table
    
    def get_policy_table(self) -> Dict[Tuple[int, ...], int]:
        return self.policy
    
    def set_learning_rate(self, learning_rate: float) -> None:
        if not 0 < learning_rate <= 1:
            raise ValueError("Learning rate must be between 0 and 1")
            
        self.learning_rate = learning_rate
    
    def set_discount_factor(self, discount_factor: float) -> None:
        if not 0 < discount_factor <= 1:
            raise ValueError("Discount factor must be between 0 and 1")
            
        self.discount_factor = discount_factor
    
    def set_epsilon(self, epsilon: float) -> None:
        if not 0 <= epsilon <= 1:
            raise ValueError("Epsilon must be between 0 and 1")
            
        self.epsilon = epsilon
    
    def get_circuit(self) -> QuantumCircuit:
        return self.circuit
    
    def get_feature_map(self) -> SecondOrderExpansion:
        return self.feature_map
    
    def get_variational_form(self) -> RYRZ:
        return self.variational_form 