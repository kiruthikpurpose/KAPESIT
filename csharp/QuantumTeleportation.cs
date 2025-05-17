using System;
using System.Numerics;
using MathNet.Numerics.LinearAlgebra;
using MathNet.Numerics.LinearAlgebra.Double;

namespace Quantum
{
    public class QuantumTeleportation
    {
        private readonly DenseVector state;
        private readonly DenseMatrix hGate;
        private readonly DenseMatrix cnotGate;
        private readonly DenseMatrix xGate;
        private readonly DenseMatrix zGate;

        public QuantumTeleportation()
        {
            state = DenseVector.Create(8, i => i == 0 ? 1.0 : 0.0);
            hGate = DenseMatrix.OfArray(new double[,] {
                { 1/Math.Sqrt(2), 1/Math.Sqrt(2) },
                { 1/Math.Sqrt(2), -1/Math.Sqrt(2) }
            });
            cnotGate = DenseMatrix.OfArray(new double[,] {
                { 1, 0, 0, 0 },
                { 0, 1, 0, 0 },
                { 0, 0, 0, 1 },
                { 0, 0, 1, 0 }
            });
            xGate = DenseMatrix.OfArray(new double[,] {
                { 0, 1 },
                { 1, 0 }
            });
            zGate = DenseMatrix.OfArray(new double[,] {
                { 1, 0 },
                { 0, -1 }
            });
        }

        public void CreateBellState()
        {
            // Apply Hadamard to first qubit
            ApplyGate(hGate, 0);
            
            // Apply CNOT
            ApplyGate(cnotGate, 1);
        }

        public void ApplyGate(DenseMatrix gate, int target)
        {
            var result = DenseVector.Create(8, 0.0);
            var gateSize = gate.RowCount;

            for (int i = 0; i < 8; i++)
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

        public void Teleport()
        {
            // Apply CNOT between Alice's qubit and her half of Bell state
            ApplyGate(cnotGate, 1);

            // Apply Hadamard to Alice's qubit
            ApplyGate(hGate, 0);

            // Measure Alice's qubits
            var aliceMeasurements = new int[2];
            for (int i = 0; i < 2; i++)
            {
                aliceMeasurements[i] = Measure();
            }

            // Apply correction gates based on measurements
            if (aliceMeasurements[0] == 1)
            {
                // Apply X gate
                ApplyGate(xGate, 2);
            }
            if (aliceMeasurements[1] == 1)
            {
                // Apply Z gate
                ApplyGate(zGate, 2);
            }
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
