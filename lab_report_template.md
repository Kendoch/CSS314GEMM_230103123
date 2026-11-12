# Parallel Computing Lab Report

**Student ID:**  230103123
**Name:**  Temirlan Bakhytzhan
**Date:**  12 november


## Phase 0 — Hardware Topology Audit & Harness Calibration

### Hardware Baseline

| Hardware Parameter | Measured Value |
|---|---|
| CPU Model String | Apple M1 |
| Physical Cores | 8 |
| Logical Threads | 8 |
| Cache Line Size | 128 Bytes |
| L1 Data Cache | 64 KB |
| L2 Cache Size | 4 MB |
| L3 Cache Size | Not reported by macOS |
| Python Version | Python 3.12.7 |
| Operating System | macOS 15.4.1 ARM64 |

### Timer Calibration

The benchmark used `time.perf_counter_ns()` to measure timer precision.

- Total clock reads: 2,000,000
- Total calibration time: 108.342 ms
- Average timer call latency: 54.17 ns

### Hardware Analysis

The Apple M1 processor provides 8 physical CPU cores and 8 logical CPUs. Its cache line size is 128 bytes.

This information will be used in subsequent experiments, especially false sharing analysis, process scaling and cache optimization.

### Verification

VERIFY_HASH [PHASE0]: E06F306576DEDE4B (P_log=8)


## Phase 1 — False Sharing and Cache Coherence

### False Sharing Experiment

The experiment was performed on an Apple M1 processor with a
128-byte cache line.

The stride was changed from 1 to 32 to investigate the effect
of memory separation between worker processes.

The lowest throughput was observed at stride 1:
2.490 Mops/s.

Throughput increased to 3.669 Mops/s at stride 16
and reached 3.824 Mops/s at stride 32.

This suggests that increasing the distance between shared
memory locations can reduce cache contention.

However, stride 32 produced better throughput than stride 16,
so the results do not prove that cache-line separation was
the only factor affecting performance.

### Scaling Experiment

For stride 1, the best result was obtained with 2 processes.
Using 8 processes reduced performance below the single-process
baseline.

For stride 16, the best result was obtained with 4 processes,
with an execution time of 72.803 ms.

The results show that parallel performance does not always
increase with the number of processes.

Process management overhead and memory contention may reduce
the benefits of parallel execution.

### Verification

VERIFY_HASH [PHASE1]: 57523340602888EB (P_log=8)

## Phase 2 — Strong and Weak Scaling

### Strong Scaling

The strong scaling experiment used a fixed problem size
while increasing the number of processes from 1 to 8.

The execution time decreased from 289.262 ms with one
process to 67.608 ms with eight processes.

The maximum measured speedup was 4.279.

The efficiency at eight processes was 0.535 (53.5%).

The results show that parallel processing significantly
improved performance. However, efficiency decreased as
the number of processes increased because of parallel
execution overhead and other system limitations.

### Weak Scaling

The weak scaling experiment increased the problem size
proportionally with the number of processes.

The execution time increased from 49.242 ms with one
process to 93.155 ms with eight processes.

The efficiency decreased from 1.000 to 0.529.

This indicates that the system did not maintain ideal
weak scaling. Additional process management and
computational overhead affected performance.

### Amdahl's and Gustafson's Laws

Amdahl's Law explains that the sequential part of a
program limits the maximum possible speedup.

Gustafson's Law describes how parallel performance
can improve when the problem size increases with the
number of processors.

The measured Gustafson estimate reached 7.475 at
eight processes.

The serial stage was included in the total execution
time. Therefore, its contribution must be measured
separately before reporting an exact serial fraction.

### Verification

VERIFY_HASH [PHASE2]: 851CE337AAAED2FB (P_log=8)

## Phase 3A — Roofline Model

### Memory Bandwidth

The memory copy experiment produced a median execution time of 95.871 ms.

The estimated memory bandwidth was 0.175 GB/s.

This measurement represents the bandwidth achieved by the tested Python implementation, not the theoretical maximum memory bandwidth of the Apple M1 processor.

### Compute Performance

The compute experiment produced a median execution time of 183.370 ms.

The estimated Python-loop performance was 0.139608 GFLOP/s.

This result shows the computational performance of the tested Python loop.

### Ridge Point

The empirical ridge point estimate was 0.797768 FLOP/Byte.

The ridge point represents the estimated boundary between memory-bound and compute-bound performance in the Roofline Model.

The results provide an experimental baseline for understanding the relationship between memory performance and computational performance.

### Verification

VERIFY_HASH [PHASE3A]: 6DE60EA5DA5CE9B4 (P_log=8)

## Phase 3B — Matrix Multiplication (GEMM)

### Loop Order Comparison

Two matrix multiplication loop orders were compared: IJK and IKJ.

The IJK implementation achieved 0.032434 GFLOP/s with a median execution time of 54.556 ms.

The IKJ implementation achieved 0.040374 GFLOP/s with a median execution time of 43.827 ms.

The IKJ implementation was faster than IJK in this experiment.

This improvement can be explained by differences in memory access patterns and cache locality.

### Block Size Optimization

Ten block sizes were tested: 4, 8, 12, 16, 24, 32, 48, 64, 96, and 128.

The best measured result was obtained with a block size of 128.

Its median execution time was 44.525 ms, and its performance was 0.039741 GFLOP/s.

The maximum error was 0.000e+00, indicating that the blocked implementation produced the same result as the reference implementation in this test.

### Conclusion

The experiment demonstrated that loop ordering and block size can influence matrix multiplication performance.

Among the tested configurations, IKJ performed better than IJK, while block size 128 achieved the highest throughput among the tested block sizes.

The implementation was single-process Python code, so this experiment evaluated loop ordering and cache behavior rather than multiprocessing GEMM.

## Phase 4 — Scheduling and Load Balancing

### Static Scheduling

Two static scheduling methods were compared:
Block and Cyclic.

Block scheduling produced a maximum worker time of
14.620 ms with a lambda value of 1.974.

Cyclic scheduling produced a maximum worker time of
12.654 ms with a lambda value of 1.901.

Cyclic scheduling demonstrated slightly better load
balancing because tasks with different computational
costs were distributed more evenly between workers.

### Dynamic Scheduling

Dynamic scheduling was tested with chunk sizes of
1, 4, 16, 64, 256, and 1024.

The best measured wall time was obtained with
chunk size 64: 106.176 ms.

However, individual worker active times were not
available in this implementation. Therefore, lambda
could not be calculated for dynamic scheduling.

The dynamic measurements also include process pool
startup overhead.

### Verification

VERIFY_HASH [PHASE4]: 607D47AD613E1F48 (P_log=8)

## Appendix — Source Code
List the exact code versions used for each experiment.
