#include <iostream>
#include <vector>
#include <cmath>
#include <random>
#include <chrono>
#include <Eigen/Dense>

using Eigen::MatrixXd;
using Eigen::VectorXd;

class QuantumProcessor {
private:
    int num_qubits;
    double error_rate;
    VectorXd state;
    std::vector<std::pair<std::string, MatrixXd>> operations;
    std::mt19937 rng;
    
public:
    QuantumProcessor(int qubits, double rate) : 
        num_qubits(qubits), error_rate(rate), rng(std::random_device{}()) {}
    
    void initialize_state(const VectorXd& initial_state) {
        state = initial_state.normalized();
    }
    
    void apply_gate(const MatrixXd& gate, const std::vector<int>& targets) {
        if (std::uniform_real_distribution<>(0.0, 1.0)(rng) < error_rate) {
            apply_error();
        }
        
        state = apply_gate_operation(gate, targets);
        operations.push_back({"gate", gate});
    }
    
private:
    VectorXd apply_gate_operation(const MatrixXd& gate, const std::vector<int>& targets) {
        MatrixXd full_gate = MatrixXd::Identity(std::pow(2, num_qubits), std::pow(2, num_qubits));
        for (int qubit : targets) {
            full_gate = full_gate.kroneckerProduct(gate);
        }
        return full_gate * state;
    }
    
    void apply_error() {
        std::normal_distribution<double> dist(0.0, error_rate);
        state += VectorXd::Random(state.size()) * dist(rng);
        state.normalize();
    }
};
