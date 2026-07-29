---
name: rust-uniffi-building
description: Build, generate, test, package, and troubleshoot shared Rust components and cross-platform bindings with Mozilla UniFFI. Use automatically when users want to write business logic once in Rust and call or reuse it from Swift, iOS, macOS, Kotlin, Android, JVM, Python, Ruby, JavaScript, browsers, desktop apps, or multiple platforms—even when they do not mention UniFFI; when they ask to bridge, expose, connect, or share Rust with Swift/Kotlin/Android/iOS; or when they need procedural-macro versus UDL selection, records, enums, errors, objects, traits, callbacks, custom types, uniffi.toml, uniffi-bindgen, async exports, generated-binding diagnostics, native-library loading, packaging, ABI, or upgrades. Verify that the locked UniFFI release supports each requested target; route hand-written C ABI work to rust-unsafe-ffi.
---

# Rust UniFFI Building

Build a narrow, versioned foreign-language API around a shared Rust library. Recognize requests such as “write the core once in Rust for Swift and Android,” “call Rust from Kotlin and iOS,” or “reuse Rust business logic across mobile and browser clients” as UniFFI evaluation/building tasks even if the user does not name UniFFI. Treat generated bindings, the compiled native library, and host-language packaging as one contract: a successful Rust build alone does not prove that Kotlin, Swift, Python, Ruby, JavaScript, or WASM consumers work.

## Scope and Routing

Use this skill for Mozilla UniFFI interface design, scaffolding, binding generation, language integration, lifecycle behavior, and end-to-end validation.

Route these adjacent tasks deliberately:

- Hand-written `extern "C"`, raw pointers, allocator ownership, or manual headers → `rust-unsafe-ffi`.
- General procedural-macro implementation or diagnostics → `rust-macros`.
- Workspace manifests, build scripts, features, cross-compilation, and artifact profiles → `rust-cargo-build`.
- Rust task supervision and runtime architecture beyond exported async calls → `rust-concurrency`.
- General test strategy, coverage, or fuzz infrastructure → `rust-testing`.

## Workflow

### 1. Pin the actual contract

Before editing, record:

- `rustc --version --verbose`, target triples, MSRV, and host platforms;
- locked `uniffi`, backend, and language-tooling versions plus enabled features;
- intended languages and minimum Kotlin/JVM, Android, Swift, Xcode, Python, Ruby, or WASM versions;
- library artifact type, package name, namespace/module name, and loading path;
- exported functions, objects, records, enums, errors, traits, callbacks, async calls, and custom types;
- threading, cancellation, ownership, destruction, and backward-compatibility expectations;
- generation owner: Cargo build, a checked-in tool, Gradle/Xcode task, CI job, or release pipeline.

Inspect `Cargo.lock` and the current official UniFFI guide. Do not copy syntax from a different UniFFI release line. The repository's golden example is evidence for its locked version, not a timeless dependency recommendation.

### 2. Choose one interface-definition strategy

| Strategy | Prefer when | Required discipline |
|---|---|---|
| Procedural macros | Rust is the API source of truth and supported constructs cover the contract | Use library mode and `uniffi::setup_scaffolding!()` exactly once |
| UDL | An explicit language-neutral schema is desired or existing UDL must remain authoritative | Generate in `build.rs` and include the generated scaffolding |
| Mixed UDL + macros | Migration or a real unsupported construct requires both | Keep UDL valid alone; make crate name match the UDL namespace |

Never call both `uniffi::setup_scaffolding!()` and `uniffi::include_scaffolding!()` in one crate. Do not mix strategies merely for convenience; it increases duplicate-definition and drift risk.

Read [Interface Model](references/interface-model.md) before designing public types or choosing UDL versus macros.

### 3. Establish scaffolding and artifact boundaries

For a procedural-macro-only crate, start with the smallest viable pattern:

```rust
uniffi::setup_scaffolding!();

#[derive(uniffi::Record)]
pub struct Greeting {
    pub message: String,
}

#[uniffi::export]
pub fn greet(name: String) -> Greeting {
    Greeting {
        message: format!("Hello, {name}!"),
    }
}
```

Build an ordinary Rust library for Rust callers and the platform artifacts required by hosts:

```toml
[lib]
crate-type = ["lib", "cdylib", "staticlib"]
```

Do not enable every crate type or UniFFI feature automatically. Select artifacts from the host packaging contract, isolate bindgen/CLI dependencies when practical, and keep runtime-facing dependencies minimal.

For UDL build scripts, generated bindings, configuration precedence, and library-mode commands, read [Scaffolding and Generation](references/scaffolding-and-generation.md).

### 4. Design an FFI-shaped public API

- Export only UniFFI-supported types or explicit custom/external conversions.
- Prefer records for immutable value transfer and objects for identity or shared state.
- Return `Arc<Self>` from exported object constructors when required by the selected UniFFI version.
- Model expected failures as exported error enums; never encode routine failures as panics.
- Keep internal Rust types private and convert at the UniFFI boundary.
- Treat names, field presence, enum variants, defaults, and error variants as host-language compatibility commitments.
- Bound strings, byte buffers, collections, recursive structures, callback frequency, and response sizes.
- Avoid exposing a Rust-centric API that becomes awkward or unsafe in every target language.

Read [Async, Lifetimes, and Callbacks](references/async-lifetimes-and-callbacks.md) before exporting futures, callbacks, traits, or stateful objects.

### 5. Generate and integrate per language

Generate bindings from the exact library/configuration combination that will ship. Keep generated sources and native artifacts version-aligned.

Validate language-specific integration rather than stopping at generated files:

- Kotlin/Android: package/JNA or platform bridge, Gradle task inputs, ABI splits, coroutine behavior, and native library loading;
- Swift/Apple: Swift sources, headers/module maps, static or dynamic library linkage, module naming, Xcode build phases, and XCFramework packaging;
- Python: extension/library discovery, generated module import, supported Python versions, and wheel/platform tagging;
- Ruby: generated wrapper loading and the feature gaps documented for the selected release;
- WASM: unstable support constraints, single-thread assumptions, JavaScript tooling, and supported UniFFI features.

Read [Language Bindings](references/language-bindings.md) only for the requested target languages.

### 6. Verify at three boundaries

Run the Rust gates first:

```bash
cargo fmt --all --check
cargo check --workspace --all-targets --all-features
cargo test --workspace --all-targets --all-features
cargo clippy --workspace --all-targets --all-features -- -D warnings
```

Then verify:

1. **Generation boundary** — bindings regenerate deterministically from a clean checkout and fail clearly on metadata, namespace, configuration, or library mismatches.
2. **Host-language boundary** — compile and run real Kotlin, Swift, Python, Ruby, or WASM tests against the produced native artifact.
3. **Distribution boundary** — install the package into a minimal consumer project and exercise loading, calls, errors, callbacks, async cancellation, and cleanup on supported platforms.

Rust tests, generated-source snapshots, and host compilation are different evidence levels. Do not claim a platform works without executing it.

Read [Testing, Packaging, and Upgrades](references/testing-packaging-and-upgrades.md) before release, CI design, or version migration.

### 7. Diagnose from the correct layer

Classify failures before changing code:

| Symptom | Inspect first |
|---|---|
| Missing exported symbol or metadata | scaffolding macro/include mode, crate features, final library artifact |
| Duplicate symbols or definitions | mixed UDL/macros, duplicate scaffolding setup, multiple generated sources |
| Bindgen cannot find crate/config | `cargo-metadata`, global `[crate-roots]`, working directory, config precedence |
| Generated code compiles but library will not load | filename, architecture, ABI, search path, signing, package contents |
| Values corrupt or fail to decode | type model, custom converter, version skew, lowering/lifting contract |
| Object disappears, leaks, or races | reference counting, host lifetime, callback registration, thread policy |
| Async hangs or cancellation leaks work | runtime feature, foreign executor/poller, cancellation and completion contract |
| Only release builds fail | dead stripping, LTO, symbol retention, feature/profile differences |

Read [Internals and Diagnostics](references/internals-and-diagnostics.md) only when surface-level checks cannot explain the failure.

## Gotchas

- UniFFI generates bindings; it does not ship, sign, publish, or load the native library for every platform.
- Generated bindings and the Rust artifact must come from compatible UniFFI metadata and configuration.
- `latest` documentation can move. Pin crate versions and record the guide snapshot used for a release decision.
- A UDL file remains a complete schema even when macros add supported items.
- Put `#[cfg]` on separate exported impl blocks when needed; conditional items inside an exported block can still generate incompatible scaffolding.
- Host-language naming, exceptions, nullability, collections, and lifecycle semantics are not identical to Rust semantics.
- Miri cannot validate the real foreign runtime. Use it for Rust-side unsafe code, then run platform integration tests.

## When Not to Use

Do not activate this skill for:

- ordinary Rust library APIs with no foreign-language consumer;
- `wasm-bindgen`, CXX, PyO3, JNI, cbindgen, Diplomat, or raw C bindings unless the task explicitly adopts or compares UniFFI;
- writing a general derive or attribute macro unrelated to UniFFI;
- packaging an already-generated binding when no UniFFI contract, code, or artifact changes are involved.

## Completion Criteria

- Pin versions, targets, languages, generation owner, and artifact/package contract.
- Choose procedural macros, UDL, or a justified mixed strategy without duplicate scaffolding.
- Keep the exported type, error, ownership, callback, async, and compatibility model explicit.
- Generate bindings from the exact shipping library and configuration.
- Run Rust gates plus real host-language and minimal-consumer tests for every claimed platform.
- Verify packaging, architecture, loading, symbol retention, cancellation, and cleanup.
- Record unsupported platforms, unexecuted tests, and version-sensitive assumptions.

## Resources

- [Interface Model](references/interface-model.md)
- [Scaffolding and Generation](references/scaffolding-and-generation.md)
- [Language Bindings](references/language-bindings.md)
- [Async, Lifetimes, and Callbacks](references/async-lifetimes-and-callbacks.md)
- [Testing, Packaging, and Upgrades](references/testing-packaging-and-upgrades.md)
- [Internals and Diagnostics](references/internals-and-diagnostics.md)
- [Official Documentation Map](references/official-doc-map.md)
- [Execution Scenarios](examples/examples.md)
- `examples/golden-uniffi/`: a compiled procedural-macro library with records, enums, objects, tests, and a version-locked local bindgen CLI.

## Data Privacy

Do not upload proprietary UDL, generated bindings, native libraries, symbols, crash dumps, or host application logs to external services without authorization.
