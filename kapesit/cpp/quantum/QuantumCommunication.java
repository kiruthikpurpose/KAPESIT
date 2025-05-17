package quantum;

import java.util.concurrent.*;
import java.util.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.locks.ReentrantReadWriteLock;
import java.security.SecureRandom;
import java.io.*;
import java.net.*;
import java.nio.ByteBuffer;
import java.nio.channels.*;
import java.util.concurrent.atomic.AtomicBoolean;

public class QuantumCommunication {
    private final int numQubits;
    private final Complex[] state;
    private final ReentrantReadWriteLock lock;
    private final ExecutorService executor;
    private final SecureRandom random;
    private final Map<String, Complex[][]> gates;
    private final AtomicBoolean isRunning;
    private final BlockingQueue<QuantumMessage> messageQueue;
    private final Map<String, SocketChannel> connections;
    private final Selector selector;
    private final ServerSocket serverSocket;
    private final int port;

    public QuantumCommunication(int numQubits, int port) throws IOException {
        if (numQubits <= 0 || port <= 0) {
            throw new IllegalArgumentException("Parameters must be positive");
        }
        this.numQubits = numQubits;
        this.port = port;
        this.state = new Complex[1 << numQubits];
        this.state[0] = Complex.ONE;
        this.lock = new ReentrantReadWriteLock();
        this.executor = Executors.newFixedThreadPool(Runtime.getRuntime().availableProcessors());
        this.random = new SecureRandom();
        this.gates = initializeGates();
        this.isRunning = new AtomicBoolean(false);
        this.messageQueue = new LinkedBlockingQueue<>();
        this.connections = new ConcurrentHashMap<>();
        this.selector = Selector.open();
        this.serverSocket = new ServerSocket(port);
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

    public void startServer() {
        executor.submit(() -> {
            try {
                while (!Thread.currentThread().isInterrupted()) {
                    Socket clientSocket = serverSocket.accept();
                    String clientId = clientSocket.getInetAddress().getHostAddress() + ":" + clientSocket.getPort();
                    connections.put(clientId, clientSocket);
                    System.out.println("New connection from " + clientId);
                }
            } catch (IOException e) {
                if (!Thread.currentThread().isInterrupted()) {
                    throw new RuntimeException("Server error", e);
                }
            }
        });
    }

    public void connect(String host, int port) throws IOException {
        Socket socket = new Socket(host, port);
        String connectionId = host + ":" + port;
        connections.put(connectionId, socket);
        System.out.println("Connected to " + connectionId);
    }

    public void sendQuantumState(String connectionId, int qubit) throws IOException {
        lock.writeLock().lock();
        try {
            Socket socket = connections.get(connectionId);
            if (socket == null) {
                throw new IllegalArgumentException("Unknown connection: " + connectionId);
            }

            // Measure qubit
            int measurement = measure(qubit);
            
            // Send measurement result
            DataOutputStream out = new DataOutputStream(socket.getOutputStream());
            out.writeInt(measurement);
            out.flush();
        } finally {
            lock.writeLock().unlock();
        }
    }

    public void receiveQuantumState(String connectionId, int qubit) throws IOException {
        lock.writeLock().lock();
        try {
            Socket socket = connections.get(connectionId);
            if (socket == null) {
                throw new IllegalArgumentException("Unknown connection: " + connectionId);
            }

            // Receive measurement result
            DataInputStream in = new DataInputStream(socket.getInputStream());
            int measurement = in.readInt();
            
            // Prepare qubit based on measurement
            if (measurement == 1) {
                applyGate("X", qubit);
            }
        } finally {
            lock.writeLock().unlock();
        }
    }

    public void teleportState(String connectionId, int sourceQubit, int targetQubit) throws IOException {
        lock.writeLock().lock();
        try {
            // Generate entangled pair
            generateEntangledPair(sourceQubit, targetQubit);
            
            // Measure source qubit and entangled qubit
            int measurement1 = measure(sourceQubit);
            int measurement2 = measure(sourceQubit + 1);
            
            // Send measurement results
            Socket socket = connections.get(connectionId);
            if (socket == null) {
                throw new IllegalArgumentException("Unknown connection: " + connectionId);
            }
            DataOutputStream out = new DataOutputStream(socket.getOutputStream());
            out.writeInt(measurement1);
            out.writeInt(measurement2);
            out.flush();
            
            // Apply corrections based on measurements
            if (measurement2 == 1) {
                applyGate("X", targetQubit);
            }
            if (measurement1 == 1) {
                applyGate("Z", targetQubit);
            }
        } finally {
            lock.writeLock().unlock();
        }
    }

    public void receiveTeleportedState(String connectionId, int targetQubit) throws IOException {
        lock.writeLock().lock();
        try {
            // Receive measurement results
            Socket socket = connections.get(connectionId);
            if (socket == null) {
                throw new IllegalArgumentException("Unknown connection: " + connectionId);
            }
            DataInputStream in = new DataInputStream(socket.getInputStream());
            int measurement1 = in.readInt();
            int measurement2 = in.readInt();
            
            // Apply corrections based on measurements
            if (measurement2 == 1) {
                applyGate("X", targetQubit);
            }
            if (measurement1 == 1) {
                applyGate("Z", targetQubit);
            }
        } finally {
            lock.writeLock().unlock();
        }
    }

    public void sendEntangledPair(String connectionId, int qubit1, int qubit2) throws IOException {
        lock.writeLock().lock();
        try {
            // Generate entangled pair
            generateEntangledPair(qubit1, qubit2);
            
            // Measure one qubit
            int measurement = measure(qubit1);
            
            // Send measurement result
            Socket socket = connections.get(connectionId);
            if (socket == null) {
                throw new IllegalArgumentException("Unknown connection: " + connectionId);
            }
            DataOutputStream out = new DataOutputStream(socket.getOutputStream());
            out.writeInt(measurement);
            out.flush();
        } finally {
            lock.writeLock().unlock();
        }
    }

    public void receiveEntangledPair(String connectionId, int qubit) throws IOException {
        lock.writeLock().lock();
        try {
            // Receive measurement result
            Socket socket = connections.get(connectionId);
            if (socket == null) {
                throw new IllegalArgumentException("Unknown connection: " + connectionId);
            }
            DataInputStream in = new DataInputStream(socket.getInputStream());
            int measurement = in.readInt();
            
            // Prepare qubit based on measurement
            if (measurement == 1) {
                applyGate("X", qubit);
            }
        } finally {
            lock.writeLock().unlock();
        }
    }

    private void generateEntangledPair(int qubit1, int qubit2) {
        lock.writeLock().lock();
        try {
            // Prepare Bell state
            applyGate("H", qubit1);
            applyControlledGate("X", qubit1, qubit2);
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
        isRunning.set(false);
        executor.shutdown();
        try {
            if (!executor.awaitTermination(60, TimeUnit.SECONDS)) {
                executor.shutdownNow();
            }
        } catch (InterruptedException e) {
            executor.shutdownNow();
            Thread.currentThread().interrupt();
        }
        
        try {
            selector.close();
            for (SocketChannel channel : connections.values()) {
                channel.close();
            }
            serverSocket.close();
        } catch (IOException e) {
            e.printStackTrace();
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

    private static class QuantumMessage {
        private final String source;
        private final byte[] data;

        public QuantumMessage(String source, byte[] data) {
            this.source = source;
            this.data = data;
        }

        public String getSource() {
            return source;
        }

        public byte[] getData() {
            return data;
        }
    }
} 