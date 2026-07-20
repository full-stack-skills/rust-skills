# Benchmarking and Regression Gates

## Benchmark design

Benchmark a meaningful unit with representative input distributions and data sizes. Prevent setup, file creation, network startup, or random generation from contaminating the measured section unless those costs are part of the contract.

Use `std::hint::black_box` or the benchmark framework's equivalent to prevent irrelevant optimization. Verify outputs outside the timed path so the optimizer cannot remove work.

Criterion provides statistical warm-up, sampling, outlier handling, reports, and comparison. Pin its version and record its MSRV. Use throughput configuration when results should be interpreted per byte, item, or operation.

## Noise control

- prefer dedicated or controlled machines for tight thresholds;
- record CPU model, governor, frequency, thermal state, OS, toolchain, target, features, allocator, and commit;
- avoid unrelated background work and shared CI runners for small changes;
- compare multiple samples and confidence intervals;
- use larger effects or trend detection when the environment is noisy.

## Regression gates

Do not fail CI on a tiny percentage without proving the runner can distinguish it. Choose one of:

- a generous hard budget for latency, memory, or binary size;
- comparison against a stored baseline on stable hardware;
- scheduled trend analysis with review rather than per-commit failure;
- deterministic instruction-count tools such as iai-callgrind where supported.

Keep raw results as artifacts with retention and privacy policy.

## Sources

- [Criterion.rs book](https://criterion-rs.github.io/criterion.rs/book/)
- [iai-callgrind](https://docs.rs/iai-callgrind/)
- [std::hint::black_box](https://doc.rust-lang.org/std/hint/fn.black_box.html)
