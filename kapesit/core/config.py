import os
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from pathlib import Path

@dataclass
class Config:
    PROJECT_ROOT: Path = field(default_factory=lambda: Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
    DATA_DIR: Path = field(default_factory=lambda: Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))) / "data")
    MODELS_DIR: Path = field(default_factory=lambda: Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))) / "models")
    LOGS_DIR: Path = field(default_factory=lambda: Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))) / "logs")
    
    QUANTUM_BACKEND: str = "qiskit"
    QUANTUM_SIMULATOR: str = "aer_simulator"
    
    AGI_MODEL_TYPE: str = "transformer"
    AGI_MODEL_SIZE: str = "large"
    
    SPACE_SIMULATION_TIMESTEP: float = 1.0
    SPACE_SIMULATION_DURATION: float = 86400.0
    
    MATERIALS_SIMULATION_ACCURACY: float = 0.001
    MATERIALS_SIMULATION_MAX_ITERATIONS: int = 1000
    
    def __post_init__(self) -> None:
        for directory in [self.DATA_DIR, self.MODELS_DIR, self.LOGS_DIR]:
            try:
                directory.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                raise RuntimeError(f"Failed to create directory {directory}: {str(e)}")
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_root": str(self.PROJECT_ROOT),
            "data_dir": str(self.DATA_DIR),
            "models_dir": str(self.MODELS_DIR),
            "logs_dir": str(self.LOGS_DIR),
            "quantum_backend": self.QUANTUM_BACKEND,
            "quantum_simulator": self.QUANTUM_SIMULATOR,
            "agi_model_type": self.AGI_MODEL_TYPE,
            "agi_model_size": self.AGI_MODEL_SIZE,
            "space_simulation_timestep": self.SPACE_SIMULATION_TIMESTEP,
            "space_simulation_duration": self.SPACE_SIMULATION_DURATION,
            "materials_simulation_accuracy": self.MATERIALS_SIMULATION_ACCURACY,
            "materials_simulation_max_iterations": self.MATERIALS_SIMULATION_MAX_ITERATIONS
        }
    
    def validate(self) -> bool:
        try:
            if not all(isinstance(v, (str, int, float, Path)) for v in self.__dict__.values()):
                return False
            if not all(isinstance(v, (int, float)) or v > 0 for k, v in self.__dict__.items() 
                      if k.endswith(('_ITERATIONS', '_DURATION', '_TIMESTEP'))):
                return False
            return True
        except Exception:
            return False 