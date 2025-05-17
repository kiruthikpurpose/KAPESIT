package communication

import (
	"math"
	"math/rand"
	"sync"
)

// Complex represents a complex number
type Complex struct {
	Real, Imag float64
}

// QuantumCommunication handles quantum communication protocols
type QuantumCommunication struct {
	mu       sync.RWMutex
	random   *rand.Rand
	gates    map[string][][]Complex
	numQubits int
	state    []Complex
}

// NewQuantumCommunication creates a new quantum communication instance
func NewQuantumCommunication(numQubits int) *QuantumCommunication {
	qc := &QuantumCommunication{
		random:   rand.New(rand.NewSource(42)),
		gates:    make(map[string][][]Complex),
		numQubits: numQubits,
		state:    make([]Complex, 1<<numQubits),
	}
	qc.initializeGates()
	qc.initializeState()
	return qc
}

func (qc *QuantumCommunication) initializeGates() {
	// Hadamard gate
	sqrt2 := 1.0 / math.Sqrt(2)
	qc.gates["H"] = [][]Complex{
		{{Real: sqrt2, Imag: 0}, {Real: sqrt2, Imag: 0}},
		{{Real: sqrt2, Imag: 0}, {Real: -sqrt2, Imag: 0}},
	}

	// CNOT gate
	qc.gates["CNOT"] = [][]Complex{
		{{Real: 1, Imag: 0}, {Real: 0, Imag: 0}, {Real: 0, Imag: 0}, {Real: 0, Imag: 0}},
		{{Real: 0, Imag: 0}, {Real: 1, Imag: 0}, {Real: 0, Imag: 0}, {Real: 0, Imag: 0}},
		{{Real: 0, Imag: 0}, {Real: 0, Imag: 0}, {Real: 0, Imag: 0}, {Real: 1, Imag: 0}},
		{{Real: 0, Imag: 0}, {Real: 0, Imag: 0}, {Real: 1, Imag: 0}, {Real: 0, Imag: 0}},
	}
}

func (qc *QuantumCommunication) initializeState() {
	qc.state[0] = Complex{Real: 1, Imag: 0}
}

// GenerateEntangledPair generates a pair of entangled qubits
func (qc *QuantumCommunication) GenerateEntangledPair() ([]Complex, []Complex) {
	qc.mu.Lock()
	defer qc.mu.Unlock()

	// Initialize Bell state
	state1 := make([]Complex, 2)
	state2 := make([]Complex, 2)

	// Apply Hadamard to first qubit
	state1[0] = Complex{Real: 1.0 / math.Sqrt(2), Imag: 0}
	state1[1] = Complex{Real: 1.0 / math.Sqrt(2), Imag: 0}

	// Apply CNOT
	state2[0] = state1[0]
	state2[1] = state1[1]

	return state1, state2
}

// QuantumTeleport teleports a quantum state
func (qc *QuantumCommunication) QuantumTeleport(state []Complex, entangledPair [][]Complex) []Complex {
	qc.mu.Lock()
	defer qc.mu.Unlock()

	if len(state) != 2 || len(entangledPair) != 2 || len(entangledPair[0]) != 2 || len(entangledPair[1]) != 2 {
		panic("Invalid input dimensions")
	}

	// Apply CNOT between state and first entangled qubit
	state = qc.applyCNOT(state, entangledPair[0])

	// Apply Hadamard to state
	state = qc.applyGate("H", state)

	// Measure state and first entangled qubit
	measurement1 := qc.measure(state)
	measurement2 := qc.measure(entangledPair[0])

	// Apply corrections to second entangled qubit
	result := make([]Complex, 2)
	copy(result, entangledPair[1])

	if measurement2 == 1 {
		result = qc.applyGate("X", result)
	}
	if measurement1 == 1 {
		result = qc.applyGate("Z", result)
	}

	return result
}

// QuantumDenseCoding encodes two classical bits into one qubit
func (qc *QuantumCommunication) QuantumDenseCoding(message int, entangledPair [][]Complex) []Complex {
	qc.mu.Lock()
	defer qc.mu.Unlock()

	if message < 0 || message > 3 {
		panic("Message must be between 0 and 3")
	}

	if len(entangledPair) != 2 || len(entangledPair[0]) != 2 || len(entangledPair[1]) != 2 {
		panic("Invalid entangled pair dimensions")
	}

	// Apply operations based on message
	state := make([]Complex, 2)
	copy(state, entangledPair[0])

	switch message {
	case 1:
		state = qc.applyGate("X", state)
	case 2:
		state = qc.applyGate("Z", state)
	case 3:
		state = qc.applyGate("X", state)
		state = qc.applyGate("Z", state)
	}

	return state
}

// QuantumDenseDecoding decodes two classical bits from one qubit
func (qc *QuantumCommunication) QuantumDenseDecoding(state []Complex, entangledPair [][]Complex) int {
	qc.mu.Lock()
	defer qc.mu.Unlock()

	if len(state) != 2 || len(entangledPair) != 2 || len(entangledPair[0]) != 2 || len(entangledPair[1]) != 2 {
		panic("Invalid input dimensions")
	}

	// Apply CNOT
	state = qc.applyCNOT(state, entangledPair[1])

	// Apply Hadamard
	state = qc.applyGate("H", state)

	// Measure both qubits
	measurement1 := qc.measure(state)
	measurement2 := qc.measure(entangledPair[1])

	// Combine measurements into message
	return (measurement1 << 1) | measurement2
}

func (qc *QuantumCommunication) applyGate(gateName string, state []Complex) []Complex {
	gate, exists := qc.gates[gateName]
	if !exists {
		panic("Unknown gate: " + gateName)
	}

	newState := make([]Complex, len(state))
	for i := range state {
		newState[i] = Complex{
			Real: gate[i][0].Real*state[0].Real - gate[i][0].Imag*state[0].Imag +
				gate[i][1].Real*state[1].Real - gate[i][1].Imag*state[1].Imag,
			Imag: gate[i][0].Real*state[0].Imag + gate[i][0].Imag*state[0].Real +
				gate[i][1].Real*state[1].Imag + gate[i][1].Imag*state[1].Real,
		}
	}

	return newState
}

func (qc *QuantumCommunication) applyCNOT(control, target []Complex) []Complex {
	if len(control) != 2 || len(target) != 2 {
		panic("Invalid input dimensions")
	}

	newTarget := make([]Complex, 2)
	if control[1].Real != 0 || control[1].Imag != 0 {
		// Control qubit is |1⟩, flip target
		newTarget[0] = target[1]
		newTarget[1] = target[0]
	} else {
		// Control qubit is |0⟩, leave target unchanged
		newTarget[0] = target[0]
		newTarget[1] = target[1]
	}

	return newTarget
}

func (qc *QuantumCommunication) measure(state []Complex) int {
	// Calculate probabilities
	prob0 := state[0].Real*state[0].Real + state[0].Imag*state[0].Imag
	prob1 := state[1].Real*state[1].Real + state[1].Imag*state[1].Imag

	// Normalize
	total := prob0 + prob1
	prob0 /= total
	prob1 /= total

	// Sample from distribution
	if qc.random.Float64() < prob0 {
		return 0
	}
	return 1
} 