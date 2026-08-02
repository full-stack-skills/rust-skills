# Cross-language Migration Testing Profile

Every `<target>-java-migration-testing` adapter shares these invariants:

- every Java test method and concrete generated case is in the denominator;
- every source fixture/resource/script/corpus/golden/data file is copied exactly;
- contract, inputs, assertions, fixture state, side effects, and cleanup remain;
- complete pinned source and target suites run;
- every case participates in golden or live Java/target comparison;
- completion requires only `MATCH`, with zero mismatch, harness failure, skip,
  ignore, or not-run;
- `<project>-test` owns whole-project replay and aggregate evidence;
- target-language obligations are additive.

The Rust adapter adds Cargo workspace/package validation, Rust test extraction,
ownership/error/async/feature/unsafe obligations, and Rust-specific runners. The
Zig adapter adds `build.zig`, `migration-test`, allocator/error/ABI/target
obligations, and Zig test extraction. Future Kotlin and Swift adapters must keep
the same shared outcome while adapting Gradle/Kotest/coroutines or
SwiftPM/XCTest/Swift Testing/ARC/concurrency mechanics.

Shared rule changes require auditing every target adapter. Target syntax and
toolchain changes stay within their target package.

The `<project>-test` package name and responsibility are invariant, but its
parent directory follows the migration roadmap's root-flat, hybrid, or
contained workspace topology. The Rust adapter must not assume `crates/`.
