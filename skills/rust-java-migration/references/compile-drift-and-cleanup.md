# Compile Drift and Migration Cleanup

Practical constraints, detection commands, and corrections for keeping a
migrated workspace compiling at its pinned toolchain with zero warnings.
These rules are distilled from repairing multi-crate Java→Rust migration
workspaces whose dependency graphs and API surfaces had drifted after the
original port.

## 1. Dependency and version drift

**Constraint.** A migration's dependency graph drifts: a dependency major or
minor release can remove a feature, gate an API behind a feature, drop a trait
implementation, rename an enum variant, or add a required struct field. The
pinned `Cargo.lock` in the original port is the baseline, not the truth.

**Detection and correction.**

| Failure | Typical error | Correction (verified cases) |
|---|---|---|
| Feature removed across versions | `package X depends on crate Y with feature F but Y does not have that feature. help: available features: ...` | Drop the stale feature or adopt the new default parser/behavior. `lopdf 0.44` removed `nom_parser` (the built-in parser is on by default). |
| API gated behind a feature | `no method named Q found for struct RequestBuilder in the current scope` | Enable the feature on the dependency, e.g. `reqwest = { features = [..., "query"] }` (`reqwest 0.13` gates `RequestBuilder::query`). |
| Trait impl removed | `the trait bound StandardUniform: Distribution<usize> is not satisfied` | Use a still-supported type and cast: `rand::random::<u64>() as usize` (`rand 0.9` dropped `usize`/`isize` sampling). |
| Enum variant renamed / struct field added | `E0599: no variant named X found for enum Op`; `E0063: missing field Y in initializer` | Read the resolved crate source under `~/.cargo/registry/src/*/<crate>-<version>/` and migrate to the current API: printpdf 0.12 renamed `SetFontSize`→`SetFont`, `WriteText`→`ShowText`, and added `XObjectTransform.no_auto_scale`. |
| Deprecated dependency API | `use of deprecated method TempDir::into_path: use TempDir::keep()` | Replace per the compiler message (`dir.keep()`). |

The compiler's `help:` text and the local registry source are authoritative;
never guess a variant or feature name.

## 2. MSRV / toolchain

**Constraint.** A workspace `rust-version` gates every build; cargo refuses an
older rustc.

**Detection.** `rustc --version`; `rustup toolchain list`.

**Error.** `error: rustc 1.93.1 is not supported by the following packages: ... requires rustc 1.94`.

**Correction.** Run with the pinned toolchain: `rustup run <ver> cargo check ...`
(or `cargo +<ver>` when the cargo shim supports it). Never silently lower the
manifest `rust-version` to match an old local rustc — the code may genuinely
require the newer language/edition features. If the manifest is wrong, change it
deliberately and record the decision.

## 3. Crate-root re-export chain breaks (E0432 flood)

**Symptom.** Many crates fail `E0432: unresolved import hutool_core::X`, while
the submodule defining `X` compiles and its own `pub use x::X;` is flagged
`unused import` — the inner re-export is unused because nothing at the crate
root consumes it.

**Diagnosis.** The crate's `lib.rs` never re-exports `X` at the crate root, or
never declares the module at all. A name moved during restructuring without
updating the root.

**Check.** From `cargo check --all-targets --workspace --keep-going`:
1. Collect every unresolved name from the `E0432` lines (parse all
   backtick-delimited names, not just the first).
2. Locate each definition: `pub struct|enum|type|trait X` across the crate.
3. Verify the module path is reachable and public (`pub mod` chain).
4. Add the root `pub use` (or `pub mod` when the consumer imports a module).

**Correction workflow.** Append the re-exports, compile the crate, and iterate
on path errors — the compiler is the ground truth for wrong paths. Verified
example: hutool-core restored ~72 root re-exports (`DateField`, `Week`, `BiMap`,
`FileReader`, `NetUtil`, `ZipUtil`, `convert`, `custom_key_map`, …) which
unblocked every downstream crate at once.

**Latent-bug trap.** A module declared in `lib.rs` but never wired in (no
`mod map;`) hides all its internal errors. The first time it is declared and
compiled, latent bugs surface in a layer — bad `super::` paths inside nested
directories (use `crate::mod::` instead), private fields accessed cross-module
(make them `pub(crate)`), etc. Fix that layer, re-run, and the next hidden layer
appears.

**Private module trap.** `mod x;` (private) blocks `crate::x::` imports from
tests and other crates → `pub mod x;` when consumers use the submodule path
(example: `hutool_core::date::`).

**Missing alias type.** Tests reference a Java name that never existed in Rust
(`BetweenFormatterLevel`) → add a mirror alias:
`pub use date::between_formatter::Level as BetweenFormatterLevel;`.

## 4. Duplicate types across crates (E0308 "similar names, distinct types")

**Symptom.** A type name exists in two crates (e.g. `AnnotationMirror` in both
`hutool-annotation` and `hutool-macro`). Dozens of `E0308` errors mix the two:
`expected AnnotationMirror, found a different AnnotationMirror`.

**Diagnosis.** A migration split created a parallel duplicate module instead of
re-exporting the canonical type.

**Correction.** Pick the crate that owns the machinery, and replace the
duplicate module's definitions with a re-export:
`pub use hutool_macro::mirror::*;`. The flood collapses to zero in one step.
Verify the canonical types carry every method the tests use before replacing.

## 5. Java-mirror naming and scaffolding norms

Java-mirror constructs are intentional inventory, not warnings to "fix" by
renaming or deleting:

- **SCREAMING_SNAKE enum variants** mirror Java constants (`ORACLE_12C`,
  `SQL_REWRITE`, `PARAMETER_ENCRYPTION`) → `#[allow(non_camel_case_types)]` on
  the enum. Never rename; the Java name is part of the mapping contract.
- **Java-mirror types/impls never constructed or used** (`Assert`, `MetroHash`,
  `DateBasic::sentinel`, cache/date utility stubs) →
  `#[allow(dead_code)]` with a short Chinese comment noting the mirror intent.
  Deleting them loses the Java object inventory.
- **Facade re-exports** (`pub use module::*;`) flagged unused →
  `#[allow(unused_imports)]` — they intentionally expose public API.
- **Type aliases mirroring Java names** (`pub type XxxEnum = crate::Xxx;`) →
  `#[allow(dead_code)]`.

## 6. private_interfaces / private_bounds

A type more private than the item that mentions it
(`type X is more private than the item Y`) → widen the type to `pub(crate)` or
`pub` to match the item, or add `#[allow(private_interfaces)]` /
`#[allow(private_bounds)]` when widening is not desired. Prefer matching
visibility; keep the item's signature unchanged.

## 7. Duplicated test blocks (E0428)

Scaffold/merge artifacts duplicate `#[test] fn name` definitions
(`the name name is defined multiple times`). Remove the later duplicate block
and keep the canonical one; confirm the canonical test exists before deleting.

## 8. Dead catch-all arms

`_ => default` in an exhaustive match that is flagged `unreachable pattern` →
remove the arm. The compiler then forces every future enum variant to be mapped
explicitly instead of silently falling into a default ("other").

## 9. Feature-gated tests and `check-cfg`

- Tests referencing a feature-gated module without enabling it →
  `E0432`/`E0433`; gate the test with `#[cfg(feature = "x")]` (example:
  FreeMarker tests behind the `freemarker` feature).
- `#[cfg(feature = "axum")]` with no declared feature → `unexpected cfg`
  warning; declare the feature on the facade
  (`axum = ["dep/axum"]`) or remove the cfg.
- A method only compiled under a feature (`TokioConsoleParts` undefined under
  `--all-features`) may leave the crate broken only in that configuration —
  always run the `--all-features` gate.

## 10. Compile-drift check workflow

```bash
# default features, all targets, continue past failures
cargo check --all-targets --workspace --keep-going
# pinned toolchain when the workspace MSRV exceeds the default rustc
rustup run <ver> cargo check --all-targets --workspace --keep-going
# every gate must also pass with all features
cargo check --all-targets --workspace --all-features --keep-going
# after cleanup, prove no behavior change
cargo test --workspace
```

Operational facts learned in the field:

- **Errors surface in layers.** `--keep-going` stops scheduling new work after
  failures, so fix the first error layer, re-run, and the next latent layer
  appears. Do not attempt to fix "all errors" from one output.
- **Attribute warnings to their owner.** Warnings from path dependencies are
  printed while checking a dependent crate; read the `-->` path before editing
  anything, and never edit a dependency while cleaning a dependent crate.
- **Deduplicate before estimating.** Warning counts include duplicates across
  lib/test targets; group `-->` lines by file to see real scope.
- **Feature-gated crates only appear under `--all-features`**; run both sets.
- **Mechanical cleanup (doc comments, `#[allow]`, import removal, `let _ =`)**
  must be followed by the test suite to prove no behavioral change. A
  pre-existing test failure that reproduces on the untouched baseline is not
  caused by cleanup — verify by running the pristine baseline before
  attributing it.

## 11. Non-code constraints

Missing build tools (e.g. `protoc` for `etcd-client`) fail the dependency's
build script, not your code; record the environment requirement instead of
editing code. External dependency future-incompat warnings (`zookeeper v0.8.0`)
are outside the migration's control.
