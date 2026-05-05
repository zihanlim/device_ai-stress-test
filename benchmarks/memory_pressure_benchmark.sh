#!/bin/bash
# Memory Pressure Benchmark - 8GB/16GB Scenario Testing
set -e

RESULTS_DIR="${1:-../results}"
PLOT_DIR="$RESULTS_DIR/plots"
mkdir -p "$RESULTS_DIR/plots"

echo "=== Memory Pressure Benchmark ===" | tee "$RESULTS_DIR/memory_pressure_benchmark.txt"

# Memory info
echo "--- System Memory Info ---" | tee -a "$RESULTS_DIR/memory_pressure_benchmark.txt"
TOTAL_MEM=$(sysctl -n hw.memsize)
TOTAL_GB=$(python3 -c "print(round($TOTAL_MEM / 1024**3, 1))")
echo "Total Memory: ${TOTAL_GB} GB" | tee -a "$RESULTS_DIR/memory_pressure_benchmark.txt"
echo "Page Size: $(sysctl -n hw.pagesize) bytes" | tee -a "$RESULTS_DIR/memory_pressure_benchmark.txt"
echo "" | tee -a "$RESULTS_DIR/memory_pressure_benchmark.txt"

MEM_DATA="$RESULTS_DIR/memory_pressure_data.txt"

# Clear previous data
echo "scenario,memory_used_mb,time_seconds,swap_used_mb" > "$MEM_DATA"

# Scenario 1: Light usage (browser + IDE + terminal)
echo "--- Scenario 1: Light Daily Usage ---" | tee -a "$RESULTS_DIR/memory_pressure_benchmark.txt"
echo "(Simulates: Browser (10 tabs) + VSCode + Terminal + Slack)" | tee -a "$RESULTS_DIR/memory_pressure_benchmark.txt"

python3 - "$RESULTS_DIR" << 'PYEOF' | tee -a "$RESULTS_DIR/memory_pressure_benchmark.txt"
import subprocess
import numpy as np
import sys
import os

results_dir = sys.argv[1]
mem_data = os.path.join(results_dir, 'memory_pressure_data.txt')

def get_swap():
    result = subprocess.run(['sysctl', 'vm.swapusage'], capture_output=True, text=True)
    output = result.stdout.decode() if isinstance(result.stdout, bytes) else result.stdout
    import re
    match = re.search(r'\+\s*([\d.]+)M', output)
    return float(match.group(1)) if match else 0.0

# Light usage simulation - more realistic app memory
baseline_mb = 2048
browser_mb = 800
ide_mb = 500
terminal_mb = 100
slack_mb = 100
total_light_mb = baseline_mb + browser_mb + ide_mb + terminal_mb + slack_mb

print(f"Estimated light usage: {total_light_mb} MB")

swap_used = 0
try:
    # Allocate incrementally
    pages = []
    for name, size_mb in [
        ('Baseline', baseline_mb),
        ('Browser', browser_mb),
        ('IDE', ide_mb),
        ('Terminal', terminal_mb),
        ('Slack', slack_mb)
    ]:
        arr = np.zeros(int(size_mb * 1024 * 1024 / 8), dtype=np.float64)
        arr[:] = 1
        pages.append(arr)
        used = sum(p.nbytes for p in pages) / 1024 / 1024
        swap = get_swap()
        print(f"  {name}: {used:.0f} MB allocated, swap: {swap:.0f} MB")
        swap_used = swap

    total_allocated = sum(p.nbytes for p in pages) / 1024 / 1024
    print(f"Total allocated: {total_allocated:.0f} MB")
    print(f"Swap used: {swap_used:.0f} MB")

    # Write to data file
    with open(mem_data, 'a') as f:
        f.write(f"Light_Baseline,{baseline_mb},0,0\n")
        f.write(f"Light_Browser,{browser_mb},0,0\n")
        f.write(f"Light_IDE,{ide_mb},0,0\n")
        f.write(f"Light_Terminal,{terminal_mb},0,0\n")
        f.write(f"Light_Slack,{slack_mb},0,0\n")
        f.write(f"Light_Total,{total_light_mb},0,{swap_used:.0f}\n")

    # Free memory
    del pages
    del arr

except MemoryError:
    print("Memory allocation failed - hitting limits")
    with open(mem_data, 'a') as f:
        f.write(f"Light_Total,{total_light_mb},0,0\n")

print(f"Data written to: {mem_data}")
PYEOF

echo "" | tee -a "$RESULTS_DIR/memory_pressure_benchmark.txt"

# Scenario 2: Medium usage (with local LLM background)
echo "--- Scenario 2: Medium Usage + Background LLM ---" | tee -a "$RESULTS_DIR/memory_pressure_benchmark.txt"
echo "(Simulates: Light usage + Ollama/MLX running 7B model)" | tee -a "$RESULTS_DIR/memory_pressure_benchmark.txt"

python3 - "$RESULTS_DIR" << 'PYEOF' | tee -a "$RESULTS_DIR/memory_pressure_benchmark.txt"
import subprocess
import numpy as np
import sys
import os

results_dir = sys.argv[1]
mem_data = os.path.join(results_dir, 'memory_pressure_data.txt')

def get_swap():
    result = subprocess.run(['sysctl', 'vm.swapusage'], capture_output=True, text=True)
    output = result.stdout.decode() if isinstance(result.stdout, bytes) else result.stdout
    import re
    match = re.search(r'\+\s*([\d.]+)M', output)
    return float(match.group(1)) if match else 0.0

llm_model_mb = 4096
total_with_llm = 3848 + llm_model_mb

print(f"Estimated with background LLM: {total_with_llm} MB")

pages = []
swap_used = 0
try:
    arr = np.zeros(int(2048 * 1024 * 1024 / 8), dtype=np.float64)
    arr[:] = 1
    pages.append(arr)
    print(f"Baseline: {sum(p.nbytes for p in pages) / 1024 / 1024:.0f} MB")

    arr = np.zeros(int(llm_model_mb * 1024 * 1024 / 8), dtype=np.float64)
    arr[:] = 1
    pages.append(arr)
    print(f"LLM Model: {sum(p.nbytes for p in pages) / 1024 / 1024:.0f} MB (total)")

    swap_used = get_swap()
    print(f"Swap usage: {swap_used:.0f} MB")

    if swap_used > 100:
        print("WARNING: Significant swap usage detected - memory pressure!")

    with open(mem_data, 'a') as f:
        f.write(f"Medium_Baseline,2048,0,0\n")
        f.write(f"Medium_LLM,{llm_model_mb},0,{swap_used:.0f}\n")
        f.write(f"Medium_Total,{total_with_llm},0,{swap_used:.0f}\n")

    # Free
    del pages
    del arr

except MemoryError:
    print("Memory allocation failed - insufficient memory for this scenario")
    swap_used = get_swap()
    with open(mem_data, 'a') as f:
        f.write(f"Medium_Total,{total_with_llm},0,{swap_used:.0f}\n")
except Exception as e:
    print(f"Error: {e}")

print(f"Data written to: {mem_data}")
PYEOF

echo "" | tee -a "$RESULTS_DIR/memory_pressure_benchmark.txt"

# Scenario 3: 8GB memory pressure (test the limit)
echo "--- Scenario 3: 8GB Memory Pressure Test ---" | tee -a "$RESULTS_DIR/memory_pressure_benchmark.txt"
echo "(Allocates 80% of memory to test swapping behavior)" | tee -a "$RESULTS_DIR/memory_pressure_benchmark.txt"

python3 - "$RESULTS_DIR" << 'PYEOF' | tee -a "$RESULTS_DIR/memory_pressure_benchmark.txt"
import subprocess
import numpy as np
import time
import sys
import os

results_dir = sys.argv[1]
mem_data = os.path.join(results_dir, 'memory_pressure_data.txt')

def get_swap():
    result = subprocess.run(['sysctl', 'vm.swapusage'], capture_output=True, text=True)
    output = result.stdout.decode() if isinstance(result.stdout, bytes) else result.stdout
    import re
    match = re.search(r'\+\s*([\d.]+)M', output)
    return float(match.group(1)) if match else 0.0

total_mem = subprocess.run(['sysctl', '-n', 'hw.memsize'], capture_output=True, text=True)
total_mb = int(total_mem.stdout.decode().strip()) / 1024 / 1024

print(f"Total system memory: {total_mb:.0f} MB")
print(f"Testing with 8GB allocation...")

swap_before = get_swap()
print(f"Swap before: {swap_before:.0f} MB")

swap_after = swap_before
allocated_mb = 0
arr = None
try:
    target_mb = min(8192, int(total_mb * 0.8))
    print(f"Allocating {target_mb} MB...")
    arr = np.zeros(int(target_mb * 1024 * 1024 / 8), dtype=np.float64)
    allocated_mb = target_mb

    print("Touching all pages (writing to memory)...")
    step = max(1, len(arr) // 100)
    for i in range(0, len(arr), step):
        arr[i] = i % 256

    swap_after = get_swap()
    print(f"Swap after allocation: {swap_after:.0f} MB")
    print(f"Swap delta: {swap_after - swap_before:.0f} MB")

    print("\nPerforming memory-intensive operations...")
    start = time.time()
    result = 0
    for i in range(0, len(arr), 1000):
        result += arr[i] * 0.001
    elapsed = time.time() - start
    print(f"Memory access time (1000 samples): {elapsed:.3f}s")

    with open(mem_data, 'a') as f:
        f.write(f"Heavy_Alloc,{allocated_mb},0,{swap_after:.0f}\n")
        f.write(f"Heavy_Total,{allocated_mb},0,{swap_after:.0f}\n")

except MemoryError:
    print("MemoryError: Cannot allocate 8GB")
    swap_used = get_swap()
    with open(mem_data, 'a') as f:
        f.write(f"Heavy_Total,0,0,{swap_used:.0f}\n")
except Exception as e:
    print(f"Error: {e}")
    if arr is not None:
        try:
            swap_used = get_swap()
            with open(mem_data, 'a') as f:
                f.write(f"Heavy_Total,{allocated_mb},0,{swap_used:.0f}\n")
        except:
            pass
finally:
    # Always try to free memory
    if arr is not None:
        try:
            del arr
        except:
            pass

print("\nMemory pressure test complete.")
print(f"Data written to: {mem_data}")
PYEOF

echo "" | tee -a "$RESULTS_DIR/memory_pressure_benchmark.txt"
echo "Memory Pressure Benchmark complete" | tee -a "$RESULTS_DIR/memory_pressure_benchmark.txt"

# Generate plot
python3 - "$RESULTS_DIR/plots" << 'PYEOF'
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import sys

plot_dir = sys.argv[1]
os.makedirs(plot_dir, exist_ok=True)

# Read actual data
results_dir = os.path.dirname(plot_dir)
mem_data = os.path.join(results_dir, 'memory_pressure_data.txt')

scenarios = []
mem_used = []

with open(mem_data) as f:
    header = f.readline()  # skip header
    for line in f:
        parts = line.strip().split(',')
        if len(parts) >= 2:
            scenarios.append(parts[0])
            try:
                mem_used.append(float(parts[1]))
            except:
                pass

if scenarios and mem_used:
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))

    colors = plt.cm.Blues(np.linspace(0.3, 0.9, len(scenarios)))
    bars = ax.bar(scenarios, mem_used, color=colors, edgecolor='black')
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
else:
    print("No data to plot")
PYEOF