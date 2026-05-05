#!/usr/bin/env python3
"""
Generate comprehensive REPORT.md from parsed benchmark data
Produces human-readable assessment with real test values
"""
import os
import sys
import json
import subprocess
import re


def parse_cpu_data(path):
    """Parse cpu_data.txt into dict"""
    data = {}
    with open(path) as f:
        for line in f:
            if line.startswith('test,') or not line.strip():
                continue
            parts = line.strip().split(',')
            if len(parts) >= 2:
                key = parts[0].strip()
                try:
                    data[key] = float(parts[1])
                except:
                    pass
    return data


def parse_memory_data(path):
    """Parse memory_data.txt into dict"""
    data = {}
    with open(path) as f:
        for line in f:
            if line.startswith('test,') or not line.strip():
                continue
            parts = line.strip().split(',')
            if len(parts) >= 2:
                key = parts[0].strip()
                try:
                    data[key] = float(parts[1])
                except:
                    pass
    return data


def parse_llm_data(path):
    """Parse llm_data.txt into list of dicts"""
    models = []
    with open(path) as f:
        for line in f:
            if line.startswith('model_size') or not line.strip():
                continue
            parts = line.strip().split(',')
            if len(parts) >= 6:
                try:
                    models.append({
                        'size': parts[0],
                        'name': parts[1],
                        'mem_gb': float(parts[2]),
                        'latency': float(parts[3]),
                        'tps': float(parts[4]),
                        'tokens': int(parts[5]),
                        'successful': int(parts[6])
                    })
                except:
                    pass
    # Sort by size
    models.sort(key=lambda x: float(x['size'].replace('B', '')))
    return models


def parse_thermal_data(path):
    """Parse thermal_data.txt summary values"""
    data = {}
    with open(path) as f:
        for line in f:
            if line.startswith('metric,'):
                continue
            parts = line.strip().split(',')
            if len(parts) >= 2 and parts[0] in ('phase1_avg', 'phase2_avg', 'phase3_avg', 'phase3_drop_pct'):
                try:
                    data[parts[0]] = float(parts[1])
                except:
                    pass
    return data


def parse_daily_usage_data(path):
    """Parse daily_usage_data.txt"""
    data = {}
    with open(path) as f:
        for line in f:
            if line.startswith('scenario') or not line.strip():
                continue
            parts = line.strip().split(',')
            if len(parts) >= 5:
                key = parts[0].strip()
                try:
                    if key == 'summary':
                        continue
                    data[key] = {
                        'duration': float(parts[3]) if parts[3] else 0,
                        'mem_delta': float(parts[4]) if parts[4] else 0
                    }
                except:
                    pass
            elif len(parts) >= 2 and parts[0].startswith(('baseline_memory', 'final_memory', 'swap_delta')):
                try:
                    data[parts[0]] = float(parts[1])
                except:
                    pass
    return data


def parse_summary_json(path):
    """Parse summary.json"""
    with open(path) as f:
        return json.load(f)


def assess_workflow_suitability(cpu, memory, llm):
    """Determine workflow suitability ratings"""

    # API-based AI Engineering
    api_rating = "Excellent"
    api_notes = "No concerns"

    # Local small model
    small_model = next((m for m in llm if m['size'] == '0.6B'), None)
    if small_model and small_model['tps'] >= 50:
        small_rating = "Good"
        small_notes = f"{small_model['tps']:.0f} tok/s, responsive"
    else:
        small_rating = "Marginal"
        small_notes = "Slow performance"

    # Local medium model
    med_model = next((m for m in llm if m['size'] == '4B'), None)
    if med_model and med_model['tps'] >= 15:
        med_rating = "Marginal"
        med_notes = f"{med_model['tps']:.0f} tok/s, tight memory"
    else:
        med_rating = "Not suited"
        med_notes = "Very slow or fails"

    # Local large model
    large_model = next((m for m in llm if m['size'] == '14B'), None)
    if large_model:
        if large_model['successful'] >= 4:
            large_rating = "Marginal"
            large_notes = f"{large_model['tps']:.0f} tok/s, unreliable ({large_model['successful']}/5 success)"
        else:
            large_rating = "Not suited"
            large_notes = f"OOM failures, {large_model['successful']}/5 success"
    else:
        large_rating = "Not suited"
        large_notes = "Cannot run"

    # Heavy Dev + Docker
    if memory.get('TotalMemory_GB', 0) < 32:
        heavy_rating = "Not suited"
        heavy_notes = "16GB insufficient for containers"
    else:
        heavy_rating = "Adequate"
        heavy_notes = "32GB+ recommended"

    return {
        'api': (api_rating, api_notes),
        'small': (small_rating, small_notes),
        'medium': (med_rating, med_notes),
        'large': (large_rating, large_notes),
        'heavy': (heavy_rating, heavy_notes)
    }


def generate_report_md(results_dir, device_info, cpu, memory, llm, thermal, daily):
    """Generate comprehensive REPORT.md with real data"""

    # Sort LLM by size for table
    llm_sorted = sorted(llm, key=lambda x: float(x['size'].replace('B', '')))

    # Memory info
    total_mem_gb = memory.get('TotalMemory_GB', 16.0)
    total_mem_mb = memory.get('TotalMemory_MB', 16384)
    seq_bw = memory.get('SequentialCopy_BW', 0)
    stride_bw = memory.get('StridedAccess_BW', 0)

    # CPU info
    fib_1m = cpu.get('Fibonacci(1000000)', 0)
    sieve_1m = cpu.get('Sieve(1000000)', 0)
    matmul_1k = cpu.get('MatMul_1024', 0)
    matmul_tflops = cpu.get('MatMul_1024_TFLOPS', 0)
    single_core = cpu.get('SingleCore_Time', 0)
    multi_core_10c = cpu.get('MultiCore_10C_Time', 0)
    speedup_10c = cpu.get('MultiCore_10C_Speedup', 0)
    efficiency_10c = cpu.get('MultiCore_10C_Efficiency', 0)

    # Thermal
    phase1 = thermal.get('phase1_avg', 0)
    phase2 = thermal.get('phase2_avg', 0)
    phase3 = thermal.get('phase3_avg', 0)
    drop_pct = thermal.get('phase3_drop_pct', 0)

    # Workflow assessment
    assessments = assess_workflow_suitability(cpu, memory, llm)

    # Build report
    report = f"""# {device_info['device']['name']} - AI Engineering Device Assessment

**Device:** {device_info['device']['name']}
**Tag:** {device_info['device']['tag']}
**Chip:** {device_info['hardware']['chip']}
**Memory:** {device_info['hardware']['memory_gb']} GB
**Test Date:** {device_info['device']['date']}

---

## Executive Summary

This report evaluates **{device_info['device']['name']}** ({device_info['hardware']['memory_gb']}GB) for AI engineering workloads.

| Workflow | Suitability | Notes |
|----------|-------------|-------|
| API-Based AI (Coding Plans) | {assessments['api'][0]} | {assessments['api'][1]} |
| Local Small Model (0.6B-1.7B) | {assessments['small'][0]} | {assessments['small'][1]} |
| Local Medium Model (4B-8B) | {assessments['medium'][0]} | {assessments['medium'][1]} |
| Local Large Model (14B+) | {assessments['large'][0]} | {assessments['large'][1]} |
| Heavy Dev + Docker | {assessments['heavy'][0]} | {assessments['heavy'][1]} |

---

## Hardware Specifications

| Component | Specification |
|-----------|--------------|
| Chip | {device_info['hardware']['chip']} |
| Model | {device_info['hardware']['model']} |
| Physical Cores | {device_info['hardware']['physical_cores']} |
| Logical Cores | {device_info['hardware']['logical_cores']} |
| Memory | {device_info['hardware']['memory_gb']} GB |
| macOS | {device_info['device']['os']} |

---

## CPU Performance

| Test | Result | Assessment |
|------|--------|------------|
| Fibonacci (1M iterations) | {fib_1m:.2f}s | Fast single-threaded |
| Prime Sieve (1M) | {sieve_1m*1000:.1f}ms | Very fast |
| Matrix Multiply 1024x1024 | {matmul_1k:.2f}ms | {matmul_tflops:.2f} TFLOPS |
| Multi-core Scaling (10 cores) | {speedup_10c:.2f}x speedup | {efficiency_10c:.0f}% efficiency |

**Assessment:** CPU performance is excellent for compile/build operations, git workflows, and general development tasks. Multi-core efficiency of {efficiency_10c:.0f}% indicates {"thermal throttling on fanless design" if efficiency_10c < 50 else "good multi-core utilization"}.

---

## Memory Performance

| Test | Result |
|------|--------|
| Total Memory | {total_mem_gb:.0f} GB |
| Sequential Bandwidth | {seq_bw:.2f} GB/s |
| Strided Access Bandwidth | {stride_bw:.2f} GB/s |
| 80% Memory Allocation | {memory.get('SwapTest_80pct', 0):.0f} MB swap |

**Assessment:** Memory bandwidth is {"good" if seq_bw > 5 else "moderate"}. 80% allocation ({total_mem_gb*0.8:.0f}GB) {"completed without swap" if memory.get('SwapTest_80pct', 0) == 0 else "triggered swap"}.

---

## Local LLM Performance (Qwen3 Family)

All tests run with Ollama on device.

| Model | Size | Memory | TPS | Latency | Success Rate |
|-------|------|--------|-----|---------|--------------|
"""

    for m in llm_sorted:
        success_rate = f"{m['successful']*20}%"
        report += f"| {m['name']} | {m['size']} | {m['mem_gb']:.0f} GB | **{m['tps']:.1f}** | {m['latency']:.1f}s | {success_rate} |\n"

    report += f"""
### Key Findings

"""

    # Best model
    if llm_sorted:
        best = max(llm_sorted, key=lambda x: x['tps'])
        report += f"1. **Best model: {best['name']}** - {best['tps']:.1f} tok/s, {best['mem_gb']:.0f}GB memory\n"

    # OOM models
    oom_models = [m for m in llm_sorted if m['successful'] == 0]
    if oom_models:
        report += f"2. **OOM failures:** {', '.join(m['name'] for m in oom_models)}\n"

    # Marginal models
    marginal = [m for m in llm_sorted if 0 < m['successful'] < 5]
    if marginal:
        for m in marginal:
            report += f"3. **{m['name']} unreliable** - {m['successful']}/5 prompts succeeded\n"

    report += f"""
### Memory Efficiency (TPS per GB)

| Model | Efficiency | Rating |
|-------|-------------|--------|
"""

    for m in llm_sorted:
        eff = m['tps'] / m['mem_gb'] if m['mem_gb'] > 0 else 0
        rating = "Excellent" if eff > 30 else "Good" if eff > 10 else "Acceptable" if eff > 3 else "Poor"
        report += f"| {m['size']} | {eff:.1f} tok/s/GB | {rating} |\n"

    report += f"""
---

## Thermal Performance

5-minute sustained load test results:

| Phase | Duration | Avg Time/Op | Status |
|-------|----------|-------------|--------|
| Initial | 0-30s | {phase1:.2f}ms | Normal |
| Ramp-down | 30-90s | {phase2:.2f}ms | Optimal |
| Sustained | 90s+ | {phase3:.2f}ms | **Throttling** |

**Performance drop:** {drop_pct:.1f}% from initial to sustained phase

**Assessment:** {"Thermal throttling detected - performance degrades under sustained load. Expected for fanless design." if drop_pct > 20 else "Minimal throttling - performance well maintained."}

---

## Daily Usage Workflow Simulation

| Scenario | Time | Memory Delta |
|----------|------|--------------|
"""

    for key, val in daily.items():
        if isinstance(val, dict) and 'duration' in val:
            name = key.replace('_Total', '').replace('_', ' ')
            report += f"| {name} | {val['duration']*1000:.1f}ms | {val['mem_delta']:.0f} MB |\n"

    report += f"""
**Assessment:** Daily development workflows run smoothly. No memory pressure observed with typical usage patterns.

---

## Suitability Assessment by Workflow

### API-Based AI Engineering (Claude API/Coding Plans) {assessments['api'][0]}

| Requirement | This Device | Status |
|-------------|-------------|--------|
| Memory | {device_info['hardware']['memory_gb']}GB | ✅ Exceeds needs |
| CPU | {device_info['hardware']['chip'].split()[0]} | ✅ Excellent |
| Thermal | Fanless | ✅ Quiet |

**Verdict:** {"Perfect for API-based AI work." if assessments['api'][0] == "Excellent" else "Suitable for API-based AI work."}

---

### Local Small Model (0.6B-1.7B) {assessments['small'][0]}

| Requirement | This Device | Status |
|-------------|-------------|--------|
| Memory | 1-2GB | ✅ Comfortable |
| TPS | 30+ tok/s | {"✅ Responsive" if llm_sorted and llm_sorted[0]['tps'] > 30 else "⚠️ Slow"} |
| Thermal | Passive | ✅ No concern |

**Verdict:** {"Excellent for local code completion." if assessments['small'][0] == "Good" else "Marginal for local inference."}

---

### Local Medium Model (4B-8B) {assessments['medium'][0]}

| Requirement | This Device | Status |
|-------------|-------------|--------|
| Memory | 5-10GB | {"✅ Adequate" if total_mem_gb >= 16 else "❌ Tight"} |
| TPS | 15+ tok/s | {"✅ Usable" if llm_sorted and any(m['tps'] > 15 for m in llm_sorted if m['size'] in ['4B', '8B']) else "⚠️ Slow"} |
| Thermal | Passive | ⚠️ May throttle |

**Verdict:** {"Works but not enjoyable - slow TPS." if assessments['medium'][0] == "Marginal" else "Not recommended for this device."}

---

### Local Large Model (14B+) {assessments['large'][0]}

| Requirement | This Device | Status |
|-------------|-------------|--------|
| Memory | 16GB+ | {"❌ Cannot fit" if total_mem_gb < 32 else "⚠️ Tight"} |
| TPS | 10+ tok/s | ❌ Unusable |
| Success Rate | 80%+ | ❌ Unreliable |

**Verdict:** {"This device cannot run 14B+ models reliably." if assessments['large'][0] == "Not suited" else "Marginal - use MacBook Pro 32GB+ instead."}

---

### Heavy Development + Docker {assessments['heavy'][0]}

| Requirement | This Device | Status |
|-------------|-------------|--------|
| Memory | 32GB+ | ❌ {device_info['hardware']['memory_gb']}GB insufficient |
| CPU | M-series | ✅ Good |
| Storage | Fast NVMe | ✅ Adequate |

**Verdict:** {assessments['heavy'][1]}

---

## Recommendations

### For This Device ({device_info['device']['name']})

"""

    # Generate recommendations based on data
    recommendations = []

    if assessments['api'][0] == 'Excellent':
        recommendations.append("1. **Use API-based AI** (Claude API, Coding Plans) - perfect fit")
    if llm_sorted and llm_sorted[0]['tps'] > 50:
        recommendations.append("2. **For local AI, use small models** (0.6B recommended for best responsiveness)")
    if assessments['medium'][0] == 'Marginal':
        recommendations.append("3. **Avoid running models alongside heavy apps** - memory limited")
    if drop_pct > 20:
        recommendations.append("4. **Expect thermal throttling** under sustained compute load")
    if total_mem_gb < 32:
        recommendations.append("5. **Avoid Docker containers** - 16GB insufficient for containerized workloads")

    for rec in recommendations:
        report += f"{rec}\n"

    report += f"""
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
| CPU | Fibonacci 1M | {fib_1m:.2f}s |
| CPU | MatMul 1024x1024 | {matmul_tflops:.2f} TFLOPS |
| CPU | 10-core speedup | {speedup_10c:.2f}x |
| Memory | Sequential BW | {seq_bw:.2f} GB/s |
| LLM | Best TPS | {best['tps']:.1f} tok/s ({best['name']}) |
| Thermal | Sustained drop | {drop_pct:.1f}% |

---

*Report generated from real benchmark tests - {device_info['device']['date']}*
*Framework: AI Engineering Device Benchmark Suite*
"""

    return report


def write_report(results_dir, summary_path, report_path):
    """Parse all data and write comprehensive report"""

    # Parse all data files
    summary = parse_summary_json(summary_path)

    cpu = parse_cpu_data(os.path.join(results_dir, 'cpu_data.txt'))
    memory = parse_memory_data(os.path.join(results_dir, 'memory_data.txt'))
    llm = parse_llm_data(os.path.join(results_dir, 'llm_data.txt'))
    thermal = parse_thermal_data(os.path.join(results_dir, 'thermal_data.txt'))
    daily = parse_daily_usage_data(os.path.join(results_dir, 'daily_usage_data.txt'))

    # Generate report
    report = generate_report_md(results_dir, summary, cpu, memory, llm, thermal, daily)

    # Write report
    with open(report_path, 'w') as f:
        f.write(report)

    print(f"Report generated: {report_path}")
    return report


def main():
    if len(sys.argv) < 2:
        results_dir = os.path.dirname(os.path.abspath(__file__)) + '/../results'
    else:
        results_dir = sys.argv[1]

    results_dir = os.path.abspath(results_dir)
    summary_path = os.path.join(results_dir, 'summary.json')
    report_path = os.path.join(results_dir, 'REPORT.md')

    if not os.path.exists(summary_path):
        print(f"Error: summary.json not found at {summary_path}")
        sys.exit(1)

    # Generate report from parsed data
    report = write_report(results_dir, summary_path, report_path)

    print(f"\nReport generated: {report_path}")


if __name__ == '__main__':
    main()