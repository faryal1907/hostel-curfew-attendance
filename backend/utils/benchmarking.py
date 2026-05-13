import time
import functools

def benchmark_timer(func):
    """Decorator that prints the execution time of the function it decorates."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        run_time = (end_time - start_time) * 1000 # Convert to ms
        print(f"DEBUG: [Benchmark] {func.__name__!r} took {run_time:.2f}ms")
        return result
    return wrapper
