import multiprocessing as mp
import platform
import subprocess
import sys
import time
from harness import emit_verify_tag

def sysctl_value(key):
    try:
        return subprocess.check_output(["sysctl", "-n", key], text=True).strip()
    except Exception:
        return "N/A"

def main():
    print("=== PHASE 0: HARDWARE BASELINE ===")
    print("CPU:", sysctl_value("machdep.cpu.brand_string") if sys.platform == "darwin" else platform.processor())
    if sys.platform == "darwin":
        for key in ("hw.physicalcpu", "hw.logicalcpu", "hw.cachelinesize",
                    "hw.l1dcachesize", "hw.l2cachesize", "hw.l3cachesize"):
            print(f"{key}: {sysctl_value(key)}")
    print("OS:", platform.platform())
    print("Python:", sys.version.replace("\n", " "))
    print("multiprocessing.cpu_count():", mp.cpu_count())

    reads = 2_000_000
    t0 = time.perf_counter_ns()
    for _ in range(reads):
        time.perf_counter_ns()
    elapsed = time.perf_counter_ns() - t0
    avg_ns = elapsed / reads
    print(f"Timer reads: {reads}")
    print(f"Total timer calibration: {elapsed / 1e6:.3f} ms")
    print(f"Average perf_counter_ns call latency: {avg_ns:.2f} ns")
    # Replace with your actual student ID before submitting.
    student_id = input("Enter your Student ID (used as seed): ").strip()
    if not student_id:
        raise SystemExit("Student ID is required.")
    try:
        seed = int(student_id)
    except ValueError:
        seed = sum(ord(c) for c in student_id)
    print(emit_verify_tag("PHASE0", seed, avg_ns, elapsed / 1e6))

if __name__ == "__main__":
    mp.freeze_support()
    main()
