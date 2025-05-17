package quantum;

import java.util.concurrent.*;
import java.util.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.locks.ReentrantReadWriteLock;
import java.security.SecureRandom;
import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.spec.SecretKeySpec;
import java.security.MessageDigest;
import java.nio.charset.StandardCharsets;

public class QuantumCryptography {
    private final int numQubits;
    private final Complex[] state;
    private final ReentrantReadWriteLock lock;
    private final ExecutorService executor;
    private final SecureRandom random;
    private final Map<String, Complex[][]> gates;
    private final Map<String, byte[]> keys;

    public QuantumCryptography(int numQubits) {
        if (numQubits <= 0) {
            throw new IllegalArgumentException("Number of qubits must be positive");
        }
        this.numQubits = numQubits;
        this.state = new Complex[1 << numQubits];
        this.state[0] = Complex.ONE;
        this.lock = new ReentrantReadWriteLock();
        this.executor = Executors.newFixedThreadPool(Runtime.getRuntime().availableProcessors());
        this.random = new SecureRandom();
        this.gates = initializeGates();
        this.keys = new HashMap<>();
    }

    private Map<String, Complex[][]> initializeGates() {
        Map<String, Complex[][]> gates = new HashMap<>();
        
        // Hadamard gate
        Complex[][] H = {
            {new Complex(1.0/Math.sqrt(2), 0), new Complex(1.0/Math.sqrt(2), 0)},
            {new Complex(1.0/Math.sqrt(2), 0), new Complex(-1.0/Math.sqrt(2), 0)}
        };
        gates.put("H", H);

        // Pauli gates
        Complex[][] X = {
            {Complex.ZERO, Complex.ONE},
            {Complex.ONE, Complex.ZERO}
        };
        gates.put("X", X);

        Complex[][] Y = {
            {Complex.ZERO, new Complex(0, -1)},
            {new Complex(0, 1), Complex.ZERO}
        };
        gates.put("Y", Y);

        Complex[][] Z = {
            {Complex.ONE, Complex.ZERO},
            {Complex.ZERO, Complex.ONE.negate()}
        };
        gates.put("Z", Z);

        return gates;
    }

    public byte[] generateQuantumKey(int keyLength) {
        lock.writeLock().lock();
        try {
            byte[] key = new byte[keyLength];
            for (int i = 0; i < keyLength; i++) {
                // Prepare qubit in superposition
                applyGate("H", 0);
                
                // Measure qubit
                int bit = measure(0);
                key[i] = (byte) bit;
            }
            return key;
        } finally {
            lock.writeLock().unlock();
        }
    }

    public byte[] encryptMessage(String message, byte[] key) {
        try {
            // Generate AES key from quantum key
            SecretKey aesKey = new SecretKeySpec(key, "AES");
            
            // Encrypt message
            Cipher cipher = Cipher.getInstance("AES");
            cipher.init(Cipher.ENCRYPT_MODE, aesKey);
            return cipher.doFinal(message.getBytes(StandardCharsets.UTF_8));
        } catch (Exception e) {
            throw new RuntimeException("Encryption failed", e);
        }
    }

    public String decryptMessage(byte[] encryptedMessage, byte[] key) {
        try {
            // Generate AES key from quantum key
            SecretKey aesKey = new SecretKeySpec(key, "AES");
            
            // Decrypt message
            Cipher cipher = Cipher.getInstance("AES");
            cipher.init(Cipher.DECRYPT_MODE, aesKey);
            byte[] decrypted = cipher.doFinal(encryptedMessage);
            return new String(decrypted, StandardCharsets.UTF_8);
        } catch (Exception e) {
            throw new RuntimeException("Decryption failed", e);
        }
    }

    public byte[] generateQuantumSignature(String message) {
        lock.writeLock().lock();
        try {
            // Generate entangled pairs
            generateEntangledPairs();
            
            // Apply message-dependent operations
            byte[] messageHash = hashMessage(message);
            for (int i = 0; i < messageHash.length; i++) {
                if ((messageHash[i] & 1) != 0) {
                    applyGate("X", i);
                }
                if ((messageHash[i] & 2) != 0) {
                    applyGate("Z", i);
                }
            }
            
            // Measure qubits
            byte[] signature = new byte[numQubits];
            for (int i = 0; i < numQubits; i++) {
                signature[i] = (byte) measure(i);
            }
            
            return signature;
        } finally {
            lock.writeLock().unlock();
        }
    }

    public boolean verifyQuantumSignature(String message, byte[] signature) {
        lock.writeLock().lock();
        try {
            // Generate entangled pairs
            generateEntangledPairs();
            
            // Apply message-dependent operations
            byte[] messageHash = hashMessage(message);
            for (int i = 0; i < messageHash.length; i++) {
                if ((messageHash[i] & 1) != 0) {
                    applyGate("X", i);
                }
                if ((messageHash[i] & 2) != 0) {
                    applyGate("Z", i);
                }
            }
            
            // Measure qubits and compare with signature
            for (int i = 0; i < numQubits; i++) {
                if (measure(i) != signature[i]) {
                    return false;
                }
            }
            
            return true;
        } finally {
            lock.writeLock().unlock();
        }
    }

    public byte[] generateQuantumRandomNumber(int length) {
        lock.writeLock().lock();
        try {
            byte[] randomBytes = new byte[length];
            for (int i = 0; i < length; i++) {
                // Prepare qubit in superposition
                applyGate("H", 0);
                
                // Measure qubit
                int bit = measure(0);
                randomBytes[i] = (byte) bit;
            }
            return randomBytes;
        } finally {
            lock.writeLock().unlock();
        }
    }

    private void generateEntangledPairs() {
        lock.writeLock().lock();
        try {
            for (int i = 0; i < numQubits; i += 2) {
                // Prepare Bell state
                applyGate("H", i);
                applyControlledGate("X", i, i + 1);
            }
        } finally {
            lock.writeLock().unlock();
        }
    }

    private byte[] hashMessage(String message) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            return digest.digest(message.getBytes(StandardCharsets.UTF_8));
        } catch (Exception e) {
            throw new RuntimeException("Hashing failed", e);
        }
    }

    private void applyGate(String gateName, int target) {
        lock.writeLock().lock();
        try {
            Complex[][] gate = gates.get(gateName);
            if (gate == null) {
                throw new IllegalArgumentException("Unknown gate: " + gateName);
            }
            applySingleQubitGate(gate, target);
        } finally {
            lock.writeLock().unlock();
        }
    }

    private void applyControlledGate(String gateName, int control, int target) {
        lock.writeLock().lock();
        try {
            Complex[][] gate = gates.get(gateName);
            if (gate == null) {
                throw new IllegalArgumentException("Unknown gate: " + gateName);
            }
            applyControlledSingleQubitGate(gate, control, target);
        } finally {
            lock.writeLock().unlock();
        }
    }

    private void applySingleQubitGate(Complex[][] gate, int target) {
        Complex[] newState = new Complex[state.length];
        int chunkSize = state.length / 4;
        CountDownLatch latch = new CountDownLatch(4);

        for (int i = 0; i < 4; i++) {
            final int start = i * chunkSize;
            final int end = (i == 3) ? state.length : start + chunkSize;
            executor.submit(() -> {
                try {
                    for (int j = start; j < end; j++) {
                        int bit = (j >> target) & 1;
                        int idx = j ^ (1 << target);
                        if (j < idx) {
                            newState[j] = gate[0][0].multiply(state[j]).add(gate[0][1].multiply(state[idx]));
                            newState[idx] = gate[1][0].multiply(state[j]).add(gate[1][1].multiply(state[idx]));
                        }
                    }
                } finally {
                    latch.countDown();
                }
            });
        }

        try {
            latch.await();
            System.arraycopy(newState, 0, state, 0, state.length);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new RuntimeException("Operation interrupted", e);
        }
    }

    private void applyControlledSingleQubitGate(Complex[][] gate, int control, int target) {
        Complex[] newState = new Complex[state.length];
        int chunkSize = state.length / 4;
        CountDownLatch latch = new CountDownLatch(4);

        for (int i = 0; i < 4; i++) {
            final int start = i * chunkSize;
            final int end = (i == 3) ? state.length : start + chunkSize;
            executor.submit(() -> {
                try {
                    for (int j = start; j < end; j++) {
                        if ((j & (1 << control)) != 0) {
                            int bit = (j >> target) & 1;
                            int idx = j ^ (1 << target);
                            if (j < idx) {
                                newState[j] = gate[0][0].multiply(state[j]).add(gate[0][1].multiply(state[idx]));
                                newState[idx] = gate[1][0].multiply(state[j]).add(gate[1][1].multiply(state[idx]));
                            }
                        } else {
                            newState[j] = state[j];
                        }
                    }
                } finally {
                    latch.countDown();
                }
            });
        }

        try {
            latch.await();
            System.arraycopy(newState, 0, state, 0, state.length);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new RuntimeException("Operation interrupted", e);
        }
    }

    public int measure(int qubit) {
        lock.writeLock().lock();
        try {
            double[] probabilities = new double[2];
            for (int i = 0; i < state.length; i++) {
                if ((i & (1 << qubit)) != 0) {
                    probabilities[1] += state[i].abs() * state[i].abs();
                } else {
                    probabilities[0] += state[i].abs() * state[i].abs();
                }
            }

            double r = random.nextDouble();
            int result = r < probabilities[0] ? 0 : 1;

            // Collapse the state
            Complex[] newState = new Complex[state.length];
            double norm = 0.0;
            for (int i = 0; i < state.length; i++) {
                if (((i >> qubit) & 1) == result) {
                    newState[i] = state[i];
                    norm += state[i].abs() * state[i].abs();
                }
            }

            // Normalize
            norm = Math.sqrt(norm);
            for (int i = 0; i < state.length; i++) {
                if (newState[i] != null) {
                    newState[i] = newState[i].multiply(1.0 / norm);
                } else {
                    newState[i] = Complex.ZERO;
                }
            }

            System.arraycopy(newState, 0, state, 0, state.length);
            return result;
        } finally {
            lock.writeLock().unlock();
        }
    }

    public void shutdown() {
        executor.shutdown();
        try {
            if (!executor.awaitTermination(60, TimeUnit.SECONDS)) {
                executor.shutdownNow();
            }
        } catch (InterruptedException e) {
            executor.shutdownNow();
            Thread.currentThread().interrupt();
        }
    }

    private static class Complex {
        public static final Complex ONE = new Complex(1.0, 0.0);
        public static final Complex ZERO = new Complex(0.0, 0.0);
        
        private final double real;
        private final double imag;

        public Complex(double real, double imag) {
            this.real = real;
            this.imag = imag;
        }

        public double getReal() {
            return real;
        }

        public double getImag() {
            return imag;
        }

        public Complex add(Complex other) {
            return new Complex(real + other.real, imag + other.imag);
        }

        public Complex multiply(double scalar) {
            return new Complex(real * scalar, imag * scalar);
        }

        public Complex multiply(Complex other) {
            return new Complex(
                real * other.real - imag * other.imag,
                real * other.imag + imag * other.real
            );
        }

        public Complex negate() {
            return new Complex(-real, -imag);
        }

        public double abs() {
            return Math.sqrt(real * real + imag * imag);
        }
    }
} 