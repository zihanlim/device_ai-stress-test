#!/usr/bin/env python3
"""
Generate All Benchmark Plots from REAL data files only
ALL data must come from real tests - no hardcoded/fake data
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
import sys
import re

# Style
sns.set_palette("muted")
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.facecolor'] = 'white'
plt.rcParams['grid.color'] = '#e0e0e0'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 10

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def parse_key_value_file(filepath):
    """Parse key=value files like cpu_data.txt"""
    data = {}
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if ',' in line and not line.startswith('#'):
                parts = line.split(',')
                if len(parts) >= 2:
                    key = parts[0].strip()
                    try:
                        value = float(parts[1].strip())
                        data[key] = value
                    except:
                        pass
    return data

def parse_iteration_file(filepath, col_time=0, col_note=None):
    """Parse iteration-based files"""
    iterations = []
    notes = []
    with open(filepath) as f:
        for line in f:
            if line.startswith('iteration') or line.startswith('metric'):
                continue
            parts = line.strip().split(',')
            if len(parts) >= 2:
                try:
                    iterations.append(float(parts[col_time]))
                    if col_note and len(parts) > col_note:
                        notes.append(parts[col_note])
                    else:
                        notes.append('')
                except:
                    pass
    return iterations, notes

def generate_cpu_plot(cpu_file, plot_dir):
    """Generate CPU benchmark plots from REAL data"""
    if not os.path.exists(cpu_file):
        print(f"CPU data not found: {cpu_file}")
        return

    data = parse_key_value_file(cpu_file)

    if not data:
        print("No CPU data to plot")
        return

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    fib_vals = [(k, v) for k, v in data.items() if 'Fibonacci' in k]
    if fib_vals:
        fib_vals.sort(key=lambda x: int(re.search(r'\d+', x[0]).group()))
        names = []
        for k, _ in fib_vals:
            num = int(re.search(r'\d+', k).group()) // 1000
            names.append(f'{num}K')
        vals = [v for _, v in fib_vals]
        axes[0].bar(names, vals, color='steelblue')
        axes[0].set_ylabel('Time (s)')
        axes[0].set_title('Fibonacci Performance')
        for i, v in enumerate(vals):
            axes[0].text(i, v + max(vals)*0.02, f'{v:.2f}s', ha='center', fontsize=9)

    sieve_vals = [(k, v) for k, v in data.items() if 'Sieve' in k]
    if sieve_vals:
        sieve_vals.sort(key=lambda x: int(re.search(r'\d+', x[0]).group()))
        names = []
        for k, _ in sieve_vals:
            num = int(re.search(r'\d+', k).group()) // 1000
            names.append(f'{num}K')
        vals = [v for _, v in sieve_vals]
        axes[1].bar(names, vals, color='coral')
        axes[1].set_ylabel('Time (s)')
        axes[1].set_title('Prime Sieve Performance')
        for i, v in enumerate(vals):
            axes[1].text(i, v + max(vals)*0.02, f'{v:.3f}s', ha='center', fontsize=9)

    matmul_vals = [(k, v) for k, v in data.items() if 'MatMul_' in k and 'TFLOPS' not in k]
    if matmul_vals:
        matmul_vals.sort(key=lambda x: int(re.search(r'\d+', x[0]).group()))
        names = [k.replace('MatMul_', '') for k, _ in matmul_vals]
        vals = [v for _, v in matmul_vals]
        axes[2].bar(names, vals, color='green')
        axes[2].set_ylabel('Time (ms)')
        axes[2].set_title('Matrix Multiplication')
        for i, v in enumerate(vals):
            axes[2].text(i, v + max(vals)*0.02, f'{v:.1f}ms', ha='center', fontsize=9)

    plt.tight_layout()
    plt.savefig(f'{plot_dir}/cpu_benchmark.png', dpi=150, bbox_inches='tight')
    print(f"Saved: {plot_dir}/cpu_benchmark.png")

def generate_cpu_scaling_plot(cpu_file, plot_dir):
    """Generate multi-core scaling plot from REAL data"""
    if not os.path.exists(cpu_file):
        print(f"CPU data not found: {cpu_file}")
        return

    data = parse_key_value_file(cpu_file)

    single_core = data.get('SingleCore_Time', 0)
    if single_core == 0:
        print("No multi-core scaling data found")
        return

    cores = []
    times = []
    speedups = []
    efficiencies = []

    for key, val in data.items():
        if 'MultiCore_' in key and 'C_Time' in key:
            core = int(re.search(r'\d+', key).group())
            cores.append(core)
            times.append(val)
            speedups.append(single_core / val)
            efficiencies.append((single_core / val) / core * 100)

    if not cores:
        print("No multi-core data found")
        return

    cores = sorted(cores)
    times = [times[cores.index(c)] for c in cores]
    speedups = [speedups[cores.index(c)] for c in cores]
    efficiencies = [efficiencies[cores.index(c)] for c in cores]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    ax1.plot(cores, speedups, 'b-o', linewidth=2, markersize=8)
    ax1.plot(cores, cores, 'r--', linewidth=1, label='Ideal Linear')
    ax1.set_xlabel('Number of Cores')
    ax1.set_ylabel('Speedup Factor')
    ax1.set_title('Multi-Core Speedup')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_xticks(cores)

    for x, y in zip(cores, speedups):
        ax1.annotate(f'{y:.1f}x', (x, y), textcoords="offset points", xytext=(0, 10), ha='center', fontsize=9)

    bars = ax2.bar(cores, efficiencies, color='steelblue', edgecolor='black')
    ax2.axhline(y=100, color='green', linestyle='--', label='Ideal (100%)')
    ax2.set_xlabel('Number of Cores')
    ax2.set_ylabel('Efficiency (%)')
    ax2.set_title('Core Utilization Efficiency')
    ax2.legend()
    ax2.set_xticks(cores)
    ax2.set_ylim(0, 110)

    for bar, eff in zip(bars, efficiencies):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2, f'{eff:.0f}%', ha='center', fontsize=9)

    plt.tight_layout()
    plt.savefig(f'{plot_dir}/cpu_scaling.png', dpi=150, bbox_inches='tight')
    print(f"Saved: {plot_dir}/cpu_scaling.png")

def generate_memory_plot(memory_file, plot_dir):
    """Generate memory benchmark plots from REAL data only"""
    if not os.path.exists(memory_file):
        print(f"Memory data not found: {memory_file}")
        return

    data = parse_key_value_file(memory_file)

    if not data:
        print("No memory data found")
        return

    seq_bw = data.get('SequentialCopy_BW', 0)
    stride_bw = data.get('StridedAccess_BW', 0)

    if seq_bw == 0 and stride_bw == 0:
        print("No memory bandwidth data found")
        return

    fig, ax = plt.subplots(1, 1, figsize=(8, 6))

    ax.bar(['Sequential\nAccess', 'Strided\nAccess'],
           [seq_bw if seq_bw > 0 else 0.1, stride_bw if stride_bw > 0 else 0.1],
           color=['#2ecc71', '#e74c3c'], edgecolor='black')
    ax.set_ylabel('Bandwidth (GB/s)')
    ax.set_title('Memory Bandwidth (Real Test)', fontsize=12, fontweight='bold')

    if seq_bw > 0:
        ax.text(0, seq_bw + 0.2, f'{seq_bw:.2f} GB/s', ha='center', fontsize=11, fontweight='bold')
    if stride_bw > 0:
        ax.text(1, stride_bw + 0.2, f'{stride_bw:.2f} GB/s', ha='center', fontsize=11, fontweight='bold')

    plt.tight_layout()
    plt.savefig(f'{plot_dir}/memory_pressure_benchmark.png', dpi=150, bbox_inches='tight')
    print(f"Saved: {plot_dir}/memory_pressure_benchmark.png")

def generate_thermal_plot(thermal_file, plot_dir):
    """Generate thermal throttling plot from REAL data - new format with thread counts"""
    if not os.path.exists(thermal_file):
        print("Thermal data not found, skipping")
        return

    data = parse_key_value_file(thermal_file)

    if not data:
        print("No thermal data found")
        return

    # Check if new format (thermal_Nt_early) or old format (iteration data)
    if 'thermal_2t_early' in data:
        # New format - aggregated by thread count
        thread_counts = []
        early_times = []
        mid_times = []
        late_times = []
        degradations = []

        for key in sorted(data.keys()):
            if key.startswith('thermal_') and key.endswith('_early'):
                threads = int(key.split('_')[1].replace('t', ''))
                thread_counts.append(threads)
                early_times.append(data[key])
                mid_times.append(data.get(f'thermal_{threads}t_mid', 0))
                late_times.append(data.get(f'thermal_{threads}t_late', 0))
                degradations.append(data.get(f'thermal_{threads}t_degradation', 0))

        if not thread_counts:
            print("No thermal data with thread counts found")
            return

        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        ax1 = axes[0]
        colors = ['green' if d < 2 else 'orange' if d < 5 else 'red' for d in degradations]
        bars = ax1.bar(range(len(thread_counts)), degradations, color=colors, edgecolor='black')
        ax1.set_xticks(range(len(thread_counts)))
        ax1.set_xticklabels([f'{t} threads' for t in thread_counts])
        ax1.set_ylabel('Thermal Degradation (%)')
        ax1.set_title('Thermal Throttling by Thread Count (120s test)')
        ax1.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax1.axhline(y=5, color='orange', linestyle='--', alpha=0.5, label='Moderate (5%)')
        ax1.axhline(y=10, color='red', linestyle='--', alpha=0.5, label='Significant (10%)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        for bar, deg in zip(bars, degradations):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
                    f'{deg:.1f}%', ha='center', fontsize=9)

        ax2 = axes[1]
        x = np.arange(len(thread_counts))
        width = 0.25

        ax2.bar(x - width, early_times, width, label='Early (0-40s)', color='lightgreen', edgecolor='black')
        ax2.bar(x, mid_times, width, label='Mid (40-80s)', color='lightyellow', edgecolor='black')
        ax2.bar(x + width, late_times, width, label='Late (80-120s)', color='lightcoral', edgecolor='black')

        ax2.set_xticks(x)
        ax2.set_xticklabels([f'{t}t' for t in thread_counts])
        ax2.set_ylabel('Time per Operation (ms)')
        ax2.set_xlabel('Thread Count')
        ax2.set_title('Performance Over Time by Thread Count')
        ax2.legend()
        ax2.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        plt.savefig(f'{plot_dir}/thermal_benchmark.png', dpi=150, bbox_inches='tight')
        print(f"Saved: {plot_dir}/thermal_benchmark.png")

        fig2, ax3 = plt.subplots(1, 1, figsize=(10, 6))
        ax3.plot(thread_counts, early_times, 'g-o', label='Early (0-40s)', linewidth=2, markersize=8)
        ax3.plot(thread_counts, mid_times, 'y-s', label='Mid (40-80s)', linewidth=2, markersize=8)
        ax3.plot(thread_counts, late_times, 'r-^', label='Late (80-120s)', linewidth=2, markersize=8)
        ax3.set_xlabel('Thread Count')
        ax3.set_ylabel('Time per Operation (ms)')
        ax3.set_title('Thermal Performance: Early vs Mid vs Late')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(f'{plot_dir}/thermal_benchmark_times.png', dpi=150, bbox_inches='tight')
        print(f"Saved: {plot_dir}/thermal_benchmark_times.png")
    else:
        print("Old thermal data format detected, skipping detailed plot")

def generate_daily_usage_plot(daily_file, plot_dir):
    """Generate daily usage plot from REAL data"""
    if not os.path.exists(daily_file):
        print(f"Daily usage data not found: {daily_file}")
        return

    scenarios = []

    with open(daily_file) as f:
        for line in f:
            if line.startswith('scenario'):
                continue
            parts = line.strip().split(',')
            if len(parts) >= 4:
                scenario = parts[0]
                try:
                    duration = float(parts[3])
                    mem_delta = float(parts[4]) if parts[4] else 0
                    scenarios.append((scenario, duration, mem_delta))
                except:
                    pass

    if not scenarios:
        print("No daily usage data found")
        return

    def get_scenario(name, default=0):
        for s in scenarios:
            if name in s[0]:
                return (s[1]*1000, s[2])
        return (default, 0)

    cold = get_scenario('ColdStart_Total')
    hot = get_scenario('HotStart_Total')
    browse = get_scenario('Browsing')
    ide = get_scenario('IDE')
    workflow = get_scenario('Workflow_Combined')

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    scenarios_names = ['Cold Start', 'Hot Start', 'Browser\n(10 tabs)', 'IDE\nWorkspace', 'Combined\nWorkflow']
    times_ms = [cold[0], hot[0], browse[0], ide[0], workflow[0]]
    mems = [cold[1], hot[1], browse[1], ide[1], workflow[1]]
    colors = ['lightblue', 'lightgreen', 'lightyellow', 'salmon', 'coral']

    bars = ax1.bar(scenarios_names, times_ms, color=colors, edgecolor='black')
    ax1.set_ylabel('Time (ms)')
    ax1.set_title('Application Start Time')
    ax1.axhline(y=1000, color='red', linestyle='--', label='1 second threshold')
    ax1.legend()

    for bar, val in zip(bars, times_ms):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(times_ms)*0.02,
                f'{val:.0f}ms', ha='center', fontsize=9)

    memory_vals = mems
    ax2.bar(scenarios_names, memory_vals, color=colors, edgecolor='black')
    ax2.set_ylabel('Memory Delta (MB)')
    ax2.set_title('Memory Usage by Scenario')
    ax2.axhline(y=16384, color='red', linestyle='--', label='16GB limit')

    plt.tight_layout()
    plt.savefig(f'{plot_dir}/daily_usage_benchmark.png', dpi=150, bbox_inches='tight')
    print(f"Saved: {plot_dir}/daily_usage_benchmark.png")

def generate_llm_plot(llm_file, plot_dir):
    """Generate LLM benchmark plot from REAL multi-model data"""
    if not os.path.exists(llm_file):
        print("LLM data not found, skipping")
        return

    sizes = []
    models = []
    mems = []
    latencies = []
    tps_values = []

    with open(llm_file) as f:
        for line in f:
            if line.startswith('model_size') or not line.strip():
                continue
            parts = line.strip().split(',')
            if len(parts) >= 6:
                sizes.append(parts[0])
                models.append(parts[1])
                mems.append(float(parts[2]))
                latencies.append(float(parts[3]))
                tps_values.append(float(parts[4]))

    if not sizes:
        print("No LLM data found")
        return

    # Sort by numeric size (0.6B, 1.7B, 4B, 8B, 14B not alphabetical)
    def get_size_num(size_label):
        return float(size_label.replace('B', ''))

    sorted_data = sorted(zip(sizes, models, mems, latencies, tps_values),
                         key=lambda x: get_size_num(x[0]))
    sizes, models, mems, latencies, tps_values = zip(*sorted_data)

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.patch.set_facecolor('white')

    colors_tps = sns.color_palette("RdYlGn_r", len(sizes))
    colors_eff = sns.color_palette("RdYlGn", len(sizes))

    ax1 = axes[0, 0]
    sns.barplot(x=list(sizes), y=list(tps_values), ax=ax1, palette=colors_tps,
                edgecolor='black', linewidth=0.5, hue=list(sizes), legend=False)
    ax1.set_xlabel('Model Size', fontsize=11)
    ax1.set_ylabel('Tokens/sec', fontsize=11)
    ax1.set_title('LLM Throughput by Model Size (Qwen3)', fontsize=12, fontweight='bold')
    ax1.axhline(y=30, color='orange', linestyle='--', alpha=0.7, label='Good (30 tok/s)')
    ax1.legend(loc='upper right')
    for bar, tps in zip(ax1.patches, tps_values):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                f'{tps:.1f}', ha='center', fontsize=9, fontweight='bold')

    ax2 = axes[0, 1]
    bars2 = ax2.bar(list(sizes), list(latencies), color=sns.color_palette("Blues_r", len(sizes)), edgecolor='black', linewidth=0.5)
    ax2.set_xlabel('Model Size', fontsize=11)
    ax2.set_ylabel('Seconds', fontsize=11)
    ax2.set_title('Average Latency by Model Size', fontsize=12, fontweight='bold')
    for bar, lat in zip(bars2, latencies):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                f'{lat:.1f}s', ha='center', fontsize=9, fontweight='bold')

    ax3 = axes[1, 0]
    bars3 = ax3.bar(list(sizes), list(mems), color=sns.color_palette("Purples_r", len(sizes)), edgecolor='black', linewidth=0.5)
    ax3.set_xlabel('Model Size', fontsize=11)
    ax3.set_ylabel('Memory (GB)', fontsize=11)
    ax3.set_title('Model Memory Requirements', fontsize=12, fontweight='bold')
    ax3.axhline(y=16, color='red', linestyle='--', linewidth=2, label='16GB (your device)')
    ax3.legend(loc='upper left')
    for bar, mem in zip(bars3, mems):
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                f'{mem:.0f}GB', ha='center', fontsize=9, fontweight='bold')

    ax4 = axes[1, 1]
    efficiency = [tps / m if m > 0 else 0 for tps, m in zip(tps_values, mems)]
    sns.barplot(x=list(sizes), y=efficiency, ax=ax4, palette=colors_eff,
                edgecolor='black', linewidth=0.5, hue=list(sizes), legend=False)
    ax4.set_xlabel('Model Size', fontsize=11)
    ax4.set_ylabel('TPS per GB Memory', fontsize=11)
    ax4.set_title('Efficiency (TPS / GB Memory)', fontsize=12, fontweight='bold')
    ax4.axhline(y=3, color='green', linestyle='--', alpha=0.7, label='Good efficiency (3)')
    ax4.legend(loc='upper right')
    for i, eff in enumerate(efficiency):
        ax4.text(i, eff + 0.5, f'{eff:.1f}', ha='center', fontsize=9, fontweight='bold')

    plt.tight_layout()
    plt.savefig(f'{plot_dir}/llm_benchmark.png', dpi=150, bbox_inches='tight')
    print(f"Saved: {plot_dir}/llm_benchmark.png")

def generate_geekbench_plot(gb_file, plot_dir):
    """Generate Geekbench AI benchmark plot from REAL data - CPU, GPU, Neural"""
    if not os.path.exists(gb_file):
        print("Geekbench AI data not found, skipping")
        return

    data = parse_key_value_file(gb_file)

    if not data:
        print("No Geekbench AI data found")
        return

    # Separate scores by backend
    cpu_scores = {}
    gpu_scores = {}
    neural_scores = {}

    for key, val in data.items():
        if key.startswith('cpu_'):
            cpu_scores[key.replace('cpu_', '')] = val
        elif key.startswith('gpu_'):
            gpu_scores[key.replace('gpu_', '')] = val
        elif key.startswith('neural_'):
            neural_scores[key.replace('neural_', '')] = val

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Plot 1: AI Scores Comparison (CPU vs GPU vs Neural)
    ax1 = axes[0, 0]
    score_types = ['ai_score', 'single_precision', 'half_precision', 'quantized']
    score_labels = ['AI Score', 'Single Prec', 'Half Prec', 'Quantized']

    labels = score_labels
    x = np.arange(len(labels))
    width = 0.25

    cpu_vals = [cpu_scores.get(st, 0) for st in score_types]
    gpu_vals = [gpu_scores.get(st, 0) for st in score_types]
    neural_vals = [neural_scores.get(st, 0) for st in score_types]

    bars1 = ax1.bar(x - width, cpu_vals, width, label='CPU', color='steelblue', edgecolor='black')
    bars2 = ax1.bar(x, gpu_vals, width, label='GPU', color='coral', edgecolor='black')
    bars3 = ax1.bar(x + width, neural_vals, width, label='Neural', color='green', edgecolor='black')
    ax1.set_ylabel('Score', fontsize=11)
    ax1.set_title('Geekbench AI: CPU vs GPU vs Neural', fontsize=12, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels)
    ax1.legend()
    ax1.set_yscale('log')

    # Plot 2: AI Score comparison (bar chart)
    ax2 = axes[0, 1]
    backends = ['CPU', 'GPU', 'Neural']
    ai_scores = [cpu_scores.get('ai_score', 0), gpu_scores.get('ai_score', 0), neural_scores.get('ai_score', 0)]
    colors = ['steelblue', 'coral', 'green']
    bars = ax2.bar(backends, ai_scores, color=colors, edgecolor='black')
    ax2.set_ylabel('AI Score', fontsize=11)
    ax2.set_title('AI Score by Backend', fontsize=12, fontweight='bold')
    for bar, val in zip(bars, ai_scores):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(ai_scores)*0.02,
                f'{val:.0f}', ha='center', fontsize=11, fontweight='bold')

    # Plot 3: Single Precision comparison
    ax3 = axes[1, 0]
    sp_scores = [cpu_scores.get('single_precision', 0), gpu_scores.get('single_precision', 0), neural_scores.get('single_precision', 0)]
    bars = ax3.bar(backends, sp_scores, color=colors, edgecolor='black')
    ax3.set_ylabel('Score', fontsize=11)
    ax3.set_title('Single Precision by Backend', fontsize=12, fontweight='bold')
    for bar, val in zip(bars, sp_scores):
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(sp_scores)*0.02,
                f'{val:.0f}', ha='center', fontsize=11, fontweight='bold')

    # Plot 4: Half Precision comparison
    ax4 = axes[1, 1]
    hp_scores = [cpu_scores.get('half_precision', 0), gpu_scores.get('half_precision', 0), neural_scores.get('half_precision', 0)]
    bars = ax4.bar(backends, hp_scores, color=colors, edgecolor='black')
    ax4.set_ylabel('Score', fontsize=11)
    ax4.set_title('Half Precision by Backend', fontsize=12, fontweight='bold')
    for bar, val in zip(bars, hp_scores):
        ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(hp_scores)*0.02,
                f'{val:.0f}', ha='center', fontsize=11, fontweight='bold')

    plt.tight_layout()
    plt.savefig(f'{plot_dir}/geekbench_ai_benchmark.png', dpi=150, bbox_inches='tight')
    print(f"Saved: {plot_dir}/geekbench_ai_benchmark.png")

    # Detailed workload breakdown plot
    fig2, axes2 = plt.subplots(4, 2, figsize=(14, 16))
    fig2.patch.set_facecolor('white')

    workloads = [
        ('pose_estimation', 'Pose Estimation'),
        ('style_transfer', 'Style Transfer'),
        ('image_segmentation', 'Image Segmentation'),
        ('object_detection', 'Object Detection'),
        ('face_detection', 'Face Detection'),
        ('depth_estimation', 'Depth Estimation'),
        ('super_resolution', 'Super Resolution'),
        ('text_classification', 'Text Classification'),
    ]

    backends = ['cpu', 'gpu', 'neural']
    backend_labels = ['CPU', 'GPU', 'Neural']
    backend_colors = ['steelblue', 'coral', 'green']

    for idx, (workload_key, workload_name) in enumerate(workloads):
        row = idx // 2
        col = idx % 2
        ax = axes2[row, col]

        sp_key = f'{workload_key}_sp'
        hp_key = f'{workload_key}_hp'

        sp_vals = [cpu_scores.get(sp_key, 0), gpu_scores.get(sp_key, 0), neural_scores.get(sp_key, 0)]
        hp_vals = [cpu_scores.get(hp_key, 0), gpu_scores.get(hp_key, 0), neural_scores.get(hp_key, 0)]

        x = np.arange(3)
        width = 0.35

        bars1 = ax.bar(x - width/2, sp_vals, width, label='Single Prec', color='steelblue', edgecolor='black', alpha=0.8)
        bars2 = ax.bar(x + width/2, hp_vals, width, label='Half Prec', color='coral', edgecolor='black', alpha=0.8)

        ax.set_ylabel('Score', fontsize=9)
        ax.set_title(workload_name, fontsize=10, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(backend_labels, fontsize=8)
        ax.set_yscale('log')
        ax.legend(fontsize=7, loc='upper left')

    plt.tight_layout()
    plt.savefig(f'{plot_dir}/geekbench_ai_workloads.png', dpi=150, bbox_inches='tight')
    print(f"Saved: {plot_dir}/geekbench_ai_workloads.png")

    # Machine Translation (LLM proxy) detailed plot
    fig3, ax3 = plt.subplots(1, 1, figsize=(10, 6))
    fig3.patch.set_facecolor('white')

    mt_sp = [cpu_scores.get('machine_translation_sp', 0), gpu_scores.get('machine_translation_sp', 0), neural_scores.get('machine_translation_sp', 0)]
    mt_hp = [cpu_scores.get('machine_translation_hp', 0), gpu_scores.get('machine_translation_hp', 0), neural_scores.get('machine_translation_hp', 0)]

    x = np.arange(3)
    width = 0.35
    ax3.bar(x - width/2, mt_sp, width, label='Single Prec', color='steelblue', edgecolor='black')
    ax3.bar(x + width/2, mt_hp, width, label='Half Prec', color='coral', edgecolor='black')
    ax3.set_ylabel('Score', fontsize=11)
    ax3.set_title('Machine Translation (LLM Task Proxy)', fontsize=12, fontweight='bold')
    ax3.set_xticks(x)
    ax3.set_xticklabels(['CPU', 'GPU', 'Neural'])
    ax3.legend()

    for i, (sp, hp) in enumerate(zip(mt_sp, mt_hp)):
        ax3.text(i - width/2, sp + 200, f'{sp:.0f}', ha='center', fontsize=9)
        ax3.text(i + width/2, hp + 200, f'{hp:.0f}', ha='center', fontsize=9)

    plt.tight_layout()
    plt.savefig(f'{plot_dir}/geekbench_ai_llm_proxy.png', dpi=150, bbox_inches='tight')
    print(f"Saved: {plot_dir}/geekbench_ai_llm_proxy.png")

def generate_memory_pressure_plot(mp_file, plot_dir):
    """Generate memory pressure benchmark plot from REAL data"""
    if not os.path.exists(mp_file):
        print("Memory pressure data not found, skipping")
        return

    scenarios = []
    mem_used = []

    with open(mp_file) as f:
        for line in f:
            if line.startswith('scenario') or not line.strip():
                continue
            parts = line.strip().split(',')
            if len(parts) >= 2:
                scenarios.append(parts[0])
                try:
                    mem_used.append(float(parts[1]))
                except:
                    pass

    if not scenarios:
        print("No memory pressure data found")
        return

    fig, ax = plt.subplots(1, 1, figsize=(10, 6))

    colors = plt.cm.Blues(np.linspace(0.3, 0.9, len(scenarios)))
    bars = ax.bar(scenarios, mem_used, color=colors, edgecolor='black')
    ax.set_xticklabels(scenarios, rotation=45, ha='right')
    ax.set_ylabel('Memory Used (MB)', fontsize=11)
    ax.set_xlabel('Scenario', fontsize=11)
    ax.set_title('Memory Pressure by Scenario', fontsize=12, fontweight='bold')
    ax.axhline(y=16384, color='red', linestyle='--', label='16GB limit')
    ax.legend()

    for bar, val in zip(bars, mem_used):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(mem_used)*0.02,
               f'{val:.0f}MB', ha='center', fontsize=9)

    plt.tight_layout()
    plt.savefig(f'{plot_dir}/memory_pressure_scenarios.png', dpi=150, bbox_inches='tight')
    print(f"Saved: {plot_dir}/memory_pressure_scenarios.png")

def main():
    if len(sys.argv) < 2:
        results_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/results'
    else:
        results_dir = sys.argv[1]

    results_dir = os.path.abspath(results_dir)
    plot_dir = os.path.join(results_dir, 'plots')
    ensure_dir(plot_dir)

    print(f"Generating plots from: {results_dir}")
    print(f"Output directory: {plot_dir}")
    print()

    cpu_file = os.path.join(results_dir, 'cpu_data.txt')
    memory_file = os.path.join(results_dir, 'memory_data.txt')
    memory_pressure_file = os.path.join(results_dir, 'memory_pressure_data.txt')
    thermal_file = os.path.join(results_dir, 'thermal_data.txt')
    daily_file = os.path.join(results_dir, 'daily_usage_data.txt')
    llm_file = os.path.join(results_dir, 'llm_data.txt')
    gb_file = os.path.join(results_dir, 'geekbench_ai_data.txt')

    generate_cpu_plot(cpu_file, plot_dir)
    generate_cpu_scaling_plot(cpu_file, plot_dir)
    generate_memory_plot(memory_file, plot_dir)
    generate_memory_pressure_plot(memory_pressure_file, plot_dir)
    generate_thermal_plot(thermal_file, plot_dir)
    generate_daily_usage_plot(daily_file, plot_dir)
    generate_llm_plot(llm_file, plot_dir)
    generate_geekbench_plot(gb_file, plot_dir)

    print()
    print("All plots generated from real data!")

if __name__ == '__main__':
    main()
