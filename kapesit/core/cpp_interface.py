import ctypes
import numpy as np
import os
from pathlib import Path
from typing import Tuple, Optional, Dict, Any, List
from ctypes import c_int, c_float, c_double, POINTER, c_void_p, c_bool
import logging

logger = logging.getLogger(__name__)

class CppMatrixOps:
    def __init__(self):
        lib_path = Path(__file__).parent.parent.parent / 'cpp' / 'libfastops.so'
        if not lib_path.exists():
            raise FileNotFoundError(f"Library not found: {lib_path}")
        try:
            self.lib = ctypes.CDLL(str(lib_path))
            self._setup_functions()
        except Exception as e:
            raise RuntimeError(f"Failed to load library: {str(e)}")
    
    def _setup_functions(self) -> None:
        self.lib.fast_matrix_multiply.argtypes = [
            POINTER(c_float), POINTER(c_float), POINTER(c_float),
            c_int, c_int, c_int
        ]
        self.lib.fast_matrix_multiply.restype = c_bool
        
        self.lib.fast_matrix_add.argtypes = [
            POINTER(c_float), POINTER(c_float), POINTER(c_float),
            c_int, c_int
        ]
        self.lib.fast_matrix_add.restype = c_bool
        
        self.lib.fast_matrix_subtract.argtypes = [
            POINTER(c_float), POINTER(c_float), POINTER(c_float),
            c_int, c_int
        ]
        self.lib.fast_matrix_subtract.restype = c_bool
        
        self.lib.fast_matrix_transpose.argtypes = [
            POINTER(c_float), POINTER(c_float), c_int, c_int
        ]
        self.lib.fast_matrix_transpose.restype = c_bool
    
    def matrix_multiply(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        if not isinstance(a, np.ndarray) or not isinstance(b, np.ndarray):
            raise TypeError("Inputs must be numpy arrays")
        if a.shape[1] != b.shape[0]:
            raise ValueError("Matrix dimensions incompatible for multiplication")
        
        m, n = a.shape
        n, p = b.shape
        result = np.zeros((m, p), dtype=np.float32)
        
        success = self.lib.fast_matrix_multiply(
            a.astype(np.float32, copy=False).ctypes.data_as(POINTER(c_float)),
            b.astype(np.float32, copy=False).ctypes.data_as(POINTER(c_float)),
            result.ctypes.data_as(POINTER(c_float)),
            m, n, p
        )
        if not success:
            raise RuntimeError("Matrix multiplication failed")
        return result
    
    def matrix_add(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        if not isinstance(a, np.ndarray) or not isinstance(b, np.ndarray):
            raise TypeError("Inputs must be numpy arrays")
        if a.shape != b.shape:
            raise ValueError("Matrix dimensions must match for addition")
        
        m, n = a.shape
        result = np.zeros((m, n), dtype=np.float32)
        
        success = self.lib.fast_matrix_add(
            a.astype(np.float32, copy=False).ctypes.data_as(POINTER(c_float)),
            b.astype(np.float32, copy=False).ctypes.data_as(POINTER(c_float)),
            result.ctypes.data_as(POINTER(c_float)),
            m, n
        )
        if not success:
            raise RuntimeError("Matrix addition failed")
        return result
    
    def matrix_subtract(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        if not isinstance(a, np.ndarray) or not isinstance(b, np.ndarray):
            raise TypeError("Inputs must be numpy arrays")
        if a.shape != b.shape:
            raise ValueError("Matrix dimensions must match for subtraction")
        
        m, n = a.shape
        result = np.zeros((m, n), dtype=np.float32)
        
        success = self.lib.fast_matrix_subtract(
            a.astype(np.float32, copy=False).ctypes.data_as(POINTER(c_float)),
            b.astype(np.float32, copy=False).ctypes.data_as(POINTER(c_float)),
            result.ctypes.data_as(POINTER(c_float)),
            m, n
        )
        if not success:
            raise RuntimeError("Matrix subtraction failed")
        return result
    
    def matrix_transpose(self, a: np.ndarray) -> np.ndarray:
        if not isinstance(a, np.ndarray):
            raise TypeError("Input must be a numpy array")
        
        m, n = a.shape
        result = np.zeros((n, m), dtype=np.float32)
        
        success = self.lib.fast_matrix_transpose(
            a.astype(np.float32, copy=False).ctypes.data_as(POINTER(c_float)),
            result.ctypes.data_as(POINTER(c_float)),
            m, n
        )
        if not success:
            raise RuntimeError("Matrix transpose failed")
        return result

class QuantumSimulator:
    def __init__(self):
        lib_path = Path(__file__).parent.parent.parent / 'cpp' / 'libquantum.so'
        if not lib_path.exists():
            raise FileNotFoundError(f"Library not found: {lib_path}")
        try:
            self.lib = ctypes.CDLL(str(lib_path))
            self._setup_functions()
        except Exception as e:
            raise RuntimeError(f"Failed to load library: {str(e)}")
    
    def _setup_functions(self) -> None:
        self.lib.quantum_evolve.argtypes = [
            POINTER(c_float), POINTER(c_float), c_int, c_float
        ]
        self.lib.quantum_evolve.restype = c_bool
        
        self.lib.quantum_measure.argtypes = [
            POINTER(c_float), POINTER(c_float), c_int
        ]
        self.lib.quantum_measure.restype = c_bool
        
        self.lib.quantum_entangle.argtypes = [
            POINTER(c_float), POINTER(c_float), c_int
        ]
        self.lib.quantum_entangle.restype = c_bool
        
        self.lib.quantum_fft.argtypes = [
            POINTER(c_float), POINTER(c_float), c_int
        ]
        self.lib.quantum_fft.restype = c_bool
    
    def evolve(self, state: np.ndarray, hamiltonian: np.ndarray, time: float) -> np.ndarray:
        if not isinstance(state, np.ndarray) or not isinstance(hamiltonian, np.ndarray):
            raise TypeError("Inputs must be numpy arrays")
        if state.shape[0] != hamiltonian.shape[0]:
            raise ValueError("State and Hamiltonian dimensions must match")
        if not isinstance(time, (int, float)) or time < 0:
            raise ValueError("Time must be a non-negative number")
        
        n = len(state)
        result = np.zeros(n, dtype=np.float32)
        
        success = self.lib.quantum_evolve(
            state.astype(np.float32, copy=False).ctypes.data_as(POINTER(c_float)),
            hamiltonian.astype(np.float32, copy=False).ctypes.data_as(POINTER(c_float)),
            n, float(time)
        )
        if not success:
            raise RuntimeError("Quantum evolution failed")
        return result
    
    def measure(self, state: np.ndarray) -> np.ndarray:
        if not isinstance(state, np.ndarray):
            raise TypeError("Input must be a numpy array")
        
        n = len(state)
        result = np.zeros(n, dtype=np.float32)
        
        success = self.lib.quantum_measure(
            state.astype(np.float32, copy=False).ctypes.data_as(POINTER(c_float)),
            result.ctypes.data_as(POINTER(c_float)),
            n
        )
        if not success:
            raise RuntimeError("Quantum measurement failed")
        return result
    
    def entangle(self, state1: np.ndarray, state2: np.ndarray) -> np.ndarray:
        if not isinstance(state1, np.ndarray) or not isinstance(state2, np.ndarray):
            raise TypeError("Inputs must be numpy arrays")
        if len(state1) != len(state2):
            raise ValueError("States must have same dimension for entanglement")
        
        n = len(state1)
        result = np.zeros(n, dtype=np.float32)
        
        success = self.lib.quantum_entangle(
            state1.astype(np.float32, copy=False).ctypes.data_as(POINTER(c_float)),
            state2.astype(np.float32, copy=False).ctypes.data_as(POINTER(c_float)),
            n
        )
        if not success:
            raise RuntimeError("Quantum entanglement failed")
        return result
    
    def fft(self, real: np.ndarray, imag: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        if not isinstance(real, np.ndarray) or not isinstance(imag, np.ndarray):
            raise TypeError("Inputs must be numpy arrays")
        if len(real) != len(imag):
            raise ValueError("Real and imaginary parts must have same length")
        
        n = len(real)
        result_real = np.zeros(n, dtype=np.float32)
        result_imag = np.zeros(n, dtype=np.float32)
        
        success = self.lib.quantum_fft(
            real.astype(np.float32, copy=False).ctypes.data_as(POINTER(c_float)),
            imag.astype(np.float32, copy=False).ctypes.data_as(POINTER(c_float)),
            n
        )
        if not success:
            raise RuntimeError("Quantum FFT failed")
        return result_real, result_imag

class ParallelOps:
    def __init__(self):
        lib_path = Path(__file__).parent.parent.parent / 'cpp' / 'libparallel.so'
        if not lib_path.exists():
            raise FileNotFoundError(f"Library not found: {lib_path}")
        try:
            self.lib = ctypes.CDLL(str(lib_path))
            self._setup_functions()
        except Exception as e:
            raise RuntimeError(f"Failed to load library: {str(e)}")
    
    def _setup_functions(self) -> None:
        self.lib.parallel_matrix_multiply.argtypes = [
            POINTER(c_float), POINTER(c_float), POINTER(c_float),
            c_int, c_int, c_int
        ]
        self.lib.parallel_matrix_multiply.restype = c_bool
        
        self.lib.parallel_vector_ops.argtypes = [
            POINTER(c_float), POINTER(c_float), POINTER(c_float),
            c_int, c_int
        ]
        self.lib.parallel_vector_ops.restype = c_bool
        
        self.lib.parallel_sort.argtypes = [
            POINTER(c_float), c_int
        ]
        self.lib.parallel_sort.restype = c_bool
        
        self.lib.parallel_reduce.argtypes = [
            POINTER(c_float), POINTER(c_float), c_int
        ]
        self.lib.parallel_reduce.restype = c_bool
        
        self.lib.parallel_scan.argtypes = [
            POINTER(c_float), POINTER(c_float), c_int
        ]
        self.lib.parallel_scan.restype = c_bool
    
    def matrix_multiply(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        if not isinstance(a, np.ndarray) or not isinstance(b, np.ndarray):
            raise TypeError("Inputs must be numpy arrays")
        if a.shape[1] != b.shape[0]:
            raise ValueError("Matrix dimensions incompatible for multiplication")
        
        m, n = a.shape
        n, p = b.shape
        result = np.zeros((m, p), dtype=np.float32)
        
        success = self.lib.parallel_matrix_multiply(
            a.astype(np.float32, copy=False).ctypes.data_as(POINTER(c_float)),
            b.astype(np.float32, copy=False).ctypes.data_as(POINTER(c_float)),
            result.ctypes.data_as(POINTER(c_float)),
            m, n, p
        )
        if not success:
            raise RuntimeError("Parallel matrix multiplication failed")
        return result
    
    def vector_ops(self, a: np.ndarray, b: np.ndarray, op: int) -> np.ndarray:
        if not isinstance(a, np.ndarray) or not isinstance(b, np.ndarray):
            raise TypeError("Inputs must be numpy arrays")
        if len(a) != len(b):
            raise ValueError("Vectors must have same length")
        if not isinstance(op, int) or op not in [0, 1, 2, 3]:
            raise ValueError("Operation must be 0 (add), 1 (subtract), 2 (multiply), or 3 (divide)")
        
        n = len(a)
        result = np.zeros(n, dtype=np.float32)
        
        success = self.lib.parallel_vector_ops(
            a.astype(np.float32, copy=False).ctypes.data_as(POINTER(c_float)),
            b.astype(np.float32, copy=False).ctypes.data_as(POINTER(c_float)),
            result.ctypes.data_as(POINTER(c_float)),
            n, op
        )
        if not success:
            raise RuntimeError("Parallel vector operation failed")
        return result
    
    def sort(self, arr: np.ndarray) -> np.ndarray:
        if not isinstance(arr, np.ndarray):
            raise TypeError("Input must be a numpy array")
        
        n = len(arr)
        result = arr.copy().astype(np.float32)
        
        success = self.lib.parallel_sort(
            result.ctypes.data_as(POINTER(c_float)),
            n
        )
        if not success:
            raise RuntimeError("Parallel sort failed")
        return result
    
    def reduce(self, arr: np.ndarray) -> float:
        if not isinstance(arr, np.ndarray):
            raise TypeError("Input must be a numpy array")
        
        n = len(arr)
        result = np.zeros(1, dtype=np.float32)
        
        success = self.lib.parallel_reduce(
            arr.astype(np.float32, copy=False).ctypes.data_as(POINTER(c_float)),
            result.ctypes.data_as(POINTER(c_float)),
            n
        )
        if not success:
            raise RuntimeError("Parallel reduce failed")
        return float(result[0])
    
    def scan(self, arr: np.ndarray) -> np.ndarray:
        if not isinstance(arr, np.ndarray):
            raise TypeError("Input must be a numpy array")
        
        n = len(arr)
        result = np.zeros(n, dtype=np.float32)
        
        success = self.lib.parallel_scan(
            arr.astype(np.float32, copy=False).ctypes.data_as(POINTER(c_float)),
            result.ctypes.data_as(POINTER(c_float)),
            n
        )
        if not success:
            raise RuntimeError("Parallel scan failed")
        return result

class NumericalOps:
    def __init__(self):
        lib_path = Path(__file__).parent.parent.parent / 'cpp' / 'libnumerical.so'
        if not lib_path.exists():
            raise FileNotFoundError(f"Library not found: {lib_path}")
        try:
            self.lib = ctypes.CDLL(str(lib_path))
            self._setup_functions()
        except Exception as e:
            raise RuntimeError(f"Failed to load library: {str(e)}")
    
    def _setup_functions(self) -> None:
        self.lib.fast_sin_cos.argtypes = [
            POINTER(c_float), POINTER(c_float), POINTER(c_float), c_int
        ]
        self.lib.fast_sin_cos.restype = c_bool
        
        self.lib.matrix_inverse.argtypes = [
            POINTER(c_float), POINTER(c_float), c_int
        ]
        self.lib.matrix_inverse.restype = c_bool
        
        self.lib.eigenvalues.argtypes = [
            POINTER(c_float), POINTER(c_float), c_int
        ]
        self.lib.eigenvalues.restype = c_bool
        
        self.lib.fft.argtypes = [
            POINTER(c_float), POINTER(c_float), c_int
        ]
        self.lib.fft.restype = c_bool
        
        self.lib.svd.argtypes = [
            POINTER(c_float), POINTER(c_float), POINTER(c_float),
            POINTER(c_float), c_int, c_int
        ]
        self.lib.svd.restype = c_bool
        
        self.lib.cholesky.argtypes = [
            POINTER(c_float), POINTER(c_float), c_int
        ]
        self.lib.cholesky.restype = c_bool
        
        self.lib.qr.argtypes = [
            POINTER(c_float), POINTER(c_float), POINTER(c_float),
            c_int, c_int
        ]
        self.lib.qr.restype = c_bool
    
    def sin_cos(self, angles: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        if not isinstance(angles, np.ndarray):
            raise TypeError("Input must be a numpy array")
        
        n = len(angles)
        sin_result = np.zeros(n, dtype=np.float32)
        cos_result = np.zeros(n, dtype=np.float32)
        
        success = self.lib.fast_sin_cos(
            angles.astype(np.float32, copy=False).ctypes.data_as(POINTER(c_float)),
            sin_result.ctypes.data_as(POINTER(c_float)),
            cos_result.ctypes.data_as(POINTER(c_float)),
            n
        )
        if not success:
            raise RuntimeError("Sin-cos computation failed")
        return sin_result, cos_result
    
    def matrix_inverse(self, a: np.ndarray) -> np.ndarray:
        if not isinstance(a, np.ndarray):
            raise TypeError("Input must be a numpy array")
        if a.shape[0] != a.shape[1]:
            raise ValueError("Matrix must be square for inversion")
        
        n = a.shape[0]
        result = np.zeros((n, n), dtype=np.float32)
        
        success = self.lib.matrix_inverse(
            a.astype(np.float32, copy=False).ctypes.data_as(POINTER(c_float)),
            result.ctypes.data_as(POINTER(c_float)),
            n
        )
        if not success:
            raise RuntimeError("Matrix inversion failed")
        return result
    
    def eigenvalues(self, a: np.ndarray) -> np.ndarray:
        if not isinstance(a, np.ndarray):
            raise TypeError("Input must be a numpy array")
        if a.shape[0] != a.shape[1]:
            raise ValueError("Matrix must be square for eigenvalue computation")
        
        n = a.shape[0]
        result = np.zeros(n, dtype=np.float32)
        
        success = self.lib.eigenvalues(
            a.astype(np.float32, copy=False).ctypes.data_as(POINTER(c_float)),
            result.ctypes.data_as(POINTER(c_float)),
            n
        )
        if not success:
            raise RuntimeError("Eigenvalue computation failed")
        return result
    
    def fft(self, real: np.ndarray, imag: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        if not isinstance(real, np.ndarray) or not isinstance(imag, np.ndarray):
            raise TypeError("Inputs must be numpy arrays")
        if len(real) != len(imag):
            raise ValueError("Real and imaginary parts must have same length")
        
        n = len(real)
        result_real = np.zeros(n, dtype=np.float32)
        result_imag = np.zeros(n, dtype=np.float32)
        
        success = self.lib.fft(
            real.astype(np.float32, copy=False).ctypes.data_as(POINTER(c_float)),
            imag.astype(np.float32, copy=False).ctypes.data_as(POINTER(c_float)),
            n
        )
        if not success:
            raise RuntimeError("FFT computation failed")
        return result_real, result_imag
    
    def svd(self, a: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        if not isinstance(a, np.ndarray):
            raise TypeError("Input must be a numpy array")
        
        m, n = a.shape
        u = np.zeros((m, m), dtype=np.float32)
        s = np.zeros(min(m, n), dtype=np.float32)
        v = np.zeros((n, n), dtype=np.float32)
        
        success = self.lib.svd(
            a.astype(np.float32, copy=False).ctypes.data_as(POINTER(c_float)),
            u.ctypes.data_as(POINTER(c_float)),
            s.ctypes.data_as(POINTER(c_float)),
            v.ctypes.data_as(POINTER(c_float)),
            m, n
        )
        if not success:
            raise RuntimeError("SVD computation failed")
        return u, s, v
    
    def cholesky(self, a: np.ndarray) -> np.ndarray:
        if not isinstance(a, np.ndarray):
            raise TypeError("Input must be a numpy array")
        if a.shape[0] != a.shape[1]:
            raise ValueError("Matrix must be square for Cholesky decomposition")
        
        n = a.shape[0]
        result = np.zeros((n, n), dtype=np.float32)
        
        success = self.lib.cholesky(
            a.astype(np.float32, copy=False).ctypes.data_as(POINTER(c_float)),
            result.ctypes.data_as(POINTER(c_float)),
            n
        )
        if not success:
            raise RuntimeError("Cholesky decomposition failed")
        return result
    
    def qr(self, a: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        if not isinstance(a, np.ndarray):
            raise TypeError("Input must be a numpy array")
        
        m, n = a.shape
        q = np.zeros((m, m), dtype=np.float32)
        r = np.zeros((m, n), dtype=np.float32)
        
        success = self.lib.qr(
            a.astype(np.float32, copy=False).ctypes.data_as(POINTER(c_float)),
            q.ctypes.data_as(POINTER(c_float)),
            r.ctypes.data_as(POINTER(c_float)),
            m, n
        )
        if not success:
            raise RuntimeError("QR decomposition failed")
        return q, r

class AssemblyOps:
    def __init__(self):
        lib_path = Path(__file__).parent.parent.parent / 'cpp' / 'libassembly.so'
        if not lib_path.exists():
            raise FileNotFoundError(f"Library not found: {lib_path}")
        try:
            self.lib = ctypes.CDLL(str(lib_path))
            self._setup_functions()
        except Exception as e:
            raise RuntimeError(f"Failed to load library: {str(e)}")
    
    def _setup_functions(self) -> None:
        self.lib.dot_product.argtypes = [
            POINTER(c_float), POINTER(c_float), c_int
        ]
        self.lib.dot_product.restype = c_float
        
        self.lib.matrix_transpose.argtypes = [
            POINTER(c_float), POINTER(c_float), c_int, c_int
        ]
        self.lib.matrix_transpose.restype = c_bool
        
        self.lib.vector_norm.argtypes = [
            POINTER(c_float), c_int
        ]
        self.lib.vector_norm.restype = c_float
        
        self.lib.convolution.argtypes = [
            POINTER(c_float), POINTER(c_float), POINTER(c_float),
            c_int, c_int, c_int, c_int
        ]
        self.lib.convolution.restype = c_bool
    
    def dot_product(self, a: np.ndarray, b: np.ndarray) -> float:
        if not isinstance(a, np.ndarray) or not isinstance(b, np.ndarray):
            raise TypeError("Inputs must be numpy arrays")
        if len(a) != len(b):
            raise ValueError("Vectors must have same length for dot product")
        
        n = len(a)
        return float(self.lib.dot_product(
            a.astype(np.float32, copy=False).ctypes.data_as(POINTER(c_float)),
            b.astype(np.float32, copy=False).ctypes.data_as(POINTER(c_float)),
            n
        ))
    
    def matrix_transpose(self, a: np.ndarray) -> np.ndarray:
        if not isinstance(a, np.ndarray):
            raise TypeError("Input must be a numpy array")
        
        m, n = a.shape
        result = np.zeros((n, m), dtype=np.float32)
        
        success = self.lib.matrix_transpose(
            a.astype(np.float32, copy=False).ctypes.data_as(POINTER(c_float)),
            result.ctypes.data_as(POINTER(c_float)),
            m, n
        )
        if not success:
            raise RuntimeError("Matrix transpose failed")
        return result
    
    def vector_norm(self, a: np.ndarray) -> float:
        if not isinstance(a, np.ndarray):
            raise TypeError("Input must be a numpy array")
        
        n = len(a)
        return float(self.lib.vector_norm(
            a.astype(np.float32, copy=False).ctypes.data_as(POINTER(c_float)),
            n
        ))
    
    def convolution(self, input_data: np.ndarray, kernel: np.ndarray) -> np.ndarray:
        if not isinstance(input_data, np.ndarray) or not isinstance(kernel, np.ndarray):
            raise TypeError("Inputs must be numpy arrays")
        if len(input_data.shape) != 2 or len(kernel.shape) != 2:
            raise ValueError("Input data and kernel must be 2D arrays")
        
        m, n = input_data.shape
        k_m, k_n = kernel.shape
        result = np.zeros((m - k_m + 1, n - k_n + 1), dtype=np.float32)
        
        success = self.lib.convolution(
            input_data.astype(np.float32, copy=False).ctypes.data_as(POINTER(c_float)),
            kernel.astype(np.float32, copy=False).ctypes.data_as(POINTER(c_float)),
            result.ctypes.data_as(POINTER(c_float)),
            m, n, k_m, k_n
        )
        if not success:
            raise RuntimeError("Convolution failed")
        return result 