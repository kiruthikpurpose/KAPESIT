import functools
import time
import logging
from typing import Callable, Any

def timer(func: Callable) -> Callable:
    """Decorator to measure function execution time."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        logging.info(f"{func.__name__} executed in {execution_time:.4f} seconds")
        return result
    return wrapper

def validate_input(*types: type) -> Callable:
    """Decorator to validate input types."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            if len(args) != len(types):
                raise TypeError("Number of arguments doesn't match expected types")
            for arg, t in zip(args, types):
                if not isinstance(arg, t):
                    raise TypeError(f"Expected {t.__name__}, got {type(arg).__name__}")
            return func(*args, **kwargs)
        return wrapper
    return decorator

def retry(max_retries: int = 3, delay: float = 1.0) -> Callable:
    """Decorator to retry function execution on failure."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    time.sleep(delay)
            return None
        return wrapper
    return decorator
