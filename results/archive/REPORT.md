# MacBook-Air-M5 - AI Engineering Device Assessment

**Device:** MacBook-Air-M5
**Tag:** 16GB-500GB
**Chip:** Apple M5
**Memory:** 16.0 GB
**Test Date:** 2026-05-04T00:00:00-07:00

---

## Executive Summary

This report evaluates **MacBook-Air-M5** (16.0GB) for AI engineering workloads.

| Workflow | Suitability | Notes |
|----------|-------------|-------|
| API-Based AI (Coding Plans) | Excellent | No concerns |
| Local Small Model (0.6B-1.7B) | Good | 69 tok/s, responsive |
| Local Medium Model (4B-8B) | Not suited | Very slow or fails |
| Local Large Model (14B+) | Not suited | OOM failures, 2/5 success |
| Heavy Dev + Docker | Not suited | 16GB insufficient for containers |

---

## Hardware Specifications

| Component | Specification |
|-----------|--------------|
| Chip | Apple M5 |
| Model | Mac16,12 |
| Physical Cores | 10 |
| Logical Cores | 10 |
| Memory | 16.0 GB |
| macOS | 15.4 |

---

## CPU Performance

| Test | Result | Assessment |
|------|--------|------------|
| Fibonacci (1M iterations) | 10.81s | Fast single-threaded |
| Prime Sieve (1M) | 44.1ms | Very fast |
| Matrix Multiply 1024x1024 | 1.53ms | 1.41 TFLOPS |
| Multi-core Scaling (10 cores) | 3.38x speedup | 34% efficiency |

**Assessment:** CPU performance is excellent for compile/build operations, git workflows, and general development tasks. Multi-core efficiency of 34% indicates thermal throttling on fanless design.

---

## Memory Performance

| Test | Result |
|------|--------|
| Total Memory | 16 GB |
| Sequential Bandwidth | 6.52 GB/s |
| Strided Access Bandwidth | 1.61 GB/s |
| 80% Memory Allocation | 0 MB swap |

**Assessment:** Memory bandwidth is good. 80% allocation (13GB) completed without swap.

---

## Local LLM Performance (Qwen3 Family)

All tests run with Ollama on device.

| Model | Size | Memory | TPS | Latency | Success Rate |
|-------|------|--------|-----|---------|--------------|
| qwen3:0.6b | 0.6B | 1 GB | **68.6** | 8.4s | 100% |
| qwen3:1.7b | 1.7B | 2 GB | **29.9** | 34.9s | 100% |
| qwen3:4b | 4B | 5 GB | **14.9** | 77.5s | 80% |
| qwen3:8b | 8B | 10 GB | **17.6** | 81.4s | 100% |
| qwen3:14b | 14B | 16 GB | **8.3** | 43.6s | 40% |

### Key Findings

1. **Best model: qwen3:0.6b** - 68.6 tok/s, 1GB memory
3. **qwen3:4b unreliable** - 4/5 prompts succeeded
3. **qwen3:14b unreliable** - 2/5 prompts succeeded

### Memory Efficiency (TPS per GB)

| Model | Efficiency | Rating |
|-------|-------------|--------|
| 0.6B | 68.6 tok/s/GB | Excellent |
| 1.7B | 15.0 tok/s/GB | Good |
| 4B | 3.0 tok/s/GB | Poor |
| 8B | 1.8 tok/s/GB | Poor |
| 14B | 0.5 tok/s/GB | Poor |

---

## Thermal Performance

5-minute sustained load test results:

| Phase | Duration | Avg Time/Op | Status |
|-------|----------|-------------|--------|
| Initial | 0-30s | 5.77ms | Normal |
| Ramp-down | 30-90s | 3.29ms | Optimal |
| Sustained | 90s+ | 1.19ms | **Throttling** |

**Performance drop:** 79.3% from initial to sustained phase

**Assessment:** Thermal throttling detected - performance degrades under sustained load. Expected for fanless design.

---

## Daily Usage Workflow Simulation

| Scenario | Time | Memory Delta |
|----------|------|--------------|
| baseline | 0.0ms | 21120 MB |
| ColdStart | 13.8ms | 11488 MB |
| HotStart | 0.0ms | 11488 MB |
| Browsing 10Tabs | 23.0ms | 76 MB |
| IDE Workspace | 67.2ms | 191 MB |
| Workflow Combined | 136.3ms | 229 MB |

**Assessment:** Daily development workflows run smoothly. No memory pressure observed with typical usage patterns.

---

## Suitability Assessment by Workflow

### API-Based AI Engineering (Claude API/Coding Plans) Excellent

| Requirement | This Device | Status |
|-------------|-------------|--------|
| Memory | 16.0GB | ✅ Exceeds needs |
| CPU | Apple | ✅ Excellent |
| Thermal | Fanless | ✅ Quiet |

**Verdict:** Perfect for API-based AI work.

---

### Local Small Model (0.6B-1.7B) Good

| Requirement | This Device | Status |
|-------------|-------------|--------|
| Memory | 1-2GB | ✅ Comfortable |
| TPS | 30+ tok/s | ✅ Responsive |
| Thermal | Passive | ✅ No concern |

**Verdict:** Excellent for local code completion.

---

### Local Medium Model (4B-8B) Not suited

| Requirement | This Device | Status |
|-------------|-------------|--------|
| Memory | 5-10GB | ✅ Adequate |
| TPS | 15+ tok/s | ✅ Usable |
| Thermal | Passive | ⚠️ May throttle |

**Verdict:** Not recommended for this device.

---

### Local Large Model (14B+) Not suited

| Requirement | This Device | Status |
|-------------|-------------|--------|
| Memory | 16GB+ | ❌ Cannot fit |
| TPS | 10+ tok/s | ❌ Unusable |
| Success Rate | 80%+ | ❌ Unreliable |

**Verdict:** This device cannot run 14B+ models reliably.

---

### Heavy Development + Docker Not suited

| Requirement | This Device | Status |
|-------------|-------------|--------|
| Memory | 32GB+ | ❌ 16.0GB insufficient |
| CPU | M-series | ✅ Good |
| Storage | Fast NVMe | ✅ Adequate |

**Verdict:** 16GB insufficient for containers

---

## Recommendations

### For This Device (MacBook-Air-M5)

1. **Use API-based AI** (Claude API, Coding Plans) - perfect fit
2. **For local AI, use small models** (0.6B recommended for best responsiveness)
4. **Expect thermal throttling** under sustained compute load
5. **Avoid Docker containers** - 16GB insufficient for containerized workloads

### For Teams Evaluating Procurement

| Use Case | Recommended Device |
|----------|-------------------|
| API-Based AI only | MacBook Air M5 16GB ✅ |
| API-Based + Light Local (0.6B) | MacBook Air M5 16GB ✅ |
| Local 7B+ regularly | MacBook Pro 32GB minimum |
| Heavy Docker/Containers | MacBook Pro 32GB or Mac Studio |

---

## Raw Data Summary

| Benchmark | Key Metric | Value |
|-----------|------------|-------|
| CPU | Fibonacci 1M | 10.81s |
| CPU | MatMul 1024x1024 | 1.41 TFLOPS |
| CPU | 10-core speedup | 3.38x |
| Memory | Sequential BW | 6.52 GB/s |
| LLM | Best TPS | 68.6 tok/s (qwen3:0.6b) |
| Thermal | Sustained drop | 79.3% |

---

*Report generated from real benchmark tests - 2026-05-04T00:00:00-07:00*
*Framework: AI Engineering Device Benchmark Suite*
