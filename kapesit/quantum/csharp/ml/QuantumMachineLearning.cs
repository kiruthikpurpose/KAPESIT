using System;
using System.Numerics;
using System.Collections.Generic;
using System.Linq;

namespace Kapesit.Quantum.ML
{
    public class QuantumMachineLearning
    {
        private readonly Random random;
        private readonly Dictionary<string, Complex[,]> gates;
        private readonly int numQubits;

        public QuantumMachineLearning(int numQubits)
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

            // Rotation gates
            gates["RX"] = new Complex[,] {
                { Complex.One, Complex.Zero },
                { Complex.Zero, Complex.One }
            };

            gates["RY"] = new Complex[,] {
                { Complex.One, Complex.Zero },
                { Complex.Zero, Complex.One }
            };

            gates["RZ"] = new Complex[,] {
                { Complex.One, Complex.Zero },
                { Complex.Zero, Complex.One }
            };

            return gates;
        }

        public Complex[] QuantumFeatureMap(double[] input)
        {
            if (input.Length > numQubits)
                throw new ArgumentException("Input dimension exceeds number of qubits");

            var state = new Complex[1 << numQubits];
            state[0] = Complex.One;

            for (int i = 0; i < input.Length; i++)
            {
                // Apply rotation gates based on input features
                ApplyRotationGate("RX", i, input[i]);
                ApplyRotationGate("RY", i, input[i] * 2);
                ApplyRotationGate("RZ", i, input[i] * 4);
            }

            return state;
        }

        private void ApplyRotationGate(string gateName, int qubit, double angle)
        {
            if (!gates.TryGetValue(gateName, out Complex[,] gate))
                throw new ArgumentException($"Unknown gate: {gateName}");

            // Update rotation matrix based on angle
            switch (gateName)
            {
                case "RX":
                    gate[0, 0] = new Complex(Math.Cos(angle / 2), 0);
                    gate[0, 1] = new Complex(0, -Math.Sin(angle / 2));
                    gate[1, 0] = new Complex(0, -Math.Sin(angle / 2));
                    gate[1, 1] = new Complex(Math.Cos(angle / 2), 0);
                    break;
                case "RY":
                    gate[0, 0] = new Complex(Math.Cos(angle / 2), 0);
                    gate[0, 1] = new Complex(-Math.Sin(angle / 2), 0);
                    gate[1, 0] = new Complex(Math.Sin(angle / 2), 0);
                    gate[1, 1] = new Complex(Math.Cos(angle / 2), 0);
                    break;
                case "RZ":
                    gate[0, 0] = new Complex(Math.Cos(angle / 2), -Math.Sin(angle / 2));
                    gate[0, 1] = Complex.Zero;
                    gate[1, 0] = Complex.Zero;
                    gate[1, 1] = new Complex(Math.Cos(angle / 2), Math.Sin(angle / 2));
                    break;
            }
        }

        public double QuantumKernel(Complex[] state1, Complex[] state2)
        {
            if (state1.Length != state2.Length)
                throw new ArgumentException("States must have the same dimension");

            Complex overlap = 0;
            for (int i = 0; i < state1.Length; i++)
            {
                overlap += Complex.Conjugate(state1[i]) * state2[i];
            }

            return overlap.Magnitude * overlap.Magnitude;
        }

        public double[] QuantumClassification(Complex[] state, List<Complex[]> trainingStates, List<int> labels)
        {
            if (trainingStates.Count != labels.Count)
                throw new ArgumentException("Training data and labels must have the same length");

            var scores = new double[2]; // Binary classification
            for (int i = 0; i < trainingStates.Count; i++)
            {
                double kernel = QuantumKernel(state, trainingStates[i]);
                scores[labels[i]] += kernel;
            }

            // Normalize scores
            double sum = scores.Sum();
            if (sum > 0)
            {
                for (int i = 0; i < scores.Length; i++)
                {
                    scores[i] /= sum;
                }
            }

            return scores;
        }

        public (double[] weights, double bias) TrainQuantumClassifier(List<double[]> trainingData, List<int> labels, int numEpochs)
        {
            if (trainingData.Count != labels.Count)
                throw new ArgumentException("Training data and labels must have the same length");

            var weights = new double[trainingData[0].Length];
            double bias = 0;
            double learningRate = 0.01;

            for (int epoch = 0; epoch < numEpochs; epoch++)
            {
                for (int i = 0; i < trainingData.Count; i++)
                {
                    var input = trainingData[i];
                    var target = labels[i];

                    // Forward pass
                    var state = QuantumFeatureMap(input);
                    var prediction = QuantumClassification(state, 
                        trainingData.Select(x => QuantumFeatureMap(x)).ToList(), 
                        labels)[1];

                    // Backward pass (simplified gradient descent)
                    double error = target - prediction;
                    for (int j = 0; j < weights.Length; j++)
                    {
                        weights[j] += learningRate * error * input[j];
                    }
                    bias += learningRate * error;
                }
            }

            return (weights, bias);
        }
    }
} 