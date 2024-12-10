from typing import Dict, List, Tuple
import math
import time

class BiometricSensor:
    def __init__(self, sampling_rate: float):
        self.sampling_rate = sampling_rate
        self.readings = []
        
    def read_vital_signs(self) -> Dict[str, float]:
        heart_rate = 60 + 20 * math.sin(time.time() / 60)
        blood_pressure = 120 + 10 * math.cos(time.time() / 30)
        oxygen = 98 + random.uniform(-1, 1)
        temperature = 37 + 0.3 * math.sin(time.time() / 3600)
        
        reading = {
            "heart_rate": heart_rate,
            "blood_pressure": blood_pressure,
            "oxygen_saturation": oxygen,
            "body_temperature": temperature
        }
        
        self.readings.append((time.time(), reading))
        return reading

class CrewMember:
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.sensor = BiometricSensor(1.0)
        self.health_status = "nominal"
        self.radiation_exposure = 0
        
    def update_health_status(self) -> Dict[str, float]:
        vitals = self.sensor.read_vital_signs()
        
        risk_score = 0
        if vitals["heart_rate"] > 100 or vitals["heart_rate"] < 50:
            risk_score += 1
        if vitals["oxygen_saturation"] < 95:
            risk_score += 2
        if abs(vitals["body_temperature"] - 37) > 1:
            risk_score += 1
            
        self.health_status = "critical" if risk_score > 2 else "nominal"
        
        return {
            "risk_score": risk_score,
            "health_status": self.health_status,
            "radiation_exposure": self.radiation_exposure
        }

class CrewHealthMonitor:
    def __init__(self):
        self.crew_members = {}
        self.alert_threshold = 2
        
    def add_crew_member(self, name: str, role: str):
        self.crew_members[name] = CrewMember(name, role)
        
    def monitor_crew_health(self) -> Dict[str, Dict[str, float]]:
        status = {}
        for name, member in self.crew_members.items():
            status[name] = member.update_health_status()
            
        return status
    
    def analyze_crew_trends(self, hours: int = 24) -> Dict[str, Dict[str, float]]:
        trends = {}
        current_time = time.time()
        
        for name, member in self.crew_members.items():
            relevant_readings = [r for r in member.sensor.readings 
                               if current_time - r[0] <= hours * 3600]
            
            if relevant_readings:
                heart_rates = [r[1]["heart_rate"] for r in relevant_readings]
                oxygen_levels = [r[1]["oxygen_saturation"] for r in relevant_readings]
                
                trends[name] = {
                    "avg_heart_rate": sum(heart_rates) / len(heart_rates),
                    "min_oxygen": min(oxygen_levels),
                    "health_deterioration": any(r[1]["risk_score"] > 
                                             self.alert_threshold for r in relevant_readings)
                }
                
        return trends