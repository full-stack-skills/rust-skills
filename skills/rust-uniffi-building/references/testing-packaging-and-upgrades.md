# Testing, Packaging, and Upgrades

Read this reference before defining CI, publishing artifacts, claiming language support, or changing UniFFI versions.

## Evidence Levels

Keep these claims separate:

| Evidence | Proves | Does not prove |
|---|---|---|
| Rust unit tests | internal behavior and boundary conversion helpers | generated host API or library loading |
| Rust compile/Clippy | selected Rust configuration compiles cleanly | foreign compilation or runtime |
| Binding generation | metadata/config can produce source files | generated source compiles or loads |
| Host-language compile | generated API matches host compiler/tooling | runtime loading and behavior |
| Host-language runtime test | calls work in that executed environment | packaging/install on all targets |
| Minimal consumer install | distributed package can be installed and loaded | untested platforms or production load |

Never report "UniFFI integration complete" based only on Rust tests or generated files.

## Rust-Side Tests

Test domain behavior without foreign runtimes, then add boundary-focused cases:

- every record/enum/error variant;
- empty, Unicode, maximum, and invalid values;
- custom type lift/lower round trips;
- object construction, mutation, close, and concurrent calls;
- callback registration and reentrancy logic;
- async success, failure, cancellation, and shutdown.

Keep internal business logic independent of UniFFI macros where practical so it remains easy to test and reuse.

## Generation Tests

From a clean checkout:

1. Build the exact target/profile library.
2. Generate bindings with pinned tooling and configuration.
3. Verify expected files exist.
4. Compile or type-check every generated language.
5. If generated files are committed, fail on unexplained diffs.
6. Record generator, library, config, UDL, feature, and target hashes.

Do not treat snapshots as the only correctness test; generated output can remain stable while runtime metadata is wrong.

## Host Runtime Tests

Create small consumer tests per language:

- import/load the package;
- call a simple function;
- transfer records, enums, strings, bytes, collections, and optionals;
- observe each exported error;
- create, share, call, close, and release objects;
- invoke callbacks in both directions;
- complete and cancel async calls;
- run from outside the repository checkout.

Use real platform runners for loader, signing, device ABI, simulator/device, and dynamic-library behavior.

## Packaging

Define a release manifest:

```text
Rust source commit:
Cargo.lock hash:
UniFFI runtime version/features:
Bindgen frontend/version:
Target triples:
Native artifact hashes:
Generated source hashes:
Host package versions:
Executed consumer tests:
Unsupported/unverified targets:
```

Packaging checks:

- native library and generated code are version-aligned;
- all claimed architectures are present;
- headers/module maps/package resources use relocatable paths;
- debug and release artifacts are not mixed;
- dead stripping/LTO retains required symbols;
- dynamic libraries are embedded/signed or discoverable as required;
- wheel, gem, AAR, Swift package, XCFramework, or equivalent metadata is correct;
- license notices cover UniFFI and bundled dependencies.

## CI Matrix

Separate fast and platform gates:

```text
PR:
  Rust fmt/check/test/Clippy
  deterministic generation
  generated-language compile

Platform:
  Android/JVM runtime tests
  Apple simulator/device or macOS runtime tests
  Python wheel install tests
  Ruby package tests
  WASM browser/Node tests when supported

Release:
  locked clean build
  package assembly
  minimal consumer installation
  signing/notarization where required
  artifact hashes and provenance
```

Do not silently skip platform jobs. Record `not run`, `blocked`, or `unsupported`.

## Upgrades

Before updating UniFFI:

1. Read the project changelog and every migration guide between locked versions.
2. Record whether runtime/backend/frontend crate versions remain synchronized.
3. Diff Cargo features and generator CLI help.
4. Regenerate every language into a clean directory.
5. Review public naming, nullability, error, trait, callback, and async changes.
6. Rebuild every native target.
7. Run all minimal consumer tests.
8. Compare artifact size, exported symbols, and package contents.
9. Define rollback to the previous generated/native artifact pair.

Never upgrade only the Rust runtime crate while leaving an incompatible generator or checked-in bindings unchanged.

The official guide currently includes a [v0.28 to v0.29 migration page](https://mozilla.github.io/uniffi-rs/latest/Upgrading.html); later upgrades may require changelog and release-note inspection beyond that page.

## Failure and Rollback

Release generated bindings and native artifacts as an atomic version. If a platform fails:

- identify whether the defect is Rust logic, metadata/generation, host integration, packaging, or loader/runtime;
- preserve the previous compatible artifact pair;
- do not regenerate one side opportunistically during rollback;
- document consumer cache invalidation and package-version policy;
- reproduce the failure in a minimal consumer before declaring recovery.

## Completion Checklist

- Rust, generation, host compile, host runtime, and install evidence are separate.
- Every claimed language has an executed minimal consumer.
- Package contents and architectures are inspected.
- Release artifacts are version-aligned and reproducible.
- Upgrade notes and CLI/features are reviewed.
- Rollback restores a compatible generated/native pair.
