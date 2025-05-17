use nalgebra::{DMatrix, DVector};
use rand::prelude::*;
use std::f64::consts::PI;

struct QuantumState {
    state: DVector<f64>,
    num_qubits: usize,
}

impl QuantumState {
    fn new(num_qubits: usize) -> Self {
        let size = 1 << num_qubits;
        let mut state = DVector::zeros(size);
        state[0] = 1.0;
        QuantumState { state, num_qubits }
    }

    fn apply_gate(&mut self, gate: &DMatrix<f64>, target: usize) {
        let mut result = DVector::zeros(1 << self.num_qubits);
        let gate_size = gate.nrows();
        
        for i in 0..(1 << self.num_qubits) {
            let mut sum = 0.0;
            for j in 0..gate_size {
                let mask = 1 << target;
                let bit_i = (i & mask) >> target;
                let bit_j = (j & mask) >> target;
                
                let index = (i & !mask) | (bit_j << target);
                sum += gate[(j, bit_i)] * self.state[index];
            }
            result[i] = sum;
        }
        
        self.state = result;
    }

    fn measure(&mut self) -> usize {
        let mut rng = thread_rng();
        let probabilities: Vec<f64> = self.state.iter().map(|&x| x.powi(2)).collect();
        let total: f64 = probabilities.iter().sum();
        let probabilities: Vec<f64> = probabilities.iter().map(|&x| x / total).collect();
        
        let mut cumulative = 0.0;
        let r: f64 = rng.gen();
        
        for (i, &prob) in probabilities.iter().enumerate() {
            cumulative += prob;
            if r <= cumulative {
                self.state.fill(0.0);
                self.state[i] = 1.0;
                return i;
            }
        }
        
        0
    }
}
