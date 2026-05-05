#!/bin/bash
# Memory Benchmark - Bandwidth, Capacity, and Pressure
set -e

RESULTS_DIR="${1:-../results}"
PLOT_DIR="$RESULTS_DIR/plots"
mkdir -p "$RESULTS_DIR/plots"

echo "=== Memory Benchmark ===" | tee "$RESULTS_DIR/memory_benchmark.txt"

# System info
echo "--- System Memory Info ---" | tee -a "$RESULTS_DIR/memory_benchmark.txt"
echo "Total Memory: $(sysctl -n hw.memsize | awk '{printf "%.1f GB", $1/1024/1024/1024}')" | tee -a "$RESULTS_DIR/memory_benchmark.txt"
echo "Page Size: $(sysctl -n hw.pagesize) bytes" | tee -a "$RESULTS_DIR/memory_benchmark.txt"
echo "" | tee -a "$RESULTS_DIR/memory_benchmark.txt"

# Run the Python benchmark
python3 "${BASH_SOURCE%/*}/memory_benchmark.py" "$RESULTS_DIR" 2>&1 | tee -a "$RESULTS_DIR/memory_benchmark.txt"

echo "" | tee -a "$RESULTS_DIR/memory_benchmark.txt"
echo "Memory Benchmark complete" | tee -a "$RESULTS_DIR/memory_benchmark.txt"