package quantum

import (
    "fmt"
    "math"
    "math/cmplx"
    "sync"
)

type Complex = complex128

type QuantumGate struct {
    Matrix [][]Complex
    Name   string
}

type QuantumCircuit struct {
    Gates     []QuantumGate
    NumQubits int
    State     []Complex
    mu        sync.RWMutex
}

func NewQuantumCircuit(numQubits int) *QuantumCircuit {
    if numQubits <= 0 {
        panic("number of qubits must be positive")
    }

    stateSize := 1 << numQubits
    state := make([]Complex, stateSize)
    state[0] = 1.0 // Initialize to |0⟩

    return &QuantumCircuit{
        Gates:     make([]QuantumGate, 0),
        NumQubits: numQubits,
        State:     state,
    }
}

func (qc *QuantumCircuit) AddGate(gate QuantumGate) {
    qc.mu.Lock()
    defer qc.mu.Unlock()
    qc.Gates = append(qc.Gates, gate)
}

func (qc *QuantumCircuit) ApplyGate(gate QuantumGate, target int) {
    qc.mu.Lock()
    defer qc.mu.Unlock()

    if target < 0 || target >= qc.NumQubits {
        panic("invalid target qubit")
    }

    newState := make([]Complex, len(qc.State))
    var wg sync.WaitGroup
    chunkSize := len(qc.State) / 4

    for i := 0; i < 4; i++ {
        wg.Add(1)
        go func(start int) {
            defer wg.Done()
            end := start + chunkSize
            if i == 3 {
                end = len(qc.State)
            }

            for j := start; j < end; j++ {
                for k := 0; k < 2; k++ {
                    idx := j ^ (1 << target)
                    newState[j] += gate.Matrix[j>>target&1][k] * qc.State[idx]
                }
            }
        }(i * chunkSize)
    }

    wg.Wait()
    qc.State = newState
}

func (qc *QuantumCircuit) Measure() int {
    qc.mu.RLock()
    defer qc.mu.RUnlock()

    probabilities := make([]float64, len(qc.State))
    for i, amp := range qc.State {
        probabilities[i] = real(amp * cmplx.Conj(amp))
    }

    // Simulate measurement
    r := rand.Float64()
    cumProb := 0.0
    for i, prob := range probabilities {
        cumProb += prob
        if r <= cumProb {
            return i
        }
    }
    return len(probabilities) - 1
}

func (qc *QuantumCircuit) GetState() []Complex {
    qc.mu.RLock()
    defer qc.mu.RUnlock()
    return append([]Complex{}, qc.State...)
}

func (qc *QuantumCircuit) Reset() {
    qc.mu.Lock()
    defer qc.mu.Unlock()

    qc.State = make([]Complex, 1<<qc.NumQubits)
    qc.State[0] = 1.0
    qc.Gates = make([]QuantumGate, 0)
}

// Common quantum gates
var (
    H = QuantumGate{
        Matrix: [][]Complex{
            {1 / math.Sqrt2, 1 / math.Sqrt2},
            {1 / math.Sqrt2, -1 / math.Sqrt2},
        },
        Name: "H",
    }

    X = QuantumGate{
        Matrix: [][]Complex{
            {0, 1},
            {1, 0},
        },
        Name: "X",
    }

    Y = QuantumGate{
        Matrix: [][]Complex{
            {0, -1i},
            {1i, 0},
        },
        Name: "Y",
    }

    Z = QuantumGate{
        Matrix: [][]Complex{
            {1, 0},
            {0, -1},
        },
        Name: "Z",
    }
)

// Rotation gates
func Rx(theta float64) QuantumGate {
    cos := complex(math.Cos(theta/2), 0)
    sin := complex(0, -math.Sin(theta/2))
    return QuantumGate{
        Matrix: [][]Complex{
            {cos, sin},
            {sin, cos},
        },
        Name: fmt.Sprintf("Rx(%.2f)", theta),
    }
}

func Ry(theta float64) QuantumGate {
    cos := complex(math.Cos(theta/2), 0)
    sin := complex(-math.Sin(theta/2), 0)
    return QuantumGate{
        Matrix: [][]Complex{
            {cos, sin},
            {-sin, cos},
        },
        Name: fmt.Sprintf("Ry(%.2f)", theta),
    }
}

func Rz(theta float64) QuantumGate {
    return QuantumGate{
        Matrix: [][]Complex{
            {cmplx.Exp(complex(0, -theta/2)), 0},
            {0, cmplx.Exp(complex(0, theta/2))},
        },
        Name: fmt.Sprintf("Rz(%.2f)", theta),
    }
}

// Example usage
func Example() {
    // Create a 2-qubit circuit
    circuit := NewQuantumCircuit(2)

    // Apply Hadamard to first qubit
    circuit.ApplyGate(H, 0)

    // Apply CNOT
    circuit.ApplyGate(X, 1)

    // Measure
    result := circuit.Measure()
    fmt.Printf("Measurement result: %d\n", result)
} 