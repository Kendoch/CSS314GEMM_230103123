import ctypes
import multiprocessing as mp
from multiprocessing import shared_memory
import time
import os
from harness import run_benchmark, emit_verify_tag

M = 16_000_000
MASK = 0xFFFFFFFFFFFFFFFF
MULT = 6364136223846793005

def fs_worker(shm_name, slot_idx, iters):
    shm = shared_memory.SharedMemory(name=shm_name)
    arr = (ctypes.c_uint64 * 512).from_buffer(shm.buf)
    acc = arr[slot_idx]
    for i in range(iters):
        acc = (acc * MULT + (i | 1)) & MASK
        arr[slot_idx] = acc
    del arr
    shm.close()

def run_once(p, stride, total=M):
    shm = shared_memory.SharedMemory(create=True, size=4096)
    try:
        arr = (ctypes.c_uint64 * 512).from_buffer(shm.buf)
        for i in range(512):
            arr[i] = i + 1
        del arr
        base, rem = divmod(total, p)
        procs = []
        t0 = time.perf_counter_ns()
        for worker in range(p):
            iters = base + (1 if worker < rem else 0)
            proc = mp.Process(target=fs_worker, args=(shm.name, worker * stride, iters))
            proc.start()
            procs.append(proc)
        for proc in procs:
            proc.join()
            if proc.exitcode != 0:
                raise RuntimeError(f"Worker exited with code {proc.exitcode}")
        return (time.perf_counter_ns() - t0) / 1e6
    finally:
        shm.close()
        shm.unlink()

def main():
    pphys = os.cpu_count() or 2
    print("Logical CPUs:", mp.cpu_count())
    print("NOTE: Python does not expose physical-core count portably; using os.cpu_count() as worker count.")
    p = max(1, min(pphys, mp.cpu_count()))
    print("Workers used:", p)
    results = {}
    for stride in (1, 2, 4, 8, 16, 32):
        stats = run_benchmark(lambda: run_once(p, stride), warmup=0, runs=3)
        throughput = M / (stats.median_ms / 1000) / 1e6
        results[stride] = stats.median_ms
        print(f"stride={stride:2d} ({stride*8:3d} B): median={stats.median_ms:.2f} ms, IQR={stats.iqr_ms:.2f} ms, throughput={throughput:.3f} Mops/s")

    print("\nProcess scaling for stride 1 and 16:")
    for stride in (1, 16):
        t1 = run_benchmark(lambda: run_once(1, stride), warmup=0, runs=3).median_ms
        for workers in sorted(set([1, 2, 4, 8, mp.cpu_count()])):
            workers = max(1, min(workers, mp.cpu_count()))
            tp = run_benchmark(lambda: run_once(workers, stride), warmup=0, runs=3).median_ms
            speedup = t1 / tp
            efficiency = speedup / workers
            kf = ((1/speedup) - (1/workers)) / (1 - (1/workers)) if workers > 1 else float("nan")
            print(f"stride={stride}, p={workers}: T={tp:.2f} ms, speedup={speedup:.3f}, efficiency={efficiency:.3f}, Karp-Flatt={kf:.5f}")
    print(emit_verify_tag("PHASE1", "REPLACE_WITH_YOUR_STUDENT_ID", results[1], results[16]))

if __name__ == "__main__":
    mp.freeze_support()
    main()
