#!/usr/bin/env python3
"""
Daily Usage Benchmark - Real-World Workflow Simulation
Run directly: python3 daily_usage_benchmark.py [results_dir]
"""
import time
import numpy as np
import subprocess
import sys
import os
import resource

def get_memory_mb():
    """Get current memory usage in MB (RSS)"""
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024

def get_swap_mb():
    """Get current swap usage in MB"""
    try:
        result = subprocess.run(['sysctl', 'vm.swapusage'], capture_output=True, text=True)
        output = result.stdout.decode() if isinstance(result.stdout, bytes) else result.stdout
        import re
        match = re.search(r'\+\s*([\d.]+)M', output)
        if match:
            return float(match.group(1))
        return 0.0
    except:
        return 0.0

def main():
    if len(sys.argv) < 2:
        results_dir = os.path.dirname(os.path.abspath(__file__)) + '/../results'
    else:
        results_dir = sys.argv[1]

    DAILY_DATA = os.path.join(results_dir, 'daily_usage_data.txt')

    # Get baseline
    baseline_mem = get_memory_mb()
    baseline_swap = get_swap_mb()

    print("--- System Memory ---")
    print(f"Baseline memory: {baseline_mem:.0f} MB")
    print(f"Baseline swap: {baseline_swap:.0f} MB")

    # Clear/create daily usage data file
    with open(DAILY_DATA, "w") as f:
        f.write("scenario,start_time_s,end_time_s,duration_s,memory_delta_mb,swap_delta_mb\n")
        f.write(f"baseline,0,{time.time():.2f},0,{baseline_mem:.0f},{baseline_swap:.0f}\n")

    print("\n--- Scenario 1: Cold Start Simulation ---")
    print("(Simulates fresh machine startup sequence)")

    scenarios = []

    # Step 1: Python environment startup
    start = time.time()
    import numpy as np
    import json
    env_time = time.time() - start
    print(f"  Python import: {env_time*1000:.0f}ms")
    scenarios.append(("ColdStart_Python", 0, env_time, env_time, 0, 0))

    # Step 2: Array allocations (simulate loading libraries)
    start = time.time()
    arr1 = np.random.rand(1000, 1000)
    load_time = time.time() - start
    mem_delta = (arr1.nbytes / 1024 / 1024)
    print(f"  Data structures: {load_time*1000:.0f}ms ({mem_delta:.0f}MB)")
    scenarios.append(("ColdStart_DataLoad", env_time, load_time + env_time, load_time, mem_delta, 0))
    del arr1

    # Step 3: File system operations (simulate project loading)
    start = time.time()
    for i in range(20):
        _ = np.random.rand(100, 100)
    fs_time = time.time() - start
    print(f"  Project files: {fs_time*1000:.0f}ms")
    scenarios.append(("ColdStart_FileOps", load_time + env_time, fs_time + load_time + env_time, fs_time, 0, 0))

    # Record cold start total
    total_cold = sum(s[3] for s in scenarios)
    print(f"  Total cold start: {total_cold*1000:.0f}ms")
    with open(DAILY_DATA, "a") as f:
        f.write(f"ColdStart_Total,0,{time.time():.2f},{total_cold:.4f},{get_memory_mb()-baseline_mem:.0f},{get_swap_mb()-baseline_swap:.0f}\n")

    print("\n--- Scenario 2: Hot Start Simulation ---")
    print("(Simulates resuming from warm state)")

    # Already warm - just small operations
    start = time.time()
    _ = np.random.rand(100, 100)
    hot_time = time.time() - start
    print(f"  Hot resume: {hot_time*1000:.0f}ms")
    with open(DAILY_DATA, "a") as f:
        f.write(f"HotStart_Total,{time.time():.2f},{time.time():.2f},{hot_time:.4f},{get_memory_mb()-baseline_mem:.0f},{get_swap_mb()-baseline_swap:.0f}\n")

    print("\n--- Scenario 3: Simulated Browser Tabs ---")
    print("(Memory for 10 browser tabs)")

    start = time.time()
    browser_arrays = []
    for i in range(10):
        arr = np.random.rand(1000, 1000)  # ~8MB per "tab"
        browser_arrays.append(arr)
    browser_time = time.time() - start
    browser_mem = sum(a.nbytes for a in browser_arrays) / 1024 / 1024
    print(f"  10 tabs allocated: {browser_time*1000:.0f}ms ({browser_mem:.0f}MB)")
    with open(DAILY_DATA, "a") as f:
        f.write(f"Browsing_10Tabs,{time.time():.2f},{time.time():.2f},{browser_time:.4f},{browser_mem:.0f},{get_swap_mb()-baseline_swap:.0f}\n")

    # Cleanup
    del browser_arrays

    print("\n--- Scenario 4: IDE Simulation ---")
    start = time.time()
    ide_arr = np.random.rand(5000, 5000)  # ~200MB IDE-like
    ide_time = time.time() - start
    ide_mem = ide_arr.nbytes / 1024 / 1024
    print(f"  IDE workspace: {ide_time*1000:.0f}ms ({ide_mem:.0f}MB)")
    with open(DAILY_DATA, "a") as f:
        f.write(f"IDE_Workspace,{time.time():.2f},{time.time():.2f},{ide_time:.4f},{ide_mem:.0f},{get_swap_mb()-baseline_swap:.0f}\n")

    print("\n--- Scenario 5: Combined Workflow (Browser + IDE + Terminal) ---")
    start = time.time()

    # Browser
    browser = [np.random.rand(1000, 1000) for _ in range(5)]
    browser_mem = sum(a.nbytes for a in browser) / 1024 / 1024

    # IDE
    ide = np.random.rand(5000, 5000)
    ide_mem = ide.nbytes / 1024 / 1024

    # Terminal (small)
    term = np.random.rand(100, 100)

    # Active work simulation
    for _ in range(10):
        _ = np.dot(browser[0], ide[:1000, :1000])

    workflow_time = time.time() - start
    total_workflow_mem = (browser_mem + ide_mem + term.nbytes / 1024 / 1024)
    swap_usage = get_swap_mb() - baseline_swap

    print(f"  Combined workflow: {workflow_time*1000:.0f}ms")
    print(f"  Total memory: {total_workflow_mem:.0f}MB")
    print(f"  Swap used: {swap_usage:.0f}MB")
    with open(DAILY_DATA, "a") as f:
        f.write(f"Workflow_Combined,{time.time():.2f},{time.time():.2f},{workflow_time:.4f},{total_workflow_mem:.0f},{swap_usage:.0f}\n")

    # Cleanup
    del browser, ide, term

    print("\n--- Memory Summary ---")
    final_mem = get_memory_mb()
    final_swap = get_swap_mb()
    print(f"Final memory: {final_mem:.0f} MB")
    print(f"Final swap: {final_swap:.0f} MB")
    print(f"Memory delta: {final_mem - baseline_mem:.0f} MB")
    print(f"Swap delta: {final_swap - baseline_swap:.0f} MB")

    # Save summary
    with open(DAILY_DATA, "a") as f:
        f.write(f"\nsummary\n")
        f.write(f"baseline_memory_mb,{baseline_mem:.0f}\n")
        f.write(f"final_memory_mb,{final_mem:.0f}\n")
        f.write(f"memory_delta_mb,{final_mem - baseline_mem:.0f}\n")
        f.write(f"baseline_swap_mb,{baseline_swap:.0f}\n")
        f.write(f"final_swap_mb,{final_swap:.0f}\n")
        f.write(f"swap_delta_mb,{final_swap - baseline_swap:.0f}\n")

    print("\nDaily Usage Benchmark complete. Data saved to:", DAILY_DATA)

if __name__ == '__main__':
    main()