import java.util.ArrayList;
import java.util.List;
import org.apache.commons.math3.linear.*;

public class QuantumCircuit {
    private int numQubits;
    private RealVector state;
    private List<QuantumGate> gates;
    
    public QuantumCircuit(int qubits) {
        this.numQubits = qubits;
        this.state = new ArrayRealVector(1 << qubits);
        this.state.setEntry(0, 1.0);
        this.gates = new ArrayList<>();
    }
    
    public void addGate(QuantumGate gate) {
        gates.add(gate);
    }
    
    public void execute() {
        RealVector currentState = state.copy();
        
        for (QuantumGate gate : gates) {
            currentState = gate.apply(currentState);
        }
        
        state = currentState;
    }
    
    public int measure() {
        double[] probabilities = new double[state.getDimension()];
        double total = 0.0;
        
        for (int i = 0; i < state.getDimension(); i++) {
            probabilities[i] = Math.pow(state.getEntry(i), 2);
            total += probabilities[i];
        }
        
        double r = Math.random() * total;
        double cumulative = 0.0;
        
        for (int i = 0; i < state.getDimension(); i++) {
            cumulative += probabilities[i];
            if (r <= cumulative) {
                // Collapse state
                state.set(0);
                state.setEntry(i, 1.0);
                return i;
            }
        }
        
        return 0;
    }
    
    public RealVector getState() {
        return state.copy();
    }
}
