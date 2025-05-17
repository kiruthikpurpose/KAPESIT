using System;
using System.Numerics;
using System.Security.Cryptography;
using System.Collections.Generic;

namespace Kapesit.Quantum.Cryptography
{
    public class QuantumCryptography
    {
        private readonly Random random;
        private readonly Dictionary<string, Complex[,]> gates;

        public QuantumCryptography()
        {
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

            // Phase gate
            gates["S"] = new Complex[,] {
                { Complex.One, Complex.Zero },
                { Complex.Zero, new Complex(0, 1) }
            };

            return gates;
        }

        public (byte[] key, byte[] basis) GenerateBB84Key(int keyLength)
        {
            byte[] key = new byte[keyLength];
            byte[] basis = new byte[keyLength];

            for (int i = 0; i < keyLength; i++)
            {
                // Randomly choose basis (0 for computational, 1 for Hadamard)
                basis[i] = (byte)random.Next(2);
                
                // Generate random bit
                key[i] = (byte)random.Next(2);
            }

            return (key, basis);
        }

        public byte[] EncryptMessage(byte[] message, byte[] key)
        {
            if (message.Length != key.Length)
                throw new ArgumentException("Message and key lengths must match");

            byte[] encrypted = new byte[message.Length];
            for (int i = 0; i < message.Length; i++)
            {
                encrypted[i] = (byte)(message[i] ^ key[i]);
            }
            return encrypted;
        }

        public byte[] DecryptMessage(byte[] encrypted, byte[] key)
        {
            return EncryptMessage(encrypted, key); // XOR is symmetric
        }

        public (byte[] key, double errorRate) SimulateEavesdropping(byte[] originalKey, byte[] basis, double eavesdropProbability)
        {
            byte[] interceptedKey = new byte[originalKey.Length];
            int errors = 0;

            for (int i = 0; i < originalKey.Length; i++)
            {
                if (random.NextDouble() < eavesdropProbability)
                {
                    // Eavesdropper measures in random basis
                    byte eavesdropBasis = (byte)random.Next(2);
                    if (eavesdropBasis != basis[i])
                    {
                        // Wrong basis measurement introduces error
                        interceptedKey[i] = (byte)(1 - originalKey[i]);
                        errors++;
                    }
                    else
                    {
                        interceptedKey[i] = originalKey[i];
                    }
                }
                else
                {
                    interceptedKey[i] = originalKey[i];
                }
            }

            double errorRate = (double)errors / originalKey.Length;
            return (interceptedKey, errorRate);
        }

        public bool VerifyKeyIntegrity(byte[] key1, byte[] key2, int sampleSize)
        {
            if (key1.Length != key2.Length)
                throw new ArgumentException("Keys must have the same length");

            int errors = 0;
            for (int i = 0; i < sampleSize; i++)
            {
                int index = random.Next(key1.Length);
                if (key1[index] != key2[index])
                    errors++;
            }

            double errorRate = (double)errors / sampleSize;
            return errorRate < 0.1; // Threshold for key integrity
        }
    }
} 