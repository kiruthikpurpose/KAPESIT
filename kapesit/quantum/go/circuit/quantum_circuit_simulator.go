package circuit

import (
    "fmt"
    "math"
    "math/cmplx"
    "sync"
)

type QuantumCircuitSimulator struct {
    numQubits int
    state     []complex128
    mu        sync.RWMutex
    gates     map[string][][]complex128
}

func NewQuantumCircuitSimulator(numQubits int) *QuantumCircuitSimulator {
    if numQubits <= 0 {
        panic("number of qubits must be positive")
    }

    stateSize := 1 << numQubits
    state := make([]complex128, stateSize)
    state[0] = 1.0 // Initialize to |0⟩

    return &QuantumCircuitSimulator{
        numQubits: numQubits,
        state:     state,
        gates:     initializeGates(),
    }
}

// ... [Rest of the implementation remains the same] ... 