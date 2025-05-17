package quantum;

import java.util.concurrent.*;
import java.util.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.locks.ReentrantReadWriteLock;
import java.security.SecureRandom;

public class QuantumSimulator {
    private final int numQubits;
    private final Complex[] state;
    private final ReentrantReadWriteLock lock;
    private final ExecutorService executor;
    private final SecureRandom random;
    private final Map<String, Complex[][]> gates;
    private final Map<String, Complex[][]> observables;

    public QuantumSimulator(int numQubits) {
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
        this.observables = initializeObservables();
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

        // Phase gates
        Complex[][] S = {
            {Complex.ONE, Complex.ZERO},
            {Complex.ZERO, new Complex(0, 1)}
        };
        gates.put("S", S);

        Complex[][] T = {
            {Complex.ONE, Complex.ZERO},
            {Complex.ZERO, new Complex(1.0/Math.sqrt(2), 1.0/Math.sqrt(2))}
        };
        gates.put("T", T);

        return gates;
    }

    private Map<String, Complex[][]> initializeObservables() {
        Map<String, Complex[][]> observables = new HashMap<>();
        
        // Pauli matrices as observables
        Complex[][] X = {
            {Complex.ZERO, Complex.ONE},
            {Complex.ONE, Complex.ZERO}
        };
        observables.put("X", X);

        Complex[][] Y = {
            {Complex.ZERO, new Complex(0, -1)},
            {new Complex(0, 1), Complex.ZERO}
        };
        observables.put("Y", Y);

        Complex[][] Z = {
            {Complex.ONE, Complex.ZERO},
            {Complex.ZERO, Complex.ONE.negate()}
        };
        observables.put("Z", Z);

        return observables;
    }

    public void applyGate(String gateName, int target) {
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

    public void applyControlledGate(String gateName, int control, int target) {
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

    public void applyRotation(String axis, double angle, int target) {
        lock.writeLock().lock();
        try {
            Complex[][] gate;
            switch (axis.toUpperCase()) {
                case "X":
                    gate = new Complex[][] {
                        {new Complex(Math.cos(angle/2), 0), new Complex(0, -Math.sin(angle/2))},
                        {new Complex(0, -Math.sin(angle/2)), new Complex(Math.cos(angle/2), 0)}
                    };
                    break;
                case "Y":
                    gate = new Complex[][] {
                        {new Complex(Math.cos(angle/2), 0), new Complex(-Math.sin(angle/2), 0)},
                        {new Complex(Math.sin(angle/2), 0), new Complex(Math.cos(angle/2), 0)}
                    };
                    break;
                case "Z":
                    gate = new Complex[][] {
                        {new Complex(Math.cos(angle/2), -Math.sin(angle/2)), Complex.ZERO},
                        {Complex.ZERO, new Complex(Math.cos(angle/2), Math.sin(angle/2))}
                    };
                    break;
                default:
                    throw new IllegalArgumentException("Invalid rotation axis: " + axis);
            }
            applySingleQubitGate(gate, target);
        } finally {
            lock.writeLock().unlock();
        }
    }

    public void applySWAP(int qubit1, int qubit2) {
        lock.writeLock().lock();
        try {
            applyControlledGate("X", qubit1, qubit2);
            applyControlledGate("X", qubit2, qubit1);
            applyControlledGate("X", qubit1, qubit2);
        } finally {
            lock.writeLock().unlock();
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

    public Complex[] getStateVector() {
        lock.readLock().lock();
        try {
            return Arrays.copyOf(state, state.length);
        } finally {
            lock.readLock().unlock();
        }
    }

    public double getExpectationValue(String observable, int qubit) {
        lock.readLock().lock();
        try {
            Complex[][] obs = observables.get(observable);
            if (obs == null) {
                throw new IllegalArgumentException("Unknown observable: " + observable);
            }

            double expectation = 0.0;
            for (int i = 0; i < state.length; i++) {
                int bit = (i >> qubit) & 1;
                Complex amplitude = state[i];
                expectation += amplitude.abs() * amplitude.abs() * (bit == 0 ? obs[0][0].getReal() : obs[1][1].getReal());
            }
            return expectation;
        } finally {
            lock.readLock().unlock();
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