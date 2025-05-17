using System;
using System.Numerics;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace Kapesit.Quantum.Communication
{
    public class QuantumCommunication
    {
        private readonly Random random;
        private readonly Dictionary<string, Complex[,]> gates;
        private readonly int numQubits;

        public QuantumCommunication(int numQubits)
        {
            this.numQubits = numQubits;
            this.random = new Random();
            this.gates = InitializeGates();
        }

        private Dictionary<string, Complex[,]> InitializeGates()
        {
            var gates = new Dictionary<string, Complex[,]>();
            
            // Hadamard gate
            var sqrt2 = 1.0 / Math.Sqrt(2);
            gates["H"] = new Complex[,] {
                { new Complex(sqrt2, 0), new Complex(sqrt2, 0) },
                { new Complex(sqrt2, 0), new Complex(-sqrt2, 0) }
            };

            // CNOT gate
            gates["CNOT"] = new Complex[,] {
                { Complex.One, Complex.Zero, Complex.Zero, Complex.Zero },
                { Complex.Zero, Complex.One, Complex.Zero, Complex.Zero },
                { Complex.Zero, Complex.Zero, Complex.Zero, Complex.One },
                { Complex.Zero, Complex.Zero, Complex.One, Complex.Zero }
            };

            return gates;
        }

        public (Complex[] state1, Complex[] state2) GenerateEntangledPair()
        {
            var state1 = new Complex[2];
            var state2 = new Complex[2];

            // Initialize to |0⟩
            state1[0] = Complex.One;
            state2[0] = Complex.One;

            // Apply Hadamard to first qubit
            ApplyGate("H", 0, state1);

            // Apply CNOT
            ApplyCNOT(state1, state2);

            return (state1, state2);
        }

        public byte[] QuantumTeleport(Complex[] state, Complex[] entangledState)
        {
            if (state.Length != 2 || entangledState.Length != 2)
                throw new ArgumentException("States must be single qubits");

            // Apply CNOT between state and first qubit of entangled pair
            ApplyCNOT(state, entangledState);

            // Apply Hadamard to state
            ApplyGate("H", 0, state);

            // Measure both qubits
            int measurement1 = Measure(state);
            int measurement2 = Measure(entangledState);

            // Apply corrections based on measurements
            var result = new byte[2];
            result[0] = (byte)measurement1;
            result[1] = (byte)measurement2;

            return result;
        }

        public Complex[] QuantumDenseCoding(byte message, Complex[] entangledState)
        {
            if (entangledState.Length != 2)
                throw new ArgumentException("State must be a single qubit");

            // Apply operations based on message
            switch (message)
            {
                case 0:
                    // Do nothing
                    break;
                case 1:
                    ApplyGate("X", 0, entangledState);
                    break;
                case 2:
                    ApplyGate("Z", 0, entangledState);
                    break;
                case 3:
                    ApplyGate("X", 0, entangledState);
                    ApplyGate("Z", 0, entangledState);
                    break;
            }

            return entangledState;
        }

        public byte QuantumDenseDecoding(Complex[] state1, Complex[] state2)
        {
            if (state1.Length != 2 || state2.Length != 2)
                throw new ArgumentException("States must be single qubits");

            // Apply CNOT
            ApplyCNOT(state1, state2);

            // Apply Hadamard to first qubit
            ApplyGate("H", 0, state1);

            // Measure both qubits
            int measurement1 = Measure(state1);
            int measurement2 = Measure(state2);

            // Combine measurements to get original message
            return (byte)((measurement1 << 1) | measurement2);
        }

        private void ApplyGate(string gateName, int qubit, Complex[] state)
        {
            if (!gates.TryGetValue(gateName, out Complex[,] gate))
                throw new ArgumentException($"Unknown gate: {gateName}");

            var newState = new Complex[state.Length];
            for (int i = 0; i < state.Length; i++)
            {
                int bit = (i >> qubit) & 1;
                int idx = i ^ (1 << qubit);
                if (i < idx)
                {
                    newState[i] = gate[0, 0] * state[i] + gate[0, 1] * state[idx];
                    newState[idx] = gate[1, 0] * state[i] + gate[1, 1] * state[idx];
                }
            }
            Array.Copy(newState, state, state.Length);
        }

        private void ApplyCNOT(Complex[] control, Complex[] target)
        {
            var newControl = new Complex[control.Length];
            var newTarget = new Complex[target.Length];

            for (int i = 0; i < control.Length; i++)
            {
                for (int j = 0; j < target.Length; j++)
                {
                    int controlBit = (i >> 0) & 1;
                    int targetBit = (j >> 0) & 1;
                    int newTargetBit = targetBit ^ controlBit;

                    if (controlBit == 1)
                    {
                        newControl[i] = control[i];
                        newTarget[newTargetBit] = target[j];
                    }
                    else
                    {
                        newControl[i] = control[i];
                        newTarget[j] = target[j];
                    }
                }
            }

            Array.Copy(newControl, control, control.Length);
            Array.Copy(newTarget, target, target.Length);
        }

        private int Measure(Complex[] state)
        {
            double[] probabilities = new double[2];
            for (int i = 0; i < state.Length; i++)
            {
                probabilities[i] = state[i].Magnitude * state[i].Magnitude;
            }

            double r = random.NextDouble();
            int result = r < probabilities[0] ? 0 : 1;

            // Collapse state
            var newState = new Complex[state.Length];
            newState[result] = Complex.One;
            Array.Copy(newState, state, state.Length);

            return result;
        }
    }
} 