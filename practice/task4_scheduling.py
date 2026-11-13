import multiprocessing as mp
import math
import time
from harness import emit_verify_tag

N=8000

def work_item(i):
    k = 1 + int((i/40)**2)
    x = (i+1)*0.0001
    for _ in range(k):
        x = math.sin(x) + math.cos(x*0.5) + math.sqrt(abs(x)+1.0)
    return x

def _static_worker(indices, timings, slot, result_queue):
    t0=time.perf_counter()
    total=0.0
    for i in indices:
        total += work_item(i)
    timings[slot]=time.perf_counter()-t0
    result_queue.put(total)

def _dynamic_worker(counter, lock, chunk, timings, slot, result_queue):
    t0=time.perf_counter()
    total=0.0
    while True:
        with lock:
            start=counter.value
            counter.value += chunk
        if start>=N:
            break
        for i in range(start,min(start+chunk,N)):
            total += work_item(i)
    timings[slot]=time.perf_counter()-t0
    result_queue.put(total)

def run_static(p, mode):
    timings=mp.Array('d',p)
    q=mp.Queue()
    processes=[]
    for w in range(p):
        if mode=="block":
            start=w*N//p
            end=(w+1)*N//p
            indices=range(start,end)
        else:
            indices=range(w,N,p)
        proc=mp.Process(target=_static_worker,args=(indices,timings,w,q))
        proc.start()
        processes.append(proc)
    for proc in processes:
        proc.join()
        if proc.exitcode != 0:
            raise RuntimeError(f"Worker failed: {proc.exitcode}")
    values=[q.get() for _ in processes]
    q.close()
    return sum(values),list(timings)

def run_dynamic(p,chunk):
    timings=mp.Array('d',p)
    counter=mp.Value('i',0)
    lock=mp.Lock()
    q=mp.Queue()
    processes=[]
    for w in range(p):
        proc=mp.Process(target=_dynamic_worker,args=(counter,lock,chunk,timings,w,q))
        proc.start()
        processes.append(proc)
    for proc in processes:
        proc.join()
        if proc.exitcode != 0:
            raise RuntimeError(f"Worker failed: {proc.exitcode}")
    values=[q.get() for _ in processes]
    q.close()
    return sum(values),list(timings)

def measure(fn):
    t0=time.perf_counter()
    value,times=fn()
    wall=(time.perf_counter()-t0)*1000
    avg=sum(times)/len(times) if times else 0
    imbalance=max(times)/avg if avg else 0
    return wall,imbalance,times,value

def main():
    p=max(1,min(mp.cpu_count(),8))
    print(f"N={N}, workers={p}")
    block=measure(lambda:run_static(p,"block"))
    cyclic=measure(lambda:run_static(p,"cyclic"))
    print(f"Block static: wall={block[0]:.2f} ms, lambda={block[1]:.3f}")
    print(f"Cyclic static: wall={cyclic[0]:.2f} ms, lambda={cyclic[1]:.3f}")
    dynamic={}
    for chunk in (1,8,64,512):
        result=measure(lambda:run_dynamic(p,chunk))
        dynamic[chunk]=result
        print(f"Dynamic C={chunk}: wall={result[0]:.2f} ms, lambda={result[1]:.3f}")
    best=min(dynamic,key=lambda x:dynamic[x][0])
    print(f"Selected chunk C*={best}")
    print(emit_verify_tag("PHASE4","REPLACE_WITH_YOUR_STUDENT_ID",block[0],dynamic[best][0]))

if __name__=="__main__":
    mp.freeze_support()
    main()
