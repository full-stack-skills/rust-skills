---
name: rust-testing
description: Design, implement, and validate Rust tests, including unit, integration, doctest, compile-fail, property, fuzz, benchmark, coverage, async, concurrency, process, daemon, IPC, terminal, platform, and hardware-facing test strategies. Use when users ask for Rust test architecture, flaky-test diagnosis, coverage gates, benchmarks, trybuild, cargo-nextest, real-process tests, or failure-path verification.
---

# Rust Testing and Benchmarking

> Based on Chapter 11 of *The Rust Programming Language* and the Rust Book.

## Capability Boundaries

### ✅ Strengths
1. Unit tests (using `#[test]`, organizing test modules with `#[cfg(test)]`)
2. Assertion macros (`assert!`, `assert_eq!`, `assert_ne!`, `debug_assert!`)
3. Test attributes (`#[should_panic]`, `#[ignore]`, `#[cfg(test)]`)
4. Integration tests (tests/ directory and shared modules)
5. Documentation tests (code blocks, hidden lines with `#`, should_panic/no_run/ignore flags)
6. cargo test runner (filtering, --nocapture, --test-threads, --include-ignored options)
7. Stable Criterion benchmarks; explicitly distinguishing stable Criterion from nightly-only libtest `#[bench]` attribute
8. Code coverage using cargo-llvm-cov
9. Asynchronous race conditions, backpressure, timeouts, process/daemon models, platform matrices, and resource-constrained testing

### ⚠️ Prerequisites
1. Understanding of Rust module system (rust-workspace)

### ❌ Out of Scope
1. Property-based tests (`proptest`) → Not currently covered
2. Mock objects → Not currently covered
3. Basic Rust syntax → Use `rust-stable` skill instead

## When to Use

- "Write unit tests"
- "Where should integration tests be placed?"
- "How do I write documentation tests?"
- "Performance benchmarking"
- "Check code coverage"

---

## Routing Boundary

Use `rust-java-migration-testing` when tests must disposition a source Java suite, distinguish mirrored tests from golden/live differential evidence, add target-specific ownership/async/error/component obligations, audit coverage-chasing tests, or verify migration lifecycle/adapter/host acceptance. Keep this skill focused on general Rust test mechanics and Rust-native test architecture.

## Unit Tests

```rust
// src/lib.rs
pub fn add(a: i32, b: i32) -> i32 { a + b }
pub fn divide(a: i32, b: i32) -> i32 {
    if b == 0 { panic!("divide by zero"); }
    a / b
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_add() {
        assert_eq!(add(2, 2), 4);
    }

    #[test]
    fn test_add_negative() {
        assert_eq!(add(-1, 1), 0, "addition with negative");
    }

    #[test]
    #[should_panic(expected = "divide by zero")]
    fn test_divide_by_zero() {
        divide(1, 0);
    }

    #[test]
    #[ignore = "not implemented"]
    fn test_future() { unimplemented!() }
}
```

## Integration Tests

```text
my-project/
├── Cargo.toml
├── src/lib.rs
└── tests/
    ├── common/          # Test shared modules
    │   └── mod.rs
    ├── integration_test.rs
    └── api_test.rs
```

```rust
// tests/integration_test.rs — Each file is an independent crate
use my_project::add;

#[test]
fn integration_test() {
    assert_eq!(add(1, 2), 3);
}

// tests/common/mod.rs — Shared helper functions
pub fn setup() { /* ... */ }
```

## Documentation Tests (doctest)

```rust
/// Add two numbers.
///
/// ```
/// use my_crate::add;
/// assert_eq!(add(2, 3), 5);
/// ```
///
/// ```rust,should_panic
/// my_crate::divide(1, 0);
/// ```
///
/// ```rust,no_run
/// // Compile but do not run
/// loop {}
/// ```
pub fn add(a: i32, b: i32) -> i32 { a + b }
```

## cargo test Commands

```bash
cargo test                    # Run all tests
cargo test test_name          # Filter by name
cargo test -- --nocapture     # Show println output
cargo test -- --test-threads=1 # Single thread
cargo test -- --skip test_name # Skip specific tests
cargo test -- --ignored       # Only run #[ignore] tests
cargo test -- --include-ignored # Include ignored tests
cargo test --doc              # Run only documentation tests
cargo test -p my-crate        # Specific package
```

## Benchmarks

Stable projects should prioritize Criterion. The built-in libtest `#[bench]` still relies on nightly's `#![feature(test)]`, which cannot be used as a stable default solution.

```rust
// Nightly-only builtin approach (do not use for stable gatekeeping)
#![feature(test)]
extern crate test;

#[cfg(test)]
mod benches {
    use test::Bencher;
    use super::*;

    #[bench]
    fn bench_add(b: &mut Bencher) {
        b.iter(|| add(1, 2));
    }
}

// Stable approach using criterion
// [dev-dependencies] criterion = { version = "0.5", features = ["html_reports"] }
use criterion::{black_box, Criterion};

fn bench_add(c: &mut Criterion) {
    c.bench_function("add", |b| b.iter(|| add(black_box(1), black_box(2))));
}
criterion_group!(benches, bench_add);
criterion_main!(benches);
```

## Code Coverage

```bash
# Install
cargo install cargo-llvm-cov

# Usage
cargo llvm-cov                   # Run and report results
cargo llvm-cov --open            # Generate HTML reports
cargo llvm-cov --lcov --output-path lcov.info  # LCOV format output
```

## Workflow

1. Prepare test environment — Ensure cargo test is available, confirm test types (unit/integration/documentation)
2. Write unit tests — Implement #[test] functions within `#[cfg(test)]` modules
3. Add integration tests — Create independent crate-type files in the tests/ directory
4. Add documentation tests — Embed executable code blocks inside /// comments
5. Run and debug — Use cargo test; use --nocapture to locate issues; prioritize resource isolation or test grouping for shared resources, avoiding permanent serialization of full test suites
6. Concurrency and platform validation — Implement bounded assertions for queue limits, slow consumers, disconnections, cancellations, timeouts, and graceful shutdowns on real target platforms; run platform-specific code directly
7. Coverage checks — Use cargo llvm-cov to verify coverage ranges

## Gotchas

1. Code in `#[cfg(test)]` modules does not compile into release builds — Helper functions should reside in tests/common/mod.rs
2. Integration test files are independent crates — Cannot use super:: or crate:: prefixes within them
3. Hidden lines (#) in documentation tests remain executable but invisible to the compiler
4. cargo test runs by default in parallel; shared resource conflicts should be resolved via unique temporary directories/ports, process isolation, nextest test group limits, or local serialization only when necessary
5. #[bench] requires #![feature(test)] — Stable Rust must use criterion instead
6. Providing a broad timeout for async tests hides deadlock causes; also assert intermediate states, task recovery, and resource counts

## On-Demand Resources

- [Test examples](examples/examples.md)
- [Macro commands and command reference](references/references.md)
- [Concurrency, daemon, and platform testing](references/concurrency-daemon-platform-testing.md): Test for memory leaks in tasks, slow consumers, race conditions, real processes, and resource-limited parallelism when reading.
- `examples/golden-tests/`: CI compilation and execution of doctest golden examples

## Official References

- [The Book ch 11](https://doc.rust-lang.org/book/ch11-00-testing.html)
- [Rustdoc Book — doctest documentation](https://doc.rust-lang.org/rustdoc/write-documentation/documentation-tests.html)
- [cargo test command reference](https://doc.rust-lang.org/cargo/commands/cargo-test.html)
- [criterion.rs library docs](https://docs.rs/criterion/)
