#!/usr/bin/env python3
"""
Benchmark Logger - Real-time JSON logging for all benchmarks
Provides structured logging with timestamps for audit trail and crash diagnostics
"""
import json
import os
import time
from datetime import datetime
from pathlib import Path

class BenchmarkLogger:
    """Real-time JSON logger for benchmark events"""

    def __init__(self, log_file, device_info=None):
        self.log_file = log_file
        self.start_time = time.time()
        self.events = []

        # Write header
        header = {
            "type": "benchmark_run",
            "device_info": device_info or {},
            "start_iso": datetime.now().isoformat(),
            "start_timestamp": self.start_time
        }
        self._write_event(header, flush=True)

    def log_event(self, event_type, data=None, timestamp=None):
        """Log a benchmark event with timestamp"""
        if timestamp is None:
            timestamp = time.time()

        event = {
            "type": event_type,
            "timestamp": timestamp,
            "elapsed_s": timestamp - self.start_time,
            "iso": datetime.fromtimestamp(timestamp).isoformat(),
            "data": data or {}
        }
        self.events.append(event)
        self._write_event(event)

    def log_metric(self, name, value, unit=None, tags=None):
        """Log a single metric"""
        self.log_event("metric", {
            "name": name,
            "value": value,
            "unit": unit,
            "tags": tags or {}
        })

    def log_iteration(self, test_name, iteration, duration_s, data=None):
        """Log an iteration within a test"""
        self.log_event("iteration", {
            "test": test_name,
            "iteration": iteration,
            "duration_s": duration_s,
            **(data or {})
        })

    def log_test_start(self, test_name, params=None):
        """Log test starting"""
        self.log_event("test_start", {
            "test": test_name,
            "params": params or {}
        })

    def log_test_complete(self, test_name, result, duration_s=None):
        """Log test completing"""
        data = {"test": test_name, "result": result}
        if duration_s:
            data["duration_s"] = duration_s
        self.log_event("test_complete", data)

    def log_error(self, error_message, context=None):
        """Log an error"""
        self.log_event("error", {
            "message": str(error_message),
            "context": context or {}
        })

    def log_summary(self, summary_data):
        """Log final summary"""
        self.log_event("summary", summary_data)

    def close(self):
        """Close the logger, write final record"""
        footer = {
            "type": "benchmark_end",
            "end_iso": datetime.now().isoformat(),
            "end_timestamp": time.time(),
            "total_events": len(self.events)
        }
        self._write_event(footer, flush=True)

    def _write_event(self, event, flush=False):
        """Write event to log file"""
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(event) + '\n')
            if flush:
                f.flush()
                os.fsync(f.fileno())

    def get_log_path(self):
        return self.log_file


def get_device_info():
    """Collect basic device info for logging"""
    import subprocess
    device = {}

    # Memory
    try:
        result = subprocess.run(['sysctl', '-n', 'hw.memsize'], capture_output=True, text=True)
        device['memory_gb'] = int(result.stdout.strip()) / (1024**3)
    except:
        pass

    # CPU
    try:
        result = subprocess.run(['sysctl', '-n', 'machdep.cpu.brand_string'], capture_output=True, text=True)
        device['cpu'] = result.stdout.strip()
    except:
        pass

    # Model
    try:
        result = subprocess.run(['sysctl', '-n', 'hw.model'], capture_output=True, text=True)
        device['model'] = result.stdout.strip()
    except:
        pass

    return device
