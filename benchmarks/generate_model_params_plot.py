#!/usr/bin/env python3
"""
Generate SOTA Model Parameter Comparison Plot
Shows the massive scale difference between local models and cloud SOTA
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# Model data: name, total params (billions), category
models = [
    # Local models (tested on MacBook Air M5)
    ("Qwen3 0.6B", 0.6, "Local"),
    ("Qwen3 1.7B", 1.7, "Local"),
    ("Qwen3 4B", 4, "Local"),
    ("Qwen3 8B", 8, "Local"),
    ("Qwen3 14B", 14, "Local"),
    ("Qwen3 30B", 30, "Local"),
    # SOTA Cloud models (corrected May 2026)
    ("Claude 4.6 Opus", 400, "SOTA"),
    ("Claude 4.7 Opus", 5000, "SOTA"),
    ("GLM-5 Turbo", 744, "SOTA"),
    ("MiniMax M2.7", 230, "SOTA"),
    ("GPT-5.5", 9700, "SOTA"),
    ("Gemini 2.5 Pro", 1200, "SOTA"),
    ("Kimi K2.6", 1000, "SOTA"),
]

names = [m[0] for m in models]
params = [m[1] for m in models]
categories = [m[2] for m in models]

# Colors
colors = ['#3498db' if cat == "Local" else '#e74c3c' for cat in categories]

fig, ax = plt.subplots(figsize=(12, 10))
fig.patch.set_facecolor('white')

# Plot on linear scale
bars = ax.barh(names, params, color=colors, edgecolor='black')
ax.set_xlabel('Parameters (Billions)', fontsize=12)
ax.set_title('AI Model Parameter Scale: Local vs SOTA Cloud (May 2026)', fontsize=14, fontweight='bold')
ax.axvline(x=16, color='green', linestyle='--', linewidth=2, label='MacBook Air M5 Memory Limit')
ax.axvline(x=30, color='blue', linestyle=':', linewidth=2, label='Largest Local Model Tested (30B)')

# Add value labels
for bar, val in zip(bars, params):
    ax.text(bar.get_width() * 1.15, bar.get_y() + bar.get_height()/2,
            f'{val:.0f}B' if val >= 100 else f'{val:.1f}B',
            va='center', fontsize=9, fontweight='bold')

# Legend
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor='#3498db', label='Local (Tested on M5)'),
                   Patch(facecolor='#e74c3c', label='SOTA Cloud (API Required)'),
                   plt.Line2D([0], [0], color='green', linestyle='--', label='16GB Memory Limit')]
ax.legend(handles=legend_elements, loc='lower right', fontsize=10)
ax.grid(True, alpha=0.3, axis='x')

plt.tight_layout()
output_path = '/Users/airnold/Developer/Stress_Test/results/plots/model_params_comparison.png'
plt.savefig(output_path, dpi=150, bbox_inches='tight')
print(f"Saved: {output_path}")

# Summary
print("\n=== Parameter Scale Summary ===")
local_max = max([m[1] for m in models if m[2] == "Local"])
sota_min = min([m[1] for m in models if m[2] == "SOTA"])
sota_max = max([m[1] for m in models if m[2] == "SOTA"])
print(f"Local models: 0.6B to {local_max:.0f}B")
print(f"SOTA cloud: {sota_min:.0f}B to {sota_max:.0f}B")
print(f"\nGap: Smallest SOTA ({sota_min:.0f}B) is {sota_min/local_max:.0f}x larger than largest local ({local_max:.0f}B)")
print(f"Largest SOTA ({sota_max:.0f}B) is {sota_max/local_max:.0f}x larger than largest local")