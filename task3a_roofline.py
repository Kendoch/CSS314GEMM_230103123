import argparse, multiprocessing as mp, time
from multiprocessing import shared_memory
from harness import run_benchmark, emit_verify_tag

def copy_worker(a_name, b_name, start, end):
    a = shared_memory.SharedMemory(name=a_name)
    b = shared_memory.SharedMemory(name=b_name)
    a.buf[start:end] = b.buf[start:end]
    a.close(); b.close()

def compute_worker(iters):
    a = 1.0000001
    b = 0.0000003
    xs = [float(i+1) / 17 for i in range(16)]
    for _ in range(iters):
        for j in range(16):
            xs[j] = xs[j] * a + b
    return sum(xs)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args()
    p = mp.cpu_count()
    size = 8 * 1024 * 1024 if args.quick else 96 * 1_000_000
    a = shared_memory.SharedMemory(create=True, size=size)
    b = shared_memory.SharedMemory(create=True, size=size)
    try:
        b.buf[:] = b"\x01" * size
        def copy_all():
            jobs=[]
            for t in range(p):
                lo=t*size//p; hi=(t+1)*size//p
                q=mp.Process(target=copy_worker,args=(a.name,b.name,lo,hi))
                jobs.append(q); q.start()
            for q in jobs:
                q.join()
                if q.exitcode: raise RuntimeError("copy worker failed")
        st=run_benchmark(copy_all,1,3 if args.quick else 7)
        bw=(2*size)/(st.median_ms/1000)/1e9
        print(f"Copy median={st.median_ms:.3f} ms; estimated bandwidth={bw:.3f} GB/s")
    finally:
        a.close(); a.unlink(); b.close(); b.unlink()
    iters=100_000 if args.quick else 5_000_000
    def compute_all():
        with mp.Pool(p) as pool:
            pool.map(compute_worker,[iters]*p)
    # Pool startup is included here: this is a practical ceiling, not a pure kernel-only timing.
    stc=run_benchmark(compute_all,0,3 if args.quick else 5)
    flops=16*2*iters*p
    gflops=flops/(stc.median_ms/1000)/1e9
    ridge=gflops/bw if bw else 0
    print(f"Compute median={stc.median_ms:.3f} ms; estimated Python-loop GFLOP/s={gflops:.6f}")
    print(f"Empirical ridge point estimate={ridge:.6f} FLOP/Byte")
    print(emit_verify_tag("PHASE3A",0,bw,gflops))

if __name__ == "__main__":
    mp.freeze_support()
    main()
