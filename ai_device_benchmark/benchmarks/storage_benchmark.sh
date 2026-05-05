#!/bin/bash
# Storage Benchmark - Disk I/O Performance
set -e

RESULTS_DIR="${1:-../results}"
mkdir -p "$RESULTS_DIR"

echo "=== Storage Benchmark ===" | tee "$RESULTS_DIR/storage_benchmark.txt"

# Storage info
echo "--- Storage Info ---" | tee -a "$RESULTS_DIR/storage_benchmark.txt"
echo "Total Disk: $(df -h / | tail -1 | awk '{print $2}')" | tee -a "$RESULTS_DIR/storage_benchmark.txt"
echo "Available: $(df -h / | tail -1 | awk '{print $4}')" | tee -a "$RESULTS_DIR/storage_benchmark.txt"
echo "" | tee -a "$RESULTS_DIR/storage_benchmark.txt"

# Create test file
TEST_FILE="/tmp/ai_benchmark_io_test_$$"
TEST_DIR="$HOME/ai_benchmark_results"
mkdir -p "$TEST_DIR"

# Sequential write test
echo "--- Sequential Write Test ---" | tee -a "$RESULTS_DIR/storage_benchmark.txt"
for block_size in 1m 10m; do
    echo "Testing with block size: $block_size" | tee -a "$RESULTS_DIR/storage_benchmark.txt"
    # Write test
    START=$(date +%s.%N)
    dd if=/dev/zero of="$TEST_FILE" bs=$block_size count=100 conv=fsync 2>&1
    END=$(date +%s.%N)
    WRITE_TIME=$(echo "$END - $START" | bc)
    WRITE_BW=$(echo "scale=2; 100 * 1 / $WRITE_TIME" | bc)
    echo "Write speed: ~${WRITE_BW} MB/s" | tee -a "$RESULTS_DIR/storage_benchmark.txt"
done

# Sequential read test
echo "" | tee -a "$RESULTS_DIR/storage_benchmark.txt"
echo "--- Sequential Read Test ---" | tee -a "$RESULTS_DIR/storage_benchmark.txt"
START=$(date +%s.%N)
dd if="$TEST_FILE" of=/dev/null bs=1m count=100 2>&1
END=$(date +%s.%N)
READ_TIME=$(echo "$END - $START" | bc)
READ_BW=$(echo "scale=2; 100 * 1 / $READ_TIME" | bc)
echo "Read speed: ~${READ_BW} MB/s" | tee -a "$RESULTS_DIR/storage_benchmark.txt"

# Random I/O test (using a smaller file for speed)
echo "" | tee -a "$RESULTS_DIR/storage_benchmark.txt"
echo "--- Random I/O Test (4K blocks) ---" | tee -a "$RESULTS_DIR/storage_benchmark.txt"
START=$(date +%s.%N)
dd if=/dev/urandom of="$TEST_FILE" bs=4k count=10000 2>&1
END=$(date +%s.%N)
RAND_TIME=$(echo "$END - $START" | bc)
echo "Random write (4K): ~$(echo "scale=2; 10000 * 4 / 1024 / $RAND_TIME" | bc) MB/s" | tee -a "$RESULTS_DIR/storage_benchmark.txt"

# Large file model loading simulation
echo "" | tee -a "$RESULTS_DIR/storage_benchmark.txt"
echo "--- Model Loading Simulation ---" | tee -a "$RESULTS_DIR/storage_benchmark.txt"
# Simulate loading a 4GB model file (typical LLM model size)
MODEL_SIZE_MB=4096
echo "Simulating load of ${MODEL_SIZE_MB} MB file..." | tee -a "$RESULTS_DIR/storage_benchmark.txt"

# Create large file for read test
dd if=/dev/zero of="$TEST_DIR/large_model.bin" bs=1m count=200 2>/dev/null

START=$(date +%s.%N)
cat "$TEST_DIR/large_model.bin" > /dev/null 2>&1
END=$(date +%s.%N)
LOAD_TIME=$(echo "$END - $START" | bc)
LOAD_BW=$(echo "scale=2; 200 / $LOAD_TIME" | bc)
echo "Model file (200 MB sample) load time: ${LOAD_TIME}s" | tee -a "$RESULTS_DIR/storage_benchmark.txt"
echo "Estimated ${MODEL_SIZE_MB} MB load time: ~$(echo "scale=1; $MODEL_SIZE_MB / 1024 * $LOAD_TIME / 200" | bc)s" | tee -a "$RESULTS_DIR/storage_benchmark.txt"

# Cleanup
rm -f "$TEST_FILE" "$TEST_DIR/large_model.bin"

echo "" | tee -a "$RESULTS_DIR/storage_benchmark.txt"
echo "Storage Benchmark complete" | tee -a "$RESULTS_DIR/storage_benchmark.txt"