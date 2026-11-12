import argparse, math, multiprocessing as mp, time
from harness import run_benchmark, emit_verify_tag

N=12_000
def work_item(i):
    k=1+(i//60)**2
    x=0.123
    for j in range(k):
        x=math.sin(x+0.000001*j)+math.cos(x*0.5)+math.sqrt(abs(x)+1e-12)*0.001
    return x

def worker_static(args):
    mode, worker, p, n = args
    t0=time.perf_counter()
    if mode=="block":
        lo=worker*n//p; hi=(worker+1)*n//p
        indices=range(lo,hi)
    else:
        indices=range(worker,n,p)
    acc=0.0
    for i in indices: acc+=work_item(i)
    return (time.perf_counter()-t0)*1000,acc

def dynamic_worker(args):
    name, lock, counter, chunk, n = args
    # This function is intentionally unused; dynamic queue is implemented with Pool chunks below.
    return 0.0

def run_static(mode,p,n):
    with mp.Pool(p) as pool:
        vals=pool.map(worker_static,[(mode,t,p,n) for t in range(p)])
    times=[x[0] for x in vals]
    return max(times), max(times)/ (sum(times)/len(times)), times

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--quick",action="store_true")
    args=ap.parse_args()
    p=mp.cpu_count(); n=1500 if args.quick else N
    print("PHASE 4 — Scheduling")
    for mode in ("block","cyclic"):
        wall,lam,times=run_static(mode,p,n)
        print(f"{mode}: worker_max={wall:.3f} ms lambda={lam:.3f} worker_times={[round(x,2) for x in times]}")
    # Dynamic scheduling using multiprocessing.Pool.imap_unordered with explicit chunksize.
    # Per-worker active times are not exposed by Pool, so lambda is reported as N/A.
    for c in (1,4,16,64,256,1024):
        t0=time.perf_counter()
        with mp.Pool(p) as pool:
            total=sum(pool.imap_unordered(work_item,range(n),chunksize=c))
        wall=(time.perf_counter()-t0)*1000
        print(f"dynamic chunk={c}: wall={wall:.3f} ms lambda=N/A (Pool does not expose per-process active time)")
    print("For strict lambda telemetry, implement dedicated workers with a shared timing array.")
    print(emit_verify_tag("PHASE4",0,0.0,0.0))

if __name__=="__main__":
    mp.freeze_support()
    main()
