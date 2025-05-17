using System;
using System.Numerics;
using MathNet.Numerics.LinearAlgebra;
using MathNet.Numerics.LinearAlgebra.Double;

namespace Quantum
{
    public class QuantumState
    {
        private readonly DenseVector state;
        private readonly int numQubits;

        public QuantumState(int numQubits)
        {
            this.numQubits = numQubits;
            this.state = DenseVector.Create(1 << numQubits, i => i == 0 ? 1.0 : 0.0);
        }

        public void ApplyGate(Matrix<double> gate, int target)
        {
            var result = DenseVector.Create(1 << numQubits, 0.0);
            var gateSize = gate.RowCount;

            for (int i = 0; i < (1 << numQubits); i++)
            {
                double sum = 0.0;
                for (int j = 0; j < gateSize; j++)
                {
                    int mask = 1 << target;
                    int bitI = (i & mask) >> target;
                    int bitJ = (j & mask) >> target;

                    int index = (i & ~mask) | (bitJ << target);
                    sum += gate[j, bitI] * state[index];
                }
                result[i] = sum;
            }

            state = result;
        }

        public int Measure()
        {
            var probabilities = new double[state.Count];
            double total = 0.0;

            for (int i = 0; i < state.Count; i++)
            {
                probabilities[i] = Math.Pow(state[i], 2);
                total += probabilities[i];
            }

            var random = new Random();
            double r = random.NextDouble() * total;
            double cumulative = 0.0;

            for (int i = 0; i < state.Count; i++)
            {
                cumulative += probabilities[i];
                if (r <= cumulative)
                {
                    var newState = DenseVector.Create(state.Count, 0.0);
                    newState[i] = 1.0;
                    state = newState;
                    return i;
                }
            }

            return 0;
        }
    }
}
