# Optimization Workflow

Use this evidence chain for every material optimization:

1. **Symptom**: state the user-visible regression or budget.
2. **Reproduction**: define data, concurrency, phase, platform, toolchain, and command.
3. **Baseline**: capture correctness and performance results with uncertainty.
4. **Profile**: identify the dominant CPU, wait, allocation, memory, size, or compile-time cause.
5. **Hypothesis**: predict which metric the change affects and possible tradeoffs.
6. **Change**: implement the smallest cause-focused correction.
7. **Verification**: rerun correctness, safety, and identical performance protocols.
8. **Guardrail**: add a benchmark, budget, telemetry, or documented manual procedure.

## Common traps

- optimizing debug builds;
- changing several variables before remeasurement;
- benchmarking toy inputs or only averages;
- replacing borrowing with unsafe code for an unmeasured gain;
- adding caches or unbounded parallelism that improve throughput while destroying memory or tail latency;
- claiming improvement from one run;
- comparing different dependency graphs, features, CPUs, or target settings;
- treating compiler output or Clippy suggestions as a performance profile.

## Result report

Report workload, commands, commits, toolchain, hardware, samples, absolute values, relative change, variance, correctness gates, secondary regressions, and remaining uncertainty. Include raw artifacts when policy permits.
