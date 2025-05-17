import ctypes
import numpy as np
import os
from ctypes import c_int, c_float, c_double, POINTER, c_void_p

class CppMatrixOps:
    def __init__(self):
        self.lib = ctypes.CDLL(os.path.join(os.path.dirname(__file__), '../../cpp/libfastops.so'))
        self._setup_functions()
    
    def _setup_functions(self):
        self.lib.fast_matrix_multiply.argtypes = [
            POINTER(c_float), POINTER(c_float), POINTER(c_float),
            c_int, c_int, c_int
        ]
        self.lib.fast_matrix_multiply.restype = None
        
        self.lib.fast_matrix_add.argtypes = [
            POINTER(c_float), POINTER(c_float), POINTER(c_float),
            c_int, c_int
        ]
        self.lib.fast_matrix_add.restype = None
        
        self.lib.fast_matrix_subtract.argtypes = [
            POINTER(c_float), POINTER(c_float), POINTER(c_float),
            c_int, c_int
        ]
        self.lib.fast_matrix_subtract.restype = None
        
        self.lib.fast_matrix_transpose.argtypes = [
            POINTER(c_float), POINTER(c_float), c_int, c_int
        ]
        self.lib.fast_matrix_transpose.restype = None
    
    def matrix_multiply(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        m, n = a.shape
        n, p = b.shape
        result = np.zeros((m, p), dtype=np.float32)
        
        self.lib.fast_matrix_multiply(
            a.astype(np.float32).ctypes.data_as(POINTER(c_float)),
            b.astype(np.float32).ctypes.data_as(POINTER(c_float)),
            result.ctypes.data_as(POINTER(c_float)),
            m, n, p
        )
        return result
    
    def matrix_add(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        m, n = a.shape
        result = np.zeros((m, n), dtype=np.float32)
        
        self.lib.fast_matrix_add(
            a.astype(np.float32).ctypes.data_as(POINTER(c_float)),
            b.astype(np.float32).ctypes.data_as(POINTER(c_float)),
            result.ctypes.data_as(POINTER(c_float)),
            m, n
        )
        return result
    
    def matrix_subtract(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        m, n = a.shape
        result = np.zeros((m, n), dtype=np.float32)
        
        self.lib.fast_matrix_subtract(
            a.astype(np.float32).ctypes.data_as(POINTER(c_float)),
            b.astype(np.float32).ctypes.data_as(POINTER(c_float)),
            result.ctypes.data_as(POINTER(c_float)),
            m, n
        )
        return result
    
    def matrix_transpose(self, a: np.ndarray) -> np.ndarray:
        m, n = a.shape
        result = np.zeros((n, m), dtype=np.float32)
        
        self.lib.fast_matrix_transpose(
            a.astype(np.float32).ctypes.data_as(POINTER(c_float)),
            result.ctypes.data_as(POINTER(c_float)),
            m, n
        )
        return result

class QuantumSimulator:
    def __init__(self):
        self.lib = ctypes.CDLL(os.path.join(os.path.dirname(__file__), '../../cpp/libquantum.so'))
        self._setup_functions()
    
    def _setup_functions(self):
        self.lib.quantum_evolve.argtypes = [
            POINTER(c_float), POINTER(c_float), c_int, c_float
        ]
        self.lib.quantum_evolve.restype = None
        
        self.lib.quantum_measure.argtypes = [
            POINTER(c_float), POINTER(c_float), c_int
        ]
        self.lib.quantum_measure.restype = None
        
        self.lib.quantum_entangle.argtypes = [
            POINTER(c_float), POINTER(c_float), c_int
        ]
        self.lib.quantum_entangle.restype = None
        
        self.lib.quantum_fft.argtypes = [
            POINTER(c_float), POINTER(c_float), c_int
        ]
        self.lib.quantum_fft.restype = None
    
    def evolve(self, state: np.ndarray, hamiltonian: np.ndarray, time: float) -> np.ndarray:
        n = len(state)
        result = np.zeros(n, dtype=np.float32)
        
        self.lib.quantum_evolve(
            state.astype(np.float32).ctypes.data_as(POINTER(c_float)),
            hamiltonian.astype(np.float32).ctypes.data_as(POINTER(c_float)),
            n, time
        )
        return result
    
    def measure(self, state: np.ndarray) -> np.ndarray:
        n = len(state)
        result = np.zeros(n, dtype=np.float32)
        
        self.lib.quantum_measure(
            state.astype(np.float32).ctypes.data_as(POINTER(c_float)),
            result.ctypes.data_as(POINTER(c_float)),
            n
        )
        return result
    
    def entangle(self, state1: np.ndarray, state2: np.ndarray) -> np.ndarray:
        n = len(state1)
        result = np.zeros(n, dtype=np.float32)
        
        self.lib.quantum_entangle(
            state1.astype(np.float32).ctypes.data_as(POINTER(c_float)),
            state2.astype(np.float32).ctypes.data_as(POINTER(c_float)),
            n
        )
        return result
    
    def fft(self, real: np.ndarray, imag: np.ndarray) -> tuple:
        n = len(real)
        result_real = np.zeros(n, dtype=np.float32)
        result_imag = np.zeros(n, dtype=np.float32)
        
        self.lib.quantum_fft(
            real.astype(np.float32).ctypes.data_as(POINTER(c_float)),
            imag.astype(np.float32).ctypes.data_as(POINTER(c_float)),
            n
        )
        return result_real, result_imag

class ParallelOps:
    def __init__(self):
        self.lib = ctypes.CDLL(os.path.join(os.path.dirname(__file__), '../../cpp/libparallel.so'))
        self._setup_functions()
    
    def _setup_functions(self):
        self.lib.parallel_matrix_multiply.argtypes = [
            POINTER(c_float), POINTER(c_float), POINTER(c_float),
            c_int, c_int, c_int
        ]
        self.lib.parallel_matrix_multiply.restype = None
        
        self.lib.parallel_vector_ops.argtypes = [
            POINTER(c_float), POINTER(c_float), POINTER(c_float),
            c_int, c_int
        ]
        self.lib.parallel_vector_ops.restype = None
        
        self.lib.parallel_sort.argtypes = [
            POINTER(c_float), c_int
        ]
        self.lib.parallel_sort.restype = None
        
        self.lib.parallel_reduce.argtypes = [
            POINTER(c_float), POINTER(c_float), c_int
        ]
        self.lib.parallel_reduce.restype = None
        
        self.lib.parallel_scan.argtypes = [
            POINTER(c_float), POINTER(c_float), c_int
        ]
        self.lib.parallel_scan.restype = None
    
    def matrix_multiply(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        m, n = a.shape
        n, p = b.shape
        result = np.zeros((m, p), dtype=np.float32)
        
        self.lib.parallel_matrix_multiply(
            a.astype(np.float32).ctypes.data_as(POINTER(c_float)),
            b.astype(np.float32).ctypes.data_as(POINTER(c_float)),
            result.ctypes.data_as(POINTER(c_float)),
            m, n, p
        )
        return result
    
    def vector_ops(self, a: np.ndarray, b: np.ndarray, op: int) -> np.ndarray:
        n = len(a)
        result = np.zeros(n, dtype=np.float32)
        
        self.lib.parallel_vector_ops(
            a.astype(np.float32).ctypes.data_as(POINTER(c_float)),
            b.astype(np.float32).ctypes.data_as(POINTER(c_float)),
            result.ctypes.data_as(POINTER(c_float)),
            n, op
        )
        return result
    
    def sort(self, arr: np.ndarray) -> np.ndarray:
        n = len(arr)
        result = arr.copy().astype(np.float32)
        
        self.lib.parallel_sort(
            result.ctypes.data_as(POINTER(c_float)),
            n
        )
        return result
    
    def reduce(self, arr: np.ndarray) -> float:
        n = len(arr)
        result = np.zeros(1, dtype=np.float32)
        
        self.lib.parallel_reduce(
            arr.astype(np.float32).ctypes.data_as(POINTER(c_float)),
            result.ctypes.data_as(POINTER(c_float)),
            n
        )
        return float(result[0])
    
    def scan(self, arr: np.ndarray) -> np.ndarray:
        n = len(arr)
        result = np.zeros(n, dtype=np.float32)
        
        self.lib.parallel_scan(
            arr.astype(np.float32).ctypes.data_as(POINTER(c_float)),
            result.ctypes.data_as(POINTER(c_float)),
            n
        )
        return result

class NumericalOps:
    def __init__(self):
        self.lib = ctypes.CDLL(os.path.join(os.path.dirname(__file__), '../../cpp/libnumerical.so'))
        self._setup_functions()
    
    def _setup_functions(self):
        self.lib.fast_sin_cos.argtypes = [
            POINTER(c_float), POINTER(c_float), POINTER(c_float), c_int
        ]
        self.lib.fast_sin_cos.restype = None
        
        self.lib.fast_matrix_inverse.argtypes = [
            POINTER(c_float), POINTER(c_float), c_int
        ]
        self.lib.fast_matrix_inverse.restype = None
        
        self.lib.fast_eigenvalues.argtypes = [
            POINTER(c_float), POINTER(c_float), c_int
        ]
        self.lib.fast_eigenvalues.restype = None
        
        self.lib.fast_fft.argtypes = [
            POINTER(c_float), POINTER(c_float), c_int
        ]
        self.lib.fast_fft.restype = None
        
        self.lib.fast_svd.argtypes = [
            POINTER(c_float), POINTER(c_float), POINTER(c_float),
            POINTER(c_float), c_int, c_int
        ]
        self.lib.fast_svd.restype = None
        
        self.lib.fast_cholesky.argtypes = [
            POINTER(c_float), POINTER(c_float), c_int
        ]
        self.lib.fast_cholesky.restype = None
        
        self.lib.fast_qr.argtypes = [
            POINTER(c_float), POINTER(c_float), POINTER(c_float),
            c_int, c_int
        ]
        self.lib.fast_qr.restype = None
    
    def sin_cos(self, angles: np.ndarray) -> tuple:
        n = len(angles)
        sin_result = np.zeros(n, dtype=np.float32)
        cos_result = np.zeros(n, dtype=np.float32)
        
        self.lib.fast_sin_cos(
            angles.astype(np.float32).ctypes.data_as(POINTER(c_float)),
            sin_result.ctypes.data_as(POINTER(c_float)),
            cos_result.ctypes.data_as(POINTER(c_float)),
            n
        )
        return sin_result, cos_result
    
    def matrix_inverse(self, a: np.ndarray) -> np.ndarray:
        n = a.shape[0]
        result = np.zeros((n, n), dtype=np.float32)
        
        self.lib.fast_matrix_inverse(
            a.astype(np.float32).ctypes.data_as(POINTER(c_float)),
            result.ctypes.data_as(POINTER(c_float)),
            n
        )
        return result
    
    def eigenvalues(self, a: np.ndarray) -> np.ndarray:
        n = a.shape[0]
        result = np.zeros(n, dtype=np.float32)
        
        self.lib.fast_eigenvalues(
            a.astype(np.float32).ctypes.data_as(POINTER(c_float)),
            result.ctypes.data_as(POINTER(c_float)),
            n
        )
        return result
    
    def fft(self, real: np.ndarray, imag: np.ndarray) -> tuple:
        n = len(real)
        result_real = np.zeros(n, dtype=np.float32)
        result_imag = np.zeros(n, dtype=np.float32)
        
        self.lib.fast_fft(
            real.astype(np.float32).ctypes.data_as(POINTER(c_float)),
            imag.astype(np.float32).ctypes.data_as(POINTER(c_float)),
            n
        )
        return result_real, result_imag
    
    def svd(self, a: np.ndarray) -> tuple:
        m, n = a.shape
        u = np.zeros((m, m), dtype=np.float32)
        s = np.zeros(min(m, n), dtype=np.float32)
        v = np.zeros((n, n), dtype=np.float32)
        
        self.lib.fast_svd(
            a.astype(np.float32).ctypes.data_as(POINTER(c_float)),
            u.ctypes.data_as(POINTER(c_float)),
            s.ctypes.data_as(POINTER(c_float)),
            v.ctypes.data_as(POINTER(c_float)),
            m, n
        )
        return u, s, v
    
    def cholesky(self, a: np.ndarray) -> np.ndarray:
        n = a.shape[0]
        result = np.zeros((n, n), dtype=np.float32)
        
        self.lib.fast_cholesky(
            a.astype(np.float32).ctypes.data_as(POINTER(c_float)),
            result.ctypes.data_as(POINTER(c_float)),
            n
        )
        return result
    
    def qr(self, a: np.ndarray) -> tuple:
        m, n = a.shape
        q = np.zeros((m, m), dtype=np.float32)
        r = np.zeros((m, n), dtype=np.float32)
        
        self.lib.fast_qr(
            a.astype(np.float32).ctypes.data_as(POINTER(c_float)),
            q.ctypes.data_as(POINTER(c_float)),
            r.ctypes.data_as(POINTER(c_float)),
            m, n
        )
        return q, r

class AssemblyOps:
    def __init__(self):
        self.lib = ctypes.CDLL(os.path.join(os.path.dirname(__file__), '../../cpp/libassembly.so'))
        self._setup_functions()
    
    def _setup_functions(self):
        self.lib.fast_dot_product.argtypes = [
            POINTER(c_float), POINTER(c_float), c_int
        ]
        self.lib.fast_dot_product.restype = c_float
        
        self.lib.fast_matrix_transpose.argtypes = [
            POINTER(c_float), POINTER(c_float), c_int, c_int
        ]
        self.lib.fast_matrix_transpose.restype = None
        
        self.lib.fast_vector_norm.argtypes = [
            POINTER(c_float), c_int
        ]
        self.lib.fast_vector_norm.restype = c_float
        
        self.lib.fast_convolution.argtypes = [
            POINTER(c_float), POINTER(c_float), POINTER(c_float),
            c_int, c_int
        ]
        self.lib.fast_convolution.restype = None
    
    def dot_product(self, a: np.ndarray, b: np.ndarray) -> float:
        n = len(a)
        return self.lib.fast_dot_product(
            a.astype(np.float32).ctypes.data_as(POINTER(c_float)),
            b.astype(np.float32).ctypes.data_as(POINTER(c_float)),
            n
        )
    
    def matrix_transpose(self, a: np.ndarray) -> np.ndarray:
        m, n = a.shape
        result = np.zeros((n, m), dtype=np.float32)
        
        self.lib.fast_matrix_transpose(
            a.astype(np.float32).ctypes.data_as(POINTER(c_float)),
            result.ctypes.data_as(POINTER(c_float)),
            m, n
        )
        return result
    
    def vector_norm(self, a: np.ndarray) -> float:
        n = len(a)
        return self.lib.fast_vector_norm(
            a.astype(np.float32).ctypes.data_as(POINTER(c_float)),
            n
        )
    
    def convolution(self, input_data: np.ndarray, kernel: np.ndarray) -> np.ndarray:
        n = len(input_data)
        k = len(kernel)
        result = np.zeros(n, dtype=np.float32)
        
        self.lib.fast_convolution(
            input_data.astype(np.float32).ctypes.data_as(POINTER(c_float)),
            kernel.astype(np.float32).ctypes.data_as(POINTER(c_float)),
            result.ctypes.data_as(POINTER(c_float)),
            n, k
        )
        return result 