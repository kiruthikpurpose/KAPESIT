package quantum

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

func initializeGates() map[string][][]complex128 {
    gates := make(map[string][][]complex128)
    
    // Hadamard gate
    sqrt2 := 1.0 / math.Sqrt(2)
    gates["H"] = [][]complex128{
        {complex(sqrt2, 0), complex(sqrt2, 0)},
        {complex(sqrt2, 0), complex(-sqrt2, 0)},
    }

    // Pauli gates
    gates["X"] = [][]complex128{
        {0, 1},
        {1, 0},
    }

    gates["Y"] = [][]complex128{
        {0, -1i},
        {1i, 0},
    }

    gates["Z"] = [][]complex128{
        {1, 0},
        {0, -1},
    }

    return gates
}

func (qc *QuantumCircuitSimulator) ApplyGate(gateName string, target int) {
    qc.mu.Lock()
    defer qc.mu.Unlock()

    if target < 0 || target >= qc.numQubits {
        panic("invalid target qubit")
    }

    gate := qc.gates[gateName]
    if gate == nil {
        panic("unknown gate: " + gateName)
    }

    newState := make([]complex128, len(qc.state))
    var wg sync.WaitGroup
    chunkSize := len(qc.state) / 4

    for i := 0; i < 4; i++ {
        wg.Add(1)
        go func(start int) {
            defer wg.Done()
            end := start + chunkSize
            if i == 3 {
                end = len(qc.state)
            }

            for j := start; j < end; j++ {
                bit := (j >> target) & 1
                idx := j ^ (1 << target)
                if j < idx {
                    newState[j] = gate[0][0]*qc.state[j] + gate[0][1]*qc.state[idx]
                    newState[idx] = gate[1][0]*qc.state[j] + gate[1][1]*qc.state[idx]
                }
            }
        }(i * chunkSize)
    }

    wg.Wait()
    qc.state = newState
}

func (qc *QuantumCircuitSimulator) ApplyControlledGate(gateName string, control, target int) {
    qc.mu.Lock()
    defer qc.mu.Unlock()

    if control < 0 || control >= qc.numQubits || target < 0 || target >= qc.numQubits {
        panic("invalid qubit indices")
    }

    gate := qc.gates[gateName]
    if gate == nil {
        panic("unknown gate: " + gateName)
    }

    newState := make([]complex128, len(qc.state))
    var wg sync.WaitGroup
    chunkSize := len(qc.state) / 4

    for i := 0; i < 4; i++ {
        wg.Add(1)
        go func(start int) {
            defer wg.Done()
            end := start + chunkSize
            if i == 3 {
                end = len(qc.state)
            }

            for j := start; j < end; j++ {
                if (j & (1 << control)) != 0 {
                    bit := (j >> target) & 1
                    idx := j ^ (1 << target)
                    if j < idx {
                        newState[j] = gate[0][0]*qc.state[j] + gate[0][1]*qc.state[idx]
                        newState[idx] = gate[1][0]*qc.state[j] + gate[1][1]*qc.state[idx]
                    }
                } else {
                    newState[j] = qc.state[j]
                }
            }
        }(i * chunkSize)
    }

    wg.Wait()
    qc.state = newState
}

func (qc *QuantumCircuitSimulator) Measure(qubit int) int {
    qc.mu.Lock()
    defer qc.mu.Unlock()

    if qubit < 0 || qubit >= qc.numQubits {
        panic("invalid qubit index")
    }

    // Calculate probabilities
    prob0 := 0.0
    prob1 := 0.0
    for i := 0; i < len(qc.state); i++ {
        if (i & (1 << qubit)) != 0 {
            prob1 += cmplx.Abs(qc.state[i]) * cmplx.Abs(qc.state[i])
        } else {
            prob0 += cmplx.Abs(qc.state[i]) * cmplx.Abs(qc.state[i])
        }
    }

    // Simulate measurement
    r := rand.Float64()
    result := 0
    if r > prob0 {
        result = 1
    }

    // Collapse state
    newState := make([]complex128, len(qc.state))
    norm := 0.0
    for i := 0; i < len(qc.state); i++ {
        if ((i >> qubit) & 1) == result {
            newState[i] = qc.state[i]
            norm += cmplx.Abs(qc.state[i]) * cmplx.Abs(qc.state[i])
        }
    }

    // Normalize
    norm = math.Sqrt(norm)
    for i := 0; i < len(qc.state); i++ {
        if cmplx.Abs(newState[i]) > 0 {
            newState[i] /= complex(norm, 0)
        }
    }

    qc.state = newState
    return result
}

func (qc *QuantumCircuitSimulator) GetState() []complex128 {
    qc.mu.RLock()
    defer qc.mu.RUnlock()
    return append([]complex128{}, qc.state...)
}

func (qc *QuantumCircuitSimulator) Reset() {
    qc.mu.Lock()
    defer qc.mu.Unlock()

    qc.state = make([]complex128, 1<<qc.numQubits)
    qc.state[0] = 1.0
}

// Example usage
func Example() {
    // Create a 2-qubit circuit
    circuit := NewQuantumCircuitSimulator(2)

    // Apply Hadamard to first qubit
    circuit.ApplyGate("H", 0)

    // Apply CNOT
    circuit.ApplyControlledGate("X", 0, 1)

    // Measure
    result := circuit.Measure(0)
    fmt.Printf("Measurement result: %d\n", result)
} 