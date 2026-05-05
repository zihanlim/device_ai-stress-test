#!/usr/bin/env python3
import subprocess
import numpy as np
import time

results_dir = '/Users/airnold/Developer/Stress_Test/ai_device_benchmark/results'
mem_data = f'{results_dir}/memory_pressure_data.txt'

def get_swap():
    result = subprocess.run(['sysctl', 'vm.swapusage'], capture_output=True, text=True)
    output = result.stdout
    if isinstance(output, str):
        pass
    else:
        output = output.decode()
    import re
    match = re.search(r'\+\s*([\d.]+)M', output)
    return float(match.group(1)) if match else 0.0

total_mem = subprocess.run(['sysctl', '-n', 'hw.memsize'], capture_output=True, text=True)
total_mb = int(total_mem.stdout.strip()) / 1024 / 1024

print(f"Total system memory: {total_mb:.0f} MB")

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

    print("Touching all pages...")
    step = max(1, len(arr) // 100)
    for i in range(0, len(arr), step):
        arr[i] = i % 256

    swap_after = get_swap()
    print(f"Swap after allocation: {swap_after:.0f} MB")
    print(f"Swap delta: {swap_after - swap_before:.0f} MB")

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
finally:
    if arr is not None:
        try:
            del arr
        except:
            pass

print(f"Data written to: {mem_data}")