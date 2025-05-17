package quantum

import (
    "math"
    "math/rand"
)

type QuantumState struct {
    state     []float64
    numQubits int
}

func NewQuantumState(numQubits int) *QuantumState {
    size := 1 << numQubits
    state := make([]float64, size)
    state[0] = 1.0
    return &QuantumState{
        state:     state,
        numQubits: numQubits,
    }
}

func (q *QuantumState) ApplyGate(gate [][]float64, target int) {
    size := 1 << q.numQubits
    result := make([]float64, size)
    gateSize := len(gate)

    for i := 0; i < size; i++ {
        sum := 0.0
        for j := 0; j < gateSize; j++ {
            mask := 1 << target
            bitI := (i & mask) >> target
            bitJ := (j & mask) >> target

            index := (i & ^mask) | (bitJ << target)
            sum += gate[j][bitI] * q.state[index]
        }
        result[i] = sum
    }

    q.state = result
}

func (q *QuantumState) Measure() int {
    probabilities := make([]float64, len(q.state))
    total := 0.0

    for i, val := range q.state {
        probabilities[i] = math.Pow(val, 2)
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
            newState := make([]float64, len(q.state))
            newState[i] = 1.0
            q.state = newState
            return i
        }
    }

    return 0
}
