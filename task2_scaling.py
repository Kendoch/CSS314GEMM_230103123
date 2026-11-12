import argparse, math, multiprocessing as mp
from harness import run_benchmark, emit_verify_tag

def parallel_kernel(args):
    start, end = args
    acc = 0.1234567
    for i in range(start, end):
        x = (i % 997) * 0.001 + acc * 0.0001
        for _ in range(35):
            x = math.sin(x) * 1.000001 + math.sqrt(abs(x) + 1e-12) * 0.000001
        acc += x
    return acc

def serial_stage(n):
    acc = 0.0
    for i in range(max(1, int(n * 0.05))):
        x = i * 0.00001 + 0.1
        for _ in range(12):
            x = math.sin(x) + math.sqrt(abs(x) + 1e-12) * 0.01
        acc += x
    return acc

def run_trial(pool, n, p):
    serial_stage(n)
    chunk = (n + p - 1) // p
    ranges = [(i, min(n, i + chunk)) for i in range(0, n, chunk)]
    pool.map(parallel_kernel, ranges)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args()
    pmax = mp.cpu_count()
    counts = list(range(1, pmax + 1))
    nstrong = 120_000 if args.quick else 1_600_000
    n0 = 20_000 if args.quick else 250_000
    reps = 3 if args.quick else 7
    print("PHASE 2 — Strong scaling")
    strong = {}
    for p in counts:
        with mp.Pool(p) as pool:
            st = run_benchmark(lambda: run_trial(pool, nstrong, p), 1, reps)
        strong[p] = st.median_ms
        print(f"strong p={p} T={st.median_ms:.3f} ms")
    t1 = strong[1]
    for p in counts:
        sp = t1 / strong[p]
        print(f"strong p={p} speedup={sp:.3f} efficiency={sp/p:.3f}")
    print("PHASE 2 — Weak scaling")
    weak = {}
    stage_a = {}
    for p in counts:
        n = p * n0
        with mp.Pool(p) as pool:
            def trial():
                stage_a[p] = serial_stage(n)
                chunk = (n + p - 1) // p
                pool.map(parallel_kernel, [(i, min(n, i+chunk)) for i in range(0,n,chunk)])
            st = run_benchmark(trial, 1, reps)
        weak[p] = st.median_ms
        alpha = (0.05 * n0 * 12) / max(1, n)  # rough workload fraction proxy, not measured time fraction
        gust = p - alpha * (p - 1)
        print(f"weak p={p} T={st.median_ms:.3f} ms efficiency={weak[1]/st.median_ms:.3f} "
              f"Gustafson_estimate={gust:.3f}")
    s = strong[1] and (1.0 / max(1.0, strong[1] / strong[1]))
    print("Serial stage is included in total time; instrument stage timing separately for the report.")
    print(emit_verify_tag("PHASE2", 0, t1/strong[pmax], weak[1]/weak[pmax]))

if __name__ == "__main__":
    mp.freeze_support()
    main()
