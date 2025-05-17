using System;
using System.Numerics;
using System.Collections.Generic;
using System.Linq;

namespace Kapesit.Quantum.Optimization
{
    public class QuantumOptimization
    {
        private readonly Random random;
        private readonly Dictionary<string, Complex[,]> gates;
        private readonly int numQubits;

        public QuantumOptimization(int numQubits)
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

            // Phase gates
            gates["S"] = new Complex[,] {
                { Complex.One, Complex.Zero },
                { Complex.Zero, new Complex(0, 1) }
            };

            gates["T"] = new Complex[,] {
                { Complex.One, Complex.Zero },
                { Complex.Zero, new Complex(Math.Cos(Math.PI/4), Math.Sin(Math.PI/4)) }
            };

            return gates;
        }

        public double[] QuantumApproximateOptimizationAlgorithm(Func<int[], double> objectiveFunction, int numIterations)
        {
            var bestSolution = new double[numQubits];
            var bestValue = double.MinValue;

            for (int iter = 0; iter < numIterations; iter++)
            {
                // Initialize quantum state
                var state = new Complex[1 << numQubits];
                state[0] = Complex.One;

                // Apply Hadamard gates to create superposition
                for (int i = 0; i < numQubits; i++)
                {
                    ApplyGate("H", i, state);
                }

                // Apply phase separation
                ApplyPhaseSeparation(objectiveFunction, state);

                // Apply mixing
                ApplyMixing(state);

                // Measure and evaluate
                var solution = MeasureState(state);
                var value = objectiveFunction(solution);

                if (value > bestValue)
                {
                    bestValue = value;
                    Array.Copy(solution, bestSolution, solution.Length);
                }
            }

            return bestSolution;
        }

        private void ApplyPhaseSeparation(Func<int[], double> objectiveFunction, Complex[] state)
        {
            var newState = new Complex[state.Length];
            for (int i = 0; i < state.Length; i++)
            {
                var bitString = GetBitString(i, numQubits);
                var value = objectiveFunction(bitString);
                newState[i] = state[i] * Complex.Exp(new Complex(0, value));
            }
            Array.Copy(newState, state, state.Length);
        }

        private void ApplyMixing(Complex[] state)
        {
            for (int i = 0; i < numQubits; i++)
            {
                ApplyGate("H", i, state);
            }
        }

        private int[] MeasureState(Complex[] state)
        {
            var result = new int[numQubits];
            var probabilities = new double[state.Length];

            // Calculate probabilities
            for (int i = 0; i < state.Length; i++)
            {
                probabilities[i] = state[i].Magnitude * state[i].Magnitude;
            }

            // Sample from probability distribution
            double r = random.NextDouble();
            double sum = 0;
            int measuredState = 0;

            for (int i = 0; i < probabilities.Length; i++)
            {
                sum += probabilities[i];
                if (r <= sum)
                {
                    measuredState = i;
                    break;
                }
            }

            // Convert to bit string
            for (int i = 0; i < numQubits; i++)
            {
                result[i] = (measuredState >> i) & 1;
            }

            return result;
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

        private int[] GetBitString(int value, int length)
        {
            var bits = new int[length];
            for (int i = 0; i < length; i++)
            {
                bits[i] = (value >> i) & 1;
            }
            return bits;
        }

        public double[] QuantumAnnealing(Func<int[], double> objectiveFunction, double initialTemp, double finalTemp, int numSteps)
        {
            var currentSolution = new int[numQubits];
            var bestSolution = new int[numQubits];
            var bestValue = double.MinValue;

            // Initialize random solution
            for (int i = 0; i < numQubits; i++)
            {
                currentSolution[i] = random.Next(2);
            }

            double currentValue = objectiveFunction(currentSolution);
            bestValue = currentValue;
            Array.Copy(currentSolution, bestSolution, numQubits);

            for (int step = 0; step < numSteps; step++)
            {
                double temperature = initialTemp + (finalTemp - initialTemp) * step / numSteps;

                // Generate neighbor solution
                var neighborSolution = new int[numQubits];
                Array.Copy(currentSolution, neighborSolution, numQubits);
                int flipIndex = random.Next(numQubits);
                neighborSolution[flipIndex] = 1 - neighborSolution[flipIndex];

                double neighborValue = objectiveFunction(neighborSolution);
                double deltaE = neighborValue - currentValue;

                // Accept or reject based on Metropolis criterion
                if (deltaE > 0 || random.NextDouble() < Math.Exp(deltaE / temperature))
                {
                    Array.Copy(neighborSolution, currentSolution, numQubits);
                    currentValue = neighborValue;

                    if (currentValue > bestValue)
                    {
                        bestValue = currentValue;
                        Array.Copy(currentSolution, bestSolution, numQubits);
                    }
                }
            }

            return bestSolution.Select(x => (double)x).ToArray();
        }
    }
} 