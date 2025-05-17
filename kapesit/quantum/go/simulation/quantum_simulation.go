package simulation

import (
	"math"
	"math/rand"
	"sync"
)

// Complex represents a complex number
type Complex struct {
	Real, Imag float64
}

// QuantumSimulation handles quantum state simulation
type QuantumSimulation struct {
	mu       sync.RWMutex
	random   *rand.Rand
	gates    map[string][][]Complex
	numQubits int
	state    []Complex
}

// NewQuantumSimulation creates a new quantum simulation instance
func NewQuantumSimulation(numQubits int) *QuantumSimulation {
	qs := &QuantumSimulation{
		random:   rand.New(rand.NewSource(42)),
		gates:    make(map[string][][]Complex),
		numQubits: numQubits,
		state:    make([]Complex, 1<<numQubits),
	}
	qs.initializeGates()
	qs.initializeState()
	return qs
}

func (qs *QuantumSimulation) initializeGates() {
	// Hadamard gate
	sqrt2 := 1.0 / math.Sqrt(2)
	qs.gates["H"] = [][]Complex{
		{{Real: sqrt2, Imag: 0}, {Real: sqrt2, Imag: 0}},
		{{Real: sqrt2, Imag: 0}, {Real: -sqrt2, Imag: 0}},
	}

	// Pauli gates
	qs.gates["X"] = [][]Complex{
		{{Real: 0, Imag: 0}, {Real: 1, Imag: 0}},
		{{Real: 1, Imag: 0}, {Real: 0, Imag: 0}},
	}

	qs.gates["Y"] = [][]Complex{
		{{Real: 0, Imag: 0}, {Real: 0, Imag: -1}},
		{{Real: 0, Imag: 1}, {Real: 0, Imag: 0}},
	}

	qs.gates["Z"] = [][]Complex{
		{{Real: 1, Imag: 0}, {Real: 0, Imag: 0}},
		{{Real: 0, Imag: 0}, {Real: -1, Imag: 0}},
	}

	// Phase gates
	qs.gates["S"] = [][]Complex{
		{{Real: 1, Imag: 0}, {Real: 0, Imag: 0}},
		{{Real: 0, Imag: 0}, {Real: 0, Imag: 1}},
	}

	qs.gates["T"] = [][]Complex{
		{{Real: 1, Imag: 0}, {Real: 0, Imag: 0}},
		{{Real: 0, Imag: 0}, {Real: 1.0 / math.Sqrt(2), Imag: 1.0 / math.Sqrt(2)}},
	}
}

func (qs *QuantumSimulation) initializeState() {
	qs.state[0] = Complex{Real: 1, Imag: 0}
}

// ApplyGate applies a quantum gate to a qubit
func (qs *QuantumSimulation) ApplyGate(gateName string, qubit int) {
	qs.mu.Lock()
	defer qs.mu.Unlock()

	gate, exists := qs.gates[gateName]
	if !exists {
		panic("Unknown gate: " + gateName)
	}

	newState := make([]Complex, len(qs.state))
	for i := 0; i < len(qs.state); i++ {
		bit := (i >> qubit) & 1
		idx := i ^ (1 << qubit)
		if i < idx {
			newState[i] = Complex{
				Real: gate[0][0].Real*qs.state[i].Real - gate[0][0].Imag*qs.state[i].Imag +
					gate[0][1].Real*qs.state[idx].Real - gate[0][1].Imag*qs.state[idx].Imag,
				Imag: gate[0][0].Real*qs.state[i].Imag + gate[0][0].Imag*qs.state[i].Real +
					gate[0][1].Real*qs.state[idx].Imag + gate[0][1].Imag*qs.state[idx].Real,
			}
			newState[idx] = Complex{
				Real: gate[1][0].Real*qs.state[i].Real - gate[1][0].Imag*qs.state[i].Imag +
					gate[1][1].Real*qs.state[idx].Real - gate[1][1].Imag*qs.state[idx].Imag,
				Imag: gate[1][0].Real*qs.state[i].Imag + gate[1][0].Imag*qs.state[i].Real +
					gate[1][1].Real*qs.state[idx].Imag + gate[1][1].Imag*qs.state[idx].Real,
			}
		}
	}
	copy(qs.state, newState)
}

// ApplyControlledGate applies a controlled quantum gate
func (qs *QuantumSimulation) ApplyControlledGate(gateName string, control, target int) {
	qs.mu.Lock()
	defer qs.mu.Unlock()

	gate, exists := qs.gates[gateName]
	if !exists {
		panic("Unknown gate: " + gateName)
	}

	newState := make([]Complex, len(qs.state))
	for i := 0; i < len(qs.state); i++ {
		controlBit := (i >> control) & 1
		targetBit := (i >> target) & 1
		idx := i ^ (1 << target)

		if controlBit == 1 && i < idx {
			newState[i] = Complex{
				Real: gate[0][0].Real*qs.state[i].Real - gate[0][0].Imag*qs.state[i].Imag +
					gate[0][1].Real*qs.state[idx].Real - gate[0][1].Imag*qs.state[idx].Imag,
				Imag: gate[0][0].Real*qs.state[i].Imag + gate[0][0].Imag*qs.state[i].Real +
					gate[0][1].Real*qs.state[idx].Imag + gate[0][1].Imag*qs.state[idx].Real,
			}
			newState[idx] = Complex{
				Real: gate[1][0].Real*qs.state[i].Real - gate[1][0].Imag*qs.state[i].Imag +
					gate[1][1].Real*qs.state[idx].Real - gate[1][1].Imag*qs.state[idx].Imag,
				Imag: gate[1][0].Real*qs.state[i].Imag + gate[1][0].Imag*qs.state[i].Real +
					gate[1][1].Real*qs.state[idx].Imag + gate[1][1].Imag*qs.state[idx].Real,
			}
		} else {
			newState[i] = qs.state[i]
		}
	}
	copy(qs.state, newState)
}

// Measure measures a qubit and returns the result
func (qs *QuantumSimulation) Measure(qubit int) int {
	qs.mu.Lock()
	defer qs.mu.Unlock()

	// Calculate probabilities
	prob0 := 0.0
	prob1 := 0.0
	for i := 0; i < len(qs.state); i++ {
		bit := (i >> qubit) & 1
		amp := qs.state[i]
		if bit == 0 {
			prob0 += amp.Real*amp.Real + amp.Imag*amp.Imag
		} else {
			prob1 += amp.Real*amp.Real + amp.Imag*amp.Imag
		}
	}

	// Normalize
	total := prob0 + prob1
	prob0 /= total
	prob1 /= total

	// Sample from distribution
	result := 0
	if qs.random.Float64() >= prob0 {
		result = 1
	}

	// Collapse state
	newState := make([]Complex, len(qs.state))
	for i := 0; i < len(qs.state); i++ {
		bit := (i >> qubit) & 1
		if bit == result {
			newState[i] = qs.state[i]
		}
	}

	// Normalize collapsed state
	norm := 0.0
	for i := range newState {
		norm += newState[i].Real*newState[i].Real + newState[i].Imag*newState[i].Imag
	}
	norm = math.Sqrt(norm)
	for i := range newState {
		newState[i].Real /= norm
		newState[i].Imag /= norm
	}

	copy(qs.state, newState)
	return result
}

// GetState returns the current quantum state
func (qs *QuantumSimulation) GetState() []Complex {
	qs.mu.RLock()
	defer qs.mu.RUnlock()

	state := make([]Complex, len(qs.state))
	copy(state, qs.state)
	return state
}

// Reset resets the quantum state to |0⟩
func (qs *QuantumSimulation) Reset() {
	qs.mu.Lock()
	defer qs.mu.Unlock()

	qs.initializeState()
}

// ApplyRotation applies a rotation gate to a qubit
func (qs *QuantumSimulation) ApplyRotation(axis string, qubit int, angle float64) {
	qs.mu.Lock()
	defer qs.mu.Unlock()

	var gate [][]Complex
	switch axis {
	case "X":
		gate = [][]Complex{
			{{Real: math.Cos(angle/2), Imag: 0}, {Real: 0, Imag: -math.Sin(angle/2)}},
			{{Real: 0, Imag: -math.Sin(angle/2)}, {Real: math.Cos(angle/2), Imag: 0}},
		}
	case "Y":
		gate = [][]Complex{
			{{Real: math.Cos(angle/2), Imag: 0}, {Real: -math.Sin(angle/2), Imag: 0}},
			{{Real: math.Sin(angle/2), Imag: 0}, {Real: math.Cos(angle/2), Imag: 0}},
		}
	case "Z":
		gate = [][]Complex{
			{{Real: math.Exp(-angle/2), Imag: 0}, {Real: 0, Imag: 0}},
			{{Real: 0, Imag: 0}, {Real: math.Exp(angle/2), Imag: 0}},
		}
	default:
		panic("Invalid rotation axis: " + axis)
	}

	newState := make([]Complex, len(qs.state))
	for i := 0; i < len(qs.state); i++ {
		bit := (i >> qubit) & 1
		idx := i ^ (1 << qubit)
		if i < idx {
			newState[i] = Complex{
				Real: gate[0][0].Real*qs.state[i].Real - gate[0][0].Imag*qs.state[i].Imag +
					gate[0][1].Real*qs.state[idx].Real - gate[0][1].Imag*qs.state[idx].Imag,
				Imag: gate[0][0].Real*qs.state[i].Imag + gate[0][0].Imag*qs.state[i].Real +
					gate[0][1].Real*qs.state[idx].Imag + gate[0][1].Imag*qs.state[idx].Real,
			}
			newState[idx] = Complex{
				Real: gate[1][0].Real*qs.state[i].Real - gate[1][0].Imag*qs.state[i].Imag +
					gate[1][1].Real*qs.state[idx].Real - gate[1][1].Imag*qs.state[idx].Imag,
				Imag: gate[1][0].Real*qs.state[i].Imag + gate[1][0].Imag*qs.state[i].Real +
					gate[1][1].Real*qs.state[idx].Imag + gate[1][1].Imag*qs.state[idx].Real,
			}
		}
	}
	copy(qs.state, newState)
} 