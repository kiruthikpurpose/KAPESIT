import java.util.ArrayList;
import java.util.List;
import org.apache.commons.math3.linear.*;

public class QuantumGate {
    private RealMatrix matrix;
    private List<Integer> targetQubits;
    
    public QuantumGate(RealMatrix matrix, List<Integer> targets) {
        this.matrix = matrix;
        this.targetQubits = targets;
    }
    
    public RealMatrix getMatrix() {
        return matrix;
    }
    
    public List<Integer> getTargetQubits() {
        return targetQubits;
    }
    
    public void apply(RealVector state) {
        RealVector result = state.copy();
        
        for (int qubit : targetQubits) {
            result = matrix.operate(result);
        }
        
        return result;
    }
}
