#!/usr/bin/env python3
"""
Geekbench AI Benchmark
Downloads/uses Geekbench AI to measure NPU/CPU/GPU AI performance

Requires: Geekbench 6 AI (https://www.geekbench.com/download/)
"""
import subprocess
import sys
import os
import json
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.benchmark_logger import BenchmarkLogger, get_device_info


def find_geekbench():
    """Find Geekbench installation"""
    paths = [
        '/Applications/Geekbench AI.app/Contents/MacOS/Geekbench AI',
        '/Applications/Geekbench 6.app/Contents/MacOS/geekbench6',
        '/Applications/Geekbench 5.app/Contents/MacOS/geekbench5',
        'geekbench6',
        'geekbench5',
    ]
    for path in paths:
        if os.path.exists(path):
            return path
        try:
            result = subprocess.run(['which', path.split('/')[-1]],
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
    return None


def run_geekbench_ai(results_dir, logger=None):
    """Run Geekbench AI and parse results - CPU and Metal separately"""
    gb_path = find_geekbench()

    if not gb_path:
        if logger:
            logger.log_error("Geekbench not found", {"path": "not installed"})
        return None

    all_scores = {}

    # Run CPU AI benchmark
    if logger:
        logger.log_event("geekbench_cpu_start", {"path": gb_path, "mode": "cpu"})

    cpu_file = os.path.join(results_dir, 'geekbench_ai_cpu')
    cmd_cpu = [gb_path, 'ai', '--cpu', '--export-json', cpu_file]

    try:
        result_cpu = subprocess.run(cmd_cpu, capture_output=True, text=True, timeout=600)
        cpu_scores = parse_geekbench_output(result_cpu.stdout + result_cpu.stderr)
        for k, v in cpu_scores.items():
            all_scores[f"cpu_{k}"] = v

        if logger:
            logger.log_event("geekbench_cpu_complete", {"scores": cpu_scores})

    except Exception as e:
        if logger:
            logger.log_error("Geekbench CPU error", {"error": str(e)})

    # Run Metal AI benchmark (GPU + NPU on Apple Silicon)
    if logger:
        logger.log_event("geekbench_metal_start", {"path": gb_path, "mode": "metal"})

    metal_file = os.path.join(results_dir, 'geekbench_ai_metal')
    cmd_metal = [gb_path, 'ai', '--metal', '--export-json', metal_file]

    try:
        result_metal = subprocess.run(cmd_metal, capture_output=True, text=True, timeout=600)
        metal_scores = parse_geekbench_output(result_metal.stdout + result_metal.stderr)
        for k, v in metal_scores.items():
            all_scores[f"metal_{k}"] = v

        if logger:
            logger.log_event("geekbench_metal_complete", {"scores": metal_scores})

    except Exception as e:
        if logger:
            logger.log_error("Geekbench Metal error", {"error": str(e)})

    if logger:
        logger.log_event("geekbench_all_complete", {"total_scores": len(all_scores)})

    if all_scores:
        # Save parsed results
        out_file = os.path.join(results_dir, 'geekbench_ai_data.txt')
        with open(out_file, 'w') as f:
            f.write("metric,value\n")
            for key, val in sorted(all_scores.items()):
                f.write(f"{key},{val}\n")

        if logger:
            for key, val in all_scores.items():
                logger.log_metric(f"geekbench_{key}", val)

        return all_scores

    return None


def parse_geekbench_output(output):
    """Parse Geekbench output for AI scores"""
    scores = {}

    patterns = {
        'cpu_ai_score': r'CPU AI Score:\s+(\d+)',
        'gpu_ai_score': r'GPU AI Score:\s+(\d+)',
        'single_precision': r'Single Precision Score:\s+(\d+\.?\d*)',
        'half_precision': r'Half Precision Score:\s+(\d+\.?\d*)',
        'quantized': r'Quantized Score:\s+(\d+\.?\d*)',
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, output, re.IGNORECASE)
        if match:
            scores[key] = float(match.group(1))

    # Also try to extract Metal/CPU scores from typical output
    # Example: "Metal AI Score. 12345"
    metal_match = re.search(r'Metal AI Score[:\s]+(\d+)', output, re.IGNORECASE)
    if metal_match:
        scores['metal_ai_score'] = float(metal_match.group(1))

    return scores


def main():
    if len(sys.argv) < 2:
        results_dir = os.path.dirname(os.path.abspath(__file__)) + '/../results'
    else:
        results_dir = sys.argv[1]

    os.makedirs(results_dir, exist_ok=True)

    LOG_FILE = os.path.join(results_dir, 'geekbench_ai_log.jsonl')
    logger = BenchmarkLogger(LOG_FILE, get_device_info())

    print("=== Geekbench AI Benchmark ===")

    scores = run_geekbench_ai(results_dir, logger)

    if scores:
        print("\nGeekbench AI Results:")
        print("-" * 40)
        for key, val in sorted(scores.items()):
            print(f"  {key}: {val}")
        print("-" * 40)
    else:
        print("\nGeekbench AI not available.")
        print("Install from: https://www.geekbench.com/download/")
        print("Or: brew install --cask geekbench")

    logger.close()


if __name__ == '__main__':
    main()