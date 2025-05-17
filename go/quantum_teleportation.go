package quantum

import (
    "math"
    "math/rand"
)

type QuantumTeleportation struct {
    state     []complex128
    bellState []complex128
    numQubits int
}

func NewQuantumTeleportation() *QuantumTeleportation {
    return &QuantumTeleportation{
        state:     []complex128{math.Sqrt(0.5), math.Sqrt(0.5)},
        bellState: []complex128{1.0, 0.0, 0.0, 1.0},
        numQubits: 2,
    }
}

func (q *QuantumTeleportation) CreateBellState() {
    // Apply Hadamard to first qubit
    hGate := []complex128{complex(1, 0), complex(1, 0), complex(1, 0), complex(-1, 0)}
    q.ApplyGate(hGate, 0)
    
    // Apply CNOT
    cnotGate := []complex128{
        complex(1, 0), complex(0, 0), complex(0, 0), complex(0, 0),
        complex(0, 0), complex(1, 0), complex(0, 0), complex(0, 0),
        complex(0, 0), complex(0, 0), complex(0, 0), complex(1, 0),
        complex(0, 0), complex(0, 0), complex(1, 0), complex(0, 0),
    }
    q.ApplyGate(cnotGate, 1)
}

func (q *QuantumTeleportation) ApplyGate(gate []complex128, target int) {
    size := 1 << q.numQubits
    result := make([]complex128, size)
    gateSize := len(gate)

    for i := 0; i < size; i++ {
        sum := complex(0, 0)
        for j := 0; j < gateSize; j++ {
            mask := 1 << target
            bitI := (i & mask) >> target
            bitJ := (j & mask) >> target

            index := (i & ^mask) | (bitJ << target)
            sum += gate[j*gateSize+bitI] * q.state[index]
        }
        result[i] = sum
    }

    q.state = result
}

func (q *QuantumTeleportation) Teleport() []complex128 {
    // Apply CNOT between Alice's qubit and her half of Bell state
    cnotGate := []complex128{
        complex(1, 0), complex(0, 0), complex(0, 0), complex(0, 0),
        complex(0, 0), complex(1, 0), complex(0, 0), complex(0, 0),
        complex(0, 0), complex(0, 0), complex(0, 0), complex(1, 0),
        complex(0, 0), complex(0, 0), complex(1, 0), complex(0, 0),
    }
    q.ApplyGate(cnotGate, 1)

    // Apply Hadamard to Alice's qubit
    hGate := []complex128{complex(1, 0), complex(1, 0), complex(1, 0), complex(-1, 0)}
    q.ApplyGate(hGate, 0)

    // Measure Alice's qubits
    aliceMeasurements := make([]int, 2)
    for i := 0; i < 2; i++ {
        aliceMeasurements[i] = q.Measure()
    }

    // Apply correction gates based on measurements
    if aliceMeasurements[0] == 1 {
        // Apply X gate
        xGate := []complex128{complex(0, 0), complex(1, 0), complex(1, 0), complex(0, 0)}
        q.ApplyGate(xGate, 2)
    }
    if aliceMeasurements[1] == 1 {
        // Apply Z gate
        zGate := []complex(1, 0), complex(0, 0), complex(0, 0), complex(-1, 0)
        q.ApplyGate(zGate, 2)
    }

    return q.state
}

func (q *QuantumTeleportation) Measure() int {
    probabilities := make([]float64, len(q.state))
    total := 0.0

    for i, val := range q.state {
        probabilities[i] = math.Pow(real(val)*real(val)+imag(val)*imag(val), 2)
        total += probabilities[i]
    }

    for i := range probabilities {
        probabilities[i] /= total
    }

    r := rand.Float64()
    cumulative := 0.0

    for i, prob := range probabilities {
        cumulative += prob
        if r <= cumulative {
            newState := make([]complex128, len(q.state))
            newState[i] = complex(1, 0)
            q.state = newState
            return i
        }
    }

    return 0
}
