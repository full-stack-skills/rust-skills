# CPU and Latency Profiling

## Sampling profilers

Use samply for an interactive cross-platform-friendly sampling workflow where supported, cargo-flamegraph for convenient folded-stack flame graphs, Instruments on macOS, perf on Linux, and pprof integrations when in-process or remote capture is required.

Build optimized code with usable symbols. Verify that frame pointers, debug information, stripping, and platform permissions allow trustworthy stacks. A profile dominated by unknown frames is not sufficient evidence.

## Interpret profiles carefully

- Wide frames consume substantial sampled CPU time.
- Tall stacks show call ancestry, not cost by themselves.
- Off-CPU waiting, lock contention, I/O, page faults, and scheduler delay may require different tools or tracing.
- Inlining, monomorphization, and async state machines can change stack presentation.
- Sample under the workload and phase that exhibits the regression.

Tail latency often comes from queueing, saturation, retries, lock hold time, allocator contention, or slow dependencies rather than one hot function. Correlate profiles with request traces and queue metrics.

## Sources

- [cargo-flamegraph](https://github.com/flamegraph-rs/flamegraph)
- [samply](https://github.com/mstange/samply)
- [pprof-rs](https://github.com/tikv/pprof-rs)
