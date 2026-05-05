#!/bin/bash
# Main Benchmark Runner - AI Engineering Device Assessment
# Usage: ./run_all_benchmarks.sh [results_dir] [device_name] [device_tag]

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
RESULTS_DIR="${1:-$SCRIPT_DIR/results/$(date +%Y%m%d_%H%M%S)}"
DEVICE_NAME="${2:-$(hostname)}"
DEVICE_TAG="${3:-MacBookAir-M5}"

mkdir -p "$RESULTS_DIR/plots"

echo "=============================================="
echo "  AI Engineering Device Benchmark Suite"
echo "=============================================="
echo ""
echo "Device: $DEVICE_NAME"
echo "Tag: $DEVICE_TAG"
echo "Results: $RESULTS_DIR"
echo "Started: $(date)"
echo ""

# Export results dir for child scripts
export RESULTS_DIR

# Run all benchmarks
echo "Running CPU Benchmark..."
bash "$SCRIPT_DIR/benchmarks/cpu_benchmark.sh" "$RESULTS_DIR"

echo ""
echo "Running Memory Benchmark..."
bash "$SCRIPT_DIR/benchmarks/memory_benchmark.sh" "$RESULTS_DIR"

echo ""
echo "Running Storage Benchmark..."
bash "$SCRIPT_DIR/benchmarks/storage_benchmark.sh" "$RESULTS_DIR"

echo ""
echo "Running Core ML/Neural Engine Benchmark..."
bash "$SCRIPT_DIR/benchmarks/coreml_benchmark.sh" "$RESULTS_DIR"

echo ""
echo "Running Thermal Throttling Benchmark..."
bash "$SCRIPT_DIR/benchmarks/thermal_benchmark.sh" "$RESULTS_DIR"

echo ""
echo "Running LLM Inference Benchmark..."
bash "$SCRIPT_DIR/benchmarks/llm_benchmark.sh" "$RESULTS_DIR"

echo ""
echo "Running Memory Pressure Benchmark..."
bash "$SCRIPT_DIR/benchmarks/memory_pressure_benchmark.sh" "$RESULTS_DIR"

echo ""
echo "Running Daily Usage Benchmark..."
bash "$SCRIPT_DIR/benchmarks/daily_usage_benchmark.sh" "$RESULTS_DIR"

echo ""
echo "Running Geekbench AI Benchmark..."
if python3 "$SCRIPT_DIR/benchmarks/geekbench_ai_benchmark.py" "$RESULTS_DIR" 2>&1 | tee -a "$RESULTS_DIR/geekbench_ai.log"; then
    echo "Geekbench AI: Completed"
else
    echo "Geekbench AI: Skipped (not installed)"
fi

echo ""
echo "=============================================="
echo "  Generating Summary Report"
echo "=============================================="

# Capture key metrics
PHYSICAL_CORES=$(sysctl -n hw.physicalcpu)
LOGICAL_CORES=$(sysctl -n hw.logicalcpu)
TOTAL_MEM=$(sysctl -n hw.memsize)
TOTAL_GB=$(python3 -c "print(round($TOTAL_MEM / 1024**3, 1))")
MODEL=$(sysctl -n hw.model)
CHIP=$(sysctl -n machdep.cpu.brand_string)

# Generate summary JSON
cat > "$RESULTS_DIR/summary.json" << EOF
{
    "device": {
        "name": "$DEVICE_NAME",
        "tag": "$DEVICE_TAG",
        "hostname": "$(hostname)",
        "date": "$(date -Iseconds)",
        "os": "$(sw_vers -productVersion 2>/dev/null || echo 'Unknown')"
    },
    "hardware": {
        "model": "$MODEL",
        "chip": "$CHIP",
        "physical_cores": $PHYSICAL_CORES,
        "logical_cores": $LOGICAL_CORES,
        "memory_gb": $TOTAL_GB,
        "memory_mb": $(python3 -c "print(int($TOTAL_MEM / 1024 / 1024))")
    }
}
EOF

# Generate comprehensive report from real data
python3 "$SCRIPT_DIR/scripts/generate_report.py" "$RESULTS_DIR"

echo ""
echo "=============================================="
echo "  Benchmark Complete"
echo "=============================================="
echo ""
echo "Results saved to: $RESULTS_DIR"
echo ""
echo "Files created:"
ls -la "$RESULTS_DIR"
echo ""
echo "Plots:"
ls -la "$RESULTS_DIR/plots" 2>/dev/null || echo "  (no plots yet)"
echo ""
echo "Summary JSON: $RESULTS_DIR/summary.json"
echo "Report: $RESULTS_DIR/REPORT.md"