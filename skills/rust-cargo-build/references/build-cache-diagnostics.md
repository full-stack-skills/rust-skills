# Cargo Build Cache and Diagnostics

Use evidence from Cargo's output layout, dependency graph, timings, and reports before deleting caches or changing profiles. Read [Build Cache](https://doc.rust-lang.org/cargo/reference/build-cache.html), [Build Timings](https://doc.rust-lang.org/cargo/reference/timings.html), and [Future Incompat Report](https://doc.rust-lang.org/cargo/reference/future-incompat-report.html).

## Distinguish storage locations

- `target-dir` contains final artifacts and, by default, intermediate build state.
- `build-dir` can place intermediate build artifacts separately when supported by the installed Cargo.
- `$CARGO_HOME` contains installed binaries plus registry and Git caches; it is not the workspace build directory.
- The internal build-directory layout is not a stable API unless the Cargo Reference explicitly documents a path.

Current Cargo can automatically garbage-collect parts of its global downloaded-source cache according to `[cache]` configuration. Workspace build artifacts are not generally cleaned by that mechanism; manage them through measured target-directory policy and `cargo clean`.

With `--target <triple>`, target artifacts live under `target/<triple>/<profile>`. Host build scripts and procedural macros remain host artifacts.

## Diagnose slow or repeated builds

```bash
cargo build --timings
cargo tree --duplicates
cargo tree -e features
cargo build -vv
```

`cargo build --timings` writes an HTML report under `target/cargo-timings/`. Use it to identify the critical path, slow build scripts, code generation time, parallelism gaps, and dependencies compiled more than once.

Interpret duplicate builds carefully:

- different package versions may be intentional;
- the same package may compile separately for host and target;
- different feature sets or profiles may create separate compilation units;
- build, dev, and normal dependency edges have different roles.

Check the graph before forcing versions or enabling more feature unification.

## Future incompatibilities

When Cargo reports code that may be rejected by a future compiler:

```bash
cargo report future-incompatibilities --id <report-id>
```

Update the affected dependency, patch it with a tracked upstream fix, or document a time-bounded exception. Do not suppress the notice without an owner and remediation condition.

## Safe cleanup

Use `cargo clean` with the narrowest supported package/profile/target selection after resolving the actual target directory. Treat it as destructive because project configuration can redirect the directory.

Do not recursively delete `$CARGO_HOME`: it may contain credentials and installed tools. If registry or Git cache corruption is proven, remove only the resolved cache entry or use an explicitly installed cache-management tool after reviewing its behavior.

Before cleanup, capture:

```bash
cargo --version
cargo locate-project --workspace
cargo metadata --no-deps --format-version 1
```

## Optimization sequence

1. Reproduce the slow or stale build with the actual command.
2. Record timings and verbose output.
3. Identify whether the bottleneck is resolution, compilation, build scripts, code generation, linking, or tests.
4. Reduce unnecessary dependencies, features, targets, or duplicate versions.
5. Adjust profiles, linker, codegen units, LTO, or debug information only after measurement.
6. Repeat the same workload and compare time, memory, disk, artifact size, and runtime trade-offs.
