#!/bin/bash
# CPU Benchmark - Single & Multi-core Performance
set -e

RESULTS_DIR="${1:-../results}"
PLOT_DIR="$RESULTS_DIR/plots"
mkdir -p "$RESULTS_DIR/plots"

echo "=== CPU Benchmark ===" | tee "$RESULTS_DIR/cpu_benchmark.txt"

# System info
echo "--- System Info ---" | tee -a "$RESULTS_DIR/cpu_benchmark.txt"
echo "Model: $(sysctl -n hw.model)" | tee -a "$RESULTS_DIR/cpu_benchmark.txt"
echo "CPU Brand: $(sysctl -n machdep.cpu.brand_string)" | tee -a "$RESULTS_DIR/cpu_benchmark.txt"
echo "Physical Cores: $(sysctl -n hw.physicalcpu)" | tee -a "$RESULTS_DIR/cpu_benchmark.txt"
echo "Logical Cores: $(sysctl -n hw.logicalcpu)" | tee -a "$RESULTS_DIR/cpu_benchmark.txt"
echo "L2 Cache: $(sysctl -n hw.l2cachesize | awk '{printf "%.1f MB", $1/1024/1024}')" | tee -a "$RESULTS_DIR/cpu_benchmark.txt"
echo "L3 Cache: $(sysctl -n hw.l3cachesize | awk '{printf "%.1f MB", $1/1024/1024}')" | tee -a "$RESULTS_DIR/cpu_benchmark.txt"
echo "" | tee -a "$RESULTS_DIR/cpu_benchmark.txt"

# Run the Python benchmark directly
python3 "${BASH_SOURCE%/*}/cpu_benchmark.py" "$RESULTS_DIR" 2>&1 | tee -a "$RESULTS_DIR/cpu_benchmark.txt"

echo "" | tee -a "$RESULTS_DIR/cpu_benchmark.txt"
echo "CPU Benchmark complete" | tee -a "$RESULTS_DIR/cpu_benchmark.txt"