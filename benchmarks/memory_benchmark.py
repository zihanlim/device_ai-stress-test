#!/usr/bin/env python3
"""
Memory Benchmark - Bandwidth, Capacity, and Pressure
Run directly: python3 memory_benchmark.py [results_dir]
"""
import time
import numpy as np
import subprocess
import sys
import os

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

    MEM_DATA = os.path.join(results_dir, 'memory_data.txt')

    # Get system memory
    result = subprocess.run(['sysctl', '-n', 'hw.memsize'], capture_output=True, text=True)
    total_mem_str = result.stdout.decode() if isinstance(result.stdout, bytes) else result.stdout
    total_mem = int(total_mem_str.strip())
    total_mem_mb = total_mem / 1024 / 1024
    total_mem_gb = total_mem / 1024 / 1024 / 1024

    print(f"Total Memory: {total_mem_gb:.1f} GB ({total_mem_mb:.0f} MB)")

    # Clear/create memory data file
    with open(MEM_DATA, "w") as f:
        f.write("test,value,unit\n")
        f.write(f"TotalMemory_MB,{total_mem_mb:.0f},MB\n")
        f.write(f"TotalMemory_GB,{total_mem_gb:.1f},GB\n")

    print("--- Memory Bandwidth Test ---")
    print("Running memory copy/allocate test...")

    # Test 1: Memory allocation speed
    print("\nAllocation speed:")
    for size in [10**6, 10**7, 10**8]:
        start = time.time()
        arr = np.zeros(size, dtype=np.float64)
        alloc_time = time.time() - start
        print(f"  Allocate {size:,} float64s: {alloc_time*1000:.2f} ms")
        with open(MEM_DATA, "a") as f:
            f.write(f"Alloc_{size},{alloc_time*1000:.4f},ms\n")

    # Test 2: Sequential copy bandwidth
    print("\nSequential copy bandwidth:")
    size = 10**8
    arr1 = np.random.rand(size)
    arr2 = np.empty(size)

    start = time.time()
    arr2[:] = arr1[:]
    copy_time = time.time() - start
    bw_seq = (size * 8) / copy_time / 1024**3  # GB/s
    print(f"  Sequential copy: {bw_seq:.2f} GB/s")
    with open(MEM_DATA, "a") as f:
        f.write(f"SequentialCopy_BW,{bw_seq:.4f},GB/s\n")

    # Test 3: Strided access bandwidth
    print("\nStrided access bandwidth:")
    stride = 1000
    start = time.time()
    result = arr1[::stride].sum()
    stride_time = time.time() - start
    bw_stride = (size / stride * 8) / stride_time / 1024**3
    print(f"  Strided access: {bw_stride:.2f} GB/s")
    with open(MEM_DATA, "a") as f:
        f.write(f"StridedAccess_BW,{bw_stride:.4f},GB/s\n")

    print("\n--- Memory Pressure Test ---")

    # Get initial swap
    initial_swap = get_swap_mb()
    print(f"Initial swap usage: {initial_swap:.0f} MB")
    with open(MEM_DATA, "a") as f:
        f.write(f"Initial_Swap,{initial_swap:.2f},MB\n")

    # Memory pressure test - allocate 80%
    print(f"\nAllocating 80% of memory ({int(0.8 * total_mem_mb)} MB)...")
    target_mb = int(total_mem_mb * 0.8)

    try:
        start = time.time()
        arr = np.zeros(int(target_mb * 1024 * 1024 / 8), dtype=np.float64)
        alloc_time = time.time() - start

        # Touch all pages
        print("Touching all pages...")
        step = max(1, len(arr) // 100)
        for i in range(0, len(arr), step):
            arr[i] = i % 256

        mid_swap = get_swap_mb()
        mid_time = time.time() - start

        print(f"  Allocation time: {mid_time:.2f}s")
        print(f"  Swap after allocation: {mid_swap:.0f} MB")
        with open(MEM_DATA, "a") as f:
            f.write(f"Pressure_AllocTime,{mid_time:.4f},s\n")
            f.write(f"Pressure_SwapAfter,{mid_swap:.2f},MB\n")

        # Free and check swap recovery
        del arr
        final_swap = get_swap_mb()
        print(f"  Swap after free: {final_swap:.0f} MB")
        with open(MEM_DATA, "a") as f:
            f.write(f"Pressure_SwapFinal,{final_swap:.2f},MB\n")

    except MemoryError as e:
        print(f"  MemoryError: {e}")
        with open(MEM_DATA, "a") as f:
            f.write(f"Pressure_Error,MemoryError,OOM\n")

    print("\n--- Swap Behavior Test ---")
    print("Testing swap under increasing load...")

    for load_percent in [20, 40, 60, 80]:
        target = int(total_mem_mb * load_percent / 100)
        print(f"  {load_percent}% load ({target} MB)...", end=" ")
        try:
            arr = np.zeros(int(target * 1024 * 1024 / 8), dtype=np.float64)
            arr[:] = 1  # Touch pages
            swap = get_swap_mb()
            print(f"swap: {swap:.0f} MB")
            with open(MEM_DATA, "a") as f:
                f.write(f"SwapTest_{load_percent}pct,{swap:.2f},MB\n")
            del arr
        except MemoryError:
            print("failed (OOM)")
            with open(MEM_DATA, "a") as f:
                f.write(f"SwapTest_{load_percent}pct,OOM,error\n")
            break

    print("\nMemory Benchmark complete. Data saved to:", MEM_DATA)

if __name__ == '__main__':
    main()