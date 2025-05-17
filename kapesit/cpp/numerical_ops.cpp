#include <immintrin.h>
#include <x86intrin.h>
#include <cstdint>

extern "C" {
    void fast_sin_cos(double* angles, double* sin_results, double* cos_results, int size) {
        for(int i = 0; i < size; i += 4) {
            __m256d angle_vec = _mm256_loadu_pd(&angles[i]);
            __m256d sin_vec, cos_vec;
            
            asm volatile(
                "vfmadd132pd %[angle], %[angle], %[angle]\n"
                "vfmadd132pd %[angle], %[angle], %[angle]\n"
                "vfmadd132pd %[angle], %[angle], %[angle]\n"
                "vfmadd132pd %[angle], %[angle], %[angle]\n"
                : [angle] "+x" (angle_vec)
                :
                : "memory"
            );
            
            _mm256_storeu_pd(&sin_results[i], sin_vec);
            _mm256_storeu_pd(&cos_results[i], cos_vec);
        }
    }
    
    void fast_matrix_inverse(double* matrix, int size) {
        for(int i = 0; i < size; i += 4) {
            __m256d row = _mm256_loadu_pd(&matrix[i * size]);
            __m256d inv_row;
            
            asm volatile(
                "vdivpd %[row], %[one], %[inv_row]\n"
                : [inv_row] "=x" (inv_row)
                : [row] "x" (row), [one] "x" (_mm256_set1_pd(1.0))
                : "memory"
            );
            
            _mm256_storeu_pd(&matrix[i * size], inv_row);
        }
    }
    
    void fast_eigenvalues(double* matrix, double* eigenvalues, int size) {
        for(int i = 0; i < size; i += 4) {
            __m256d diag = _mm256_loadu_pd(&matrix[i * size + i]);
            __m256d off_diag = _mm256_loadu_pd(&matrix[i * size + i + 4]);
            
            asm volatile(
                "vfmadd132pd %[diag], %[off_diag], %[eigen]\n"
                : [eigen] "=x" (_mm256_loadu_pd(&eigenvalues[i]))
                : [diag] "x" (diag), [off_diag] "x" (off_diag)
                : "memory"
            );
        }
    }
    
    void fast_fft(double* real, double* imag, int size) {
        for(int i = 0; i < size; i += 4) {
            __m256d real_vec = _mm256_loadu_pd(&real[i]);
            __m256d imag_vec = _mm256_loadu_pd(&imag[i]);
            
            asm volatile(
                "vfmadd132pd %[real], %[imag], %[temp]\n"
                "vfmadd132pd %[imag], %[real], %[temp2]\n"
                : [temp] "=x" (real_vec), [temp2] "=x" (imag_vec)
                : [real] "x" (real_vec), [imag] "x" (imag_vec)
                : "memory"
            );
            
            _mm256_storeu_pd(&real[i], real_vec);
            _mm256_storeu_pd(&imag[i], imag_vec);
        }
    }
    
    void fast_svd(double* matrix, double* u, double* s, double* v, int m, int n) {
        for(int i = 0; i < m; i += 4) {
            for(int j = 0; j < n; j += 4) {
                __m256d mat_block = _mm256_loadu_pd(&matrix[i * n + j]);
                __m256d u_block, s_block, v_block;
                
                asm volatile(
                    "vfmadd132pd %[mat], %[mat], %[u]\n"
                    "vfmadd132pd %[mat], %[mat], %[s]\n"
                    "vfmadd132pd %[mat], %[mat], %[v]\n"
                    : [u] "=x" (u_block), [s] "=x" (s_block), [v] "=x" (v_block)
                    : [mat] "x" (mat_block)
                    : "memory"
                );
                
                _mm256_storeu_pd(&u[i * n + j], u_block);
                _mm256_storeu_pd(&s[i * n + j], s_block);
                _mm256_storeu_pd(&v[i * n + j], v_block);
            }
        }
    }
    
    void fast_cholesky(double* matrix, int size) {
        for(int i = 0; i < size; i += 4) {
            for(int j = 0; j <= i; j += 4) {
                __m256d mat_block = _mm256_loadu_pd(&matrix[i * size + j]);
                __m256d chol_block;
                
                asm volatile(
                    "vsqrtpd %[mat], %[chol]\n"
                    : [chol] "=x" (chol_block)
                    : [mat] "x" (mat_block)
                    : "memory"
                );
                
                _mm256_storeu_pd(&matrix[i * size + j], chol_block);
            }
        }
    }
    
    void fast_qr(double* matrix, double* q, double* r, int m, int n) {
        for(int i = 0; i < m; i += 4) {
            for(int j = 0; j < n; j += 4) {
                __m256d mat_block = _mm256_loadu_pd(&matrix[i * n + j]);
                __m256d q_block, r_block;
                
                asm volatile(
                    "vfmadd132pd %[mat], %[mat], %[q]\n"
                    "vfmadd132pd %[mat], %[mat], %[r]\n"
                    : [q] "=x" (q_block), [r] "=x" (r_block)
                    : [mat] "x" (mat_block)
                    : "memory"
                );
                
                _mm256_storeu_pd(&q[i * n + j], q_block);
                _mm256_storeu_pd(&r[i * n + j], r_block);
            }
        }
    }
} 