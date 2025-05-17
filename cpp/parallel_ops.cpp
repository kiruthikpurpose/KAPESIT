#include <vector>
#include <thread>
#include <immintrin.h>
#include <omp.h>

extern "C" {
    void parallel_matrix_multiply(double* a, double* b, double* c, int m, int k, int n) {
        #pragma omp parallel for collapse(2)
        for(int i = 0; i < m; i++) {
            for(int j = 0; j < n; j++) {
                __m256d sum = _mm256_setzero_pd();
                for(int l = 0; l < k; l += 4) {
                    __m256d a_vec = _mm256_loadu_pd(&a[i * k + l]);
                    __m256d b_vec = _mm256_loadu_pd(&b[l * n + j]);
                    sum = _mm256_add_pd(sum, _mm256_mul_pd(a_vec, b_vec));
                }
                double temp[4];
                _mm256_storeu_pd(temp, sum);
                c[i * n + j] = temp[0] + temp[1] + temp[2] + temp[3];
            }
        }
    }
    
    void parallel_vector_ops(double* a, double* b, double* c, int size, int op_type) {
        #pragma omp parallel for
        for(int i = 0; i < size; i += 4) {
            __m256d a_vec = _mm256_loadu_pd(&a[i]);
            __m256d b_vec = _mm256_loadu_pd(&b[i]);
            __m256d result;
            
            switch(op_type) {
                case 0: // Add
                    result = _mm256_add_pd(a_vec, b_vec);
                    break;
                case 1: // Subtract
                    result = _mm256_sub_pd(a_vec, b_vec);
                    break;
                case 2: // Multiply
                    result = _mm256_mul_pd(a_vec, b_vec);
                    break;
                case 3: // Divide
                    result = _mm256_div_pd(a_vec, b_vec);
                    break;
            }
            
            _mm256_storeu_pd(&c[i], result);
        }
    }
    
    void parallel_sort(double* arr, int size) {
        #pragma omp parallel
        {
            int num_threads = omp_get_num_threads();
            int thread_id = omp_get_thread_num();
            int chunk_size = size / num_threads;
            int start = thread_id * chunk_size;
            int end = (thread_id == num_threads - 1) ? size : (thread_id + 1) * chunk_size;
            
            std::sort(&arr[start], &arr[end]);
        }
        
        for(int step = 1; step < size; step *= 2) {
            #pragma omp parallel for
            for(int i = 0; i < size; i += 2 * step) {
                int mid = std::min(i + step, size);
                int end = std::min(i + 2 * step, size);
                
                std::inplace_merge(&arr[i], &arr[mid], &arr[end]);
            }
        }
    }
    
    void parallel_reduce(double* arr, int size, double* result) {
        double sum = 0.0;
        #pragma omp parallel for reduction(+:sum)
        for(int i = 0; i < size; i++) {
            sum += arr[i];
        }
        *result = sum;
    }
    
    void parallel_scan(double* arr, int size, double* result) {
        #pragma omp parallel
        {
            int num_threads = omp_get_num_threads();
            int thread_id = omp_get_thread_num();
            int chunk_size = size / num_threads;
            int start = thread_id * chunk_size;
            int end = (thread_id == num_threads - 1) ? size : (thread_id + 1) * chunk_size;
            
            double local_sum = 0.0;
            for(int i = start; i < end; i++) {
                local_sum += arr[i];
                result[i] = local_sum;
            }
        }
        
        for(int step = 1; step < size; step *= 2) {
            #pragma omp parallel for
            for(int i = step; i < size; i++) {
                result[i] += result[i - step];
            }
        }
    }
} 