# Language Binding Integration

Read only the sections for the requested target languages. Generation is not delivery: each language needs its own build, loading, packaging, and runtime test.

## Shared Integration Contract

For every language, pin:

- generated-source version and checksum;
- native library version, target triple, architecture, and build profile;
- module/package name and public namespace;
- configuration and UniFFI metadata version;
- minimum language runtime and build-tool versions;
- artifact location and loader/search-path rules;
- debug-symbol, stripping, signing, and release packaging policy.

Never mix generated code from one Rust library with a different native artifact. Test a clean consumer that does not inherit repository-local paths or environment variables.

## Kotlin and Android

Verify:

- Kotlin package naming from `uniffi.toml`;
- JVM/JNA or the selected backend dependencies required by the generated code;
- Gradle task inputs and outputs for Rust builds and binding generation;
- Android ABI splits such as `arm64-v8a`, `armeabi-v7a`, `x86`, and `x86_64` only where supported;
- placement under the correct `jniLibs` or packaging location;
- library load order and filename;
- coroutine cancellation and dispatch behavior for async exports;
- exception mapping and object cleanup on the JVM/Android runtime.

Keep Gradle tasks incremental and deterministic:

- declare UDL/Rust/config/toolchain inputs;
- declare generated sources and native libraries as outputs;
- avoid absolute developer paths;
- ensure release builds do not reuse debug artifacts;
- run instrumentation/device tests when loading depends on Android runtime behavior.

Test at least:

- one successful call with Unicode and empty values;
- each exported error variant;
- object construction, method calls, and release;
- callback from Rust into Kotlin;
- async completion and cancellation;
- every packaged ABI on an emulator/device or equivalent real loader.

Official sources:

- [Kotlin configuration](https://mozilla.github.io/uniffi-rs/latest/kotlin/configuration.html)
- [Integrating with Gradle](https://mozilla.github.io/uniffi-rs/latest/kotlin/gradle.html)
- [Kotlin lifetimes](https://mozilla.github.io/uniffi-rs/latest/kotlin/lifetimes.html)

## Swift and Apple Platforms

Verify:

- Swift module name, generated Swift source, C header, and module map;
- static versus dynamic linking choice;
- target architecture and deployment minimums;
- Xcode search paths, build phases, and generated-source ownership;
- module-map/header paths after packaging;
- simulator versus device slices;
- code signing and embedding for dynamic libraries/frameworks;
- async/throws mapping, actor/thread expectations, and object release.

For multi-platform distribution, build each required Rust target before assembling an XCFramework. Do not combine incompatible or duplicate architecture slices. Validate the final archive from a clean Swift package or Xcode app rather than only compiling generated Swift inside the source repository.

If using `uniffi-bindgen-swift`, pin it independently where UniFFI's release policy separates frontend/backend versions. Check the selected tool's help and release notes.

Test at least:

- Swift module import in a minimal application;
- simulator and device builds;
- error-to-`throws` behavior;
- records/enums with naming edge cases;
- async task cancellation;
- object lifetime across autorelease/ARC boundaries;
- release archive with the same optimization, LTO, and stripping settings as production.

Official sources:

- [Swift bindings](https://mozilla.github.io/uniffi-rs/latest/swift/overview.html)
- [uniffi-bindgen-swift](https://mozilla.github.io/uniffi-rs/latest/swift/uniffi-bindgen-swift.html)
- [Swift configuration](https://mozilla.github.io/uniffi-rs/latest/swift/configuration.html)
- [Compiling a Swift module](https://mozilla.github.io/uniffi-rs/latest/swift/module.html)
- [Integrating with Xcode](https://mozilla.github.io/uniffi-rs/latest/swift/xcode.html)

## Python

Verify:

- supported Python versions and generated module name;
- native library naming and discovery on Linux, macOS, and Windows;
- wheel platform/architecture tags;
- package-data inclusion for generated Python and the native library;
- loader behavior outside the source checkout;
- exception mapping and object finalization;
- async support expectations for the selected release.

Do not rely on `LD_LIBRARY_PATH`, `DYLD_LIBRARY_PATH`, or the current directory as the production loader policy. Install a built wheel into a fresh virtual environment and import it from another directory.

Test:

- wheel installation and import;
- success and exported errors;
- bytes, Unicode, optional values, records, and enums;
- repeated object creation/destruction;
- threads or async behavior claimed by the package;
- all published wheel targets.

Official source: [Python configuration](https://mozilla.github.io/uniffi-rs/latest/python/configuration.html).

## Ruby

Check the selected UniFFI release for feature gaps before claiming parity with Kotlin, Swift, or Python. Pin Ruby versions, generated wrapper dependencies, native loading, exception behavior, and object cleanup.

Test the installed gem or package from a clean environment. Explicitly document unsupported docstrings, async behavior, traits, or other gaps discovered in the locked release.

Official source: [Ruby configuration](https://mozilla.github.io/uniffi-rs/latest/ruby/configuration.html).

## WASM

Treat UniFFI WASM as an explicitly unstable target unless the locked release states otherwise. Verify:

- required UniFFI feature flags;
- single-threaded runtime assumptions;
- supported and unsupported interface types;
- JavaScript glue and bundler requirements;
- async behavior and event-loop integration;
- browser versus Node host;
- artifact size and initialization contract.

Do not present UniFFI WASM as interchangeable with `wasm-bindgen`, WASI, or the component model. Choose the host/runtime first and validate in that actual host.

Official source: [WASM configuration](https://mozilla.github.io/uniffi-rs/latest/wasm/configuration.html).

## Cross-Language Release Matrix

Track evidence explicitly:

| Language | Generator/tool version | Native target | Host build | Runtime test | Package install | Status |
|---|---|---|---|---|---|---|
| Kotlin/Android | | | | | | |
| Swift/Apple | | | | | | |
| Python | | | | | | |
| Ruby | | | | | | |
| WASM | | | | | | |

Use `not run`, `blocked`, or `unsupported` rather than treating an empty cell as success.
