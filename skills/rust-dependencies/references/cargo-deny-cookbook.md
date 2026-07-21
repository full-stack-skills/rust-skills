# cargo-deny Configuration Cookbook

Practical recipes for `deny.toml` covering all four checks. See [`cargo-deny` docs](https://embarkstudios.github.io/cargo-deny/) for the full reference.

## Install and run

```bash
cargo install cargo-deny --locked
cargo deny init          # creates deny.toml with sensible defaults
cargo deny check         # runs all four checks
cargo deny check advisories licenses bans sources   # explicit
```

## 1. Advisories — RustSec scan

### Minimal

```toml
[advisories]
db-urls = ["https://github.com/rustsec/advisory-db"]
yanked = "deny"          # error on yanked versions
```

### Ignore specific advisories (with comment)

```toml
[advisories]
db-urls = ["https://github.com/rustsec/advisory-db"]

# Reason: the affected API isn't used; tracked for fix in v2.0
ignore = [
    "RUSTSEC-2024-0001",
    "RUSTSEC-2023-0071",
]

# Trigger CI failure on new advisories
unmaintained = "workspace"   # warn on unmaintained crates in workspace only
```

### CI integration

```yaml
# .github/workflows/deny.yml
name: cargo-deny
on: [push, pull_request]
jobs:
  deny:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: EmbarkStudios/cargo-deny-action@v2
```

## 2. Licenses — policy enforcement

### Permissive default

```toml
[licenses]
allow = [
    "MIT",
    "Apache-2.0",
    "Apache-2.0 WITH LLVM-exception",
    "BSD-2-Clause",
    "BSD-3-Clause",
    "ISC",
    "Unicode-DFS-2016",
    "Unicode-3.0",
    "Zlib",
    "CC0-1.0",
    "Unlicense",
]
confidence-threshold = 0.93
```

### Copyleft policy (strict)

```toml
[licenses]
allow = [
    "MIT",
    "Apache-2.0",
    "BSD-3-Clause",
]
deny = [
    "GPL-2.0",
    "GPL-3.0",
    "AGPL-3.0",
    "LGPL-2.0",
    "LGPL-3.0",
    "SSPL-1.0",
    "EUPL-1.2",
]
```

### Exceptions

```toml
[[licenses.exceptions]]
allow = ["OpenSSL"]
name = "openssl-sys"
version = "*"

[[licenses.clarify]]
name = "ring"
version = "*"
expression = "MIT AND ISC AND OpenSSL"
license-files = [
    { path = "LICENSE", hash = 0xbd0eed23 }
]
```

## 3. Bans — forbidden crates

### Forbid `openssl` (prefer rustls)

```toml
[bans]
multiple-versions = "warn"
wildcards = "deny"          # no "2.*" requirements

[[bans.deny]]
name = "openssl"
version = "*"

[[bans.deny]]
name = "openssl-sys"
version = "*"

[[bans.deny]]
name = "openssl-probe"
version = "*"
```

### Forbid old versions

```toml
[[bans.deny]]
name = "chrono"
version = "<0.4.20"          # CVE-2020-26235 territory

[[bans.deny]]
name = "time"
version = "<0.2.23"
```

### Required workspace dependencies

```toml
[bans]
workspace-dependencies = "deny"   # all external deps must go via [workspace.dependencies]
```

### Skip tree on specific crates

```toml
[[bans.skip-tree]]
name = "windows-sys"
version = "*"
```

## 4. Sources — registry policy

### Allow only crates.io

```toml
[sources]
unknown-registry = "deny"
unknown-git = "deny"
allow-registry = ["crates-io"]
allow-git = []
```

### Allow crates.io + private registry

```toml
[sources]
unknown-registry = "deny"
unknown-git = "deny"

allow-registry = [
    "crates-io",
    "my-registry",       # name must match [registries.my-registry] in .cargo/config.toml
]
```

### Allow specific git sources

```toml
[sources]
unknown-git = "deny"
allow-git = [
    "https://github.com/your-org/forked-crate",
]
```

## Full strict example

```toml
# deny.toml — strict policy for a security-conscious org

[graph]
all-features = true        # check the entire feature matrix

[advisories]
version = 2
db-urls = ["https://github.com/rustsec/advisory-db"]
yanked = "deny"
unmaintained = "deny"
ignore = []

[licenses]
confidence-threshold = 0.93
allow = [
    "MIT",
    "Apache-2.0",
    "BSD-3-Clause",
    "ISC",
    "Unicode-3.0",
    "Zlib",
]

[bans]
multiple-versions = "deny"
wildcards = "deny"
highlight = "all"
workspace-dependencies = "deny"
deny = [
    { name = "openssl", version = "*" },
    { name = "openssl-sys", version = "*" },
]

[sources]
unknown-registry = "deny"
unknown-git = "deny"
allow-registry = ["crates-io"]
allow-git = []
```

## Output interpretation

```bash
cargo deny check licenses
```

```
error: failed to scan licenses
  → license = "GPL-3.0" detected
    in package "gpl-crate v1.0.0"
    which is a dependency of "my-crate v0.1.0"
```

For each error:
- Add the package to `[[licenses.exceptions]]` (with reason)
- Or `[[bans.deny]]` the crate entirely
- Or remove the dependency

## Tips

- Run `cargo deny init` to get a starting `deny.toml`
- Run `cargo deny list` to see all licenses in the tree
- Run `cargo deny check --verbose` for detailed output
- For monorepos, put `deny.toml` at workspace root
- Pin `cargo-deny` version in CI (`cargo install cargo-deny --locked --version 0.16.x`)

## Source

- [cargo-deny Book](https://embarkstudios.github.io/cargo-deny/)
- [deny.toml reference](https://embarkstudios.github.io/cargo-deny/check/index.html)
