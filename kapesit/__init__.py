"""
KAPESIT - Advanced Quantum Computing and AI Framework
"""

from .core.cpp_interface import (
    CppMatrixOps,
    QuantumSimulator,
    ParallelOps,
    NumericalOps,
    AssemblyOps
)

from .space.quantum_gravity import QuantumGravity
from .space.quantum_field import QuantumField
from .space.quantum_cosmology import QuantumCosmology
from .agi.quantum_reasoning import QuantumReasoning
from .agi.multi_agent import MultiAgentSystem
from .core.config import Config
from .core.logger import setup_logger

__version__ = "1.0.0"
__author__ = "KAPESIT Team"
__license__ = "MIT"

__all__ = [
    'CppMatrixOps',
    'QuantumSimulator',
    'ParallelOps',
    'NumericalOps',
    'AssemblyOps',
    'QuantumGravity',
    'QuantumField',
    'QuantumCosmology',
    'QuantumReasoning',
    'MultiAgentSystem'
]

config = Config()
logger = setup_logger() 