#include <vector>
#include <complex>
#include <thread>
#include <mutex>
#include <cmath>
#include <immintrin.h>

extern "C" {
    void quantum_evolve(double* state, double* hamiltonian, int dim, double dt, int steps) {
        std::vector<std::complex<double>> state_vec(dim);
        std::vector<std::complex<double>> hamiltonian_vec(dim * dim);
        
        for(int i = 0; i < dim; i++) {
            state_vec[i] = std::complex<double>(state[2*i], state[2*i+1]);
        }
        
        for(int i = 0; i < dim * dim; i++) {
            hamiltonian_vec[i] = std::complex<double>(hamiltonian[2*i], hamiltonian[2*i+1]);
        }
        
        int num_threads = std::thread::hardware_concurrency();
        std::vector<std::thread> threads;
        std::mutex mtx;
        
        for(int step = 0; step < steps; step++) {
            std::vector<std::complex<double>> new_state(dim);
            
            for(int t = 0; t < num_threads; t++) {
                threads.emplace_back([&, t]() {
                    int chunk_size = dim / num_threads;
                    int start = t * chunk_size;
                    int end = (t == num_threads - 1) ? dim : (t + 1) * chunk_size;
                    
                    for(int i = start; i < end; i++) {
                        std::complex<double> sum(0, 0);
                        for(int j = 0; j < dim; j++) {
                            sum += hamiltonian_vec[i * dim + j] * state_vec[j];
                        }
                        new_state[i] = sum * std::complex<double>(0, -dt);
                    }
                });
            }
            
            for(auto& thread : threads) {
                thread.join();
            }
            threads.clear();
            
            for(int i = 0; i < dim; i++) {
                state_vec[i] += new_state[i];
                state[2*i] = state_vec[i].real();
                state[2*i+1] = state_vec[i].imag();
            }
        }
    }
    
    void quantum_measure(double* state, double* observables, int dim, double* results) {
        __m256d sum = _mm256_setzero_pd();
        
        for(int i = 0; i < dim; i += 2) {
            __m256d state_vec = _mm256_loadu_pd(&state[2*i]);
            __m256d obs_vec = _mm256_loadu_pd(&observables[2*i]);
            __m256d prod = _mm256_mul_pd(state_vec, obs_vec);
            sum = _mm256_add_pd(sum, prod);
        }
        
        double temp[4];
        _mm256_storeu_pd(temp, sum);
        results[0] = temp[0] + temp[1];
        results[1] = temp[2] + temp[3];
    }
    
    void quantum_entangle(double* state1, double* state2, int dim, double* result) {
        #pragma omp parallel for
        for(int i = 0; i < dim; i++) {
            for(int j = 0; j < dim; j++) {
                result[i * dim + j] = state1[i] * state2[j];
            }
        }
    }
    
    void quantum_fourier_transform(double* input, double* output, int size) {
        std::vector<std::complex<double>> temp(size);
        
        for(int i = 0; i < size; i++) {
            temp[i] = std::complex<double>(input[2*i], input[2*i+1]);
        }
        
        for(int k = 0; k < size; k++) {
            std::complex<double> sum(0, 0);
            for(int n = 0; n < size; n++) {
                double angle = 2 * M_PI * k * n / size;
                std::complex<double> w(std::cos(angle), -std::sin(angle));
                sum += temp[n] * w;
            }
            output[2*k] = sum.real();
            output[2*k+1] = sum.imag();
        }
    }
} 