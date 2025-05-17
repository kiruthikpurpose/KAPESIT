#include <iostream>
#include <vector>
#include <cmath>
#include <Eigen/Dense>
#include <random>
#include <chrono>

using Eigen::MatrixXd;
using Eigen::VectorXd;

class QuantumGate {
private:
    MatrixXd gate_matrix;
    std::vector<int> target_qubits;
    
public:
    QuantumGate(const MatrixXd& matrix, const std::vector<int>& targets) :
        gate_matrix(matrix), target_qubits(targets) {}
    
    MatrixXd get_matrix() const { return gate_matrix; }
    std::vector<int> get_targets() const { return target_qubits; }
};

class QuantumCircuit {
private:
    int num_qubits;
    VectorXd state;
    std::vector<QuantumGate> gates;
    std::mt19937 rng;
    
public:
    QuantumCircuit(int qubits) : 
        num_qubits(qubits), 
        state(VectorXd::Zero(std::pow(2, qubits))),
        rng(std::random_device{}()) {
        state(0) = 1.0;
    }
    
    void add_gate(const MatrixXd& matrix, const std::vector<int>& targets) {
        gates.push_back(QuantumGate(matrix, targets));
    }
    
    void execute() {
        for (const auto& gate : gates) {
            apply_gate(gate);
        }
    }
    
    VectorXd measure() {
        double probabilities[std::pow(2, num_qubits)];
        for (int i = 0; i < std::pow(2, num_qubits); i++) {
            probabilities[i] = std::pow(state(i), 2);
        }
        
        std::discrete_distribution<> dist(probabilities, probabilities + std::pow(2, num_qubits));
        int result = dist(rng);
        
        // Collapse state
        state.setZero();
        state(result) = 1.0;
        
        return state;
    }
    
private:
    void apply_gate(const QuantumGate& gate) {
        MatrixXd full_gate = MatrixXd::Identity(std::pow(2, num_qubits), std::pow(2, num_qubits));
        for (int qubit : gate.get_targets()) {
            full_gate = full_gate.kroneckerProduct(gate.get_matrix());
        }
        state = full_gate * state;
    }
};
