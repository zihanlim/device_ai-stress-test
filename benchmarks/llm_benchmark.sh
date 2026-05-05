#!/bin/bash
# LLM Benchmark - Local AI Inference with Ollama
set -e

RESULTS_DIR="${1:-../results}"
PLOT_DIR="$RESULTS_DIR/plots"
mkdir -p "$RESULTS_DIR/plots"

echo "=== LLM Benchmark ===" | tee "$RESULTS_DIR/llm_benchmark.txt"

# Check Ollama
if ! command -v ollama &> /dev/null; then
    echo "ERROR: Ollama not installed. Install with: brew install ollama"
    exit 1
fi

echo "Ollama version: $(ollama --version)" | tee -a "$RESULTS_DIR/llm_benchmark.txt"
echo "" | tee -a "$RESULTS_DIR/llm_benchmark.txt"

# Run the Python benchmark
python3 "${BASH_SOURCE%/*}/llm_benchmark.py" "$RESULTS_DIR" 2>&1 | tee -a "$RESULTS_DIR/llm_benchmark.txt"

echo "" | tee -a "$RESULTS_DIR/llm_benchmark.txt"
echo "LLM Benchmark complete" | tee -a "$RESULTS_DIR/llm_benchmark.txt"
