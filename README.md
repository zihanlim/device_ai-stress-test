# AI Engineering Device Benchmark Suite

A portable benchmark suite for assessing hardware suitability for AI engineering workloads on MacBook Air/Pro and Mac Studio devices.

**Primary Use Case:** Determine if a MacBook is suitable for API-based AI engineering (Claude API, Coding Plans) and local LLM inference.

<div style="border: 2px solid black; border-radius: 8px; padding: 16px; margin: 16px 0;">

## TL;DR — MacBook Air M5 (16GB) Results

**Primary Use Case: API-Based AI Engineering (Claude,ONA,AWB Coding Plans)**

### Most Important Considerations for API AI Workflows

| Priority | Factor | Result | Verdict |
|----------|--------|-------------|---------|
| **1st** | **Memory headroom** | 16GB, zero swap under load | ✅ Comfortable — Tested, can run IDE + Browser + Slack without pressure |
| **2nd** | **Storage speed** | 14 GB/s read | ✅ Excellent — fast project file loading |
| **3rd** | **CPU single-core** | Fibonacci 1M: 8.9s | ✅ Responsive — quick compiles, snappy UI |

**What doesn't matter for API coding:**
- LLM TPS (cloud APIs inference happens in servers, not local inference)
- GPU/Neural Engine scores
- Thermal throttling (you're mostly waiting on network, not sustained compute as inference doesnt happen locally)

### Full Benchmark Summary

| Component | Score | Notes |
|-----------|-------|-------|
| **GPU AI** | **11,637** | Best for AI workloads |
| **CPU AI** | 4,298 | 2.7x slower than GPU |
| **Neural Engine** | 4,138 | Excels at quantized/int8 tasks |
| **Storage** | 14 GB/s read, 6.9 GB/s write | Excellent |
| **Memory** | 14.5 GB/s bandwidth, zero swap | Great |
| **CPU** | 4.58x/10 cores, 46% efficiency, ~1.7 TFLOPS | Good |
| **Thermal** | ≤6% max degradation (fanless, moderate throttling) | Good for sustained workloads |

### Bottom Line

**For API-based AI coding plans:** The M5 Air is sufficient. Memory headroom, storage speed, and CPU single-core performance are all good. Our daily workflow uses SOTA API models (Claude Sonnet 4.6 at ~110 TPS, Opus 4.7 at ~81 TPS), and are categorically faster than any local model.

**For local LLM:** Stick to **qwen3:0.6b** (164 tok/s, 1GB) or **qwen3:1.7b** (65 tok/s, 2GB). The 4B model at 38 tok/s is usable but slower than 1.7B. The 8B model at 19 tok/s is slow and barefly usable. Anything larger models with more parameters hits memory limits.

**Memory constraint:** If you also run Docker, 16GB is tight — more RAM, 32GB+ Pro recommended. Docker Desktop alone consumes 8-12GB, leaving only 4-8GB for IDE + browser + system. A loaded IDE (VS Code + extensions + iOS simulator) can use 4-6GB, and an 8B model needs ~5GB, leaving almost no headroom. For Docker + local models, 32GB minimum. But from observation of ERP use cases, since the team do not run docker locally and ERP do not run local models, MacBook Air 16GB is sufficient.

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