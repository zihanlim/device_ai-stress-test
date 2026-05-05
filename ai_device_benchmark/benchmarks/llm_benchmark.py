#!/usr/bin/env python3
"""
LLM Benchmark - Local AI Inference with Ollama
Run directly: python3 llm_benchmark.py [results_dir]

Tests multiple model sizes to determine device capability:
- Small (0.6B-1.7B): Smooth, uses ~1-2GB
- Medium (4B-8B): Tight fit, ~5-10GB
- Large (14B-30B): Tests memory limits on 16GB device

Requires: ollama installed and running
  brew install ollama
  ollama serve

Real-time JSON logging for audit trail and crash diagnostics
"""
import time
import subprocess
import sys
import os
import json

# Add scripts path for logger
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.benchmark_logger import BenchmarkLogger, get_device_info

def check_ollama():
    """Check if Ollama is installed and running"""
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def get_ollama_version():
    """Get Ollama version"""
    try:
        result = subprocess.run(['ollama', '--version'], capture_output=True, text=True)
        return result.stdout.strip()
    except:
        return "Unknown"

def pull_model(model_name, logger=None):
    """Pull a model if not already present"""
    if logger:
        logger.log_event("model_pull_start", {"model": model_name})

    try:
        result = subprocess.run(
            ['ollama', 'pull', model_name],
            capture_output=True, text=True, timeout=600
        )
        success = result.returncode == 0
        if logger:
            logger.log_event("model_pull_complete", {"model": model_name, "success": success})
        return success
    except Exception as e:
        if logger:
            logger.log_error(f"Failed to pull {model_name}", {"error": str(e)})
        return False

def list_available_models():
    """List available Ollama models"""
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        models = []
        for line in result.stdout.split('\n')[1:]:
            if line.strip():
                parts = line.split()
                if parts:
                    models.append(parts[0])
        return models
    except:
        return []

def run_llm_prompt(model, prompt, timeout=120, logger=None):
    """Run a single LLM prompt and measure latency"""
    start = time.time()

    if logger:
        logger.log_event("prompt_start", {"model": model, "prompt_preview": prompt[:50]})

    try:
        result = subprocess.run(
            ['ollama', 'run', model, prompt],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        elapsed = time.time() - start

        if result.returncode == 0:
            if logger:
                logger.log_event("prompt_complete", {
                    "model": model,
                    "latency_s": elapsed,
                    "response_length": len(result.stdout)
                })
            return elapsed, result.stdout

        if logger:
            logger.log_event("prompt_failed", {
                "model": model,
                "latency_s": elapsed,
                "return_code": result.returncode
            })
        return elapsed, None

    except subprocess.TimeoutExpired:
        elapsed = time.time() - start
        if logger:
            logger.log_event("prompt_timeout", {"model": model, "timeout_s": timeout})
        return timeout, None
    except Exception as e:
        elapsed = time.time() - start
        if logger:
            logger.log_error("Prompt execution error", {"model": model, "error": str(e)})
        return elapsed, None

def count_tokens(text):
    """Rough token count"""
    if not text:
        return 0
    return len(text.split()) * 1.3

def benchmark_model(model, size_label, mem_est, test_prompts, logger, timeout=180):
    """Benchmark a single model with multiple prompts"""
    logger.log_test_start(f"llm_{size_label}", {"model": model, "memory_gb": mem_est})
    print(f"  Benchmarking {model}...")

    results = []
    for i, prompt in enumerate(test_prompts):
        logger.log_iteration(f"llm_{size_label}", i+1, 0, {"prompt_preview": prompt[:30]})

        elapsed, response = run_llm_prompt(model, prompt, timeout=timeout, logger=logger)

        if response:
            tokens = count_tokens(response)
            tps = tokens / elapsed if elapsed > 0 else 0
            results.append({
                'prompt_num': i + 1,
                'latency_s': elapsed,
                'tokens': int(tokens),
                'tps': tps,
                'success': True
            })
            print(f"    Prompt {i+1}: {elapsed:.2f}s, {tps:.1f} tok/s")
        else:
            results.append({
                'prompt_num': i + 1,
                'latency_s': elapsed if elapsed else 0,
                'tokens': 0,
                'tps': 0,
                'success': False
            })
            print(f"    Prompt {i+1}: FAILED")

        logger.log_iteration(f"llm_{size_label}", i+1, elapsed, {
            "success": results[-1]['success'],
            "tokens": results[-1]['tokens'],
            "tps": results[-1]['tps']
        })

    logger.log_test_complete(f"llm_{size_label}", {"results": results})
    return results

def main():
    if len(sys.argv) < 2:
        results_dir = os.path.dirname(os.path.abspath(__file__)) + '/../results'
    else:
        results_dir = sys.argv[1]

    os.makedirs(results_dir, exist_ok=True)

    # Initialize JSON logger (real-time logging)
    LLM_LOG = os.path.join(results_dir, 'llm_log.jsonl')
    logger = BenchmarkLogger(LLM_LOG, get_device_info())

    print("=== LLM Benchmark (Multi-Model) ===\n")

    if not check_ollama():
        logger.log_error("Ollama not found", {})
        print("ERROR: Ollama not found. Install with: brew install ollama")
        print("Then start with: ollama serve")
        sys.exit(1)

    ollama_version = get_ollama_version()
    logger.log_metric("ollama_version", ollama_version)
    print(f"Ollama version: {ollama_version}")

    # Models to test - different sizes (Qwen3 family)
    MODELS_TO_TEST = [
        ('qwen3:0.6b', '0.6B', 1),
        ('qwen3:1.7b', '1.7B', 2),
        ('qwen3:4b', '4B', 5),
        ('qwen3:8b', '8B', 10),
        ('qwen3:14b', '14B', 16),
        ('qwen3:30b', '30B', 32),
    ]

    available = list_available_models()
    logger.log_metric("available_models", available)
    print(f"Available models: {', '.join(available) if available else 'None'}\n")

    test_prompts = [
        "What is 2+2? Answer in one word.",
        "Write a Python function to calculate fibonacci numbers.",
        "Explain the difference between a process and a thread in computing.",
        "Write a short email to your manager explaining you'll be late.",
        "What are the main differences between Apple Silicon M-series and Intel?",
    ]

    all_results = {}

    for model_name, size_label, mem_est in MODELS_TO_TEST:
        available = list_available_models()
        if model_name not in available:
            print(f"\nModel {model_name} not found. Pulling...")
            if not pull_model(model_name, logger):
                print(f"  Failed to pull {model_name}, skipping...")
                continue
            print(f"  {model_name} pulled successfully")

        print(f"\n--- Testing {model_name} ({size_label}) ---")
        logger.log_event("model_test_start", {"model": model_name, "size": size_label})

        results = benchmark_model(model_name, size_label, mem_est, test_prompts, logger, timeout=180)

        successful = [r for r in results if r['success']]
        if successful:
            avg_latency = sum(r['latency_s'] for r in successful) / len(successful)
            avg_tps = sum(r['tps'] for r in successful) / len(successful)
            total_tokens = sum(r['tokens'] for r in successful)
            all_results[size_label] = {
                'model': model_name,
                'size': size_label,
                'mem_gb': mem_est,
                'avg_latency': avg_latency,
                'avg_tps': avg_tps,
                'total_tokens': total_tokens,
                'successful': len(successful),
                'results': results
            }
            print(f"  Avg: {avg_latency:.2f}s latency, {avg_tps:.1f} tok/s")

            logger.log_metric(f"tps_{size_label}", avg_tps, "tokens/sec", {"model": model_name})
            logger.log_metric(f"latency_{size_label}", avg_latency, "seconds", {"model": model_name})
        else:
            print(f"  All prompts failed for {model_name}")
            logger.log_error("All prompts failed", {"model": model_name})
            # Record failed model with 0 values so it appears in plots
            all_results[size_label] = {
                'model': model_name,
                'size': size_label,
                'mem_gb': mem_est,
                'avg_latency': 0,
                'avg_tps': 0,
                'total_tokens': 0,
                'successful': 0,
                'results': []
            }

    if not all_results:
        logger.log_error("No models tested successfully", {})
        print("\nERROR: No models tested successfully.")
        sys.exit(1)

    # Save summary to TXT (for quick human viewing - keep for convenience)
    LLAMA_DATA = os.path.join(results_dir, 'llm_data.txt')
    with open(LLAMA_DATA, "w") as f:
        f.write("model_size,model_name,mem_gb,avg_latency_s,avg_tps,total_tokens,successful_prompts\n")
        for size, data in sorted(all_results.items()):
            f.write(f"{size},{data['model']},{data['mem_gb']},{data['avg_latency']:.4f},"
                   f"{data['avg_tps']:.2f},{data['total_tokens']},{data['successful']}\n")

    # Log summary to JSON logger
    logger.log_summary({
        "models_tested": len(all_results),
        "fastest_model": max(all_results.items(), key=lambda x: x[1]['avg_tps'])[0],
        "results": all_results
    })

    print("\n" + "="*60)
    print("LLM BENCHMARK SUMMARY")
    print("="*60)
    print(f"{'Size':<8} {'Model':<20} {'Memory':<10} {'Latency':<10} {'TPS':<10}")
    print("-"*60)
    for size, data in sorted(all_results.items()):
        print(f"{size:<8} {data['model']:<20} {data['mem_gb']}GB{'':<7} "
              f"{data['avg_latency']:.2f}s{'':<5} {data['avg_tps']:.1f}")
    print("="*60)

    max_tps_model = max(all_results.items(), key=lambda x: x[1]['avg_tps'])
    print(f"\nFastest: {max_tps_model[1]['model']} at {max_tps_model[1]['avg_tps']:.1f} tok/s")

    logger.close()

    print(f"\nJSON log: {LLM_LOG}")
    print(f"TXT summary: {LLAMA_DATA}")

if __name__ == '__main__':
    main()