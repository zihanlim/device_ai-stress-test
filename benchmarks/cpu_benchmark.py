#!/usr/bin/env python3
"""
CPU Benchmark - Single & Multi-core Performance
Run directly: python3 cpu_benchmark.py [results_dir]
"""
import time
import numpy as np
import sys
import os
import multiprocessing

def fib_iterative(n):
    if n < 2: return n
    a, b = 0, 1
    for _ in range(n-1):
        a, b = b, a + b
    return b

def sieve(n):
    sieve = [True] * (n+1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(n**0.5)+1):
        if sieve[i]:
            for j in range(i*i, n+1, i):
                sieve[j] = False
    return sum(sieve)

def is_prime(n):
    if n < 2: return False
    if n == 2: return True
    if n % 2 == 0: return False
    for i in range(3, int(n**0.5)+1, 2):
        if n % i == 0: return False
    return True

def chunk_range(args):
    start, end = args
    return sum(1 for i in range(start, end) if is_prime(i))

def run_sieve_parallel(n, cores):
    chunk_size = n // cores
    ranges = [(i*chunk_size, (i+1)*chunk_size) for i in range(cores)]
    if n % cores != 0:
        ranges[-1] = (ranges[-1][0], n)

    with multiprocessing.Pool(processes=cores) as pool:
        results = pool.map(chunk_range, ranges)

    return sum(results)

# Module-level function for multiprocessing (must be picklable)
def run_fib_chunk(args):
    start, end = args
    count = 0
    for n in range(start, end):
        count += fib_iterative(n)
    return count

def main():
    if len(sys.argv) < 2:
        results_dir = os.path.dirname(os.path.abspath(__file__)) + '/../results'
    else:
        results_dir = sys.argv[1]

    CPU_DATA = os.path.join(results_dir, 'cpu_data.txt')

    # Clear/create CPU data file
    with open(CPU_DATA, "w") as f:
        f.write("test,value,unit\n")

    print("--- Single-threaded Performance ---")

    # Fibonacci benchmark
    for n in [100000, 500000, 1000000]:
        start = time.time()
        fib_iterative(n)
        t = time.time() - start
        print(f"Fibonacci({n}): {t:.4f}s")
        with open(CPU_DATA, "a") as f:
            f.write(f"Fibonacci({n}),{t:.6f},s\n")

    print("")

    # Prime sieve benchmark
    for n in [100000, 500000, 1000000]:
        start = time.time()
        count = sieve(n)
        t = time.time() - start
        print(f"Sieve({n}): {t:.4f}s ({count} primes)")
        with open(CPU_DATA, "a") as f:
            f.write(f"Sieve({n}),{t:.6f},s\n")

    print("")
    print("--- Multi-core Scaling Test ---")

    # Multi-core scaling test
    n = 5000000
    available_cores = multiprocessing.cpu_count()

    # Single core baseline
    print("Running single-core baseline...")
    start = time.time()
    sum(is_prime(i) for i in range(n))
    single_core_time = time.time() - start
    print(f"  Single-core (n={n}): {single_core_time:.2f}s")
    with open(CPU_DATA, "a") as f:
        f.write(f"SingleCore_Time,{single_core_time:.6f},s\n")

    # Multi-core tests - test ALL core configurations: 1, 2, 4, 6, 8, 10
    for cores in [1, 2, 4, 6, 8, 10]:
        if cores > available_cores:
            continue
        print(f"Running {cores}-core test...")

        # Use is_prime (same as single-core baseline) for consistent comparison
        n_tasks = 5000000  # Same workload as single-core baseline

        start = time.time()
        if cores == 1:
            # Single process - same as baseline
            result = sum(1 for i in range(n_tasks) if is_prime(i))
        else:
            # Multi-process using pool
            chunk_size = n_tasks // cores
            ranges = [(i*chunk_size, (i+1)*chunk_size) for i in range(cores)]
            if n_tasks % cores != 0:
                ranges[-1] = (ranges[-1][0], n_tasks)
            with multiprocessing.Pool(processes=cores) as pool:
                results = pool.map(chunk_range, ranges)
            result = sum(results)
        elapsed = time.time() - start

        speedup = single_core_time / elapsed
        efficiency = (speedup / cores) * 100

        print(f"  {cores}-core: {elapsed:.2f}s (speedup: {speedup:.2f}x, efficiency: {efficiency:.0f}%)")
        with open(CPU_DATA, "a") as f:
            f.write(f"MultiCore_{cores}C_Time,{elapsed:.6f},s\n")
            f.write(f"MultiCore_{cores}C_Speedup,{speedup:.4f},x\n")
            f.write(f"MultiCore_{cores}C_Efficiency,{efficiency:.2f},%\n")

    print("")
    print("--- ML Workload Simulation ---")

    # Matrix multiplication benchmark
    for size in [512, 1024, 2048]:
        x = np.random.rand(size, size).astype(np.float32)
        y = np.random.rand(size, size).astype(np.float32)

        # Warmup
        for _ in range(3):
            np.dot(x, y)

        # Benchmark
        iterations = 50 if size <= 1024 else 10
        start = time.time()
        for _ in range(iterations):
            z = np.dot(x, y)
        elapsed = time.time() - start

        t_ms = elapsed / iterations * 1000
        tflops = (size * size * size * 2 * iterations) / elapsed / 1e12

        print(f"MatMul {size}x{size}: {t_ms:.2f} ms/op ({tflops:.2f} TFLOPS)")
        with open(CPU_DATA, "a") as f:
            f.write(f"MatMul_{size},{t_ms:.4f},ms\n")
            f.write(f"MatMul_{size}_TFLOPS,{tflops:.4f},TFLOPS\n")

    print("")
    print("CPU Benchmark complete. Data saved to:", CPU_DATA)

if __name__ == '__main__':
    main()