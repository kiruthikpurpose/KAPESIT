import numpy as np
from typing import List, Tuple, Optional
import math

class NeuralNetwork:
    def __init__(self, layers: List[int], activation: str = 'relu'):
        self.layers = layers
        self.weights = []
        self.biases = []
        self.initialize_weights()
        self.activation = activation

    def initialize_weights(self):
        for i in range(len(self.layers) - 1):
            weight = np.random.randn(self.layers[i], self.layers[i + 1]) * np.sqrt(2 / self.layers[i])
            bias = np.zeros((1, self.layers[i + 1]))
            self.weights.append(weight)
            self.biases.append(bias)

    def relu(self, x: np.ndarray) -> np.ndarray:
        return np.maximum(0, x)

    def sigmoid(self, x: np.ndarray) -> np.ndarray:
        return 1 / (1 + np.exp(-x))

    def softmax(self, x: np.ndarray) -> np.ndarray:
        exp_x = np.exp(x - np.max(x, axis=1, keepdims=True))
        return exp_x / np.sum(exp_x, axis=1, keepdims=True)

    def forward(self, x: np.ndarray) -> np.ndarray:
        a = x
        for i in range(len(self.weights) - 1):
            z = np.dot(a, self.weights[i]) + self.biases[i]
            if self.activation == 'relu':
                a = self.relu(z)
            elif self.activation == 'sigmoid':
                a = self.sigmoid(z)
        
        # Output layer
        z = np.dot(a, self.weights[-1]) + self.biases[-1]
        return self.softmax(z)

    def backward(self, x: np.ndarray, y: np.ndarray, learning_rate: float = 0.01) -> float:
        # Forward pass
        activations = [x]
        zs = []
        a = x
        for i in range(len(self.weights) - 1):
            z = np.dot(a, self.weights[i]) + self.biases[i]
            zs.append(z)
            if self.activation == 'relu':
                a = self.relu(z)
            elif self.activation == 'sigmoid':
                a = self.sigmoid(z)
            activations.append(a)
        
        # Output layer
        z = np.dot(a, self.weights[-1]) + self.biases[-1]
        zs.append(z)
        a = self.softmax(z)
        activations.append(a)

        # Backward pass
        delta = activations[-1] - y
        gradients = []
        
        for i in range(len(self.weights) - 1, -1, -1):
            if self.activation == 'relu':
                delta = delta * (activations[i] > 0)
            elif self.activation == 'sigmoid':
                delta = delta * (activations[i] * (1 - activations[i]))
            
            gradient = np.dot(activations[i].T, delta)
            gradients.append((gradient, np.sum(delta, axis=0, keepdims=True)))
            
            if i > 0:
                delta = np.dot(delta, self.weights[i].T)

        # Update weights and biases
        for i in range(len(self.weights)):
            self.weights[i] -= learning_rate * gradients[-(i + 1)][0]
            self.biases[i] -= learning_rate * gradients[-(i + 1)][1]

        # Calculate loss
        return -np.mean(np.sum(y * np.log(activations[-1]), axis=1))

class ReinforcementLearning:
    def __init__(self, state_space: int, action_space: int, alpha: float = 0.1, gamma: float = 0.99):
        self.state_space = state_space
        self.action_space = action_space
        self.alpha = alpha
        self.gamma = gamma
        self.q_table = np.zeros((state_space, action_space))

    def choose_action(self, state: int, epsilon: float = 0.1) -> int:
        if np.random.random() < epsilon:
            return np.random.randint(self.action_space)
        return np.argmax(self.q_table[state])

    def update_q_table(self, state: int, action: int, reward: float, next_state: int) -> None:
        current_q = self.q_table[state, action]
        next_max = np.max(self.q_table[next_state])
        new_q = (1 - self.alpha) * current_q + self.alpha * (reward + self.gamma * next_max)
        self.q_table[state, action] = new_q

class GeneticAlgorithm:
    def __init__(self, population_size: int, mutation_rate: float = 0.01):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.population = []

    def initialize_population(self, chromosome_length: int) -> None:
        self.population = np.random.randint(2, size=(self.population_size, chromosome_length))

    def fitness(self, chromosome: np.ndarray) -> float:
        # Implement specific fitness function based on requirements
        return np.sum(chromosome)

    def selection(self) -> Tuple[np.ndarray, np.ndarray]:
        fitness_scores = np.array([self.fitness(chrom) for chrom in self.population])
        probabilities = fitness_scores / np.sum(fitness_scores)
        return np.random.choice(
            self.population,
            size=2,
            replace=False,
            p=probabilities
        )

    def crossover(self, parent1: np.ndarray, parent2: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        crossover_point = np.random.randint(1, len(parent1))
        child1 = np.concatenate((parent1[:crossover_point], parent2[crossover_point:]))
        child2 = np.concatenate((parent2[:crossover_point], parent1[crossover_point:]))
        return child1, child2

    def mutate(self, chromosome: np.ndarray) -> np.ndarray:
        for i in range(len(chromosome)):
            if np.random.random() < self.mutation_rate:
                chromosome[i] = 1 - chromosome[i]
        return chromosome

    def evolve(self, generations: int) -> np.ndarray:
        for _ in range(generations):
            new_population = []
            for _ in range(self.population_size // 2):
                parent1, parent2 = self.selection()
                child1, child2 = self.crossover(parent1, parent2)
                child1 = self.mutate(child1)
                child2 = self.mutate(child2)
                new_population.extend([child1, child2])
            self.population = np.array(new_population)
        return self.population[np.argmax([self.fitness(chrom) for chrom in self.population])]
