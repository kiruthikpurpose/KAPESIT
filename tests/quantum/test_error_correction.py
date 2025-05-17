import numpy as np
import pytest
from kapesit.quantum.error_correction import SurfaceCode, StabilizerCode

def test_surface_code():
    distance = 3
    surface_code = SurfaceCode(distance)
    
    # Test initialization
    assert surface_code.num_qubits == 2 * distance * distance
    assert surface_code.syndrome_qubits == (distance - 1) * (distance - 1)
    
    # Test encoding
    state = np.zeros(2**surface_code.num_qubits)
    state[0] = 1.0
    encoded_state = surface_code.encode(state)
    assert len(encoded_state) == 2**(surface_code.num_qubits + surface_code.syndrome_qubits)
    
    # Test decoding
    decoded_state = surface_code.decode(encoded_state)
    assert len(decoded_state) == 2**surface_code.num_qubits
    np.testing.assert_array_almost_equal(decoded_state, state)
    
    # Test syndrome measurement
    syndrome = surface_code.measure_syndrome(encoded_state)
    assert len(syndrome) == surface_code.syndrome_qubits
    assert all(s in [0, 1] for s in syndrome)
    
    # Test error handling
    with pytest.raises(ValueError):
        surface_code.encode(np.zeros(2**(surface_code.num_qubits + 1)))
    with pytest.raises(ValueError):
        surface_code.decode(np.zeros(2**(surface_code.num_qubits + surface_code.syndrome_qubits + 1)))

def test_stabilizer_code():
    num_qubits = 4
    num_stabilizers = 2
    stabilizer_code = StabilizerCode(num_qubits, num_stabilizers)
    
    # Test initialization
    assert stabilizer_code.num_qubits == num_qubits
    assert stabilizer_code.num_stabilizers == num_stabilizers
    assert len(stabilizer_code.stabilizers) == num_stabilizers
    
    # Test encoding
    state = np.zeros(2**num_qubits)
    state[0] = 1.0
    encoded_state = stabilizer_code.encode(state)
    assert len(encoded_state) == 2**num_qubits
    
    # Test decoding
    decoded_state = stabilizer_code.decode(encoded_state)
    assert len(decoded_state) == 2**num_qubits
    np.testing.assert_array_almost_equal(decoded_state, state)
    
    # Test stabilizer application
    for stabilizer in stabilizer_code.stabilizers:
        assert len(stabilizer) == num_qubits
        assert all(p in ['I', 'X', 'Y', 'Z'] for p in stabilizer)
    
    # Test error handling
    with pytest.raises(ValueError):
        stabilizer_code.encode(np.zeros(2**(num_qubits + 1)))
    with pytest.raises(ValueError):
        stabilizer_code.decode(np.zeros(2**(num_qubits + 1)))

def test_integration():
    # Test integration between surface code and stabilizer code
    distance = 3
    surface_code = SurfaceCode(distance)
    stabilizer_code = StabilizerCode(surface_code.num_qubits, 2)
    
    # Create initial state
    state = np.zeros(2**surface_code.num_qubits)
    state[0] = 1.0
    
    # Encode with surface code
    surface_encoded = surface_code.encode(state)
    
    # Encode with stabilizer code
    stabilizer_encoded = stabilizer_code.encode(state)
    
    # Decode both
    surface_decoded = surface_code.decode(surface_encoded)
    stabilizer_decoded = stabilizer_code.decode(stabilizer_encoded)
    
    # Verify results
    np.testing.assert_array_almost_equal(surface_decoded, state)
    np.testing.assert_array_almost_equal(stabilizer_decoded, state) 