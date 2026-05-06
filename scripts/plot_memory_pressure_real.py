#!/usr/bin/env python3
"""Generate memory pressure scenario plots from real benchmark data"""
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

RESULTS_DIR = '/Users/arnold_neo/Developer/device_ai-stress-test/results/MacBookNeo-A18Pro'

# Read full log to get all data - use second run only (after 14:00)
with open(f'{RESULTS_DIR}/memory_pressure_real_log.jsonl') as f:
    entries = [json.loads(line) for line in f]

SCENARIO_START_TS = 1778040000  # ~14:00
results_by_scenario = {}
for entry in entries:
    if entry.get('type') == 'test_complete':
        ts = entry.get('timestamp', 0)
        if ts > SCENARIO_START_TS:
            result = entry['data']['result']
            sn = result['scenario_num']
            results_by_scenario[sn] = result

scenarios = []
for sn in sorted(results_by_scenario.keys()):
    r = results_by_scenario[sn]
    measurements = r.get('measurements', [])
    free_pcts = [m.get('memory_free_pct', 0) for m in measurements] if measurements else [0]
    scenarios.append({
        'scenario_num': r['scenario_num'],
        'scenario_name': r['scenario_name'],
        'peak_active_gb': r['peak_active_gb'],
        'avg_active_gb': r['avg_active_gb'],
        'peak_compressed_gb': r['peak_compressed_gb'],
        'peak_chrome_mb': r.get('peak_chrome_mb', 0),
        'peak_vscode_mb': r.get('peak_vscode_mb', 0),
        'peak_ollama_mb': r.get('peak_ollama_mb', 0),
        'avg_free_pct': sum(free_pcts) / len(free_pcts) if free_pcts else 0,
    })

scenario_names = [s['scenario_name'] for s in scenarios]
peak_active = [s['peak_active_gb'] for s in scenarios]
peak_compressed = [s['peak_compressed_gb'] for s in scenarios]
memory_free_pct = [s['avg_free_pct'] for s in scenarios]

fig, ax = plt.subplots(figsize=(14, 7))
x = np.arange(len(scenario_names))
width = 0.35

bars1 = ax.bar(x - width/2, peak_active, width, label='Active Memory', color='#2563eb')
bars2 = ax.bar(x + width/2, peak_compressed, width, label='Compressed Memory', color='#dc2626')

ax.set_ylabel('Memory (GB)', fontsize=12)
ax.set_title('Memory Pressure Scenarios - Real App Measurements\nMacBook Neo A18Pro (8GB)', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(scenario_names, rotation=45, ha='right', fontsize=9)
ax.legend(loc='upper right')
ax.set_ylim(0, 6)

for bar in bars1:
    ax.annotate(f'{bar.get_height():.2f}', xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                ha='center', va='bottom', fontsize=8)
for bar in bars2:
    ax.annotate(f'{bar.get_height():.2f}', xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                ha='center', va='bottom', fontsize=8)

plt.tight_layout()
plt.savefig(f'{RESULTS_DIR}/plots/memory_pressure_real_scenarios.png', dpi=150)
print(f"Saved: {RESULTS_DIR}/plots/memory_pressure_real_scenarios.png")

# Memory free percentage trend
fig2, ax2 = plt.subplots(figsize=(14, 7))

colors = ['#22c55e' if v > 50 else '#eab308' if v > 30 else '#ef4444' for v in memory_free_pct]
bars = ax2.bar(x, memory_free_pct, color=colors)
ax2.set_ylabel('Free Memory %', fontsize=12)
ax2.set_title('Memory Headroom by Scenario\nGreen>50% Yellow>30% Red<30%', fontsize=14, fontweight='bold')
ax2.set_xticks(x)
ax2.set_xticklabels(scenario_names, rotation=45, ha='right', fontsize=9)
ax2.axhline(y=30, color='red', linestyle='--', alpha=0.5, label='30% threshold')
ax2.legend()
ax2.set_ylim(0, 100)

for bar, val in zip(bars, memory_free_pct):
    ax2.annotate(f'{val:.0f}%', xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.savefig(f'{RESULTS_DIR}/plots/memory_pressure_real_headroom.png', dpi=150)
print(f"Saved: {RESULTS_DIR}/plots/memory_pressure_real_headroom.png")

# Component breakdown
ollama_mem = [s['peak_ollama_mb']/1024 for s in scenarios]
chrome_mem = [s['peak_chrome_mb']/1024 for s in scenarios]
vscode_mem = [s['peak_vscode_mb']/1024 for s in scenarios]

fig3, ax3 = plt.subplots(figsize=(14, 7))
ax3.bar(x, np.array(chrome_mem) + np.array(vscode_mem) + np.array(ollama_mem),
        label='Chrome', color='#4285f4', alpha=0.9)
ax3.bar(x, np.array(vscode_mem) + np.array(ollama_mem),
        label='VS Code', color='#0078d4', alpha=0.9)
ax3.bar(x, np.array(ollama_mem),
        label='Ollama', color='#ec6f3e', alpha=0.9)

ax3.set_ylabel('Memory (GB)', fontsize=12)
ax3.set_title('App Memory Usage by Scenario\n(Chrome + VS Code + Ollama)', fontsize=14, fontweight='bold')
ax3.set_xticks(x)
ax3.set_xticklabels(scenario_names, rotation=45, ha='right', fontsize=9)
ax3.legend(loc='upper right')
ax3.set_ylim(0, 12)

plt.tight_layout()
plt.savefig(f'{RESULTS_DIR}/plots/memory_pressure_real_components.png', dpi=150)
print(f"Saved: {RESULTS_DIR}/plots/memory_pressure_real_components.png")

print("Done!")
