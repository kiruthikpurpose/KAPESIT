package error_correction

import (
	"math"
	"math/rand"
	"sync"
)

// Complex represents a complex number
type Complex struct {
	Real, Imag float64
}

// ErrorType represents different types of quantum errors
type ErrorType int

const (
	NoError ErrorType = iota
	BitFlip
	PhaseFlip
	BitPhaseFlip
)

// QuantumErrorCorrection handles quantum error correction
type QuantumErrorCorrection struct {
	mu       sync.RWMutex
	random   *rand.Rand
	gates    map[string][][]Complex
	numQubits int
	state    []Complex
}

// NewQuantumErrorCorrection creates a new quantum error correction instance
func NewQuantumErrorCorrection(numQubits int) *QuantumErrorCorrection {
	qec := &QuantumErrorCorrection{
		random:   rand.New(rand.NewSource(42)),
		gates:    make(map[string][][]Complex),
		numQubits: numQubits,
		state:    make([]Complex, 1<<numQubits),
	}
	qec.initializeGates()
	qec.initializeState()
	return qec
}

func (qec *QuantumErrorCorrection) initializeGates() {
	// Hadamard gate
	sqrt2 := 1.0 / math.Sqrt(2)
	qec.gates["H"] = [][]Complex{
		{{Real: sqrt2, Imag: 0}, {Real: sqrt2, Imag: 0}},
		{{Real: sqrt2, Imag: 0}, {Real: -sqrt2, Imag: 0}},
	}

	// CNOT gate
	qec.gates["CNOT"] = [][]Complex{
		{{Real: 1, Imag: 0}, {Real: 0, Imag: 0}, {Real: 0, Imag: 0}, {Real: 0, Imag: 0}},
		{{Real: 0, Imag: 0}, {Real: 1, Imag: 0}, {Real: 0, Imag: 0}, {Real: 0, Imag: 0}},
		{{Real: 0, Imag: 0}, {Real: 0, Imag: 0}, {Real: 0, Imag: 0}, {Real: 1, Imag: 0}},
		{{Real: 0, Imag: 0}, {Real: 0, Imag: 0}, {Real: 1, Imag: 0}, {Real: 0, Imag: 0}},
	}

	// Phase gate
	qec.gates["S"] = [][]Complex{
		{{Real: 1, Imag: 0}, {Real: 0, Imag: 0}},
		{{Real: 0, Imag: 0}, {Real: 0, Imag: 1}},
	}
}

func (qec *QuantumErrorCorrection) initializeState() {
	qec.state[0] = Complex{Real: 1, Imag: 0}
}

// EncodeShor encodes a logical qubit using Shor code
func (qec *QuantumErrorCorrection) EncodeShor(logicalQubit int) {
	qec.mu.Lock()
	defer qec.mu.Unlock()

	// Apply CNOT gates to create entanglement
	for i := 0; i < 8; i++ {
		qec.applyCNOT(logicalQubit, logicalQubit+1+i)
	}

	// Apply Hadamard gates
	for i := 0; i < 9; i++ {
		qec.applyGate("H", logicalQubit+i)
	}
}

// DecodeShor decodes a logical qubit using Shor code
func (qec *QuantumErrorCorrection) DecodeShor(logicalQubit int) {
	qec.mu.Lock()
	defer qec.mu.Unlock()

	// Apply Hadamard gates
	for i := 0; i < 9; i++ {
		qec.applyGate("H", logicalQubit+i)
	}

	// Apply CNOT gates to disentangle
	for i := 0; i < 8; i++ {
		qec.applyCNOT(logicalQubit, logicalQubit+1+i)
	}
}

// ApplyError applies a quantum error to a qubit
func (qec *QuantumErrorCorrection) ApplyError(qubit int, errorType ErrorType) {
	qec.mu.Lock()
	defer qec.mu.Unlock()

	switch errorType {
	case BitFlip:
		qec.applyGate("X", qubit)
	case PhaseFlip:
		qec.applyGate("Z", qubit)
	case BitPhaseFlip:
		qec.applyGate("Y", qubit)
	}
}

// MeasureSyndrome measures the error syndrome
func (qec *QuantumErrorCorrection) MeasureSyndrome(logicalQubit int) []int {
	qec.mu.Lock()
	defer qec.mu.Unlock()

	syndrome := make([]int, 8)
	
	// Measure stabilizers
	for i := 0; i < 8; i++ {
		syndrome[i] = qec.measure(logicalQubit + i)
	}

	return syndrome
}

// CorrectError corrects errors based on syndrome
func (qec *QuantumErrorCorrection) CorrectError(logicalQubit int, syndrome []int) {
	qec.mu.Lock()
	defer qec.mu.Unlock()

	// Simple error correction based on syndrome
	for i, s := range syndrome {
		if s == 1 {
			qec.applyGate("X", logicalQubit+i)
		}
	}
}

func (qec *QuantumErrorCorrection) applyGate(gateName string, qubit int) {
	gate, exists := qec.gates[gateName]
	if !exists {
		panic("Unknown gate: " + gateName)
	}

	newState := make([]Complex, len(qec.state))
	for i := 0; i < len(qec.state); i++ {
		bit := (i >> qubit) & 1
		idx := i ^ (1 << qubit)
		if i < idx {
			newState[i] = Complex{
				Real: gate[0][0].Real*qec.state[i].Real - gate[0][0].Imag*qec.state[i].Imag +
					gate[0][1].Real*qec.state[idx].Real - gate[0][1].Imag*qec.state[idx].Imag,
				Imag: gate[0][0].Real*qec.state[i].Imag + gate[0][0].Imag*qec.state[i].Real +
					gate[0][1].Real*qec.state[idx].Imag + gate[0][1].Imag*qec.state[idx].Real,
			}
			newState[idx] = Complex{
				Real: gate[1][0].Real*qec.state[i].Real - gate[1][0].Imag*qec.state[i].Imag +
					gate[1][1].Real*qec.state[idx].Real - gate[1][1].Imag*qec.state[idx].Imag,
				Imag: gate[1][0].Real*qec.state[i].Imag + gate[1][0].Imag*qec.state[i].Real +
					gate[1][1].Real*qec.state[idx].Imag + gate[1][1].Imag*qec.state[idx].Real,
			}
		}
	}
	copy(qec.state, newState)
}

func (qec *QuantumErrorCorrection) applyCNOT(control, target int) {
	newState := make([]Complex, len(qec.state))
	for i := 0; i < len(qec.state); i++ {
		controlBit := (i >> control) & 1
		targetBit := (i >> target) & 1
		newTargetBit := targetBit ^ controlBit

		if controlBit == 1 {
			idx := i ^ (1 << target)
			newState[idx] = qec.state[i]
		} else {
			newState[i] = qec.state[i]
		}
	}
	copy(qec.state, newState)
}

func (qec *QuantumErrorCorrection) measure(qubit int) int {
	probabilities := make([]float64, 2)
	for i := 0; i < len(qec.state); i++ {
		if (i & (1 << qubit)) != 0 {
			probabilities[1] += qec.state[i].Real*qec.state[i].Real + qec.state[i].Imag*qec.state[i].Imag
		} else {
			probabilities[0] += qec.state[i].Real*qec.state[i].Real + qec.state[i].Imag*qec.state[i].Imag
		}
	}

	r := qec.random.Float64()
	result := 0
	if r >= probabilities[0] {
		result = 1
	}

	// Collapse state
	newState := make([]Complex, len(qec.state))
	norm := 0.0
	for i := 0; i < len(qec.state); i++ {
		if ((i >> qubit) & 1) == result {
			newState[i] = qec.state[i]
			norm += qec.state[i].Real*qec.state[i].Real + qec.state[i].Imag*qec.state[i].Imag
		}
	}

	// Normalize
	norm = math.Sqrt(norm)
	for i := 0; i < len(qec.state); i++ {
		if newState[i].Real != 0 || newState[i].Imag != 0 {
			newState[i].Real /= norm
			newState[i].Imag /= norm
		}
	}

	copy(qec.state, newState)
	return result
} 