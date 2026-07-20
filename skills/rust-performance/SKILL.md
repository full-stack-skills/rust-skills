---
name: rust-performance
description: Measure, profile, optimize, and regression-test Rust performance across latency, throughput, CPU, allocations, memory, binary size, and compile time using representative workloads, Criterion, iai-callgrind, cargo-flamegraph, samply, DHAT, heap or pprof tools, cargo-bloat, cargo-llvm-lines, and build timings. Use when users report slow Rust code, high memory or CPU, large binaries, noisy benchmarks, tail-latency regressions, or need performance budgets and evidence-backed optimization.
---

# Rust Performance

Optimize from evidence. Define the user-visible metric, reproduce the workload, establish a stable baseline, profile the dominant cost, change one cause, and prove both correctness and improvement.

## Scope and Routing

Use this skill for microbenchmarks, end-to-end load tests, CPU profiles, allocation and heap analysis, binary size, compile time, cache behavior, and regression budgets.

Route concurrency semantics to `rust-concurrency`, telemetry pipelines to `rust-observability`, general test architecture to `rust-testing`, release profiles and features to `rust-cargo-build`, and semantic review to `rust-code-review`.

## Workflow

### 1. Define the performance contract

Record the workload, dataset, inputs, concurrency, platform, CPU and memory limits, toolchain, target, features, allocator, build profile, warm-up, cache state, and success metrics. Distinguish throughput from p50/p95/p99 latency and steady-state from startup or shutdown.

Do not optimize debug builds or synthetic inputs unless they represent the actual problem.

### 2. Establish a reproducible baseline

- Verify correctness before benchmarking.
- Use release-like optimization, codegen units, LTO, panic strategy, and target CPU settings intentionally.
- Isolate background load, power management, thermal throttling, and noisy shared runners.
- Record raw samples and uncertainty, not only one average.
- Compare the same commit, toolchain, dependency graph, and hardware when enforcing small regressions.

Read [Benchmarking and Regression Gates](references/benchmarking-and-regressions.md).

### 3. Choose the measurement layer

| Question | Tool or evidence |
|---|---|
| Is a pure operation faster? | Criterion or Divan microbenchmark |
| Did instruction-level cost change? | iai-callgrind on supported systems |
| Where is CPU time spent? | samply, cargo-flamegraph, Instruments, perf, pprof |
| Where are allocations retained? | DHAT, heap profiler, allocator metrics |
| Why is the binary large? | cargo-bloat and feature inspection |
| What drives compile time? | Cargo build timings and cargo-llvm-lines |
| Does the service meet its SLO? | Representative load test plus observability |

A microbenchmark does not prove end-to-end latency, overload behavior, or memory bounds.

### 4. Profile before editing

Capture a profile under the failing workload. Preserve symbols and use the same optimized artifact intended for comparison. Separate on-CPU work, waiting, lock contention, I/O, allocation, page faults, and scheduler overhead. Read [CPU and Latency Profiling](references/cpu-and-latency-profiling.md).

### 5. Optimize the dominant cause

Common changes include algorithmic complexity, fewer passes, better batching, avoiding repeated parsing or allocation, borrowing instead of cloning, data-layout improvements, reduced synchronization, bounded queues, streaming, feature reduction, and moving CPU work off async workers.

Do not use unsafe, custom allocators, SIMD, lock-free structures, or caching until simpler changes are insufficient and invariants plus fallback behavior are tested.

### 6. Measure memory, size, and build cost

Track peak RSS, retained heap, allocation rate, fragmentation, cache growth, buffer bounds, binary sections, monomorphization, debug information, enabled features, macro expansion, and incremental versus clean compile time. Read [Memory, Binary Size, and Compile Time](references/memory-size-and-compile-time.md).

### 7. Prove the result

Rerun correctness tests and the exact baseline protocol. Report absolute and relative results, variance, hardware and software context, tradeoffs, and regressions in secondary metrics. Add a durable benchmark or budget only when the environment can detect the intended threshold reliably.

## Completion Criteria

- Define a representative workload and user-visible metric.
- Record reproducible baseline evidence before optimization.
- Profile and identify the dominant cost rather than guessing.
- Preserve correctness and safety through targeted tests.
- Re-measure under the same protocol and report uncertainty plus tradeoffs.
- Add a stable regression check or explain why the environment is too noisy.

## Resources

- [Benchmarking and Regression Gates](references/benchmarking-and-regressions.md)
- [CPU and Latency Profiling](references/cpu-and-latency-profiling.md)
- [Memory, Binary Size, and Compile Time](references/memory-size-and-compile-time.md)
- [Optimization Workflow](references/optimization-workflow.md)
- [Execution Scenarios](examples/examples.md)
- `examples/golden-performance/`: a compiled Criterion benchmark target.

## Upstream Sources

- [Criterion.rs](https://criterion-rs.github.io/criterion.rs/book/)
- [iai-callgrind](https://docs.rs/iai-callgrind/)
- [cargo-flamegraph](https://github.com/flamegraph-rs/flamegraph)
- [samply](https://github.com/mstange/samply)
- [cargo-bloat](https://github.com/RazrFalcon/cargo-bloat)
- [Cargo build timings](https://doc.rust-lang.org/cargo/reference/timings.html)

## Data Privacy

This skill does not collect, store, or transmit user data. Profiles, heap dumps, command lines, symbols, and benchmark datasets may contain sensitive information; confirm storage and upload policy before sharing them.
