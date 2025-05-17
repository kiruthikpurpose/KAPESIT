using System;
using System.Numerics;
using System.Threading.Tasks;
using System.Collections.Concurrent;

namespace Kapesit.Quantum.Simulation
{
    public class QuantumSimulator
    {
        private readonly int numQubits;
        private readonly Complex[] state;
        private readonly ConcurrentDictionary<string, Complex[,]> gates;
        private readonly object stateLock = new object();

        public QuantumSimulator(int numQubits)
        {
            if (numQubits <= 0)
                throw new ArgumentException("Number of qubits must be positive");

            this.numQubits = numQubits;
            this.state = new Complex[1 << numQubits];
            this.state[0] = Complex.One;
            this.gates = InitializeGates();
        }

        private ConcurrentDictionary<string, Complex[,]> InitializeGates()
        {
            var gates = new ConcurrentDictionary<string, Complex[,]>();
            
            // Hadamard gate
            var sqrt2 = 1.0 / Math.Sqrt(2);
            gates["H"] = new Complex[,] {
                { new Complex(sqrt2, 0), new Complex(sqrt2, 0) },
                { new Complex(sqrt2, 0), new Complex(-sqrt2, 0) }
            };

            // Pauli gates
            gates["X"] = new Complex[,] {
                { Complex.Zero, Complex.One },
                { Complex.One, Complex.Zero }
            };

            gates["Y"] = new Complex[,] {
                { Complex.Zero, new Complex(0, -1) },
                { new Complex(0, 1), Complex.Zero }
            };

            gates["Z"] = new Complex[,] {
                { Complex.One, Complex.Zero },
                { Complex.Zero, -Complex.One }
            };

            return gates;
        }

        public void ApplyGate(string gateName, int target)
        {
            if (!gates.TryGetValue(gateName, out Complex[,] gate))
                throw new ArgumentException($"Unknown gate: {gateName}");

            lock (stateLock)
            {
                var newState = new Complex[state.Length];
                Parallel.For(0, state.Length, i =>
                {
                    int bit = (i >> target) & 1;
                    int idx = i ^ (1 << target);
                    if (i < idx)
                    {
                        newState[i] = gate[0, 0] * state[i] + gate[0, 1] * state[idx];
                        newState[idx] = gate[1, 0] * state[i] + gate[1, 1] * state[idx];
                    }
                });
                Array.Copy(newState, state, state.Length);
            }
        }

        public int Measure(int qubit)
        {
            lock (stateLock)
            {
                double[] probabilities = new double[2];
                for (int i = 0; i < state.Length; i++)
                {
                    if ((i & (1 << qubit)) != 0)
                        probabilities[1] += state[i].Magnitude * state[i].Magnitude;
                    else
                        probabilities[0] += state[i].Magnitude * state[i].Magnitude;
                }

                Random random = new Random();
                double r = random.NextDouble();
                int result = r < probabilities[0] ? 0 : 1;

                // Collapse state
                var newState = new Complex[state.Length];
                double norm = 0.0;
                for (int i = 0; i < state.Length; i++)
                {
                    if (((i >> qubit) & 1) == result)
                    {
                        newState[i] = state[i];
                        norm += state[i].Magnitude * state[i].Magnitude;
                    }
                }

                // Normalize
                norm = Math.Sqrt(norm);
                for (int i = 0; i < state.Length; i++)
                {
                    if (newState[i].Magnitude > 0)
                        newState[i] /= norm;
                }

                Array.Copy(newState, state, state.Length);
                return result;
            }
        }

        public Complex[] GetState()
        {
            lock (stateLock)
            {
                return (Complex[])state.Clone();
            }
        }
    }
} 