# Cross-language Java Migration Profile

`rust-java-migration` is the Rust target adapter of a shared Java migration
contract. Other target-language skill packages expose the same pair:

| Package | Migration | Testing |
|---|---|---|
| `rust-skills` | `rust-java-migration` | `rust-java-migration-testing` |
| `zig-skills` | `zig-java-migration` | `zig-java-migration-testing` |
| `kotlin-skills` | `kotlin-java-migration` | `kotlin-java-migration-testing` |
| `swift-skills` | `swift-java-migration` | `swift-java-migration-testing` |

## Shared invariants

Every target adapter keeps identical source-side rules:

- full Java object/member/test/asset denominator;
- blocking states `MISSING`, `MISPLACED`, `STUB`, `PARTIAL`, `UNVERIFIED`;
- no semantic simplification or facade/file-count completion;
- exact source asset copies and every-case result comparison;
- dedicated `<project>-test` whole-project acceptance module;
- separate structural, behavioral, host, non-functional, and production claims;
- target-language tests are additive and never replace source parity.

Every testing adapter requires all source cases `MATCH` and zero mismatch,
harness failure, skip, ignore, or not-run. Coverage and two green suites are not
parity evidence.

## Target adapter boundary

Only these concerns vary by target:

- compiler/runtime, build manifest, module system, crate/package boundaries,
  and scale-appropriate workspace layout;
- naming and API idioms;
- error/null/generic/async/concurrency mapping;
- ownership, allocation, cleanup, and lifecycle model;
- reflection, annotations, code generation, serialization, and SPI replacement;
- test syntax, whole-project build command, platform/feature/target matrix;
- target-specific obligations such as Rust ownership/unsafe, Zig allocators/ABI,
  Kotlin coroutine/Flow/JVM interop, or Swift ARC/Sendable/actor isolation.

Do not move these target details into the shared denominator or weaken shared
completion rules to accommodate one language.

## Composition

The target migration skill owns migration governance and explicitly routes
language mechanics to skills in its own package. For Rust, compose with
`rust-stable`, `rust-workspace`, `rust-api-design`, `rust-testing`, and applicable
domain skills. For Zig, the corresponding adapter composes with `zig-0.16`,
`zig-build-system`, `zig-project-structure`, and `zig-testing`.

When a shared rule changes, audit all existing target pairs. When a compiler,
layout, test runner, or language obligation changes, update only that target
adapter.

For Rust, the target adapter must derive Cargo packages from Rust boundaries
before selecting root-flat, hybrid/domain-grouped, or contained member paths.
Java module count is never a sufficient layout rule.
