import numpy as np
from dataclasses import dataclass
from typing import List, Tuple, Optional
from scipy.integrate import solve_ivp

@dataclass
class CelestialBody:
    name: str
    mass: float
    radius: float
    position: np.ndarray
    velocity: np.ndarray

class OrbitalSimulator:
    G = 6.67430e-11
    
    def __init__(self):
        self.bodies: List[CelestialBody] = []
        self.time_span = (0, 86400)  # 1 day in seconds
        self.time_step = 1.0
    
    def add_body(self, body: CelestialBody) -> None:
        self.bodies.append(body)
    
    def calculate_acceleration(self, state: np.ndarray, t: float) -> np.ndarray:
        n_bodies = len(self.bodies)
        accelerations = np.zeros((n_bodies, 3))
        
        for i in range(n_bodies):
            for j in range(n_bodies):
                if i != j:
                    r = state[j*6:j*6+3] - state[i*6:i*6+3]
                    r_mag = np.linalg.norm(r)
                    accelerations[i] += self.G * self.bodies[j].mass * r / (r_mag ** 3)
        
        return accelerations.flatten()
    
    def run_simulation(self) -> Tuple[np.ndarray, np.ndarray]:
        initial_state = np.zeros(6 * len(self.bodies))
        for i, body in enumerate(self.bodies):
            initial_state[i*6:i*6+3] = body.position
            initial_state[i*6+3:i*6+6] = body.velocity
        
        solution = solve_ivp(
            self.calculate_acceleration,
            self.time_span,
            initial_state,
            method='RK45',
            t_eval=np.arange(self.time_span[0], self.time_span[1], self.time_step)
        )
        
        return solution.t, solution.y
    
    def calculate_orbital_elements(self, body_index: int) -> dict:
        body = self.bodies[body_index]
        r = body.position
        v = body.velocity
        
        h = np.cross(r, v)
        n = np.cross([0, 0, 1], h)
        
        e = np.cross(v, h) / self.G - r / np.linalg.norm(r)
        e_mag = np.linalg.norm(e)
        
        a = -self.G * body.mass / (2 * np.linalg.norm(v)**2)
        i = np.arccos(h[2] / np.linalg.norm(h))
        
        return {
            'semi_major_axis': a,
            'eccentricity': e_mag,
            'inclination': i,
            'angular_momentum': h
        }
    
    def predict_collision(self, body1_index: int, body2_index: int) -> Optional[float]:
        t, states = self.run_simulation()
        
        for i, t_val in enumerate(t):
            pos1 = states[body1_index*6:body1_index*6+3, i]
            pos2 = states[body2_index*6:body2_index*6+3, i]
            
            distance = np.linalg.norm(pos1 - pos2)
            if distance < (self.bodies[body1_index].radius + self.bodies[body2_index].radius):
                return t_val
        
        return None 