# Rust Performance Execution Scenarios

## Optimize a hot parser

User request:

> This parser consumes too much CPU after the last release.

Reproduce the real data distribution, compare the relevant commits, profile optimized builds, identify the dominant path, make one cause-focused change, and report Criterion plus profile evidence with correctness tests.

## Diagnose high service memory

User request:

> RSS grows under load and does not return after traffic stops.

Separate allocator retention, live heap, caches, queues, connection buffers, task stacks, and mapped memory. Bound the suspected resource, verify shutdown and idle behavior, and compare heap plus RSS evidence.

## Reduce binary and compile size

User request:

> Our Rust CLI binary and release build became much larger.

Compare features and dependency graphs, inspect Cargo timings, cargo-bloat, and monomorphization, then evaluate profile settings and dependency reductions without hiding symbols or dropping capabilities required for operations.
