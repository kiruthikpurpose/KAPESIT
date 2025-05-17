import numpy as np
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
import math
from scipy.integrate import odeint

class CelestialBody:
    def __init__(self, name: str, mass: float, position: np.ndarray,
                 velocity: np.ndarray, radius: float):
        self.name = name
        self.mass = mass
        self.position = position
        self.velocity = velocity
        self.radius = radius
        self.trail = []
        self.properties_history = []

    def update_position(self, dt: float) -> None:
        self.position += self.velocity * dt
        self.trail.append({
            'timestamp': datetime.now(),
            'position': self.position.copy(),
            'velocity': self.velocity.copy()
        })

    def calculate_gravitational_force(self, other: 'CelestialBody') -> np.ndarray:
        G = 6.67430e-11  # Gravitational constant
        r = other.position - self.position
        distance = np.linalg.norm(r)
        force_magnitude = G * self.mass * other.mass / (distance ** 2)
        return force_magnitude * r / distance

class SpaceSystem:
    def __init__(self, bodies: List[CelestialBody]):
        self.bodies = bodies
        self.time = 0
        self.time_history = []
        self.collision_history = []

    def update_system(self, dt: float) -> None:
        forces = [np.zeros(3) for _ in self.bodies]
        
        # Calculate forces between all bodies
        for i, body1 in enumerate(self.bodies):
            for j, body2 in enumerate(self.bodies):
                if i != j:
                    forces[i] += body1.calculate_gravitational_force(body2)
        
        # Update velocities and positions
        for body, force in zip(self.bodies, forces):
            acceleration = force / body.mass
            body.velocity += acceleration * dt
            body.update_position(dt)
        
        self.time += dt
        self.time_history.append(self.time)
        
        # Check for collisions
        self._check_collisions()

    def _check_collisions(self) -> None:
        for i, body1 in enumerate(self.bodies):
            for j, body2 in enumerate(self.bodies):
                if i < j:
                    distance = np.linalg.norm(body2.position - body1.position)
                    if distance < (body1.radius + body2.radius):
                        self.collision_history.append({
                            'timestamp': datetime.now(),
                            'bodies': (body1.name, body2.name),
                            'distance': distance,
                            'position': (body1.position, body2.position)
                        })

class SpaceMission:
    def __init__(self, spacecraft: CelestialBody, destination: CelestialBody,
                 start_time: datetime):
        self.spacecraft = spacecraft
        self.destination = destination
        self.start_time = start_time
        self.current_time = start_time
        self.mission_log = []
        self.fuel_consumption = 0

    def plan_trajectory(self, duration: float, dt: float = 60) -> List[Tuple[float, np.ndarray]]:
        time_points = np.arange(0, duration, dt)
        
        def system_dynamics(y, t):
            pos, vel = y[:3], y[3:]
            force = self.spacecraft.calculate_gravitational_force(self.destination)
            return np.concatenate([vel, force / self.spacecraft.mass])
        
        initial_state = np.concatenate([self.spacecraft.position, self.spacecraft.velocity])
        solution = odeint(system_dynamics, initial_state, time_points)
        
        trajectory = [(t, sol[:3]) for t, sol in zip(time_points, solution)]
        return trajectory

    def execute_maneuver(self, thrust: float, duration: float) -> None:
        acceleration = thrust / self.spacecraft.mass
        self.spacecraft.velocity += acceleration * duration
        self.fuel_consumption += thrust * duration
        
        self.mission_log.append({
            'timestamp': self.current_time,
            'maneuver': 'thrust',
            'thrust': thrust,
            'duration': duration,
            'fuel_consumed': thrust * duration
        })

    def calculate_distance_to_destination(self) -> float:
        return np.linalg.norm(self.destination.position - self.spacecraft.position)

class SpaceWeather:
    def __init__(self, solar_wind_speed: float, solar_wind_density: float,
                 magnetic_field_strength: float):
        self.solar_wind_speed = solar_wind_speed
        self.solar_wind_density = solar_wind_density
        self.magnetic_field_strength = magnetic_field_strength
        self.radiation_levels = {}
        self.weather_history = []

    def calculate_radiation_level(self, distance_from_sun: float) -> float:
        # Inverse square law for radiation
        base_radiation = 1e-6  # Base radiation at 1 AU
        return base_radiation * (1 / (distance_from_sun ** 2))

    def update_weather(self, dt: float) -> None:
        # Update solar wind parameters
        self.solar_wind_speed += np.random.normal(0, 10)
        self.solar_wind_density += np.random.normal(0, 0.1)
        self.magnetic_field_strength += np.random.normal(0, 0.01)
        
        self.weather_history.append({
            'timestamp': datetime.now(),
            'solar_wind_speed': self.solar_wind_speed,
            'solar_wind_density': self.solar_wind_density,
            'magnetic_field_strength': self.magnetic_field_strength
        })

class SpaceStation:
    def __init__(self, position: np.ndarray, crew_capacity: int,
                 life_support: float, power_generation: float):
        self.position = position
        self.crew_capacity = crew_capacity
        self.life_support = life_support
        self.power_generation = power_generation
        self.crew = []
        self.system_status = {}
        self.maintenance_log = []

    def add_crew_member(self, crew_member: 'CrewMember') -> bool:
        if len(self.crew) < self.crew_capacity:
            self.crew.append(crew_member)
            return True
        return False

    def calculate_power_usage(self) -> float:
        base_power = 1000  # Base power usage in kW
        crew_power = len(self.crew) * 100  # Power per crew member
        life_support = self.life_support * 500  # Life support power
        return base_power + crew_power + life_support

    def perform_maintenance(self, system: str, duration: float) -> None:
        self.maintenance_log.append({
            'timestamp': datetime.now(),
            'system': system,
            'duration': duration,
            'crew': [member.name for member in self.crew]
        })

class CrewMember:
    def __init__(self, name: str, role: str, experience: float,
                 health_status: float):
        self.name = name
        self.role = role
        self.experience = experience
        self.health_status = health_status
        self.missions = []
        self.training_records = []

    def perform_task(self, task: str, duration: float) -> float:
        # Task performance is based on experience and health
        performance = self.experience * self.health_status
        return performance * duration

    def add_training(self, skill: str, hours: float) -> None:
        self.training_records.append({
            'timestamp': datetime.now(),
            'skill': skill,
            'hours': hours
        })
        self.experience += hours / 100  # Experience gain per hour of training

    def evaluate_fitness(self) -> float:
        # Fitness is based on health and recent training
        recent_training = sum(record['hours'] for record in self.training_records[-10:])
        return self.health_status * (1 + recent_training / 100)

class SpaceTelescope:
    def __init__(self, aperture: float, field_of_view: float,
                 wavelength_range: Tuple[float, float]):
        self.aperture = aperture
        self.field_of_view = field_of_view
        self.wavelength_range = wavelength_range
        self.observations = []
        self.calibration_history = []

    def observe_target(self, target: 'CelestialBody', exposure_time: float) -> Dict[str, Any]:
        observation = {
            'timestamp': datetime.now(),
            'target': target.name,
            'position': target.position.copy(),
            'exposure_time': exposure_time,
            'data_quality': self._calculate_data_quality()
        }
        self.observations.append(observation)
        return observation

    def _calculate_data_quality(self) -> float:
        # Data quality is based on aperture and exposure time
        base_quality = self.aperture * 100
        return min(base_quality, 100)  # Cap at 100% quality

    def calibrate(self, calibration_source: 'CelestialBody') -> None:
        self.calibration_history.append({
            'timestamp': datetime.now(),
            'source': calibration_source.name,
            'aperture': self.aperture,
            'field_of_view': self.field_of_view
        })
