import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from scipy.integrate import solve_ivp
from scipy.interpolate import interp1d
import astropy.units as u
from astropy.coordinates import SkyCoord
from astropy.time import Time

@dataclass
class RadiationEnvironment:
    solar_flux: float  # W/m²
    cosmic_ray_flux: float  # particles/cm²/s
    trapped_particles: Dict[str, float]  # particles/cm²/s for different energy bands
    geomagnetic_index: float  # Kp index

@dataclass
class ThermalEnvironment:
    temperature: float  # K
    heat_flux: float  # W/m²
    albedo: float  # dimensionless
    emissivity: float  # dimensionless

@dataclass
class AtmosphericEnvironment:
    density: float  # kg/m³
    pressure: float  # Pa
    temperature: float  # K
    composition: Dict[str, float]  # mole fractions

class SpaceEnvironmentSimulator:
    def __init__(self):
        self.radiation = RadiationEnvironment(
            solar_flux=1361.0,
            cosmic_ray_flux=1.0,
            trapped_particles={"protons": 1e4, "electrons": 1e5},
            geomagnetic_index=3.0
        )
        
        self.thermal = ThermalEnvironment(
            temperature=300.0,
            heat_flux=0.0,
            albedo=0.3,
            emissivity=0.9
        )
        
        self.atmosphere = AtmosphericEnvironment(
            density=1.225,
            pressure=101325.0,
            temperature=288.15,
            composition={"N2": 0.78, "O2": 0.21, "Ar": 0.01}
        )
        
        self._load_environment_models()
    
    def _load_environment_models(self) -> None:
        # Load solar cycle data
        self.solar_cycle = interp1d(
            np.linspace(0, 11, 100),
            np.random.normal(1361, 10, 100)
        )
        
        # Load cosmic ray data
        self.cosmic_ray_model = interp1d(
            np.linspace(0, 100, 1000),
            np.random.lognormal(0, 1, 1000)
        )
        
        # Load atmospheric model
        self.atmospheric_model = {
            "density": lambda h: 1.225 * np.exp(-h/8500),
            "temperature": lambda h: 288.15 - 6.5 * h/1000,
            "pressure": lambda h: 101325 * np.exp(-h/8500)
        }
    
    def calculate_radiation_dose(
        self,
        position: np.ndarray,
        time: float,
        shielding_thickness: float = 0.1
    ) -> Dict[str, float]:
        # Calculate distance from Sun
        sun_distance = np.linalg.norm(position)
        solar_flux = self.radiation.solar_flux / (sun_distance**2)
        
        # Calculate cosmic ray flux
        cosmic_ray_flux = self.cosmic_ray_model(time)
        
        # Calculate trapped particle flux
        trapped_flux = sum(self.radiation.trapped_particles.values())
        
        # Calculate shielding factor
        shielding_factor = np.exp(-shielding_thickness / 0.1)
        
        return {
            "solar_radiation": solar_flux * shielding_factor,
            "cosmic_rays": cosmic_ray_flux * shielding_factor,
            "trapped_particles": trapped_flux * shielding_factor,
            "total_dose": (solar_flux + cosmic_ray_flux + trapped_flux) * shielding_factor
        }
    
    def calculate_thermal_balance(
        self,
        position: np.ndarray,
        surface_properties: Dict[str, float],
        time: float
    ) -> Dict[str, float]:
        # Calculate solar heating
        sun_distance = np.linalg.norm(position)
        solar_flux = self.radiation.solar_flux / (sun_distance**2)
        
        # Calculate albedo heating
        albedo_flux = solar_flux * self.thermal.albedo
        
        # Calculate infrared radiation
        ir_flux = 5.67e-8 * self.thermal.emissivity * (self.thermal.temperature**4)
        
        # Calculate total heat flux
        total_flux = solar_flux + albedo_flux - ir_flux
        
        return {
            "solar_heating": solar_flux,
            "albedo_heating": albedo_flux,
            "infrared_cooling": ir_flux,
            "total_heat_flux": total_flux,
            "equilibrium_temperature": (total_flux / (5.67e-8 * self.thermal.emissivity))**(1/4)
        }
    
    def calculate_atmospheric_conditions(
        self,
        altitude: float,
        latitude: float,
        longitude: float,
        time: Time
    ) -> Dict[str, float]:
        # Calculate basic atmospheric properties
        density = self.atmospheric_model["density"](altitude)
        temperature = self.atmospheric_model["temperature"](altitude)
        pressure = self.atmospheric_model["pressure"](altitude)
        
        # Calculate wind conditions
        wind_speed = 10 * np.sin(2 * np.pi * time.jd / 365.25)
        wind_direction = 45 * np.sin(2 * np.pi * time.jd / 365.25)
        
        return {
            "density": density,
            "temperature": temperature,
            "pressure": pressure,
            "wind_speed": wind_speed,
            "wind_direction": wind_direction,
            "composition": self.atmosphere.composition
        }
    
    def simulate_environmental_effects(
        self,
        position: np.ndarray,
        velocity: np.ndarray,
        time: float,
        spacecraft_properties: Dict[str, float]
    ) -> Dict[str, Dict[str, float]]:
        # Calculate all environmental effects
        radiation_effects = self.calculate_radiation_dose(
            position,
            time,
            spacecraft_properties.get("shielding_thickness", 0.1)
        )
        
        thermal_effects = self.calculate_thermal_balance(
            position,
            spacecraft_properties,
            time
        )
        
        # Convert position to lat/lon/alt
        lat, lon, alt = self._cartesian_to_geodetic(position)
        
        atmospheric_effects = self.calculate_atmospheric_conditions(
            alt,
            lat,
            lon,
            Time(time, format='jd')
        )
        
        return {
            "radiation": radiation_effects,
            "thermal": thermal_effects,
            "atmospheric": atmospheric_effects
        }
    
    def _cartesian_to_geodetic(self, position: np.ndarray) -> Tuple[float, float, float]:
        x, y, z = position
        r = np.sqrt(x**2 + y**2 + z**2)
        lat = np.arcsin(z/r)
        lon = np.arctan2(y, x)
        alt = r - 6371000  # Earth radius in meters
        return np.degrees(lat), np.degrees(lon), alt
    
    def predict_space_weather(
        self,
        position: np.ndarray,
        time: Time,
        forecast_hours: int = 24
    ) -> Dict[str, np.ndarray]:
        # Generate space weather forecast
        times = np.linspace(0, forecast_hours, 100)
        
        # Solar activity forecast
        solar_activity = self.solar_cycle(times/24/365.25)
        
        # Geomagnetic activity forecast
        geomagnetic_activity = 3 + 2 * np.sin(2 * np.pi * times/12)
        
        # Radiation belt forecast
        radiation_belt = {
            "protons": 1e4 * (1 + 0.5 * np.sin(2 * np.pi * times/24)),
            "electrons": 1e5 * (1 + 0.3 * np.sin(2 * np.pi * times/24))
        }
        
        return {
            "time": times,
            "solar_activity": solar_activity,
            "geomagnetic_activity": geomagnetic_activity,
            "radiation_belt": radiation_belt
        } 