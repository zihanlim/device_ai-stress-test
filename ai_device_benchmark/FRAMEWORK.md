# AI Engineering Device Benchmark Framework

A comprehensive, portable benchmark suite for assessing hardware suitability for AI engineering workloads. Designed for cross-device comparison and departmental device procurement decisions.

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Benchmark Suite](#benchmark-suite)
4. [Daily Usage Scenarios](#daily-usage-scenarios)
5. [Output Files](#output-files)
6. [Cross-Device Comparison](#cross-device-comparison)
7. [Installation Requirements](#installation-requirements)
8. [Benchmark Results Guide](#benchmark-results-guide)
9. [Suitability Assessment Guide](#suitability-assessment-guide)

---

## Overview

This framework provides standardized benchmarks that simulate real AI engineering daily workflows:

- **Local Development**: Code compilation, terminal operations, IDE performance
- **API-Based AI**: Claude API/Coding Plans usage (network-independent local tests)
- **Local Inference**: Core ML/ANE capabilities for on-device model inference
- **Memory Pressure**: Multi-tasking with browser, IDE, and background LLM
- **Thermal Management**: Sustained workload behavior (critical for fanless devices)
- **LLM Inference**: Ollama/MLX performance measurement

### Hardware Support

| Platform | Status |
|----------|--------|
| Apple Silicon M-series (M1-M5) | **Fully Tested** |
| Intel Macs | Partial (no ANE/CoreML) |
| Linux | Partial (some scripts macOS-specific) |

---

## Quick Start

```bash
# Navigate to framework
cd ai_device_benchmark

# Run all benchmarks
./run_all_benchmarks.sh [results_dir] [device_name] [device_tag]

# Example
./run_all_benchmarks.sh ~/benchmark_results "MacBook-Air-M5" "Engineering-Dept-2026"

# Generate plots from existing results
python3 scripts/generate_plots.py results/
```

### Prerequisites

```bash
# Python packages (for benchmarks and plotting)
pip3 install numpy matplotlib seaborn

# Optional: For LLM benchmarks
brew install ollama

# Optional: For Apple Silicon MLX acceleration
pip3 install mlx
```

---

## Benchmark Suite

### 1. CPU Benchmark (`benchmarks/cpu_benchmark.sh`)

**Tests:**
- Single-threaded performance (Fibonacci iterative, prime sieve)
- Multi-threaded performance (parallel prime calculation)
- ML-style matrix operations (TFLOPS measurement)

**Output:** `cpu_benchmark.txt` + `plots/cpu_benchmark.png`

**Key Metrics:**
- Operations per second (single-threaded)
- Multi-core scaling efficiency
- Matrix multiplication TFLOPS

---

### 2. Memory Benchmark (`benchmarks/memory_benchmark.sh`)

**Tests:**
- Memory allocation speed
- Sequential copy bandwidth (GB/s)
- Strided access bandwidth (ML layer access patterns)
- Memory pressure behavior (swap trigger)

**Output:** `memory_benchmark.txt`

**Key Metrics:**
- Sequential bandwidth (GB/s)
- Swap trigger threshold
- Maximum allocation before OOM

---

### 3. Storage Benchmark (`benchmarks/storage_benchmark.sh`)

**Tests:**
- Sequential read/write speeds
- Random I/O performance (4K blocks)
- Large file handling (model loading simulation)

**Output:** `storage_benchmark.txt`

**Key Metrics:**
- Sequential read MB/s
- Sequential write MB/s
- Random read MB/s
- Estimated model load time

---

### 4. Core ML / Neural Engine Benchmark (`benchmarks/coreml_benchmark.sh`)

**Tests:**
- MPS (Metal Performance Shaders) availability
- Matrix multiplication throughput (TFLOPS)
- Core ML model inference capability

**Output:** `coreml_benchmark.txt`

**Key Metrics:**
- TFLOPS for matrix operations
- MPS availability
- Estimated LLM inference tokens/sec

---

### 5. Thermal Throttling Benchmark (`benchmarks/thermal_benchmark.sh`)

**Tests:**
- Performance over 5-minute sustained load
- CPU frequency maintenance
- Thermal throttling detection
- Phase analysis (initial, ramp-down, sustained)

**Output:** `thermal_benchmark.txt` + `plots/thermal_benchmark.png` + `plots/cpu_frequency.png`

**Key Metrics:**
- Performance drop percentage per phase
- CPU frequency over time
- Throttling threshold time
- Recovery behavior

**Critical for:** MacBook Air (fanless) - determines if device can handle sustained AI workloads

---

### 6. LLM Inference Benchmark (`benchmarks/llm_benchmark.sh`)

**Tests Qwen3 model family across sizes to determine device capability:**
- Small (0.6B-1.7B): Smooth, uses ~1-2GB
- Medium (4B-8B): Tight fit, ~5-10GB
- Large (14B-30B): Tests memory limits on 16GB device

**Output:** `llm_data.txt` + `plots/llm_benchmark.png`

**Key Metrics:**
- Tokens per second per model size
- Latency per model size
- Memory requirements per model
- Efficiency (TPS per GB memory)

**Models Tested (Qwen3 Family):**
| Model | Size | Memory |
|-------|------|--------|
| qwen3:0.6b | 0.6B | ~0.5GB |
| qwen3:1.7b | 1.7B | ~1.4GB |
| qwen3:4b | 4B | ~2.5GB |
| qwen3:8b | 8B | ~5.2GB |
| qwen3:14b | 14B | ~9.3GB |
| qwen3:30b | 30B | ~18GB (fails on 16GB) |

**Requires Ollama:**
```bash
brew install ollama
ollama serve
# Models are auto-pulled as needed
```

---

### 7. Geekbench AI Benchmark (`benchmarks/geekbench_ai_benchmark.py`)

**Cross-platform AI benchmark measuring CPU, GPU, NPU performance:**
- Runs **CPU and Metal separately** for procurement comparison:
  - `--cpu` - M5 10-core CPU AI performance
  - `--metal` - GPU + 38 TOPS Neural Engine (ANE) combined
- Single Precision, Half Precision, and Quantized scores for each
- Native macOS support with Metal acceleration
- Installs via Mac App Store or direct download
- Auto-integrated into full benchmark suite

**Output:** `geekbench_ai_data.txt` + `plots/geekbench_ai_benchmark.png`

**Procurement Comparison Output:**
| Score Type | CPU | Metal |
|------------|-----|-------|
| AI Score | M5 10-core | GPU + ANE |
| Single Precision | ✓ | ✓ |
| Half Precision | ✓ | ✓ |
| Quantized (int8) | ✓ | ✓ |

---

### 8. Memory Pressure Benchmark (`benchmarks/memory_pressure_benchmark.sh`)

**Tests:**
- Light usage (browser + IDE + terminal)
- Medium usage + background LLM
- 8GB memory pressure (swap behavior)

**Output:** `memory_pressure_benchmark.txt` + `memory_pressure_data.txt` + `plots/memory_pressure_scenarios.png`

**Scenarios:**
| Scenario | Memory Usage | Description |
|----------|--------------|-------------|
| Light | ~4GB | Browser (10 tabs) + VSCode + Terminal + Slack |
| Medium + LLM | ~8GB | Above + 7B Q4 model in background |
| Heavy | 8GB allocation | Tests swap behavior at memory limit |

---

### 9. Daily Usage Benchmark (`benchmarks/daily_usage_benchmark.sh`)

**Tests:**
- Cold start vs hot start
- Browser + IDE + LLM combined workflow
- Realistic multitasking scenarios

**Output:** `daily_usage_benchmark.txt` + `plots/daily_usage_benchmark.png`

**Workflow Simulation:**
1. Cold Start - Time to ready state
2. Hot Start - Resume from warm state
3. Full Workflow - Browser + IDE + Local LLM

---

## Daily Usage Scenarios

### Scenario 1: API-Based AI Engineering (Typical)

```
Work Pattern:
- Browser (15 tabs) - Documentation, API references
- VSCode - Code editing
- Terminal - Git, builds, scripts
- Slack - Team communication
- Claude API/Coding Plans - AI assistance

Memory: ~4-5 GB
Suitability: 16GB EXCELLENT
```

### Scenario 2: Local Small Model (7B Q4)

```
Work Pattern:
- Everything above
- Ollama running llama3.2:1b or mistral:7b
- Model loaded in background

Memory: ~8-9 GB
Suitability: 16GB ADEQUATE (tight)
```

### Scenario 3: Local Medium Model (13B Q4)

```
Work Pattern:
- Everything above
- Ollama running 13B model

Memory: ~12-14 GB
Suitability: 16GB BORDERLINE (swap likely)
Recommendation: 32GB for regular 13B+ use
```

### Scenario 4: Heavy Development + Docker

```
Work Pattern:
- Everything above
- Docker containers
- Large codebase indexing

Memory: 16GB STRUGGLES
Recommendation: 32GB MacBook Pro or Mac Studio
```

---

## Generated Plots

All plots are generated by running `python3 scripts/generate_plots.py results/`

### Core Performance Plots

| Plot | Description |
|------|-------------|
| `cpu_benchmark.png` | Fibonacci, Prime Sieve, Matrix Multiplication times |
| `cpu_scaling.png` | Multi-core speedup and efficiency (1-10 cores) |
| `memory_pressure_benchmark.png` | Sequential vs strided memory bandwidth |
| `memory_pressure_scenarios.png` | Memory used by pressure scenario |
| `thermal_benchmark.png` | Performance degradation over sustained load |
| `daily_usage_benchmark.png` | Cold/hot start times, workflow simulation |
| `llm_benchmark.png` | 4-panel: TPS, latency, memory, efficiency by model size |
| `geekbench_ai_benchmark.png` | CPU vs Metal AI scores comparison (if Geekbench installed) |

---

## Output Files

Each benchmark run generates:

```
results/
├── *_log.jsonl              # Real-time JSON event log (NEW)
├── *_data.txt               # Summary data (TXT/CSV for quick viewing)
├── thermal_data.txt         # Thermal throttling iteration data
├── daily_usage_data.txt     # Workflow simulation data
└── plots/                   # All generated plots
```

### JSON Event Log (`*_log.jsonl`)

Real-time structured logging with timestamps. Each line is a JSON event:

```json
{"type": "benchmark_run", "device_info": {...}, "start_iso": "2026-04-30T17:17:26"}
{"type": "metric", "timestamp": 1777540646.8, "elapsed_s": 0.08, "data": {"name": "ollama_version", "value": "0.22.0"}}
{"type": "prompt_start", "timestamp": 1777540646.8, "elapsed_s": 0.1, "data": {"model": "qwen3:0.6b", "prompt_preview": "..."}}
{"type": "prompt_complete", "timestamp": 1777540649.0, "elapsed_s": 2.28, "data": {"model": "qwen3:0.6b", "latency_s": 2.18, "tokens": 193}}
{"type": "error", "timestamp": 1777541801.0, "elapsed_s": 1154.3, "data": {"message": "Prompt timeout", "model": "qwen3:14b"}}
```

**Event Types:**
| Type | Description |
|------|-------------|
| `benchmark_run` | Header with device info, start time |
| `metric` | Named metric (version, available models) |
| `test_start` | Test phase started |
| `iteration` | Iteration within a test |
| `prompt_start/complete/timeout` | LLM prompt events |
| `model_test_start/complete` | Model test lifecycle |
| `error` | Error with context |
| `summary` | Final summary data |
| `benchmark_end` | Footer with event count |

**Benefits:**
- Crash recovery: Partial data preserved if interrupted
- Timeline analysis: Performance over test duration
- Audit trail: Timestamps for procurement documentation
- Granular data: Iteration-by-iteration metrics

### TXT/CSV Summary (for quick viewing)

```
model_size,model_name,mem_gb,avg_latency_s,avg_tps,total_tokens,successful_prompts
0.6B,qwen3:0.6b,1,8.4420,68.58,2990,5
...
```

### Extracting Metrics

```bash
# Get TPS for all models from TXT
cat llm_data.txt | grep -v model_size | cut -d',' -f1,5

# From JSON log - get all prompt events
cat llm_log.jsonl | jq 'select(.type == "prompt_complete")'

# Get TPS over time for a specific model
cat llm_log.jsonl | jq -r 'select(.type == "prompt_complete" and .data.model == "qwen3:0.6b") | .data.tps'

# Get timing for first prompt of each model
cat llm_log.jsonl | jq -r 'select(.type == "prompt_start") | .data.model, .elapsed_s'

# Get all errors
cat llm_log.jsonl | jq 'select(.type == "error")'

# Timeline of events for debugging
cat llm_log.jsonl | jq -r '[.elapsed_s, .type, .data.model // empty] | @csv'

# Count events by type
cat llm_log.jsonl | jq -r '.type' | sort | uniq -c | sort -rn
```

---

## Cross-Device Comparison

### Running on Multiple Devices

```bash
# MacBook Air M5 (16GB)
./run_all_benchmarks.sh ~/results/macbook-air-m5 "MacBook-Air-M5" "16GB"

# MacBook Pro M4 (24GB)
./run_all_benchmarks.sh ~/results/macbook-pro-m4 "MacBook-Pro-M4" "24GB"

# Mac Studio M2 Ultra (128GB)
./run_all_benchmarks.sh ~/results/mac-studio-m2u "Mac-Studio-M2U" "128GB"
```

### Extracting Key Metrics for Comparison

```bash
# Extract memory
cat ~/results/*/summary.json | jq '.hardware.memory_gb'

# Extract CPU cores
cat ~/results/*/summary.json | jq '.hardware.physical_cores'

# Extract thermal throttling data
grep "Phase 3" ~/results/*/thermal_benchmark.txt

# Compare LLM performance
cat ~/results/*/llm_data.csv
```

---

## Installation Requirements

### Required (Built-in)

- macOS (for full feature set)
- Python 3.x with numpy
- bash/zsh
- sysctl, vm_stat (built-in)

### Optional (For Full LLM Testing)

```bash
# Ollama - for local LLM inference testing
brew install ollama

# Qwen3 models for testing (auto-pulled by benchmark)
# qwen3:0.6b, qwen3:1.7b, qwen3:4b, qwen3:8b, qwen3:14b, qwen3:30b

# MLX - Apple Silicon optimized ML (if using Python MLX)
pip3 install mlx

# Core ML tools
pip3 install coremltools

# Plotting
pip3 install matplotlib seaborn
```

---

## Benchmark Results Guide

### Understanding the Plots

#### CPU Benchmark (`cpu_benchmark.png`)
- **Fibonacci bars**: Single-threaded computation time (lower is better)
- **Sieve bars**: Prime calculation time (lower is better)
- **MatMul bars**: Matrix multiplication time per operation (lower is better)

#### Thermal Benchmark (`thermal_benchmark.png`)
- **Scatter plot**: Time per operation over iterations
- **Colors**: Green (initial) → Orange (ramp-down) → Red (sustained/throttling)
- **Threshold lines**: Orange at 10ms, Red at 50ms indicate throttling

#### Memory Pressure (`memory_pressure_benchmark.png`)
- **Allocations**: Memory used by each scenario
- **Available**: Remaining memory (goes to 0 = limit reached)

#### LLM Benchmark (`llm_benchmark.png`)
- **TPS by Model**: Tokens per second for each model (higher is better)
- **TPS vs Size**: Performance curve showing scaling
- **Memory footprint**: RAM required per model
- **Efficiency**: TPS per GB memory (higher = better utilization)

### Key Thresholds

| Metric | Good | Warning | Critical |
|--------|------|---------|----------|
| Single operation (thermal) | <5ms | 5-20ms | >20ms |
| Sustained load throttling | None | <20% drop | >50% drop |
| Memory headroom | >8GB | 4-8GB | <4GB |
| LLM TPS (7B model) | >15 t/s | 8-15 t/s | <8 t/s |

---

## Suitability Assessment Guide

### For API-Based AI Engineering (Coding Plans)

| Spec | Minimum | Recommended | MacBook Air M5 |
|------|---------|-------------|----------------|
| RAM | 8GB | 16GB | 16GB ✓ |
| CPU | Apple M1 | M3+ | M5 ✓ |
| Storage | 256GB | 512GB+ | 500GB ✓ |
| Thermal | Any | Any | Fanless (good) |

**Verdict: WELL SUITED** for API-based AI work

### For Local 7B Model Inference

| Spec | Minimum | Recommended | MacBook Air M5 |
|------|---------|-------------|----------------|
| RAM | 16GB | 32GB | 16GB (tight) |
| CPU | Apple M1 | M3+ | M5 ✓ |
| Storage | 512GB | 1TB | 500GB (ok) |
| Thermal | Active | Any | Fanless (throttle) |

**Verdict: MARGINALLY SUITED** - 16GB works but thermal throttling under sustained load

### For Local 13B+ Model Inference

| Spec | Minimum | Recommended | MacBook Air M5 |
|------|---------|-------------|----------------|
| RAM | 32GB | 64GB | 16GB ✗ |
| CPU | M3 Pro | M3 Max | M5 (ok) |
| Storage | 1TB | 2TB | 500GB ✗ |
| Thermal | Active | Active | Fanless ✗ |

**Verdict: NOT SUITED** - Need MacBook Pro 32GB+ or Mac Studio

---

## Framework Maintenance

### Adding Custom Benchmarks

1. Create script in `benchmarks/`
2. Follow naming convention: `*_benchmark.sh`
3. Accept `RESULTS_DIR` as first argument
4. Generate plots in `$RESULTS_DIR/plots/`
5. Add to main runner in `run_all_benchmarks.sh`

### Regenerating Plots

If you've modified data files and want to regenerate plots:

```bash
python3 scripts/generate_plots.py results/
```

### Updating Plots

All plots use matplotlib. For custom visualizations:

```python
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
# ... create plot ...
plt.savefig(f'{plot_dir}/my_plot.png', dpi=150, bbox_inches='tight')
```

---

## Troubleshooting

### "Ollama not found"
```bash
brew install ollama
```

### "matplotlib not installed"
```bash
pip3 install matplotlib
```

### "Permission denied" on thermal tests
Some thermal monitoring requires elevated privileges. Run with `sudo` if needed.

### Benchmark hangs (Fibonacci)
Ensure you're using iterative algorithms, not recursive. See updated scripts.

---

## Future Enhancements

- [ ] GPU/metal benchmark for graphics-intensive AI
- [ ] Network latency benchmark (simulate API conditions)
- [ ] IDE benchmark (VSCode startup, project indexing)
- [ ] Battery life benchmark (video vs compute)
- [ ] Docker benchmark (if departmental needs change)
- [ ] Multi-user simulation (corporate environment)
- [x] **MLX-LM direct benchmark (bypass Ollama for more accurate Apple Silicon metrics)** - Use `pip3 install mlx-lm` for native MLX benchmarking
- [x] **Geekbench AI** - Industry standard cross-platform AI benchmark (auto-integrated into suite)
- [ ] **MLPerf Client** - Industry-standard LLM benchmark from MLCommons (requires manual setup)

---

## Benchmark Results (MacBook Air M5 16GB - Real Tests)

### Hardware Specs
- **Chip**: Apple M5
- **Cores**: 10 (8 performance + 2 efficiency)
- **Memory**: 16 GB
- **Storage**: 500 GB

### CPU Performance (Real)
| Test | Result |
|------|--------|
| Fibonacci (1M) | 10.8s |
| Prime Sieve (1M) | 0.044s (44ms) |
| Matrix Mul 1024x1024 | 1.53ms, 1.41 TFLOPS |
| Multi-core Scaling | 3.38x at 10 cores (34% efficiency) |

### Memory Performance (Real)
| Test | Result |
|------|--------|
| Sequential Bandwidth | 6.52 GB/s |
| Strided Bandwidth | 1.61 GB/s |
| 80% Allocation | Completed, no swap used |

### LLM Performance (Real - Qwen3 Family)
| Model | Size | Latency | TPS | Efficiency |
|-------|------|---------|-----|------------|
| qwen3:0.6b | 0.6B | 8.44s | 68.6 | 68.6 tok/s/GB |
| qwen3:1.7b | 1.7B | 34.94s | 29.9 | 15.0 tok/s/GB |
| qwen3:4b | 4B | 77.48s | 14.9 | 3.0 tok/s/GB |
| qwen3:8b | 8B | 81.39s | 17.6 | 1.8 tok/s/GB |
| qwen3:14b | 14B | 43.57s | 8.3 | 0.5 tok/s/GB |
| qwen3:30b | 30B | FAILED | - | OOM |

**Best choice for this device:** qwen3:0.6b (68.6 tok/s, <1GB memory)
**Avoid on 16GB:** 30B model - exceeds memory, all prompts failed

### Thermal Throttling (5-min sustained test)
| Phase | Duration | Avg Time/op |
|-------|----------|-------------|
| Initial | 0-30s | ~5ms |
| Ramp-down | 30-90s | ~2ms |
| Sustained | 90s+ | Significant throttling detected |

**Note**: Fanless design - throttling expected under sustained load

---

*Framework created for departmental device assessment - 2026-04-30*
*Last updated with MacBook Air M5 benchmark results*