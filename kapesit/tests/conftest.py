import pytest
import numpy as np
import kapesit as kp

@pytest.fixture
def quantum_simulator():
    return kp.QuantumSimulator()

@pytest.fixture
def numerical_ops():
    return kp.NumericalOps()

@pytest.fixture
def assembly_ops():
    return kp.AssemblyOps()

@pytest.fixture
def parallel_ops():
    return kp.ParallelOps()

@pytest.fixture
def cpp_matrix_ops():
    return kp.CppMatrixOps()

@pytest.fixture
def random_matrix():
    return np.random.rand(100, 100).astype(np.float32)

@pytest.fixture
def random_vector():
    return np.random.rand(100).astype(np.float32)

@pytest.fixture
def quantum_state():
    return np.array([1, 0], dtype=np.float32)

@pytest.fixture
def hamiltonian():
    return np.array([[0, 1], [1, 0]], dtype=np.float32) 