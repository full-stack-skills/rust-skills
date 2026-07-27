# Cargo Metadata and Automation

Use Cargo's documented machine-readable interfaces instead of scraping human output or the internal `target` layout. Read [cargo metadata](https://doc.rust-lang.org/cargo/commands/cargo-metadata.html), [Package ID Specifications](https://doc.rust-lang.org/cargo/reference/pkgid-spec.html), and [External Tools](https://doc.rust-lang.org/cargo/reference/external-tools.html).

## Workspace and dependency metadata

```bash
cargo metadata --format-version 1
cargo metadata --format-version 1 --no-deps
cargo metadata --format-version 1 --filter-platform <triple>
```

- Use `--no-deps` for workspace structure without transitive package data.
- Use full metadata when dependency nodes and edges are required.
- Add `--locked`, `--offline`, or `--frozen` according to lockfile and network policy.
- Treat unknown JSON fields as forward-compatible additions.
- Do not assume array ordering when the schema does not make it a contract.
- Compare opaque package IDs for identity; do not reconstruct their serialized form.

Use a JSON parser or a library such as `cargo_metadata`; do not parse formatted terminal output.

## Compiler artifact messages

For build automation, use Cargo's JSON message format rather than guessing artifact paths:

```bash
cargo build --message-format=json-render-diagnostics
```

Parse one JSON object per line and handle documented message reasons. Keep human diagnostics visible or rendered appropriately; do not discard build failures after extracting artifact paths.

## Package ID specifications

Commands such as `cargo update`, `cargo tree --invert`, and `cargo pkgid` accept package ID specifications. Start with the shortest unambiguous package name, then add version or source qualification only when Cargo reports ambiguity.

```bash
cargo pkgid serde
cargo update -p serde@1.0.219
```

Do not hand-edit `Cargo.lock` package IDs.

## External subcommands

An executable named `cargo-foo` can be invoked as `cargo foo`. Before adopting or building an external subcommand:

- check whether stable Cargo already provides the capability;
- pin installation and version policy in CI;
- inspect its mutation, network, credential, and execution behavior;
- avoid assuming third-party flags follow Cargo's built-in conventions;
- prefer structured output when the tool provides it.

## Automation contract

1. Pin or record Cargo version.
2. Resolve the workspace root explicitly.
3. Select the manifest, packages, features, targets, target triple, and profile.
4. Select lockfile/network policy.
5. Parse only documented JSON interfaces.
6. fail on non-zero exit status even if partial JSON was produced.
7. Avoid leaking manifest metadata, source URLs, environment values, or registry credentials into logs.
