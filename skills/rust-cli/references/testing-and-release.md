# CLI Testing and Release

## Test Layers

1. Perform pure function tests on the parsed command model.
2. Conduct domain-specific testing of the I/O execution layer with injected inputs.
3. Launch real binaries, asserting stdout, stderr, exit codes, and file side effects.
4. Run compatibility tests across supported platform matrices.

Real process testing may utilize `std::process::Command` from the standard library or select among existing repository dependencies such as `assert_cmd`, `trycmd`, or snapshot tools. Do not introduce multiple overlapping test libraries solely for a simple assertion.

## Process Testing Checklist

- Assert that output belongs to correct standard streams;
- Simultaneously assert both success and failure exit codes;
- Isolate the current directory, environment variables, configuration directories, and temporary files;
- Avoid reliance on global development machine configurations or accidental programs in PATH;
- For human-readable text content, assert only stable fragments; for machine-format data, assert complete structures;
- Set test timeouts for potentially hanging child processes;
- Confirm signal semantics when testing signals to avoid disguising cross-platform behavior.

## Release Checklist

- Ensure `--help`, examples, and shell completion match actual parameters exactly;
- Version information must originate from a single source;
- Release builds should not depend on development machine paths or undeclared resources;
- Artifacts must exclude secrets, test configurations, and debug data;
- Installation methods, binary names, and minimum Rust versions must be validated;
- All claimed supported targets must be built via CI or release pipelines;
- Packaging, signing, archiving, and package manager operations should be coordinated by `rust-cargo-build`.

## Main Resources

- [CLI Book: Testing](https://rust-cli.github.io/book/tutorial/testing.html)
- [CLI Book: Packaging](https://rust-cli.github.io/book/tutorial/packaging.html)
- [`std::process::Command`](https://doc.rust-lang.org/stable/std/process/struct.Command.html)
