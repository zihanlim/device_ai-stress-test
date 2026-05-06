# AI Engineering Device Benchmark Suite

A portable benchmark suite for assessing hardware suitability for AI engineering workloads on MacBook Air/Pro and Mac Studio devices.

**Primary Use Case:** Determine if a MacBook is suitable for API-based AI engineering (Claude API, Coding Plans) and local LLM inference.

<div style="border: 2px solid black; border-radius: 8px; padding: 16px; margin: 16px 0;">

## Device Results

This repo contains benchmark results for multiple devices. Each device has its own report in `results/[DeviceName]/`.

| Device | Memory | Verdict |
|--------|--------|---------|
| **MacBook Air M5 (16GB)** | 16GB | ✅ Excellent for API workflows, adequate for local 8B |
| **MacBook Neo A18Pro (8GB)** | 8GB | ⚠️ Borderline for API workflows, limited to 1.7B local |

For full device-specific reports, see:
- [MacBook Air M5 Results](results/MacBookAirM5/REPORT.md)
- [MacBook Neo A18Pro Results](results/MacBookNeo-A18Pro/REPORT.md)

### Quick Comparison

| Factor | MacBook Air M5 (16GB) | MacBook Neo A18Pro (8GB) |
|--------|----------------------|--------------------------|
| Memory headroom | ✅ Comfortable | ⚠️ Tight |
| Local LLM | Up to 8B | Up to 1.7B |
| Docker | ⚠️ Tight (8-12GB) | ❌ Not recommended |
| CPU single-core | 8.9s (Fibonacci) | 9.95s (Fibonacci) |
| Storage | 14 GB/s read | 11.4 GB/s read |
| Thermal | ≤6% throttling | ≤8% throttling |

**Key insight:** The Neo A18Pro chip is functionally similar to iPhone 16 Pro (same silicon). Neo wins on sustained workloads due to better cooling and larger battery.

</div>

---

## Quick Start

```bash
# Run all benchmarks (foreground - shows output, ~25 min)
./run_all_benchmarks.sh results/ "MacBook-Air-M5" "Engineering-Dept"

# Run in background (free terminal, log to file)
nohup ./run_all_benchmarks.sh results/ "MacBook-Air-M5" "Engineering-Dept" > benchmark_run.log 2>&1 &
tail -f benchmark_run.log

# Generate plots from existing results
python3 scripts/generate_plots.py results/
```

## What Gets Tested

| Benchmark | Measures | Duration |
|-----------|----------|----------|
| CPU | Fibonacci, Prime Sieve, Matrix Multiply, Multi-core scaling | ~30s |
| Memory | Bandwidth, allocation speed, pressure behavior | ~30s |
| Storage | Sequential read/write, random I/O | ~1min |
| Core ML | Neural Engine (ANE) matrix operations | ~30s |
| Thermal | Performance over 5-min sustained load | ~5min |
| LLM | Qwen3 models (0.6B-14B) via Ollama | ~15min |
| Geekbench AI | NPU/CPU/GPU AI scores (if installed) | ~5min |
| Daily Usage | Cold/hot start, workflow simulation | ~2min |

**Total runtime:** ~25 minutes

## Prerequisites

```bash
# Required
pip3 install numpy matplotlib seaborn

# For LLM benchmarks (optional)
brew install ollama
ollama serve

# For Core ML / Neural Engine benchmarks (optional)
pip3 install coremltools

# For Geekbench AI (optional - download from https://www.geekbench.com/download/)
```

## Output

```
results/
├── REPORT.md                    # Human-readable summary
├── summary.json                 # Machine-readable summary
├── cpu_data.txt                 # Raw CPU metrics
├── memory_data.txt              # Raw memory metrics
├── llm_data.txt                 # Raw LLM metrics
├── geekbench_ai_data.txt        # Raw Geekbench scores (if run)
├── *_log.jsonl                  # Real-time JSON event logs
├── plots/                       # All visualizations
│   ├── cpu_benchmark.png
│   ├── memory_pressure_benchmark.png
│   ├── thermal_benchmark.png
│   ├── llm_benchmark.png
│   ├── model_params_comparison.png
│   └── geekbench_ai_benchmark.png
└── daily_usage_data.txt         # Workflow simulation data
```

## The Scale Reality: Why Local Inference ≠ SOTA

State-of-the-art AI models (May 2026) are orders of magnitude larger than what local hardware can run:

| Model Family | Latest Model | Total Parameters | Status |
|--------------|--------------|------------------|--------|
| Kimi (Moonshot) | K2.6 | ~1 Trillion | Verified |
| GLM (Zhipu) | GLM-5 | ~744 Billion | Verified |
| Claude (Anthropic) | Opus 4.6 | ~400B+ | Verified |
| MiniMax | M2.7 | ~230 Billion | Verified |
| Gemini (Google) | 2.5 Pro | ~1.2 Trillion | Estimated |
| Claude (Anthropic) | Opus 4.7 | ~4 Trillion | Estimated |
| GPT (OpenAI) | GPT-5.5 | ~9 Trillion | Estimated |

**Note:** Parameter counts are either verified (from public sources) or estimated (industry projections). Estimated values show ranges where available. Cloud providers keep exact figures proprietary.

**Key insight:** The smallest verified SOTA model (MiniMax M2.7 at 230B) is **~8x larger** than the largest local model that can run on 16GB MacBook Air (30B). Estimated SOTA models at 1T-9T parameters are **30-300x larger** than the largest local model.

Local inference is for: code completion (0.6B-1.7B), privacy-preserving work, offline use, learning.
API access is required for: complex reasoning, planning, production AI features.

![Model Scale Comparison](results/plots/model_params_comparison.png)

## Benchmarks

### LLM Inference (Qwen3 Family)

Tests local AI inference capability without external API:

| Model | Size | Memory | Expected TPS | Status on 16GB |
|-------|------|--------|---------------|----------------|
| qwen3:0.6b | 0.6B | ~1GB | 60-70 tok/s | ✅ Excellent |
| qwen3:1.7b | 1.7B | ~2GB | 25-35 tok/s | ✅ Good |
| qwen3:4b | 4B | ~5GB | 12-18 tok/s | ⚠️ Marginal |
| qwen3:8b | 8B | ~10GB | 15-20 tok/s | ⚠️ Tight |
| qwen3:14b | 14B | ~16GB | 5-10 tok/s | ❌ Unreliable |
| qwen3:30b | 30B | - | - | ❌ OOM |

### Thermal Throttling

5-minute sustained load test. Critical for MacBook Air (fanless). Detects when performance drops due to heat.

### Geekbench AI (Optional)

Standardized cross-device comparison. Runs **CPU, GPU, and Neural Engine separately**:

| Mode | Hardware | What it tests |
|------|----------|---------------|
| CPU | M5 10-core CPU | CPU AI performance |
| GPU | M5 10-core GPU | GPU AI performance |
| Neural | 38 TOPS NPU | Neural Engine AI performance |

Scores: AI Score, Single Precision, Half Precision, Quantized (int8)

Install from https://www.geekbench.com/download/

## Interpreting Results

### For API-Based AI Engineering (Coding Plans)
- **16GB MacBook Air M5:** ✅ Excellent - No concerns
- **16GB MacBook Pro M5:** ✅ Excellent - Better thermal headroom

### For Local LLM Inference
- **0.6B-1.7B models:** ✅ Good - Use qwen3:0.6b for best responsiveness
- **4B-8B models:** ⚠️ Marginal - Slow, memory tight
- **14B+ models:** ❌ Not suited - OOM failures, extreme throttling

### For Heavy Dev + Docker
- **16GB devices:** ❌ Not suited - 32GB minimum recommended
- **MacBook Pro 32GB+ or Mac Studio:** ✅ Suited

## Extracting Metrics

```bash
# Get LLM TPS
grep -E "^[^#]" results/llm_data.txt | cut -d',' -f1,5

# Get thermal phase summary
grep "Phase" results/thermal_benchmark.txt

# Parse JSON logs
cat results/llm_log.jsonl | jq 'select(.type == "prompt_complete")'
```

## Project Structure

```
ai_device_benchmark/
├── benchmarks/           # Individual benchmark scripts
│   ├── cpu_benchmark.py
│   ├── memory_benchmark.py
│   ├── llm_benchmark.py
│   ├── thermal_benchmark.py
│   └── geekbench_ai_benchmark.py
├── scripts/
│   ├── benchmark_logger.py    # JSON real-time logging
│   └── generate_plots.py     # Plot generation from real data
├── run_all_benchmarks.sh     # Main runner
├── FRAMEWORK.md              # Detailed documentation
└── results/                  # Output directory
```

## Cross-Device Comparison

Run on multiple devices, then compare:

```bash
# Extract key metrics for comparison
cat ~/results/*/summary.json | jq '{device: .device.name, memory: .hardware.memory_gb}'

# Compare LLM performance
grep -h "^0.6B" ~/results/*/llm_data.txt
```

## License

Internal use for departmental device assessment.