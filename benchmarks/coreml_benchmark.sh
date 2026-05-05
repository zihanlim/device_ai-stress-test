#!/bin/bash
# Core ML / Neural Engine Benchmark
set -e

RESULTS_DIR="${1:-../results}"
mkdir -p "$RESULTS_DIR"

echo "=== Core ML / Neural Engine Benchmark ===" | tee "$RESULTS_DIR/coreml_benchmark.txt"

# Check for Apple Silicon
echo "--- System Info ---" | tee -a "$RESULTS_DIR/coreml_benchmark.txt"
echo "Chip: $(sysctl -n machdep.cpu.brand_string)" | tee -a "$RESULTS_DIR/coreml_benchmark.txt"

# Check for Neural Engine (ANE)
echo "" | tee -a "$RESULTS_DIR/coreml_benchmark.txt"
echo "--- Neural Engine Availability ---" | tee -a "$RESULTS_DIR/coreml_benchmark.txt"

if [[ -f "/usr/bin/coremlutil" ]]; then
    coremlutil --version 2>/dev/null || echo "Core ML tools available" | tee -a "$RESULTS_DIR/coreml_benchmark.txt"
else
    echo "Core ML tools not found in standard location" | tee -a "$RESULTS_DIR/coreml_benchmark.txt"
fi

# Check for MPS (Metal Performance Shaders) support
echo "" | tee -a "$RESULTS_DIR/coreml_benchmark.txt"
echo "--- Metal / MPS Support ---" | tee -a "$RESULTS_DIR/coreml_benchmark.txt"
if python3 -c "import torch; print(f'PyTorch version: {torch.__version__}'); print(f'MPS available: {torch.backends.mps.is_available()}')" 2>/dev/null; then
    echo "PyTorch MPS available" | tee -a "$RESULTS_DIR/coreml_benchmark.txt"
else
    echo "PyTorch MPS check failed (PyTorch may not be installed)" | tee -a "$RESULTS_DIR/coreml_benchmark.txt"
fi

# Core ML inference benchmark using CoreMLRunner (if available) or PyTorch
echo "" | tee -a "$RESULTS_DIR/coreml_benchmark.txt"
echo "--- Core ML Inference Benchmark ---" | tee -a "$RESULTS_DIR/coreml_benchmark.txt"

python3 -c "
import time
import subprocess
import sys

# Check if we can use coremltools
try:
    import coremltools as ct
    print('Core ML Tools available')
    HAS_CT = True
except ImportError:
    print('Core ML Tools not installed (pip install coremltools)')
    HAS_CT = False

# Check PyTorch with MPS
try:
    import torch
    print(f'PyTorch version: {torch.__version__}')
    if torch.backends.mps.is_available():
        print('MPS (Metal) is available')
        HAS_MPS = True
    else:
        print('MPS not available')
        HAS_MPS = False
except ImportError:
    print('PyTorch not installed')
    HAS_MPS = False

# Simple matrix multiplication benchmark as proxy for ANE performance
if HAS_MPS or (HAS_CT and sys.platform == 'darwin'):
    print('')
    print('Running matrix multiplication benchmark...')

    device = 'mps' if HAS_MPS else 'cpu'

    for size in [512, 1024, 2048]:
        # Warmup
        if HAS_MPS:
            x = torch.randn(size, size, device='mps')
            y = torch.randn(size, size, device='mps')
            _ = torch.mm(x, y)
            torch.mps.synchronize()

        # Benchmark
        iterations = 50
        if HAS_MPS:
            x = torch.randn(size, size, device='mps')
            y = torch.randn(size, size, device='mps')
            torch.mps.synchronize()
            start = time.time()
            for _ in range(iterations):
                _ = torch.mm(x, y)
            torch.mps.synchronize()
            elapsed = time.time() - start
        else:
            x = torch.randn(size, size)
            y = torch.randn(size, size)
            start = time.time()
            for _ in range(iterations):
                _ = torch.mm(x, y)
            elapsed = time.time() - start

        tflops = (size * size * size * 2 * iterations) / elapsed / 1e12
        print(f'Matrix size {size}x{size}: {elapsed/iterations*1000:.2f} ms/op ({tflops:.2f} TFLOPS)')
else:
    print('No Core ML/MPS backend available for benchmark')
" 2>&1 | tee -a "$RESULTS_DIR/coreml_benchmark.txt"

echo "" | tee -a "$RESULTS_DIR/coreml_benchmark.txt"
echo "Core ML Benchmark complete" | tee -a "$RESULTS_DIR/coreml_benchmark.txt"