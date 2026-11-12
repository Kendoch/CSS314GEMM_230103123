import argparse
import ctypes
import multiprocessing as mp
from multiprocessing import shared_memory
from harness import run_benchmark, emit_verify_tag

M_DEFAULT = 24_000_000
MASK = 0xFFFFFFFFFFFFFFFF
MULT = 6364136223846793005

def fs_worker(name, slot_idx, iters):
    shm = shared_memory.SharedMemory(name=name)
    arr = (ctypes.c_uint64 * 512).from_buffer(shm.buf)
    acc = arr[slot_idx]
    for i in range(iters):
        acc = (acc * MULT + (i | 1)) & MASK
        arr[slot_idx] = acc
    del arr
    shm.close()

def execute(p, stride, total_steps):
    shm = shared_memory.SharedMemory(create=True, size=4096)
    try:
        arr = (ctypes.c_uint64 * 512).from_buffer(shm.buf)
        for i in range(512):
            arr[i] = i + 1
        del arr
        procs = []
        iters = max(1, total_steps // p)
        for t in range(p):
            proc = mp.Process(target=fs_worker, args=(shm.name, t * stride, iters))
            procs.append(proc)
            proc.start()
        for proc in procs:
            proc.join()
            if proc.exitcode != 0:
                raise RuntimeError(f"Worker exited with code {proc.exitcode}")
    finally:
        shm.close()
        shm.unlink()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", type=int, default=M_DEFAULT)
    ap.add_argument("--quick", action="store_true", help="Use fewer iterations for a smoke test")
    args = ap.parse_args()
    steps = 400_000 if args.quick else args.steps
    pmax = mp.cpu_count()
    print("PHASE 1 — False sharing")
    stride_times = {}
    for stride in (1, 2, 4, 8, 16, 32):
        s = run_benchmark(lambda: execute(pmax, stride, steps), 1 if args.quick else 2,
                          3 if args.quick else 7)
        throughput = steps / (s.median_ms / 1000) / 1e6
        stride_times[stride] = s.median_ms
        print(f"stride={stride:2d} offset={stride*8:3d} B median={s.median_ms:.3f} ms "
              f"IQR={s.iqr_ms:.3f} ms throughput={throughput:.3f} Mops/s")
    print("\nScaling (stride 1 and 16)")
    counts = sorted(set([1, 2, 4, 8, 16, pmax]))
    counts = [p for p in counts if p <= pmax]
    scaling = {}
    for stride in (1, 16):
        t1 = None
        for p in counts:
            s = run_benchmark(lambda p=p, stride=stride: execute(p, stride, steps),
                              1 if args.quick else 2, 3 if args.quick else 7)
            if p == 1:
                t1 = s.median_ms
            speedup = t1 / s.median_ms
            eff = speedup / p
            karp = ((1/speedup) - (1/p)) / (1 - 1/p) if p >= 2 else float("nan")
            scaling[(stride,p)] = s.median_ms
            print(f"stride={stride} p={p} T={s.median_ms:.3f} ms S={speedup:.3f} "
                  f"E={eff:.3f} e={karp:.5f}")
    print(emit_verify_tag("PHASE1", 0, stride_times[1], stride_times[16]))

if __name__ == "__main__":
    mp.freeze_support()
    main()
