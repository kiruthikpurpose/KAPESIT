package simulation

import (
	"math"
	"math/cmplx"
	"math/rand"
	"sync"
)

// Complex represents a complex number
type Complex struct {
	Real, Imag float64
}

// QuantumCircuit represents a quantum circuit simulator
type QuantumCircuit struct {
	mu       sync.RWMutex
	random   *rand.Rand
	gates    map[string][][]Complex
	numQubits int
	state    []Complex
}

// NewQuantumCircuit creates a new quantum circuit instance
func NewQuantumCircuit(numQubits int) *QuantumCircuit {
	qc := &QuantumCircuit{
		random:   rand.New(rand.NewSource(42)),
		gates:    make(map[string][][]Complex),
		numQubits: numQubits,
		state:    make([]Complex, 1<<numQubits),
	}
	qc.initializeGates()
	qc.initializeState()
	return qc
}

func (qc *QuantumCircuit) initializeGates() {
	// Hadamard gate
	sqrt2 := 1.0 / math.Sqrt(2)
	qc.gates["H"] = [][]Complex{
		{{Real: sqrt2, Imag: 0}, {Real: sqrt2, Imag: 0}},
		{{Real: sqrt2, Imag: 0}, {Real: -sqrt2, Imag: 0}},
	}

	// Pauli gates
	qc.gates["X"] = [][]Complex{
		{{Real: 0, Imag: 0}, {Real: 1, Imag: 0}},
		{{Real: 1, Imag: 0}, {Real: 0, Imag: 0}},
	}

	qc.gates["Y"] = [][]Complex{
		{{Real: 0, Imag: 0}, {Real: 0, Imag: -1}},
		{{Real: 0, Imag: 1}, {Real: 0, Imag: 0}},
	}

	qc.gates["Z"] = [][]Complex{
		{{Real: 1, Imag: 0}, {Real: 0, Imag: 0}},
		{{Real: 0, Imag: 0}, {Real: -1, Imag: 0}},
	}
}

func (qc *QuantumCircuit) initializeState() {
	qc.state[0] = Complex{Real: 1, Imag: 0}
}

// ApplyGate applies a quantum gate to a specific qubit
func (qc *QuantumCircuit) ApplyGate(gateName string, qubit int) {
	qc.mu.Lock()
	defer qc.mu.Unlock()

	gate, exists := qc.gates[gateName]
	if !exists {
		panic("Unknown gate: " + gateName)
	}

	newState := make([]Complex, len(qc.state))
	for i := 0; i < len(qc.state); i++ {
		bit := (i >> qubit) & 1
		idx := i ^ (1 << qubit)
		if i < idx {
			newState[i] = Complex{
				Real: gate[0][0].Real*qc.state[i].Real - gate[0][0].Imag*qc.state[i].Imag +
					gate[0][1].Real*qc.state[idx].Real - gate[0][1].Imag*qc.state[idx].Imag,
				Imag: gate[0][0].Real*qc.state[i].Imag + gate[0][0].Imag*qc.state[i].Real +
					gate[0][1].Real*qc.state[idx].Imag + gate[0][1].Imag*qc.state[idx].Real,
			}
			newState[idx] = Complex{
				Real: gate[1][0].Real*qc.state[i].Real - gate[1][0].Imag*qc.state[i].Imag +
					gate[1][1].Real*qc.state[idx].Real - gate[1][1].Imag*qc.state[idx].Imag,
				Imag: gate[1][0].Real*qc.state[i].Imag + gate[1][0].Imag*qc.state[i].Real +
					gate[1][1].Real*qc.state[idx].Imag + gate[1][1].Imag*qc.state[idx].Real,
			}
		}
	}
	copy(qc.state, newState)
}

// Measure measures a specific qubit
func (qc *QuantumCircuit) Measure(qubit int) int {
	qc.mu.Lock()
	defer qc.mu.Unlock()

	probabilities := make([]float64, 2)
	for i := 0; i < len(qc.state); i++ {
		if (i & (1 << qubit)) != 0 {
			probabilities[1] += qc.state[i].Real*qc.state[i].Real + qc.state[i].Imag*qc.state[i].Imag
		} else {
			probabilities[0] += qc.state[i].Real*qc.state[i].Real + qc.state[i].Imag*qc.state[i].Imag
		}
	}

	r := qc.random.Float64()
	result := 0
	if r >= probabilities[0] {
		result = 1
	}

	// Collapse state
	newState := make([]Complex, len(qc.state))
	norm := 0.0
	for i := 0; i < len(qc.state); i++ {
		if ((i >> qubit) & 1) == result {
			newState[i] = qc.state[i]
			norm += qc.state[i].Real*qc.state[i].Real + qc.state[i].Imag*qc.state[i].Imag
		}
	}

	// Normalize
	norm = math.Sqrt(norm)
	for i := 0; i < len(qc.state); i++ {
		if newState[i].Real != 0 || newState[i].Imag != 0 {
			newState[i].Real /= norm
			newState[i].Imag /= norm
		}
	}

	copy(qc.state, newState)
	return result
}

// GetState returns the current quantum state
func (qc *QuantumCircuit) GetState() []Complex {
	qc.mu.RLock()
	defer qc.mu.RUnlock()

	state := make([]Complex, len(qc.state))
	copy(state, qc.state)
	return state
}

// Reset resets the circuit to its initial state
func (qc *QuantumCircuit) Reset() {
	qc.mu.Lock()
	defer qc.mu.Unlock()

	for i := range qc.state {
		qc.state[i] = Complex{Real: 0, Imag: 0}
	}
	qc.state[0] = Complex{Real: 1, Imag: 0}
} 