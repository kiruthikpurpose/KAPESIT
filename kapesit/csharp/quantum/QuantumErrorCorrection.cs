using System;
using System.Numerics;
using System.Threading;
using System.Threading.Tasks;
using System.Collections.Concurrent;
using System.Collections.Generic;

namespace Quantum
{
    public class QuantumErrorCorrection
    {
        private readonly int numQubits;
        private readonly Complex[] state;
        private readonly ReaderWriterLockSlim lock;
        private readonly ConcurrentDictionary<string, Complex[,]> gates;
        private readonly ConcurrentDictionary<ErrorType, Complex[,]> errorGates;

        public enum ErrorType
        {
            BitFlip,    // X error
            PhaseFlip,  // Z error
            Combined    // Y error
        }

        public QuantumErrorCorrection(int numQubits)
        {
            if (numQubits <= 0)
                throw new ArgumentException("Number of qubits must be positive");

            this.numQubits = numQubits;
            this.state = new Complex[1 << numQubits];
            this.state[0] = Complex.One;
            this.lock = new ReaderWriterLockSlim();
            this.gates = InitializeGates();
            this.errorGates = InitializeErrorGates();
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

        private ConcurrentDictionary<ErrorType, Complex[,]> InitializeErrorGates()
        {
            var errorGates = new ConcurrentDictionary<ErrorType, Complex[,]>();
            
            // Bit flip (X) error
            errorGates[ErrorType.BitFlip] = new Complex[,] {
                { Complex.Zero, Complex.One },
                { Complex.One, Complex.Zero }
            };

            // Phase flip (Z) error
            errorGates[ErrorType.PhaseFlip] = new Complex[,] {
                { Complex.One, Complex.Zero },
                { Complex.Zero, -Complex.One }
            };

            // Combined (Y) error
            errorGates[ErrorType.Combined] = new Complex[,] {
                { Complex.Zero, new Complex(0, -1) },
                { new Complex(0, 1), Complex.Zero }
            };

            return errorGates;
        }

        public void EncodeShorCode(int logicalQubit)
        {
            lock.EnterWriteLock();
            try
            {
                // First layer: encode against bit flips
                for (int i = 0; i < 3; i++)
                {
                    int physicalQubit = logicalQubit + i;
                    ApplyControlledGate("X", logicalQubit, physicalQubit);
                }

                // Second layer: encode against phase flips
                for (int i = 0; i < 3; i++)
                {
                    int block = i * 3;
                    ApplyGate("H", logicalQubit + block);
                    ApplyGate("H", logicalQubit + block + 1);
                    ApplyGate("H", logicalQubit + block + 2);
                    
                    ApplyControlledGate("X", logicalQubit + block, logicalQubit + block + 1);
                    ApplyControlledGate("X", logicalQubit + block + 1, logicalQubit + block + 2);
                }
            }
            finally
            {
                lock.ExitWriteLock();
            }
        }

        public void DecodeShorCode(int logicalQubit)
        {
            lock.EnterWriteLock();
            try
            {
                // First layer: decode phase flips
                for (int i = 0; i < 3; i++)
                {
                    int block = i * 3;
                    ApplyControlledGate("X", logicalQubit + block + 1, logicalQubit + block + 2);
                    ApplyControlledGate("X", logicalQubit + block, logicalQubit + block + 1);
                    
                    ApplyGate("H", logicalQubit + block);
                    ApplyGate("H", logicalQubit + block + 1);
                    ApplyGate("H", logicalQubit + block + 2);
                }

                // Second layer: decode bit flips
                for (int i = 0; i < 3; i++)
                {
                    int physicalQubit = logicalQubit + i;
                    ApplyControlledGate("X", logicalQubit, physicalQubit);
                }
            }
            finally
            {
                lock.ExitWriteLock();
            }
        }

        public void EncodeSteaneCode(int logicalQubit)
        {
            lock.EnterWriteLock();
            try
            {
                // Prepare |0⟩ state
                ApplyGate("H", logicalQubit + 3);
                ApplyGate("H", logicalQubit + 4);
                ApplyGate("H", logicalQubit + 5);
                ApplyGate("H", logicalQubit + 6);

                // Apply CNOT gates
                ApplyControlledGate("X", logicalQubit, logicalQubit + 3);
                ApplyControlledGate("X", logicalQubit, logicalQubit + 4);
                ApplyControlledGate("X", logicalQubit, logicalQubit + 5);
                ApplyControlledGate("X", logicalQubit, logicalQubit + 6);
            }
            finally
            {
                lock.ExitWriteLock();
            }
        }

        public void DecodeSteaneCode(int logicalQubit)
        {
            lock.EnterWriteLock();
            try
            {
                // Apply CNOT gates
                ApplyControlledGate("X", logicalQubit, logicalQubit + 6);
                ApplyControlledGate("X", logicalQubit, logicalQubit + 5);
                ApplyControlledGate("X", logicalQubit, logicalQubit + 4);
                ApplyControlledGate("X", logicalQubit, logicalQubit + 3);

                // Measure ancilla qubits
                Measure(logicalQubit + 3);
                Measure(logicalQubit + 4);
                Measure(logicalQubit + 5);
                Measure(logicalQubit + 6);
            }
            finally
            {
                lock.ExitWriteLock();
            }
        }

        public int[] MeasureSyndrome(int logicalQubit, bool isShorCode)
        {
            lock.EnterWriteLock();
            try
            {
                int[] syndrome = new int[isShorCode ? 6 : 4];
                int index = 0;

                if (isShorCode)
                {
                    // Measure bit flip syndromes
                    for (int i = 0; i < 3; i++)
                    {
                        int block = i * 3;
                        syndrome[index++] = Measure(logicalQubit + block) ^ Measure(logicalQubit + block + 1);
                    }

                    // Measure phase flip syndromes
                    for (int i = 0; i < 3; i++)
                    {
                        int block = i * 3;
                        ApplyGate("H", logicalQubit + block);
                        ApplyGate("H", logicalQubit + block + 1);
                        ApplyGate("H", logicalQubit + block + 2);
                        syndrome[index++] = Measure(logicalQubit + block) ^ Measure(logicalQubit + block + 1);
                    }
                }
                else
                {
                    // Measure X stabilizers
                    syndrome[index++] = Measure(logicalQubit) ^ Measure(logicalQubit + 1) ^ Measure(logicalQubit + 2);
                    syndrome[index++] = Measure(logicalQubit + 1) ^ Measure(logicalQubit + 2) ^ Measure(logicalQubit + 3);

                    // Measure Z stabilizers
                    ApplyGate("H", logicalQubit);
                    ApplyGate("H", logicalQubit + 1);
                    ApplyGate("H", logicalQubit + 2);
                    ApplyGate("H", logicalQubit + 3);
                    syndrome[index++] = Measure(logicalQubit) ^ Measure(logicalQubit + 1) ^ Measure(logicalQubit + 2);
                    syndrome[index++] = Measure(logicalQubit + 1) ^ Measure(logicalQubit + 2) ^ Measure(logicalQubit + 3);
                }

                return syndrome;
            }
            finally
            {
                lock.ExitWriteLock();
            }
        }

        public void CorrectError(int logicalQubit, int[] syndrome, bool isShorCode)
        {
            lock.EnterWriteLock();
            try
            {
                if (isShorCode)
                {
                    // Correct bit flip errors
                    for (int i = 0; i < 3; i++)
                    {
                        if (syndrome[i] == 1)
                        {
                            int block = i * 3;
                            ApplyGate("X", logicalQubit + block);
                        }
                    }

                    // Correct phase flip errors
                    for (int i = 3; i < 6; i++)
                    {
                        if (syndrome[i] == 1)
                        {
                            int block = (i - 3) * 3;
                            ApplyGate("Z", logicalQubit + block);
                        }
                    }
                }
                else
                {
                    // Correct X errors
                    if (syndrome[0] == 1 && syndrome[1] == 0)
                        ApplyGate("X", logicalQubit);
                    else if (syndrome[0] == 0 && syndrome[1] == 1)
                        ApplyGate("X", logicalQubit + 3);
                    else if (syndrome[0] == 1 && syndrome[1] == 1)
                        ApplyGate("X", logicalQubit + 1);

                    // Correct Z errors
                    if (syndrome[2] == 1 && syndrome[3] == 0)
                        ApplyGate("Z", logicalQubit);
                    else if (syndrome[2] == 0 && syndrome[3] == 1)
                        ApplyGate("Z", logicalQubit + 3);
                    else if (syndrome[2] == 1 && syndrome[3] == 1)
                        ApplyGate("Z", logicalQubit + 1);
                }
            }
            finally
            {
                lock.ExitWriteLock();
            }
        }

        public void ApplyError(int qubit, ErrorType errorType)
        {
            lock.EnterWriteLock();
            try
            {
                if (!errorGates.TryGetValue(errorType, out Complex[,] errorGate))
                    throw new ArgumentException($"Unknown error type: {errorType}");

                ApplySingleQubitGate(errorGate, qubit);
            }
            finally
            {
                lock.ExitWriteLock();
            }
        }

        private void ApplyGate(string gateName, int target)
        {
            lock.EnterWriteLock();
            try
            {
                if (!gates.TryGetValue(gateName, out Complex[,] gate))
                    throw new ArgumentException($"Unknown gate: {gateName}");

                ApplySingleQubitGate(gate, target);
            }
            finally
            {
                lock.ExitWriteLock();
            }
        }

        private void ApplyControlledGate(string gateName, int control, int target)
        {
            lock.EnterWriteLock();
            try
            {
                if (!gates.TryGetValue(gateName, out Complex[,] gate))
                    throw new ArgumentException($"Unknown gate: {gateName}");

                ApplyControlledSingleQubitGate(gate, control, target);
            }
            finally
            {
                lock.ExitWriteLock();
            }
        }

        private void ApplySingleQubitGate(Complex[,] gate, int target)
        {
            var newState = new Complex[state.Length];
            var chunkSize = state.Length / 4;
            var tasks = new Task[4];

            for (int i = 0; i < 4; i++)
            {
                int start = i * chunkSize;
                int end = (i == 3) ? state.Length : start + chunkSize;
                tasks[i] = Task.Run(() =>
                {
                    for (int j = start; j < end; j++)
                    {
                        int bit = (j >> target) & 1;
                        int idx = j ^ (1 << target);
                        if (j < idx)
                        {
                            newState[j] = gate[0, 0] * state[j] + gate[0, 1] * state[idx];
                            newState[idx] = gate[1, 0] * state[j] + gate[1, 1] * state[idx];
                        }
                    }
                });
            }

            Task.WaitAll(tasks);
            Array.Copy(newState, state, state.Length);
        }

        private void ApplyControlledSingleQubitGate(Complex[,] gate, int control, int target)
        {
            var newState = new Complex[state.Length];
            var chunkSize = state.Length / 4;
            var tasks = new Task[4];

            for (int i = 0; i < 4; i++)
            {
                int start = i * chunkSize;
                int end = (i == 3) ? state.Length : start + chunkSize;
                tasks[i] = Task.Run(() =>
                {
                    for (int j = start; j < end; j++)
                    {
                        if ((j & (1 << control)) != 0)
                        {
                            int bit = (j >> target) & 1;
                            int idx = j ^ (1 << target);
                            if (j < idx)
                            {
                                newState[j] = gate[0, 0] * state[j] + gate[0, 1] * state[idx];
                                newState[idx] = gate[1, 0] * state[j] + gate[1, 1] * state[idx];
                            }
                        }
                        else
                        {
                            newState[j] = state[j];
                        }
                    }
                });
            }

            Task.WaitAll(tasks);
            Array.Copy(newState, state, state.Length);
        }

        public int Measure(int qubit)
        {
            lock.EnterWriteLock();
            try
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

                // Collapse the state
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
            finally
            {
                lock.ExitWriteLock();
            }
        }
    }
} 