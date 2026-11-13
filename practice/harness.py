from dataclasses import dataclass
import multiprocessing as mp
import hashlib
import time
import statistics
import os
import platform
import subprocess
from typing import Callable

@dataclass
class BenchStats:
    min_ms: float
    median_ms: float
    iqr_ms: float
    samples_ms: list

def fnv1a_hash(s: str) -> int:
    h = 14695981039346656037
    for b in s.encode("utf-8"):
        h = ((h ^ b) * 1099511628211) & 0xFFFFFFFFFFFFFFFF
    return h

def run_benchmark(fn: Callable, warmup: int = 2, runs: int = 7) -> BenchStats:
    for _ in range(warmup):
        fn()
    samples = []
    for _ in range(runs):
        t0 = time.perf_counter_ns()
        fn()
        samples.append((time.perf_counter_ns() - t0) / 1e6)
    ordered = sorted(samples)
    q1 = ordered[len(ordered) // 4]
    q3 = ordered[(3 * len(ordered)) // 4]
    return BenchStats(min(ordered), statistics.median(ordered), q3 - q1, samples)

def emit_verify_tag(phase: str, seed: str, m1: float, m2: float) -> str:
    hw = mp.cpu_count()
    sig = fnv1a_hash(f"{phase}|{seed}|{hw}|{m1:.4f}|{m2:.4f}")
    return f"VERIFY_HASH[{phase}]: {sig:016X} (P_log={hw})"

def cpu_info():
    info = {
        "platform": platform.platform(),
        "processor": platform.processor() or platform.machine(),
        "physical_cores": None,
        "logical_threads": mp.cpu_count(),
        "cache_line_bytes": None,
        "L1d": "unknown",
        "L2": "unknown",
        "L3": "unknown",
    }
    if platform.system() == "Darwin":
        commands = {
            "physical_cores": ["sysctl", "-n", "hw.physicalcpu"],
            "logical_threads": ["sysctl", "-n", "hw.logicalcpu"],
            "cache_line_bytes": ["sysctl", "-n", "hw.cachelinesize"],
            "L1d": ["sysctl", "-n", "hw.l1dcachesize"],
            "L2": ["sysctl", "-n", "hw.l2cachesize"],
            "L3": ["sysctl", "-n", "hw.l3cachesize"],
            "processor": ["sysctl", "-n", "machdep.cpu.brand_string"],
        }
        for key, cmd in commands.items():
            try:
                info[key] = subprocess.check_output(cmd, text=True).strip()
            except Exception:
                pass
    elif platform.system() == "Linux":
        try:
            text = Path("/proc/cpuinfo").read_text(errors="ignore")
            for line in text.splitlines():
                if line.lower().startswith("model name"):
                    info["processor"] = line.split(":", 1)[1].strip()
                    break
            info["physical_cores"] = os.cpu_count()
        except Exception:
            pass
    return info
