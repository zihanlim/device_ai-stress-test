#!/bin/bash
# Thermal Throttling Benchmark - Redesigned
# Tests CPU frequency and performance maintenance under sustained multi-core load
# Shows how thermal throttling affects performance at different core counts

RESULTS_DIR="${1:-../results}"
PLOT_DIR="$RESULTS_DIR/plots"
mkdir -p "$RESULTS_DIR/plots"

echo "=== Thermal Throttling Benchmark (Redesigned) ===" | tee "$RESULTS_DIR/thermal_benchmark.txt"

THERMAL_DATA="$RESULTS_DIR/thermal_data.txt"

# System info
echo "--- System Info ---" | tee -a "$RESULTS_DIR/thermal_benchmark.txt"
echo "Model: $(sysctl -n hw.model)" | tee -a "$RESULTS_DIR/thermal_benchmark.txt"
echo "Chip: $(sysctl -n machdep.cpu.brand_string)" | tee -a "$RESULTS_DIR/thermal_benchmark.txt"
echo "Physical Cores: $(sysctl -n hw.physicalcpu)" | tee -a "$RESULTS_DIR/thermal_benchmark.txt"
echo "" | tee -a "$RESULTS_DIR/thermal_benchmark.txt"

# Clear previous data
echo "test,value,unit" > "$THERMAL_DATA"

# Write Python script - using threading not multiprocessing (avoid fork issues in bash)
python3 - "$RESULTS_DIR" << 'PYEOF'
import time
import threading
import sys
import os
from collections import deque

RESULTS_DIR = sys.argv[1]

def cpu_intensive_work(duration_s, result_list, idx):
    """Do sustained CPU work and report performance metrics"""
    start_time = time.time()
    iterations = 0
    operation_times = []

    while time.time() - start_time < duration_s:
        iter_start = time.time()

        # CPU-intensive integer work (not floating point, more representative of general compute)
        total = 0
        for i in range(500000):
            total += i * 17 % 31

        iter_time = time.time() - iter_start
        operation_times.append(iter_time * 1000)  # Convert to ms
        iterations += 1

    result_list[idx] = operation_times

def run_thermal_test(num_threads, duration_s=120):
    """Run thermal test with specified number of threads for duration"""
    print(f"\n--- Testing {num_threads} thread(s) for {duration_s}s ---")

    # Use threads since we're in a bash heredoc and can't use fork safely
    result_list = [None] * num_threads
    threads = []

    # Start worker threads
    for i in range(num_threads):
        t = threading.Thread(target=cpu_intensive_work, args=(duration_s, result_list, i))
        t.start()
        threads.append(t)

    # Wait for all threads
    for t in threads:
        t.join()

    # Analyze results
    all_times = []
    for times in result_list:
        if times:
            all_times.extend(times)

    # Divide into time windows (first 10s, middle, end)
    n = len(all_times)
    window_size = min(n // 3, 100)

    early_avg = sum(all_times[:window_size]) / window_size if window_size > 0 else 0
    mid_avg = sum(all_times[n//3:n//3+window_size]) / window_size if window_size > 0 else 0
    late_avg = sum(all_times[-window_size:]) / window_size if window_size > 0 else 0

    print(f"  Early ({duration_s//3}s): {early_avg:.2f} ms/op")
    print(f"  Mid ({duration_s//3*2}s): {mid_avg:.2f} ms/op")
    print(f"  Late ({duration_s}s): {late_avg:.2f} ms/op")

    if early_avg > 0:
        degradation = (1 - late_avg / early_avg) * 100
        print(f"  Thermal degradation: {degradation:.1f}%")

    return {
        'threads': num_threads,
        'early': early_avg,
        'mid': mid_avg,
        'late': late_avg,
        'degradation': degradation if early_avg > 0 else 0
    }

# Run tests for different thread counts (2, 4, 6, 8, 10)
results = []

for threads in [2, 4, 6, 8, 10]:
    try:
        result = run_thermal_test(threads, duration_s=120)
        results.append(result)
    except Exception as e:
        print(f"Error testing {threads} threads: {e}")

# Save results
THERMAL_DATA = os.path.join(RESULTS_DIR, "thermal_data.txt")

with open(THERMAL_DATA, "w") as f:
    f.write("test,value,unit\n")

    for r in results:
        f.write(f"thermal_{r['threads']}t_early,{r['early']:.4f},ms\n")
        f.write(f"thermal_{r['threads']}t_mid,{r['mid']:.4f},ms\n")
        f.write(f"thermal_{r['threads']}t_late,{r['late']:.4f},ms\n")
        f.write(f"thermal_{r['threads']}t_degradation,{r['degradation']:.2f},%\n")

print(f"\nData saved to: {THERMAL_DATA}")
PYEOF

echo "" | tee -a "$RESULTS_DIR/thermal_benchmark.txt"
echo "Thermal Throttling Benchmark complete" | tee -a "$RESULTS_DIR/thermal_benchmark.txt"