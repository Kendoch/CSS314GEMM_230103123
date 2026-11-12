from dataclasses import dataclass
import hashlib
import multiprocessing as mp
import statistics
import time
from typing import Callable

@dataclass
class BenchStats:
    min_ms: float
    median_ms: float
    iqr_ms: float
    max_ms: float

def fnv1a_hash(s: str) -> int:
    h = 14695981039346656037
    for b in s.encode("utf-8"):
        h ^= b
        h = (h * 1099511628211) & 0xFFFFFFFFFFFFFFFF
    return h

def run_benchmark(fn: Callable[[], None], warmup_runs: int = 2,
                  timed_runs: int = 7) -> BenchStats:
    for _ in range(warmup_runs):
        fn()
    samples = []
    for _ in range(timed_runs):
        t0 = time.perf_counter_ns()
        fn()
        samples.append((time.perf_counter_ns() - t0) / 1e6)
    samples.sort()
    mid = len(samples) // 2
    med = statistics.median(samples)
    q25 = samples[len(samples) // 4]
    q75 = samples[(3 * len(samples)) // 4]
    return BenchStats(samples[0], med, q75 - q25, samples[-1])

def emit_verify_tag(task_id: str, student_seed: int,
                    primary_metric: float, secondary_metric: float) -> str:
    hw = mp.cpu_count()
    payload = (f"{task_id}|{student_seed}|{hw}|"
               f"{primary_metric:.4f}|{secondary_metric:.4f}")
    return f"VERIFY_HASH [{task_id}]: {fnv1a_hash(payload):016X} (P_log={hw})"
