import multiprocessing as mp
import time
from harness import cpu_info, emit_verify_tag

def main():
    info = cpu_info()
    print("=== PHASE 0: HARDWARE ===")
    for key, value in info.items():
        print(f"{key}: {value}")

    n = 1_000_000
    t0 = time.perf_counter_ns()
    for _ in range(n):
        time.perf_counter_ns()
    elapsed = time.perf_counter_ns() - t0
    avg_ns = elapsed / n
    print(f"perf_counter_ns average call latency: {avg_ns:.3f} ns")
    print(emit_verify_tag("PHASE0", "REPLACE_WITH_YOUR_STUDENT_ID", avg_ns, float(mp.cpu_count())))

if __name__ == "__main__":
    main()
