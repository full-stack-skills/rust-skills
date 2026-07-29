# Rust UniFFI Execution Scenarios

## Build a shared Rust core for Android and iOS

User request:

> Expose this Rust library to Kotlin on Android and Swift on iOS. Use UniFFI and package artifacts for both applications.

Pin UniFFI and host tool versions, select procedural macros or UDL, define the supported type/ownership/error contract, and build the target native artifacts. Generate Kotlin and Swift bindings from the shipping libraries, integrate Gradle and Xcode/XCFramework packaging, then run minimal Android and Apple consumer tests. Do not claim completion after `cargo build`.

## Migrate a UDL project toward procedural macros

User request:

> This UniFFI crate duplicates every API in Rust and UDL. Move what is supported to procedural macros without breaking existing Swift and Python callers.

Inventory UDL and generated public APIs, pin a baseline, and migrate in compatibility-preserving stages. Keep UDL valid during mixed mode, make crate name match the namespace, avoid duplicate scaffolding, regenerate both languages, diff generated APIs, and run old/new consumer contract tests before removing UDL items.

## Diagnose release-only Swift loading failures

User request:

> Debug Swift works, but the archived iOS app cannot load the UniFFI library.

Compare debug/release features, target slices, static/dynamic linkage, module map/header paths, dead stripping/LTO, embedding, signing, and package contents. Inspect the archive and run a release-mode minimal consumer. Do not rewrite generated Swift until the artifact and loader contract has been proven.

## Add a cancellable async API

User request:

> Export this async Rust operation to Kotlin coroutines and Swift async/await, including cancellation.

Verify the locked UniFFI async/runtime features, define cancellation and child-task ownership, avoid detached unsupervised work, preserve exported errors, and test completion/cancellation at multiple timing points in both host languages.

## Near miss: hand-written C ABI

User request:

> Design an extern C API returning an allocated byte buffer to a C++ caller.

Use `rust-unsafe-ffi`, not this skill, unless the user explicitly chooses UniFFI. The task requires manual layout, ownership, allocator, and unwinding contracts.
