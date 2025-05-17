package quantum;

import java.util.concurrent.*;
import java.util.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.locks.ReentrantReadWriteLock;

public class QuantumAlgorithms {
    private final int numQubits;
    private final Complex[] state;
    private final ReentrantReadWriteLock lock;
    private final ExecutorService executor;
    private final Random random;

    public QuantumAlgorithms(int numQubits) {
        if (numQubits <= 0) {
            throw new IllegalArgumentException("Number of qubits must be positive");
        }
        this.numQubits = numQubits;
        this.state = new Complex[1 << numQubits];
        this.state[0] = Complex.ONE;
        this.lock = new ReentrantReadWriteLock();
        this.executor = Executors.newFixedThreadPool(Runtime.getRuntime().availableProcessors());
        this.random = new Random();
    }

    public void applyHadamard(int target) {
        lock.writeLock().lock();
        try {
            Complex[] newState = new Complex[state.length];
            int chunkSize = state.length / 4;
            CountDownLatch latch = new CountDownLatch(4);

            for (int i = 0; i < 4; i++) {
                final int start = i * chunkSize;
                final int end = (i == 3) ? state.length : start + chunkSize;
                executor.submit(() -> {
                    try {
                        for (int j = start; j < end; j++) {
                            int idx = j ^ (1 << target);
                            newState[j] = state[j].add(state[idx]).multiply(1.0 / Math.sqrt(2));
                        }
                    } finally {
                        latch.countDown();
                    }
                });
            }

            latch.await();
            System.arraycopy(newState, 0, state, 0, state.length);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new RuntimeException("Operation interrupted", e);
        } finally {
            lock.writeLock().unlock();
        }
    }

    public void applyCNOT(int control, int target) {
        lock.writeLock().lock();
        try {
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
                                int idx = j ^ (1 << target);
                                newState[j] = state[idx];
                            } else {
                                newState[j] = state[j];
                            }
                        }
                    } finally {
                        latch.countDown();
                    }
                });
            }

            latch.await();
            System.arraycopy(newState, 0, state, 0, state.length);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new RuntimeException("Operation interrupted", e);
        } finally {
            lock.writeLock().unlock();
        }
    }

    public int measure() {
        lock.readLock().lock();
        try {
            double[] probabilities = new double[state.length];
            double sum = 0.0;
            for (int i = 0; i < state.length; i++) {
                probabilities[i] = state[i].abs() * state[i].abs();
                sum += probabilities[i];
            }

            double r = random.nextDouble() * sum;
            double cumProb = 0.0;
            for (int i = 0; i < probabilities.length; i++) {
                cumProb += probabilities[i];
                if (r <= cumProb) {
                    return i;
                }
            }
            return probabilities.length - 1;
        } finally {
            lock.readLock().unlock();
        }
    }

    public void quantumFourierTransform() {
        lock.writeLock().lock();
        try {
            for (int i = 0; i < numQubits; i++) {
                applyHadamard(i);
                for (int j = i + 1; j < numQubits; j++) {
                    applyPhaseRotation(j, i, Math.PI / (1 << (j - i)));
                }
            }
            // Reverse qubits
            for (int i = 0; i < numQubits / 2; i++) {
                applySWAP(i, numQubits - 1 - i);
            }
        } finally {
            lock.writeLock().unlock();
        }
    }

    public void groverSearch(int markedState) {
        lock.writeLock().lock();
        try {
            // Initialize superposition
            for (int i = 0; i < numQubits; i++) {
                applyHadamard(i);
            }

            // Optimal number of iterations
            int iterations = (int) (Math.PI / 4 * Math.sqrt(1 << numQubits));
            for (int i = 0; i < iterations; i++) {
                // Oracle
                if (markedState >= 0 && markedState < state.length) {
                    state[markedState] = state[markedState].negate();
                }

                // Diffusion operator
                for (int j = 0; j < numQubits; j++) {
                    applyHadamard(j);
                }
                for (int j = 0; j < state.length; j++) {
                    state[j] = state[j].negate();
                }
                state[0] = state[0].add(Complex.ONE);
                for (int j = 0; j < numQubits; j++) {
                    applyHadamard(j);
                }
            }
        } finally {
            lock.writeLock().unlock();
        }
    }

    public void quantumPhaseEstimation(Complex[][] unitary, int precision) {
        lock.writeLock().lock();
        try {
            // Initialize control qubits
            for (int i = 0; i < precision; i++) {
                applyHadamard(i);
            }

            // Apply controlled operations
            for (int i = 0; i < precision; i++) {
                for (int j = 0; j < (1 << i); j++) {
                    applyControlledUnitary(i, unitary);
                }
            }

            // Inverse QFT
            for (int i = 0; i < precision / 2; i++) {
                applySWAP(i, precision - 1 - i);
            }
            for (int i = 0; i < precision; i++) {
                for (int j = i + 1; j < precision; j++) {
                    applyPhaseRotation(j, i, -Math.PI / (1 << (j - i)));
                }
                applyHadamard(i);
            }
        } finally {
            lock.writeLock().unlock();
        }
    }

    private void applyPhaseRotation(int target, int control, double angle) {
        lock.writeLock().lock();
        try {
            Complex phase = new Complex(Math.cos(angle), Math.sin(angle));
            for (int i = 0; i < state.length; i++) {
                if ((i & (1 << control)) != 0) {
                    state[i] = state[i].multiply(phase);
                }
            }
        } finally {
            lock.writeLock().unlock();
        }
    }

    private void applySWAP(int qubit1, int qubit2) {
        lock.writeLock().lock();
        try {
            for (int i = 0; i < state.length; i++) {
                if (((i >> qubit1) & 1) != ((i >> qubit2) & 1)) {
                    int j = i ^ (1 << qubit1) ^ (1 << qubit2);
                    if (i < j) {
                        Complex temp = state[i];
                        state[i] = state[j];
                        state[j] = temp;
                    }
                }
            }
        } finally {
            lock.writeLock().unlock();
        }
    }

    private void applyControlledUnitary(int control, Complex[][] unitary) {
        lock.writeLock().lock();
        try {
            Complex[] newState = new Complex[state.length];
            for (int i = 0; i < state.length; i++) {
                if ((i & (1 << control)) != 0) {
                    for (int j = 0; j < unitary.length; j++) {
                        Complex sum = Complex.ZERO;
                        for (int k = 0; k < unitary.length; k++) {
                            sum = sum.add(unitary[j][k].multiply(state[i ^ (j << control) ^ (k << control)]));
                        }
                        newState[i ^ (j << control)] = sum;
                    }
                } else {
                    newState[i] = state[i];
                }
            }
            System.arraycopy(newState, 0, state, 0, state.length);
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