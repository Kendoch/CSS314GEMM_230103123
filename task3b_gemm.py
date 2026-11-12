import argparse, multiprocessing as mp, time
from harness import run_benchmark

N=384
TILES=(4,8,12,16,24,32,48,64,96,128)

def make_matrices(n):
    a=[((i*7)%101)/101.0 for i in range(n*n)]
    b=[((i*11)%97)/97.0 for i in range(n*n)]
    return a,b

def gemm_ijk(a,b,n):
    c=[0.0]*(n*n)
    for i in range(n):
        for j in range(n):
            s=0.0
            for k in range(n): s += a[i*n+k]*b[k*n+j]
            c[i*n+j]=s
    return c

def gemm_ikj(a,b,n):
    c=[0.0]*(n*n)
    for i in range(n):
        row=i*n
        for k in range(n):
            aik=a[row+k]; bk=k*n
            for j in range(n):
                c[row+j] += aik*b[bk+j]
    return c

def gemm_blocked(a,b,n,bs):
    c=[0.0]*(n*n)
    for ii in range(0,n,bs):
      for kk in range(0,n,bs):
       for jj in range(0,n,bs):
        for i in range(ii,min(ii+bs,n)):
         ci=i*n; ai=i*n
         for k in range(kk,min(kk+bs,n)):
          aik=a[ai+k]; bk=k*n
          for j in range(jj,min(jj+bs,n)):
           c[ci+j]+=aik*b[bk+j]
    return c

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--quick",action="store_true")
    args=ap.parse_args()
    n=96 if args.quick else N
    a,b=make_matrices(n)
    reps=1 if args.quick else 3
    variants=[("ijk",lambda:gemm_ijk(a,b,n)),("ikj",lambda:gemm_ikj(a,b,n))]
    for name,fn in variants:
        st=run_benchmark(fn,0,reps)
        g=2*n**3/(st.median_ms/1000)/1e9
        print(f"{name}: median={st.median_ms:.3f} ms GFLOP/s={g:.6f}")
        if name=="ikj": reference=fn()
    best=None
    for bs in TILES:
        st=run_benchmark(lambda:gemm_blocked(a,b,n,bs),0,reps)
        result=gemm_blocked(a,b,n,bs)
        err=max(abs(x-y) for x,y in zip(reference,result))
        g=2*n**3/(st.median_ms/1000)/1e9
        footprint=3*bs*bs*8
        print(f"BS={bs:3d} median={st.median_ms:.3f} ms GFLOP/s={g:.6f} "
              f"tile_footprint={footprint} B max_error={err:.3e}")
        if best is None or g>best[0]: best=(g,bs)
    print(f"Best measured tile: BS={best[1]}, GFLOP/s={best[0]:.6f}")
    print("Note: this single-process Python implementation is a loop-order/cache experiment, not multiprocessing GEMM.")

if __name__=="__main__":
    mp.freeze_support()
    main()
