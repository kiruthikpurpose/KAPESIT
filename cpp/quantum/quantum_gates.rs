use ndarray::{Array1, Array2};
use num_complex::Complex;
use std::f64::consts::PI;

#[derive(Debug, Clone)]
pub struct QuantumGate {
    matrix: Array2<Complex<f64>>,
    name: String,
}

impl QuantumGate {
    pub fn new(matrix: Array2<Complex<f64>>, name: String) -> Self {
        QuantumGate { matrix, name }
    }

    pub fn apply(&self, state: &Array1<Complex<f64>>) -> Array1<Complex<f64>> {
        self.matrix.dot(state)
    }

    pub fn get_name(&self) -> &str {
        &self.name
    }
}

pub struct QuantumGates {
    pub hadamard: QuantumGate,
    pub pauli_x: QuantumGate,
    pub pauli_y: QuantumGate,
    pub pauli_z: QuantumGate,
    pub phase: QuantumGate,
    pub cnot: QuantumGate,
}

impl QuantumGates {
    pub fn new() -> Self {
        let sqrt2 = 1.0 / (2.0f64.sqrt());
        
        let hadamard = QuantumGate::new(
            Array2::from_shape_vec((2, 2), vec![
                Complex::new(sqrt2, 0.0), Complex::new(sqrt2, 0.0),
                Complex::new(sqrt2, 0.0), Complex::new(-sqrt2, 0.0),
            ]).unwrap(),
            "H".to_string(),
        );

        let pauli_x = QuantumGate::new(
            Array2::from_shape_vec((2, 2), vec![
                Complex::new(0.0, 0.0), Complex::new(1.0, 0.0),
                Complex::new(1.0, 0.0), Complex::new(0.0, 0.0),
            ]).unwrap(),
            "X".to_string(),
        );

        let pauli_y = QuantumGate::new(
            Array2::from_shape_vec((2, 2), vec![
                Complex::new(0.0, 0.0), Complex::new(0.0, -1.0),
                Complex::new(0.0, 1.0), Complex::new(0.0, 0.0),
            ]).unwrap(),
            "Y".to_string(),
        );

        let pauli_z = QuantumGate::new(
            Array2::from_shape_vec((2, 2), vec![
                Complex::new(1.0, 0.0), Complex::new(0.0, 0.0),
                Complex::new(0.0, 0.0), Complex::new(-1.0, 0.0),
            ]).unwrap(),
            "Z".to_string(),
        );

        let phase = QuantumGate::new(
            Array2::from_shape_vec((2, 2), vec![
                Complex::new(1.0, 0.0), Complex::new(0.0, 0.0),
                Complex::new(0.0, 0.0), Complex::new(0.0, 1.0),
            ]).unwrap(),
            "S".to_string(),
        );

        let cnot = QuantumGate::new(
            Array2::from_shape_vec((4, 4), vec![
                Complex::new(1.0, 0.0), Complex::new(0.0, 0.0), Complex::new(0.0, 0.0), Complex::new(0.0, 0.0),
                Complex::new(0.0, 0.0), Complex::new(1.0, 0.0), Complex::new(0.0, 0.0), Complex::new(0.0, 0.0),
                Complex::new(0.0, 0.0), Complex::new(0.0, 0.0), Complex::new(0.0, 0.0), Complex::new(1.0, 0.0),
                Complex::new(0.0, 0.0), Complex::new(0.0, 0.0), Complex::new(1.0, 0.0), Complex::new(0.0, 0.0),
            ]).unwrap(),
            "CNOT".to_string(),
        );

        QuantumGates {
            hadamard,
            pauli_x,
            pauli_y,
            pauli_z,
            phase,
            cnot,
        }
    }

    pub fn rotation_x(&self, theta: f64) -> QuantumGate {
        let cos_theta = (theta / 2.0).cos();
        let sin_theta = (theta / 2.0).sin();
        
        QuantumGate::new(
            Array2::from_shape_vec((2, 2), vec![
                Complex::new(cos_theta, 0.0), Complex::new(0.0, -sin_theta),
                Complex::new(0.0, -sin_theta), Complex::new(cos_theta, 0.0),
            ]).unwrap(),
            format!("Rx({})", theta),
        )
    }

    pub fn rotation_y(&self, theta: f64) -> QuantumGate {
        let cos_theta = (theta / 2.0).cos();
        let sin_theta = (theta / 2.0).sin();
        
        QuantumGate::new(
            Array2::from_shape_vec((2, 2), vec![
                Complex::new(cos_theta, 0.0), Complex::new(-sin_theta, 0.0),
                Complex::new(sin_theta, 0.0), Complex::new(cos_theta, 0.0),
            ]).unwrap(),
            format!("Ry({})", theta),
        )
    }

    pub fn rotation_z(&self, theta: f64) -> QuantumGate {
        let exp_neg = Complex::new(0.0, -theta / 2.0).exp();
        let exp_pos = Complex::new(0.0, theta / 2.0).exp();
        
        QuantumGate::new(
            Array2::from_shape_vec((2, 2), vec![
                exp_neg, Complex::new(0.0, 0.0),
                Complex::new(0.0, 0.0), exp_pos,
            ]).unwrap(),
            format!("Rz({})", theta),
        )
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use approx::assert_relative_eq;

    #[test]
    fn test_hadamard_gate() {
        let gates = QuantumGates::new();
        let state = Array1::from_vec(vec![Complex::new(1.0, 0.0), Complex::new(0.0, 0.0)]);
        let result = gates.hadamard.apply(&state);
        
        let sqrt2 = 1.0 / (2.0f64.sqrt());
        assert_relative_eq!(result[0].re, sqrt2, epsilon = 1e-10);
        assert_relative_eq!(result[1].re, sqrt2, epsilon = 1e-10);
    }

    #[test]
    fn test_pauli_x_gate() {
        let gates = QuantumGates::new();
        let state = Array1::from_vec(vec![Complex::new(1.0, 0.0), Complex::new(0.0, 0.0)]);
        let result = gates.pauli_x.apply(&state);
        
        assert_relative_eq!(result[0].re, 0.0, epsilon = 1e-10);
        assert_relative_eq!(result[1].re, 1.0, epsilon = 1e-10);
    }
} 