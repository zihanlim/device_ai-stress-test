#!/bin/bash
# Geekbench AI Benchmark
# Downloads and runs Geekbench AI to measure NPU/CPU/GPU AI performance
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
RESULTS_DIR="${1:-$SCRIPT_DIR/../results}"
mkdir -p "$RESULTS_DIR"

GEEKBENCH_URL="https://www.geekbench.com/download/"
GEEKBENCH_AI="$RESULTS_DIR/geekbench_ai"

echo "=== Geekbench AI Benchmark ==="
echo "Results directory: $RESULTS_DIR"

# Check if geekbench6 is available
if command -v geekbench6 &> /dev/null; then
    echo "Found geekbench6 in PATH"
    GEEKBENCH_CMD="geekbench6"
elif [ -d "/Applications/Geekbench 6" ]; then
    echo "Found Geekbench 6 app"
    GEEKBENCH_CMD="/Applications/Geekbench 6.app/Contents/MacOS/geekbench6"
elif [ -f "$GEEKBENCH_AI" ]; then
    chmod +x "$GEEKBENCH_AI"
    GEEKBENCH_CMD="$GEEKBENCH_AI"
else
    echo "Geekbench AI not found. Please install from: https://www.geekbench.com/download/"
    echo "Or run: brew install --cask geekbench"
    exit 1
fi

# Run Geekbench AI benchmark
echo ""
echo "Running Geekbench AI benchmark..."
echo "This measures: CPU AI Score, GPU AI Score (where applicable)"
echo ""

if ! "$GEEKBENCH_CMD" ai --metal --csv 2>/dev/null; then
    # Try without metal flag if running on Mac without discrete GPU
    echo "Trying OpenCL/Compute benchmark..."
    "$GEEKBENCH_CMD" ai --csv 2>/dev/null || true
fi

# Also try the standard geekbench6 command structure
OUTPUT=$("$GEEKBENCH_CMD" 2>&1 || true)
echo "$OUTPUT"

# Try to parse results if available
RESULTS_FILE="$RESULTS_DIR/geekbench_ai_results.txt"
"$GEEKBENCH_CMD" --export-json "$RESULTS_DIR/geekbench_ai.json" 2>/dev/null || true

if [ -f "$RESULTS_DIR/geekbench_ai.json" ]; then
    echo ""
    echo "JSON results saved to: $RESULTS_DIR/geekbench_ai.json"
fi

echo ""
echo "Geekbench AI benchmark complete."