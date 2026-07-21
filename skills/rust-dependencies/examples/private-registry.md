# Private Registry and Source Replacement

Recipes for private registries, mirrors, and offline/vendored builds.

## Scenario A: Private registry for proprietary crates

You have internal crates that aren't on crates.io. Use a private registry.

### 1. Set up a registry server

Options:
- [Cloudsmith](https://cloudsmith.com/) — managed, has Rust support
- [AWS CodeArtifact](https://aws.amazon.com/codeartifact/) — AWS-native
- [jektitor](https://github.com/jeltitor/jektitor) — self-hosted
- [ktra](https://github.com/moriturus/ktra) — self-hosted, simpler
- [Casper](https://github.com/ducharmemp/casper) — sparse protocol

### 2. Configure credentials

```toml
# ~/.cargo/credentials.toml (or credentials)
[registry]
my-registry = { token = "your-token-here" }
```

Or via env var:

```bash
export CARGO_REGISTRIES_MY_REGISTRY_TOKEN=your-token-here
```

### 3. Register the registry index

```toml
# .cargo/config.toml
[registries.my-registry]
index = "sparse+https://my-registry.example.com/index/"
# Or git protocol:
# index = "https://my-registry.example.com/git/index/"
```

The `sparse+` prefix enables the faster sparse protocol (recommended for new setups).

### 4. Use the registry

```toml
# Cargo.toml
[dependencies]
my-private-crate = { version = "1.0", registry = "my-registry" }
```

### 5. Publish to the private registry

```bash
cargo publish --registry my-registry
```

## Scenario B: Mirror crates.io (China / corporate proxy)

You want all crates.io traffic to go through a mirror. Use **source replacement** (transparent — Cargo.toml stays unchanged).

### Using rsproxy.cn (China mirror)

```toml
# .cargo/config.toml
[source.rsproxy]
registry = "sparse+https://rsproxy.cn/index/"

[source.crates-io]
replace-with = "rsproxy"

[source.rsproxy-sparse]
registry = "sparse+https://rsproxy.cn/index/"

[registries.rsproxy]
index = "https://rsproxy.cn/crates.io-index"
```

### Using TUNA mirror

```toml
[source.tuna]
registry = "sparse+https://mirrors.tuna.tsinghua.edu.cn/crates.io-index/"

[source.crates-io]
replace-with = "tuna"
```

### Using a corporate proxy

```toml
[source.corporate]
registry = "sparse+https://mirrors.corp.example.com/crates.io-index/"

[source.crates-io]
replace-with = "corporate"
```

## Scenario C: Vendored (air-gapped / reproducible)

You need to build without network access. Vendor all deps.

### 1. Vendor

```bash
# In a workspace with network access:
cargo vendor vendor/ > .cargo/config.toml
# This writes all deps to vendor/ AND appends the config to redirect crates.io
```

### 2. The generated config

```toml
# .cargo/config.toml
[source.crates-io]
replace-with = "vendored-sources"

[source.vendored-sources]
directory = "vendor"
```

### 3. Commit vendor/ to git

```bash
git add vendor/ .cargo/config.toml
git commit -m "vendor dependencies for air-gapped builds"
```

The `vendor/` directory is large (100s of MB for big projects) but stable across CI runs.

### 4. Build offline

```bash
cargo build --offline       # or --frozen
```

## Scenario D: Git fork as dependency

You need a patched version of a crate that's not yet published.

### Option A: Git source

```toml
[dependencies]
serde = { git = "https://github.com/your-fork/serde", branch = "patch-branch" }
```

Caveats:
- Cannot publish to crates.io (must publish the patched version first)
- CI requires git access to that URL
- `Cargo.lock` records the commit hash

### Option B: Publish a fork under a new name

```toml
[dependencies]
serde-fork = { version = "1.0", package = "serde" }   # not real syntax
```

Actually rename via:

```toml
[dependencies]
my-serde-patch = { version = "1.0", package = "serde-patched" }
```

### Option C: Source replacement for a single crate

```toml
# .cargo/config.toml
[source.my-patched-serde]
git = "https://github.com/your-fork/serde"

[source.crates-io]
replace-with = "my-patched-serde"
```

Affects ALL crates in the workspace — use with caution.

## Scenario E: Multiple registries side by side

```toml
# .cargo/config.toml
[registries.corporate]
index = "sparse+https://crates.corp.example.com/index/"

[registries.experimental]
index = "sparse+https://crates.exp.example.com/index/"
```

```toml
# Cargo.toml
[dependencies]
internal-lib = { version = "1.0", registry = "corporate" }
experimental-lib = { version = "0.1", registry = "experimental" }
```

Each dep declares its registry explicitly.

## Scenario F: Make a registry the default

If you want `cargo publish` and `cargo add` to default to your registry (not crates.io):

```toml
# .cargo/config.toml
[registry]
default = "my-registry"

[registries.my-registry]
index = "sparse+https://crates.example.com/index/"
```

## Common pitfalls

### `error: failed to authenticate`

Token missing or wrong. Verify:

```bash
echo $CARGO_REGISTRIES_MY_REGISTRY_TOKEN
cat ~/.cargo/credentials
```

### `error: registry index not found`

URL wrong. Test with `curl`:

```bash
curl -sI https://my-registry.example.com/index/config.json
```

Should return 200 with `content-type: text/plain` or `application/json`.

### Sparse vs git protocol

- `sparse+https://...` — modern, fast (recommended)
- `https://...` (without sparse) — git protocol, slower

Sparse is the default in modern Cargo (1.68+).

### Token rotation

```bash
# Update token
cargo login --registry my-registry <new-token>

# Or delete and re-add
rm ~/.cargo/credentials.toml
cargo login --registry my-registry <token>
```

## Security notes

- Never commit `~/.cargo/credentials` to git
- For CI: use secrets injected as env vars (`CARGO_REGISTRIES_X_TOKEN`)
- Rotate tokens quarterly
- Audit who has publish access (registry server admin UI)

## Source

- [Cargo — Source Replacement](https://doc.rust-lang.org/cargo/reference/source-replacement.html)
- [Cargo — Registries](https://doc.rust-lang.org/cargo/reference/registries.html)
- [Cargo — Registry Authentication](https://doc.rust-lang.org/cargo/reference/registry-authentication.html)
- [Cargo — Vendor](https://doc.rust-lang.org/cargo/commands/cargo-vendor.html)
