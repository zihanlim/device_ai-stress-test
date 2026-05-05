#!/usr/bin/env python3
"""
Thermal Throttling Benchmark - 5 minute sustained load test
Run directly: python3 thermal_benchmark.py [results_dir]
"""
import time
import numpy as np
import subprocess
import threading
import sys
import os

def main():
    if len(sys.argv) < 2:
        results_dir = os.path.dirname(os.path.abspath(__file__)) + '/../results'
    else:
        results_dir = sys.argv[1]

    THERMAL_DATA = os.path.join(results_dir, 'thermal_data.txt')
    PLOT_DIR = os.path.join(results_dir, 'plots')
    os.makedirs(PLOT_DIR, exist_ok=True)

    # Data collection
    times = []
    cpu_freqs = []
    stop_flag = False

    def monitor_system():
        """Monitor CPU frequency in background"""
        global stop_flag
        while not stop_flag:
            try:
                result = subprocess.run(['sysctl', '-n', 'hw.cpufrequency'], capture_output=True, text=True)
                output = result.stdout.decode() if isinstance(result.stdout, bytes) else result.stdout
                freq_hz = int(output.strip())
                freq_ghz = freq_hz / 1e9
                cpu_freqs.append(freq_ghz)
            except:
                cpu_freqs.append(0)
            time.sleep(5)  # Sample every 5 seconds

    print("Running sustained CPU load (5 minutes)...")

    # Start monitoring thread
    monitor = threading.Thread(target=monitor_system)
    monitor.start()

    iteration = 0
    start_time = time.time()

    # Initial intense phase (first 30 seconds)
    print("Phase A: Initial burst (30s)...")
    for i in range(30):
        iter_start = time.time()
        x = np.random.rand(500, 500)
        y = np.random.rand(500, 500)
        z = np.dot(x, y)
        _ = np.sum(z)
        elapsed = time.time() - iter_start
        times.append(elapsed * 1000)
        if i % 5 == 0:
            elapsed_total = time.time() - start_time
            print(f"  {elapsed_total:.0f}s: {elapsed*1000:.1f} ms/op")
        iteration += 1

    # Sustained phase (4.5 minutes = 270 seconds total)
    print("\nPhase B: Sustained load (4.5 min)...")
    sample_count = 0
    while time.time() - start_time < 300:  # 5 minutes total
        iter_start = time.time()
        x = np.random.rand(400, 400)
        y = np.random.rand(400, 400)
        z = np.dot(x, y)
        _ = np.sum(z)
        elapsed = time.time() - iter_start
        times.append(elapsed * 1000)

        sample_count += 1
        if sample_count % 20 == 0:  # Print every ~20 seconds
            elapsed_total = time.time() - start_time
            avg_recent = np.mean(times[-20:])
            print(f"  {elapsed_total:.0f}s: {elapsed*1000:.1f} ms/op (avg recent: {avg_recent:.1f} ms)")

    # Stop monitoring
    stop_flag = True
    monitor.join()

    # Analysis
    print("\n" + "="*50)
    print("THERMAL THROTTLING ANALYSIS")
    print("="*50)

    # Divide into phases
    n = len(times)
    phase1 = times[:30] if len(times) >= 30 else times
    phase2 = times[30:90] if len(times) > 30 else []
    phase3 = times[90:] if len(times) > 90 else []

    if len(phase1) > 0:
        print(f"\nPhase 1 (0-30s):  avg = {np.mean(phase1):.1f} ms/op")
    if len(phase2) > 0:
        print(f"Phase 2 (30-90s): avg = {np.mean(phase2):.1f} ms/op")
    if len(phase3) > 0:
        print(f"Phase 3 (90s+):  avg = {np.mean(phase3):.1f} ms/op")

    # Calculate throttling
    if len(phase1) > 0 and len(phase3) > 0 and np.mean(phase1) > 0:
        phase3_drop = (1 - np.mean(phase3) / np.mean(phase1)) * 100
        print(f"\nPerformance drop Phase 1 -> Phase 3: {phase3_drop:.1f}%")

        if phase3_drop > 20:
            print("\n⚠️  SIGNIFICANT THROTTLING DETECTED (>20% drop)")
        elif phase3_drop > 10:
            print("\n⚡ MODERATE THROTTLING (10-20% drop)")
        else:
            print("\n✓ MINIMAL THROTTLING (<10% drop)")

    # Save ALL data to thermal_data.txt
    with open(THERMAL_DATA, "w") as f:
        # Header
        f.write("metric,value\n")

        # Phase summaries
        if len(phase1) > 0:
            f.write(f"phase1_avg,{np.mean(phase1):.4f}\n")
        if len(phase2) > 0:
            f.write(f"phase2_avg,{np.mean(phase2):.4f}\n")
        if len(phase3) > 0:
            f.write(f"phase3_avg,{np.mean(phase3):.4f}\n")
        if len(phase1) > 0 and len(phase3) > 0:
            f.write(f"phase3_drop_pct,{phase3_drop:.2f}\n")

        # CPU frequency stats
        valid_freqs = [f for f in cpu_freqs if f > 0]
        if valid_freqs:
            f.write(f"freq_initial,{valid_freqs[0]:.2f}\n")
            f.write(f"freq_avg,{np.mean(valid_freqs):.2f}\n")
            f.write(f"freq_min,{np.min(valid_freqs):.2f}\n")
            f.write(f"freq_final,{valid_freqs[-1]:.2f}\n")

        # All iteration times
        f.write("\niteration,time_ms,phase\n")
        for i, t in enumerate(times):
            if i < 30:
                phase = "initial"
            elif i < 90:
                phase = "rampdown"
            else:
                phase = "sustained"
            f.write(f"{i},{t:.2f},{phase}\n")

        # All frequency samples
        if cpu_freqs:
            f.write("\nfrequency_sample,freq_ghz,elapsed_seconds\n")
            for i, freq in enumerate(cpu_freqs):
                f.write(f"{i},{freq:.2f},{i*5}\n")

    print(f"\nData saved to: {THERMAL_DATA}")

if __name__ == '__main__':
    main()