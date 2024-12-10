from typing import List, Tuple, Dict
import math
import cmath
import random

class WaveFunction:
    def __init__(self, n: int, l: int, m: int):
        self.n = n
        self.l = l
        self.m = m
        self.energy = -13.6 / (n * n)
        
    def calculate_radial_part(self, r: float) -> complex:
        a0 = 5.29177210903e-11
        rho = 2 * r / (self.n * a0)
        
        if self.n == 1:
            return 2 * math.exp(-rho/2)
        elif self.n == 2 and self.l == 0:
            return (1/math.sqrt(2)) * (1 - rho/2) * math.exp(-rho/2)
        elif self.n == 2 and self.l == 1:
            return (1/math.sqrt(24)) * rho * math.exp(-rho/2)
        return complex(0, 0)

class QuantumSimulator:
    def __init__(self):
        self.states = []
        self.measurements = []
        
    def simulate_particle_in_box(self, length: float, n: int, 
                               num_points: int) -> List[Tuple[float, float]]:
        wavefunction = []
        dx = length / num_points
        
        for i in range(num_points):
            x = i * dx
            psi = math.sqrt(2/length) * math.sin(n * math.pi * x / length)
            probability = abs(psi) ** 2
            wavefunction.append((x, probability))
            
        return wavefunction
    
    def calculate_tunneling_probability(self, barrier_height: float, 
                                     barrier_width: float, 
                                     particle_energy: float) -> float:
        if particle_energy >= barrier_height:
            return 1.0
            
        k = math.sqrt(2 * 9.1093837015e-31 * (barrier_height - particle_energy)) / 6.62607015e-34
        return math.exp(-2 * k * barrier_width)
    
    def simulate_quantum_oscillator(self, n: int, 
                                  num_points: int) -> List[Tuple[float, float]]:
        results = []
        x_max = math.sqrt(2 * (2 * n + 1))
        dx = 2 * x_max / num_points
        
        def hermite(x: float, n: int) -> float:
            if n == 0:
                return 1
            elif n == 1:
                return 2 * x
            else:
                h0, h1 = 1, 2 * x
                for i in range(2, n + 1):
                    h0, h1 = h1, 2 * x * h1 - 2 * (i - 1) * h0
                return h1
        
        for i in range(num_points):
            x = -x_max + i * dx
            psi = (1 / math.sqrt(2**n * math.factorial(n)) * 
                  math.pi**(-0.25) * math.exp(-x*x/2) * 
                  hermite(x, n))
            probability = abs(psi) ** 2
            results.append((x, probability))
            
        return results