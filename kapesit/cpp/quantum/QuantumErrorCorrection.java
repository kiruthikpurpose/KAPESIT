package quantum;

import java.util.concurrent.*;
import java.util.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.locks.ReentrantReadWriteLock;
import java.security.SecureRandom;

public class QuantumErrorCorrection {
    private final int numQubits;
    private final Complex[] state;
    private final ReentrantReadWriteLock lock;
    private final ExecutorService executor;
    private final SecureRandom random;
    private final Map<String, Complex[][]> gates;
    private final Map<ErrorType, Complex[][]> errorGates;

    public enum ErrorType {
        BIT_FLIP,    // X error
        PHASE_FLIP,  // Z error
        COMBINED     // Y error
    }

    public QuantumErrorCorrection(int numQubits) {
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
        this.errorGates = initializeErrorGates();
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

    private Map<ErrorType, Complex[][]> initializeErrorGates() {
        Map<ErrorType, Complex[][]> errorGates = new HashMap<>();
        
        // Bit flip (X) error
        Complex[][] X = {
            {Complex.ZERO, Complex.ONE},
            {Complex.ONE, Complex.ZERO}
        };
        errorGates.put(ErrorType.BIT_FLIP, X);

        // Phase flip (Z) error
        Complex[][] Z = {
            {Complex.ONE, Complex.ZERO},
            {Complex.ZERO, Complex.ONE.negate()}
        };
        errorGates.put(ErrorType.PHASE_FLIP, Z);

        // Combined (Y) error
        Complex[][] Y = {
            {Complex.ZERO, new Complex(0, -1)},
            {new Complex(0, 1), Complex.ZERO}
        };
        errorGates.put(ErrorType.COMBINED, Y);

        return errorGates;
    }

    public void encodeShorCode(int logicalQubit) {
        lock.writeLock().lock();
        try {
            // First layer: encode against bit flips
            for (int i = 0; i < 3; i++) {
                int physicalQubit = logicalQubit + i;
                applyControlledGate("X", logicalQubit, physicalQubit);
            }

            // Second layer: encode against phase flips
            for (int i = 0; i < 3; i++) {
                int block = i * 3;
                applyGate("H", logicalQubit + block);
                applyGate("H", logicalQubit + block + 1);
                applyGate("H", logicalQubit + block + 2);
                
                applyControlledGate("X", logicalQubit + block, logicalQubit + block + 1);
                applyControlledGate("X", logicalQubit + block + 1, logicalQubit + block + 2);
            }
        } finally {
            lock.writeLock().unlock();
        }
    }

    public void decodeShorCode(int logicalQubit) {
        lock.writeLock().lock();
        try {
            // First layer: decode phase flips
            for (int i = 0; i < 3; i++) {
                int block = i * 3;
                applyControlledGate("X", logicalQubit + block + 1, logicalQubit + block + 2);
                applyControlledGate("X", logicalQubit + block, logicalQubit + block + 1);
                
                applyGate("H", logicalQubit + block);
                applyGate("H", logicalQubit + block + 1);
                applyGate("H", logicalQubit + block + 2);
            }

            // Second layer: decode bit flips
            for (int i = 0; i < 3; i++) {
                int physicalQubit = logicalQubit + i;
                applyControlledGate("X", logicalQubit, physicalQubit);
            }
        } finally {
            lock.writeLock().unlock();
        }
    }

    public void encodeSteaneCode(int logicalQubit) {
        lock.writeLock().lock();
        try {
            // Prepare |0⟩ state
            applyGate("H", logicalQubit + 3);
            applyGate("H", logicalQubit + 4);
            applyGate("H", logicalQubit + 5);
            applyGate("H", logicalQubit + 6);

            // Apply CNOT gates
            applyControlledGate("X", logicalQubit, logicalQubit + 3);
            applyControlledGate("X", logicalQubit, logicalQubit + 4);
            applyControlledGate("X", logicalQubit, logicalQubit + 5);
            applyControlledGate("X", logicalQubit, logicalQubit + 6);
        } finally {
            lock.writeLock().unlock();
        }
    }

    public void decodeSteaneCode(int logicalQubit) {
        lock.writeLock().lock();
        try {
            // Apply CNOT gates
            applyControlledGate("X", logicalQubit, logicalQubit + 6);
            applyControlledGate("X", logicalQubit, logicalQubit + 5);
            applyControlledGate("X", logicalQubit, logicalQubit + 4);
            applyControlledGate("X", logicalQubit, logicalQubit + 3);

            // Measure ancilla qubits
            measure(logicalQubit + 3);
            measure(logicalQubit + 4);
            measure(logicalQubit + 5);
            measure(logicalQubit + 6);
        } finally {
            lock.writeLock().unlock();
        }
    }

    public int[] measureSyndrome(int logicalQubit, boolean isShorCode) {
        lock.writeLock().lock();
        try {
            int[] syndrome = new int[isShorCode ? 6 : 4];
            int index = 0;

            if (isShorCode) {
                // Measure bit flip syndromes
                for (int i = 0; i < 3; i++) {
                    int block = i * 3;
                    syndrome[index++] = measure(logicalQubit + block) ^ measure(logicalQubit + block + 1);
                }

                // Measure phase flip syndromes
                for (int i = 0; i < 3; i++) {
                    int block = i * 3;
                    applyGate("H", logicalQubit + block);
                    applyGate("H", logicalQubit + block + 1);
                    applyGate("H", logicalQubit + block + 2);
                    syndrome[index++] = measure(logicalQubit + block) ^ measure(logicalQubit + block + 1);
                }
            } else {
                // Measure X stabilizers
                syndrome[index++] = measure(logicalQubit) ^ measure(logicalQubit + 1) ^ measure(logicalQubit + 2);
                syndrome[index++] = measure(logicalQubit + 1) ^ measure(logicalQubit + 2) ^ measure(logicalQubit + 3);

                // Measure Z stabilizers
                applyGate("H", logicalQubit);
                applyGate("H", logicalQubit + 1);
                applyGate("H", logicalQubit + 2);
                applyGate("H", logicalQubit + 3);
                syndrome[index++] = measure(logicalQubit) ^ measure(logicalQubit + 1) ^ measure(logicalQubit + 2);
                syndrome[index++] = measure(logicalQubit + 1) ^ measure(logicalQubit + 2) ^ measure(logicalQubit + 3);
            }

            return syndrome;
        } finally {
            lock.writeLock().unlock();
        }
    }

    public void correctError(int logicalQubit, int[] syndrome, boolean isShorCode) {
        lock.writeLock().lock();
        try {
            if (isShorCode) {
                // Correct bit flip errors
                for (int i = 0; i < 3; i++) {
                    if (syndrome[i] == 1) {
                        int block = i * 3;
                        applyGate("X", logicalQubit + block);
                    }
                }

                // Correct phase flip errors
                for (int i = 3; i < 6; i++) {
                    if (syndrome[i] == 1) {
                        int block = (i - 3) * 3;
                        applyGate("Z", logicalQubit + block);
                    }
                }
            } else {
                // Correct X errors
                if (syndrome[0] == 1 && syndrome[1] == 0) {
                    applyGate("X", logicalQubit);
                } else if (syndrome[0] == 0 && syndrome[1] == 1) {
                    applyGate("X", logicalQubit + 3);
                } else if (syndrome[0] == 1 && syndrome[1] == 1) {
                    applyGate("X", logicalQubit + 1);
                }

                // Correct Z errors
                if (syndrome[2] == 1 && syndrome[3] == 0) {
                    applyGate("Z", logicalQubit);
                } else if (syndrome[2] == 0 && syndrome[3] == 1) {
                    applyGate("Z", logicalQubit + 3);
                } else if (syndrome[2] == 1 && syndrome[3] == 1) {
                    applyGate("Z", logicalQubit + 1);
                }
            }
        } finally {
            lock.writeLock().unlock();
        }
    }

    public void applyError(int qubit, ErrorType errorType) {
        lock.writeLock().lock();
        try {
            Complex[][] errorGate = errorGates.get(errorType);
            if (errorGate == null) {
                throw new IllegalArgumentException("Unknown error type: " + errorType);
            }
            applySingleQubitGate(errorGate, qubit);
        } finally {
            lock.writeLock().unlock();
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