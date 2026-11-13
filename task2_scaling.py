import multiprocessing as mp
import math
import os
from harness import run_benchmark, emit_verify_tag

def stage_b_range(args):
    start, end, seed = args
    acc = 0.0
    for i in range(start, end):
        x = (i + seed) * 0.000001
        for j in range(30):
            x = x * 1.0000001 + math.sin(x) * 0.000001
        acc += x
    return acc

def run_pipeline(pool, n, p):
    # Serial Stage A: first 5% of elements, 10 math operations per element.
    a_n = max(1, int(0.05 * n))
    a_acc = 0.0
    for i in range(a_n):
        x = (i + 1) * 0.00001
        for _ in range(10):
            x = math.sin(x) + math.sqrt(abs(x) + 1.0)
        a_acc += x
    # Stage B: all N elements are divided across the persistent process pool.
    chunk = (n + p - 1) // p
    ranges = [(s, min(s + chunk, n), a_n) for s in range(0, n, chunk)]
    return a_acc + sum(pool.map(stage_b_range, ranges))

def main():
    logical = mp.cpu_count()
    print("Logical CPUs:", logical)
    n_strong = 1_200_000
    strong_times = {}
    for p in range(1, logical + 1):
        with mp.Pool(processes=p) as pool:
            stats = run_benchmark(lambda: run_pipeline(pool, n_strong, p), warmup=1, runs=3)
        strong_times[p] = stats.median_ms
        print(f"STRONG p={p}: T={stats.median_ms:.2f} ms, IQR={stats.iqr_ms:.2f} ms")
    t1 = strong_times[1]
    strong_speedups = {p: t1/t for p, t in strong_times.items()}
    print("\nStrong scaling:")
    for p in range(1, logical + 1):
        print(f"p={p}: speedup={strong_speedups[p]:.3f}, efficiency={strong_speedups[p]/p:.3f}")
    # Estimate serial fraction from measured Stage A time separately.
    a_n = int(0.05*n_strong)
    def stage_a_only():
        z = 0.0
        for i in range(a_n):
            x = (i+1)*0.00001
            for _ in range(10):
                x = math.sin(x) + math.sqrt(abs(x)+1.0)
            z += x
        return z
    a_ms = run_benchmark(stage_a_only, warmup=1, runs=3).median_ms
    s = min(1.0, a_ms/t1)
    print(f"Amdahl serial fraction estimate s={s:.5f}; theoretical cap={1/s if s else float('inf'):.3f}")

    print("\nWeak scaling:")
    n0 = 200_000
    weak_times = {}
    for p in range(1, logical + 1):
        n = p*n0
        with mp.Pool(processes=p) as pool:
            stats = run_benchmark(lambda: run_pipeline(pool, n, p), warmup=1, runs=3)
        weak_times[p] = stats.median_ms
        alpha = a_ms / stats.median_ms
        gust = p - alpha*(p-1)
        efficiency = weak_times[1]/stats.median_ms
        print(f"WEAK p={p}: N={n}, T={stats.median_ms:.2f} ms, weak_eff={efficiency:.3f}, alpha={alpha:.4f}, Gustafson={gust:.3f}")
    print(emit_verify_tag("PHASE2", "REPLACE_WITH_YOUR_STUDENT_ID", strong_speedups[logical], logical - (a_ms/weak_times[logical])*(logical-1)))

if __name__ == "__main__":
    mp.freeze_support()
    main()
