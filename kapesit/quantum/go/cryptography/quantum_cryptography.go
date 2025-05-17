package cryptography

import (
	"crypto/rand"
	"encoding/binary"
	"math"
	"sync"
)

// Complex represents a complex number
type Complex struct {
	Real, Imag float64
}

// QuantumCryptography handles quantum cryptography operations
type QuantumCryptography struct {
	mu     sync.RWMutex
	gates  map[string][][]Complex
	random *rand.Rand
}

// NewQuantumCryptography creates a new quantum cryptography instance
func NewQuantumCryptography() *QuantumCryptography {
	qc := &QuantumCryptography{
		gates:  make(map[string][][]Complex),
		random: rand.New(rand.NewSource(42)),
	}
	qc.initializeGates()
	return qc
}

func (qc *QuantumCryptography) initializeGates() {
	// Hadamard gate
	sqrt2 := 1.0 / math.Sqrt(2)
	qc.gates["H"] = [][]Complex{
		{{Real: sqrt2, Imag: 0}, {Real: sqrt2, Imag: 0}},
		{{Real: sqrt2, Imag: 0}, {Real: -sqrt2, Imag: 0}},
	}

	// Phase gate
	qc.gates["P"] = [][]Complex{
		{{Real: 1, Imag: 0}, {Real: 0, Imag: 0}},
		{{Real: 0, Imag: 0}, {Real: 1, Imag: 0}},
	}
}

// GenerateBB84Key generates a key using the BB84 protocol
func (qc *QuantumCryptography) GenerateBB84Key(keyLength int) ([]byte, []byte) {
	qc.mu.Lock()
	defer qc.mu.Unlock()

	// Generate random key and basis
	key := make([]byte, keyLength)
	basis := make([]byte, keyLength)
	for i := 0; i < keyLength; i++ {
		key[i] = byte(qc.random.Intn(2))
		basis[i] = byte(qc.random.Intn(2))
	}

	return key, basis
}

// EncryptMessage encrypts a message using a quantum key
func (qc *QuantumCryptography) EncryptMessage(message, key []byte) []byte {
	if len(message) != len(key) {
		panic("Message and key must have the same length")
	}

	encrypted := make([]byte, len(message))
	for i := range message {
		encrypted[i] = message[i] ^ key[i]
	}

	return encrypted
}

// DecryptMessage decrypts a message using a quantum key
func (qc *QuantumCryptography) DecryptMessage(encrypted, key []byte) []byte {
	if len(encrypted) != len(key) {
		panic("Encrypted message and key must have the same length")
	}

	decrypted := make([]byte, len(encrypted))
	for i := range encrypted {
		decrypted[i] = encrypted[i] ^ key[i]
	}

	return decrypted
}

// SimulateEavesdropping simulates an eavesdropper's interference
func (qc *QuantumCryptography) SimulateEavesdropping(originalKey, basis []byte, eavesdropProbability float64) ([]byte, float64) {
	if len(originalKey) != len(basis) {
		panic("Key and basis must have the same length")
	}

	eavesdroppedKey := make([]byte, len(originalKey))
	errors := 0

	for i := range originalKey {
		if qc.random.Float64() < eavesdropProbability {
			// Eavesdropper measures in random basis
			eavesdropperBasis := byte(qc.random.Intn(2))
			if eavesdropperBasis != basis[i] {
				// Wrong basis measurement introduces error
				eavesdroppedKey[i] = 1 - originalKey[i]
				errors++
			} else {
				eavesdroppedKey[i] = originalKey[i]
			}
		} else {
			eavesdroppedKey[i] = originalKey[i]
		}
	}

	errorRate := float64(errors) / float64(len(originalKey))
	return eavesdroppedKey, errorRate
}

// VerifyKeyIntegrity verifies the integrity of two keys
func (qc *QuantumCryptography) VerifyKeyIntegrity(key1, key2 []byte, sampleSize int) float64 {
	if len(key1) != len(key2) {
		panic("Keys must have the same length")
	}

	if sampleSize > len(key1) {
		sampleSize = len(key1)
	}

	// Sample random positions
	sample := make([]int, sampleSize)
	for i := range sample {
		sample[i] = qc.random.Intn(len(key1))
	}

	// Compare sampled bits
	errors := 0
	for _, pos := range sample {
		if key1[pos] != key2[pos] {
			errors++
		}
	}

	return float64(errors) / float64(sampleSize)
}

// GenerateEntangledPair generates a pair of entangled qubits
func (qc *QuantumCryptography) GenerateEntangledPair() ([]Complex, []Complex) {
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
func (qc *QuantumCryptography) QuantumTeleport(state []Complex, entangledPair [][]Complex) []Complex {
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

func (qc *QuantumCryptography) applyGate(gateName string, state []Complex) []Complex {
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

func (qc *QuantumCryptography) applyCNOT(control, target []Complex) []Complex {
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

func (qc *QuantumCryptography) measure(state []Complex) int {
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