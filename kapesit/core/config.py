import os
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class Config:
    PROJECT_ROOT: str = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    DATA_DIR: str = os.path.join(PROJECT_ROOT, "data")
    MODELS_DIR: str = os.path.join(PROJECT_ROOT, "models")
    LOGS_DIR: str = os.path.join(PROJECT_ROOT, "logs")
    
    QUANTUM_BACKEND: str = "qiskit"
    QUANTUM_SIMULATOR: str = "aer_simulator"
    
    AGI_MODEL_TYPE: str = "transformer"
    AGI_MODEL_SIZE: str = "large"
    
    SPACE_SIMULATION_TIMESTEP: float = 1.0
    SPACE_SIMULATION_DURATION: float = 86400.0
    
    MATERIALS_SIMULATION_ACCURACY: float = 0.001
    MATERIALS_SIMULATION_MAX_ITERATIONS: int = 1000
    
    def __post_init__(self):
        os.makedirs(self.DATA_DIR, exist_ok=True)
        os.makedirs(self.MODELS_DIR, exist_ok=True)
        os.makedirs(self.LOGS_DIR, exist_ok=True)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_root": self.PROJECT_ROOT,
            "data_dir": self.DATA_DIR,
            "models_dir": self.MODELS_DIR,
            "logs_dir": self.LOGS_DIR,
            "quantum_backend": self.QUANTUM_BACKEND,
            "quantum_simulator": self.QUANTUM_SIMULATOR,
            "agi_model_type": self.AGI_MODEL_TYPE,
            "agi_model_size": self.AGI_MODEL_SIZE,
            "space_simulation_timestep": self.SPACE_SIMULATION_TIMESTEP,
            "space_simulation_duration": self.SPACE_SIMULATION_DURATION,
            "materials_simulation_accuracy": self.MATERIALS_SIMULATION_ACCURACY,
            "materials_simulation_max_iterations": self.MATERIALS_SIMULATION_MAX_ITERATIONS
        } 