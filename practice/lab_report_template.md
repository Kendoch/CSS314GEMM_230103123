# Performance Evaluation and Optimization in Parallel Computing

**Student ID:** 230103123
**Device:** Apple M1
hw.physicalcpu: 8
hw.logicalcpu: 8
hw.cachelinesize: 128
hw.l1dcachesize: 65536
hw.l2cachesize: 4194304 
**Python version:**  Python 3.9.6
**Date:** 13.11.2026

> Run each script on your own computer. Replace every placeholder with measured output. Do not invent timings or verification hashes.

=== PHASE 0: HARDWARE ===
platform: macOS-15.4.1-arm64-arm-64bit
processor: Apple M1
physical_cores: 8
logical_threads: 8
cache_line_bytes: 128
L1d: 65536
L2: 4194304
L3: 
perf_counter_ns average call latency: 52.354 ns
VERIFY_HASH[PHASE0]: 4625665064C1CE42 (P_log=8)
| Measurement | Result |
|---|---:|
| Logical CPUs | 8 |
| Workers used | 8 |

| Stride (elements) | Stride (bytes) | Median (ms) | IQR (ms) | Throughput (Mops/s) |
|---:|---:|---:|---:|---:|
| 1 | 8 | 554.75 | 39.04 | 28.842 |
| 2 | 16 | 530.62 | 20.63 | 30.154 |
| 4 | 32 | 515.92 | 5.56 | 31.013 |
| 8 | 64 | 516.89 | 21.05 | 30.954 |
| 16 | 128 | 499.59 | 34.62 | 32.026 |
| 32 | 256 | 493.98 | 38.06 | 32.390 |

### Process Scaling

| Stride | Processes | Time (ms) | Speedup | Efficiency | Karp-Flatt |
|---:|---:|---:|---:|---:|---:|
| 1 | 1 | 2025.88 | 1.033 | 1.033 | — |
| 1 | 2 | 1087.09 | 1.925 | 0.963 | 0.03882 |
| 1 | 4 | 607.10 | 3.447 | 0.862 | 0.05343 |
| 1 | 8 | 516.67 | 4.051 | 0.506 | 0.13927 |
| 16 | 1 | 2077.23 | 0.984 | 0.984 | — |
| 16 | 2 | 1110.38 | 1.841 | 0.920 | 0.08666 |
| 16 | 4 | 606.30 | 3.371 | 0.843 | 0.06223 |
| 16 | 8 | 514.01 | 3.976 | 0.497 | 0.14459 |

### Discussion

The results show that increasing the stride generally improves throughput. Stride 32 achieved the highest throughput of 32.390 Mops/s. This suggests that spacing shared data further apart can reduce false sharing.

Increasing the number of processes improved performance up to 8 processes. However, efficiency decreased as the process count increased. At 8 processes, efficiency was approximately 0.5 for both tested strides. This may be caused by parallel overhead and resource contention.

### Verification

VERIFY_HASH[PHASE1]: B35BF86C7550BD99 (P_log=8)

| Measurement | Result |
|---|---:|
| Logical CPUs | 8 |
| Amdahl serial fraction | 0.02671 |
| Theoretical speedup cap | 37.444 |

### Strong Scaling

| Processes | Time (ms) | IQR (ms) | Speedup | Efficiency |
|---:|---:|---:|---:|---:|
| 1 | 1593.37 | 14.73 | 1.000 | 1.000 |
| 2 | 881.03 | 25.61 | 1.809 | 0.904 |
| 3 | 631.29 | 10.77 | 2.524 | 0.841 |
| 4 | 478.60 | 0.73 | 3.329 | 0.832 |
| 5 | 445.40 | 6.13 | 3.577 | 0.715 |
| 6 | 418.37 | 7.49 | 3.809 | 0.635 |
| 7 | 390.14 | 5.02 | 4.084 | 0.583 |
| 8 | 375.19 | 25.03 | 4.247 | 0.531 |

### Weak Scaling

| Processes | Problem size (N) | Time (ms) | Weak efficiency | Alpha | Gustafson speedup |
|---:|---:|---:|---:|---:|---:|
| 1 | 200000 | 245.90 | 1.000 | 0.1730 | 1.000 |
| 2 | 400000 | 259.66 | 0.947 | 0.1639 | 1.836 |
| 3 | 600000 | 280.18 | 0.878 | 0.1519 | 2.696 |
| 4 | 800000 | 302.16 | 0.814 | 0.1408 | 3.578 |
| 5 | 1000000 | 383.94 | 0.640 | 0.1108 | 4.557 |
| 6 | 1200000 | 432.70 | 0.568 | 0.0983 | 5.508 |
| 7 | 1400000 | 500.14 | 0.492 | 0.0851 | 6.490 |
| 8 | 1600000 | 526.72 | 0.467 | 0.0808 | 7.434 |

### Discussion

Strong scaling improved as the number of processes increased. The best result was achieved with 8 processes, with a speedup of 4.247. However, efficiency decreased to 0.531.

Weak scaling showed that execution time increased as the problem size and process count increased. Weak efficiency decreased from 1.000 to 0.467. This indicates that the system could not maintain the same performance per process as the workload grew.

### Verification

VERIFY_HASH[PHASE2]: DB86BDEB9BEE3F85 (P_log=8)
## Phase 3 — Roofline and GEMM

| Measurement | Result |
|---|---:|
| Sustained copy bandwidth (GB/s) | 1.351 |
| Compute proxy (GFLOP/s) | 0.3945 |
| Ridge point (FLOP/byte) | 0.2921 |

| Variant | Block size | Median (ms) | GFLOP/s | Max absolute error |
|---|---:|---:|---:|---:|
| Naive i-j-k | — | 437.59 | 0.07668 | — |
| Reordered i-k-j | — | 407.40 | 0.08236 | — |
| Blocked | 8 | 505.47 | 0.06638 | 0.000e+00 |
| Blocked | 16 | 475.86 | 0.07051 | 0.000e+00 |
| Blocked | 32 | 438.84 | 0.07646 | 0.000e+00 |
| Blocked | 64 | 432.92 | 0.07751 | 0.000e+00 |
| Blocked | 96 | 431.84 | 0.07770 | 0.000e+00 |
| Blocked | 128 | 428.00 | 0.07840 | 0.000e+00 |

### Discussion

The reordered i-k-j variant was the fastest. It achieved 407.40 ms and 0.08236 GFLOP/s. It improves memory access order by accessing elements in a more sequential way.

The blocked variant showed better performance with larger tile sizes. The best result was achieved with a block size of 128 (428.00 ms). Small tiles may cause additional loop overhead. Larger tiles can improve data reuse, but their footprint must fit within the available cache capacity.

However, none of the blocked variants outperformed the reordered i-k-j implementation.

### Verification

`VERIFY_HASH[PHASE3]: B809C0B024AE1C8A (P_log=8)`

| Measurement | Result |
|---|---:|
| Problem size (N) | 8000 |
| Workers | 8 |
| Selected chunk size (C*) | 1 |

| Scheduling strategy | Chunk size | Wall time (ms) | Lambda |
|---|---:|---:|---:|
| Block static | — | 4383.11 | 2.467 |
| Cyclic static | — | 2722.48 | 1.053 |
| Dynamic | 1 | 2757.24 | 1.004 |
| Dynamic | 8 | 2787.81 | 1.008 |
| Dynamic | 64 | 2962.36 | 1.063 |
| Dynamic | 512 | 3333.06 | 1.435 |

### Discussion

Block static scheduling had the longest execution time at 4383.11 ms. Cyclic static scheduling performed better, reducing the time to 2722.48 ms.

Among the dynamic strategies, chunk size 1 achieved the lowest execution time of 2757.24 ms. It was also selected as the best chunk size. Larger chunks increased execution time, reaching 3333.06 ms with chunk size 512.

These results suggest that cyclic and small-chunk dynamic scheduling handle the workload imbalance better than block static scheduling.

### Verification

VERIFY_HASH[PHASE4]: A846F46B572B7200 (P_log=8)
## Verification lines

Paste all five exact output lines:

```text
VERIFY_HASH[PHASE0]: 4625665064C1CE42 (P_log=8)
VERIFY_HASH[PHASE1]: B35BF86C7550BD99 (P_log=8)
VERIFY_HASH[PHASE2]: DB86BDEB9BEE3F85 (P_log=8)
VERIFY_HASH[PHASE3]: B809C0B024AE1C8A (P_log=8)
VERIFY_HASH[PHASE4]: A846F46B572B7200 (P_log=8)
```

## Reproducibility notes

Record the command used to run each script, device power mode, background workload, and any deviations from the handout.
