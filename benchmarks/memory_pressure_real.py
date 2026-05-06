#!/usr/bin/env python3
"""
Real Memory Pressure Benchmark - Actual App Measurement
Measures memory usage with real applications, not synthetic allocations.

Scenarios:
1. Idle baseline
2. Browser only (Chrome with 10 work URLs)
3. IDE only (VS Code with device_ai-stress-test repo)
4. Light dev (VS Code + Terminal + Browser 3 tabs)
5. Daily dev (VS Code + Browser 10 tabs + Terminal)
6. Daily + Claude Code (Daily dev + claude CLI)
7. Daily + 0.6B LLM (Daily dev + ollama qwen3:0.6b)
8. Daily + 1.7B LLM (Daily dev + ollama qwen3:1.7b)
9. Daily + 4B LLM (Daily dev + ollama qwen3:4b)
10. Daily + 8B LLM (Daily dev + ollama qwen3:8b)
11b. Daily + dual LLMs (Daily dev + qwen3:0.6b + qwen3:1.7b simultaneously)

Measures via: ps, vm_stat, memory_pressure, sysctl
Accounts for 16KB page size on Apple Silicon
"""

import subprocess
import json
import time
import os
import sys
import re
from pathlib import Path
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.benchmark_logger import BenchmarkLogger, get_device_info

# Apple Silicon page size: 16KB (16384 bytes)
PAGE_SIZE = 16384

def get_memory_metrics():
    """Get memory metrics from vm_stat and memory_pressure"""
    metrics = {}

    # Get vm_stat data
    try:
        result = subprocess.run(['vm_stat'], capture_output=True, text=True)
        for line in result.stdout.split('\n'):
            if 'Pages free' in line:
                match = re.search(r'(\d+)', line)
                if match:
                    metrics['pages_free'] = int(match.group(1))
            elif 'Pages active' in line:
                match = re.search(r'(\d+)', line)
                if match:
                    metrics['pages_active'] = int(match.group(1))
            elif 'Pages inactive' in line:
                match = re.search(r'(\d+)', line)
                if match:
                    metrics['pages_inactive'] = int(match.group(1))
            elif 'Pages wired down' in line:
                match = re.search(r'(\d+)', line)
                if match:
                    metrics['pages_wired'] = int(match.group(1))
            elif 'Pages occupied by compressor' in line:
                match = re.search(r'(\d+)', line)
                if match:
                    metrics['pages_compressed'] = int(match.group(1))
    except:
        pass

    # Get memory_pressure data
    try:
        result = subprocess.run(['memory_pressure'], capture_output=True, text=True)
        for line in result.stdout.split('\n'):
            if 'System-wide memory free percentage' in line:
                match = re.search(r'(\d+)%', line)
                if match:
                    metrics['memory_free_pct'] = int(match.group(1))
    except:
        pass

    # Get swap usage
    try:
        result = subprocess.run(['sysctl', 'vm.swapusage'], capture_output=True, text=True)
        match = re.search(r'used = (\d+)M', result.stdout)
        if match:
            metrics['swap_used_mb'] = int(match.group(1))
    except:
        pass

    # Convert pages to GB
    if 'pages_active' in metrics:
        metrics['memory_active_gb'] = (metrics['pages_active'] * PAGE_SIZE) / (1024**3)
    if 'pages_compressed' in metrics:
        metrics['memory_compressed_gb'] = (metrics['pages_compressed'] * PAGE_SIZE) / (1024**3)
    if 'pages_free' in metrics:
        metrics['memory_free_gb'] = (metrics['pages_free'] * PAGE_SIZE) / (1024**3)

    return metrics

def get_process_memory(process_name):
    """Get RSS memory for a specific process in MB"""
    try:
        result = subprocess.run(
            ['pgrep', '-f', process_name],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            return 0

        pids = result.stdout.strip().split('\n')
        total_mb = 0
        for pid in pids:
            if pid:
                try:
                    ps_result = subprocess.run(
                        ['ps', '-p', pid, '-o', 'rss='],
                        capture_output=True, text=True
                    )
                    if ps_result.returncode == 0:
                        mb = int(ps_result.stdout.strip()) / 1024
                        total_mb += mb
                except:
                    pass
        return total_mb
    except:
        return 0

def launch_chrome_with_tabs(num_tabs=10):
    """Launch Chrome with specified number of work-related tabs"""
    work_urls = [
        'https://github.com/zihanlim/device_ai-stress-test',
        'https://docs.python.org/3/',
        'https://cloud.google.com',
        'https://aws.amazon.com',
        'https://github.com',
        'https://stackoverflow.com',
        'https://pytorch.org',
        'https://www.tensorflow.org',
        'https://huggingface.co',
        'https://claude.ai',
    ]

    urls = work_urls[:num_tabs]
    url_args = ' '.join([f'"{url}"' for url in urls])

    try:
        subprocess.Popen(f'open -a "Google Chrome" {url_args}', shell=True)
        time.sleep(3)
        return True
    except:
        return False

def launch_vscode():
    """Launch VS Code with the device_ai-stress-test repo"""
    try:
        repo_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        subprocess.Popen(['code', repo_path])
        time.sleep(3)
        return True
    except:
        return False

def run_ollama_model(model_name, prompt=None, duration_s=30):
    """Run an ollama model for specified duration"""
    if prompt is None:
        prompt = "Explain quantum computing in detail."

    try:
        proc = subprocess.Popen(
            ['ollama', 'run', model_name, prompt],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(duration_s)
        return proc
    except:
        return None

def measure_scenario(scenario_num, scenario_name, setup_fn, duration_s=60, logger=None):
    """Run a scenario and measure memory usage"""
    print(f"\n--- Scenario {scenario_num}: {scenario_name} ---")

    if logger:
        logger.log_test_start(f"memory_scenario_{scenario_num}", {"name": scenario_name})

    # Setup the scenario
    processes = setup_fn()

    # Wait for apps to settle
    time.sleep(5)

    # Measure memory over time
    measurements = []
    start_time = time.time()
    measurement_interval = 5  # seconds

    while time.time() - start_time < duration_s:
        metrics = get_memory_metrics()
        metrics['timestamp'] = time.time() - start_time
        metrics['chrome_mb'] = get_process_memory('Chrome')
        metrics['vscode_mb'] = get_process_memory('Code')
        metrics['ollama_mb'] = get_process_memory('ollama')

        measurements.append(metrics)

        active_gb = metrics.get('memory_active_gb', 0)
        compressed_gb = metrics.get('memory_compressed_gb', 0)
        free_gb = metrics.get('memory_free_gb', 0)
        swap_mb = metrics.get('swap_used_mb', 0)

        print(f"  T+{metrics['timestamp']:.0f}s: Active={active_gb:.2f}GB, "
              f"Compressed={compressed_gb:.2f}GB, Free={free_gb:.2f}GB, "
              f"Swap={swap_mb}MB, Chrome={metrics['chrome_mb']:.0f}MB, "
              f"VS Code={metrics['vscode_mb']:.0f}MB, Ollama={metrics['ollama_mb']:.0f}MB")

        time.sleep(measurement_interval)

    # Calculate summary stats
    if measurements:
        active_values = [m.get('memory_active_gb', 0) for m in measurements]
        compressed_values = [m.get('memory_compressed_gb', 0) for m in measurements]

        summary = {
            'scenario_num': scenario_num,
            'scenario_name': scenario_name,
            'peak_active_gb': max(active_values),
            'avg_active_gb': sum(active_values) / len(active_values),
            'peak_compressed_gb': max(compressed_values),
            'avg_swap_mb': sum([m.get('swap_used_mb', 0) for m in measurements]) / len(measurements),
            'peak_chrome_mb': max([m.get('chrome_mb', 0) for m in measurements]),
            'peak_vscode_mb': max([m.get('vscode_mb', 0) for m in measurements]),
            'peak_ollama_mb': max([m.get('ollama_mb', 0) for m in measurements]),
            'measurements': measurements
        }

        print(f"  SUMMARY: Peak Active={summary['peak_active_gb']:.2f}GB, "
              f"Avg Active={summary['avg_active_gb']:.2f}GB, "
              f"Peak Compressed={summary['peak_compressed_gb']:.2f}GB")

        if logger:
            logger.log_test_complete(f"memory_scenario_{scenario_num}", summary)

        # Cleanup processes
        if isinstance(processes, list):
            for proc in processes:
                try:
                    proc.terminate()
                except:
                    pass

        return summary

    return None

def cleanup_apps():
    """Force kill all apps and verify cleanup"""
    # Force kill all target processes
    subprocess.run(['killall', '-9', 'Chrome'], capture_output=True)
    subprocess.run(['killall', '-9', 'Google Chrome'], capture_output=True)
    subprocess.run(['killall', '-9', 'Code'], capture_output=True)
    subprocess.run(['killall', '-9', 'ollama'], capture_output=True)
    subprocess.run(['killall', '-9', 'node'], capture_output=True)
    subprocess.run(['killall', '-9', 'com.apple.webkit.API'], capture_output=True)  # WebKit helpers
    time.sleep(3)

    # Verify Chrome is dead (Chrome Helper can respawn)
    chrome_pids = subprocess.run(['pgrep', '-f', 'Chrome'], capture_output=True, text=True).stdout.strip()
    if chrome_pids:
        print(f"  Warning: Chrome still running: {chrome_pids}")
        subprocess.run(['killall', '-9', 'Google Chrome'], capture_output=True)
        time.sleep(2)

    # Verify Code is dead
    code_pids = subprocess.run(['pgrep', '-f', 'Code'], capture_output=True, text=True).stdout.strip()
    if code_pids:
        print(f"  Warning: VS Code still running: {code_pids}")
        subprocess.run(['killall', '-9', 'Code'], capture_output=True)
        time.sleep(2)

    # Verify ollama is dead
    ollama_pids = subprocess.run(['pgrep', '-f', 'ollama'], capture_output=True, text=True).stdout.strip()
    if ollama_pids:
        print(f"  Warning: Ollama still running: {ollama_pids}")
        subprocess.run(['killall', '-9', 'ollama'], capture_output=True)
        time.sleep(2)

    print("  All apps cleaned up and verified")

def main():
    if len(sys.argv) < 2:
        results_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/../results'
    else:
        results_dir = sys.argv[1]

    os.makedirs(results_dir, exist_ok=True)

    # Initialize logger
    MEMORY_LOG = os.path.join(results_dir, 'memory_pressure_real_log.jsonl')
    logger = BenchmarkLogger(MEMORY_LOG, get_device_info())

    print("=== Real Memory Pressure Benchmark ===\n")

    all_results = []

    # Scenario 1: Idle baseline - clean system
    cleanup_apps()

    def setup_idle():
        return []

    results = measure_scenario(1, "Idle baseline", setup_idle, duration_s=60, logger=logger)
    if results:
        all_results.append(results)

    # Scenario 2: Browser only (10 tabs)
    def setup_browser_only():
        launch_chrome_with_tabs(10)
        return []

    results = measure_scenario(2, "Browser only (10 tabs)", setup_browser_only, duration_s=60, logger=logger)
    if results:
        all_results.append(results)

    # Close Chrome
    cleanup_apps()

    # Scenario 3: IDE only
    def setup_ide_only():
        launch_vscode()
        return []

    results = measure_scenario(3, "IDE only (VS Code)", setup_ide_only, duration_s=60, logger=logger)
    if results:
        all_results.append(results)

    # Scenario 4: Light dev (VS Code + Terminal + 3 browser tabs)
    def setup_light_dev():
        launch_vscode()
        launch_chrome_with_tabs(3)
        return []

    results = measure_scenario(4, "Light dev (VS Code + Browser 3 tabs)", setup_light_dev, duration_s=60, logger=logger)
    if results:
        all_results.append(results)

    # Close apps
    cleanup_apps()

    # Scenario 5: Daily dev (VS Code + 10 browser tabs)
    def setup_daily_dev():
        launch_vscode()
        launch_chrome_with_tabs(10)
        return []

    results = measure_scenario(5, "Daily dev (VS Code + Browser 10 tabs)", setup_daily_dev, duration_s=60, logger=logger)
    if results:
        all_results.append(results)

    # Scenario 6: Daily + Claude Code
    def setup_daily_claude():
        launch_vscode()
        launch_chrome_with_tabs(10)
        # Launch claude CLI in background
        subprocess.Popen(['claude'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return []

    results = measure_scenario(6, "Daily + Claude Code", setup_daily_claude, duration_s=60, logger=logger)
    if results:
        all_results.append(results)

    # Close apps
    cleanup_apps()

    # Scenarios 7-10: Daily + LLM models
    for scenario_num, model_name, model_label in [
        (7, 'qwen3:0.6b', '0.6B'),
        (8, 'qwen3:1.7b', '1.7B'),
        (9, 'qwen3:4b', '4B'),
        (10, 'qwen3:8b', '8B'),
    ]:
        def setup_daily_llm():
            launch_vscode()
            launch_chrome_with_tabs(10)
            # Run ollama model
            proc = run_ollama_model(model_name, duration_s=50)
            return [proc] if proc else []

        results = measure_scenario(
            scenario_num,
            f"Daily + {model_label} LLM",
            setup_daily_llm,
            duration_s=60,
            logger=logger
        )
        if results:
            all_results.append(results)

        # Close apps between LLM scenarios
        cleanup_apps()

    # Scenario 11b: Daily + dual LLMs
    def setup_daily_dual_llm():
        launch_vscode()
        launch_chrome_with_tabs(10)
        # Run two ollama models simultaneously
        proc1 = run_ollama_model('qwen3:0.6b', duration_s=50)
        time.sleep(2)
        proc2 = run_ollama_model('qwen3:1.7b', duration_s=48)
        return [proc1, proc2] if proc1 and proc2 else []

    results = measure_scenario(
        11,
        "Daily + dual LLMs (0.6B + 1.7B)",
        setup_daily_dual_llm,
        duration_s=60,
        logger=logger
    )
    if results:
        all_results.append(results)

    # Final cleanup
    cleanup_apps()

    # Save results to CSV
    MEMORY_CSV = os.path.join(results_dir, 'memory_pressure_real.csv')
    with open(MEMORY_CSV, 'w') as f:
        f.write('scenario_num,scenario_name,peak_active_gb,avg_active_gb,peak_compressed_gb,avg_swap_mb,peak_chrome_mb,peak_vscode_mb,peak_ollama_mb\n')
        for result in all_results:
            f.write(f"{result['scenario_num']},{result['scenario_name']},{result['peak_active_gb']:.2f},"
                   f"{result['avg_active_gb']:.2f},{result['peak_compressed_gb']:.2f},"
                   f"{result['avg_swap_mb']:.2f},{result['peak_chrome_mb']:.0f},"
                   f"{result['peak_vscode_mb']:.0f},{result['peak_ollama_mb']:.0f}\n")

    # Save JSON summary
    MEMORY_JSON = os.path.join(results_dir, 'memory_pressure_real_summary.json')
    summary_data = {
        'timestamp': datetime.now().isoformat(),
        'device_info': get_device_info(),
        'scenarios': [
            {
                'scenario_num': r['scenario_num'],
                'scenario_name': r['scenario_name'],
                'peak_active_gb': r['peak_active_gb'],
                'avg_active_gb': r['avg_active_gb'],
                'peak_compressed_gb': r['peak_compressed_gb'],
                'avg_swap_mb': r['avg_swap_mb'],
            }
            for r in all_results
        ]
    }
    with open(MEMORY_JSON, 'w') as f:
        json.dump(summary_data, f, indent=2)

    logger.log_summary({'scenarios_tested': len(all_results), 'results': all_results})
    logger.close()

    print("\n" + "="*80)
    print("REAL MEMORY PRESSURE BENCHMARK SUMMARY")
    print("="*80)
    print(f"{'Scenario':<40} {'Peak Active':<15} {'Peak Compressed':<15} {'Swap':<10}")
    print("-"*80)
    for result in all_results:
        print(f"{result['scenario_name']:<40} {result['peak_active_gb']:>6.2f}GB{'':<8} "
              f"{result['peak_compressed_gb']:>6.2f}GB{'':<8} {result['avg_swap_mb']:>6.0f}MB")
    print("="*80)

    print(f"\nResults saved to:")
    print(f"  CSV: {MEMORY_CSV}")
    print(f"  JSON: {MEMORY_JSON}")
    print(f"  Log: {MEMORY_LOG}")

if __name__ == '__main__':
    main()
