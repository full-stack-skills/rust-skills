# Cargo Registries and Authentication

Use this reference for alternate registries, source replacement, vendoring, credential providers, login/logout, and private registry configuration. Read [Registries](https://doc.rust-lang.org/cargo/reference/registries.html), [Registry Authentication](https://doc.rust-lang.org/cargo/reference/registry-authentication.html), and [Source Replacement](https://doc.rust-lang.org/cargo/reference/source-replacement.html).

## Choose the correct mechanism

| Need | Mechanism |
|---|---|
| Publish to or depend on an alternate registry | `[registries.<name>]` and dependency `registry = "<name>"` |
| Redirect crates.io resolution to a compatible mirror | `[source.crates-io] replace-with = "<source>"` |
| Build from checked-in or generated local dependency sources | Directory source produced by `cargo vendor` |
| Use one local crate implementation during development | Path dependency or `[patch]`, not source replacement |
| Authenticate to a registry | A configured credential provider |

Registries and sources are related but not interchangeable. Source replacement requires equivalent crate contents and checksums; it is not a general dependency override.

## Alternate registry

```toml
[registries.company]
index = "sparse+https://registry.example.invalid/index/"

[registry]
global-credential-providers = ["cargo:token"]
```

```toml
[dependencies]
internal-api = { version = "1.2", registry = "company" }
```

Use the exact index URL and protocol required by the registry. Do not guess whether it supports sparse or Git index access.

## Source replacement and vendoring

```toml
[source.crates-io]
replace-with = "vendored-sources"

[source.vendored-sources]
directory = "vendor"
```

Generate the directory source using the installed Cargo:

```bash
cargo vendor vendor/
```

Commit the generated Cargo configuration or pass it to the intended build environment deliberately. Re-run vendoring after lockfile changes and validate with the required offline or frozen build.

Git dependencies are separate sources and are not automatically converted into crates.io mirror traffic.

## Credentials

- Prefer configured credential providers over embedding tokens in manifests, repository config, shell history, or generated logs.
- Confirm the registry name and credential provider before `cargo login`.
- Use CI secret injection supported by the selected provider.
- Do not print `credentials.toml` or broad environment dumps during diagnosis.
- Treat `cargo logout`, owner changes, publication, and yanking as external mutations requiring explicit authorization.

The [Credential Provider Protocol](https://doc.rust-lang.org/cargo/reference/credential-provider-protocol.html) is for implementing or integrating credential helpers. Do not implement a custom provider when a supported built-in or organizational provider already satisfies the security boundary.

## Registry implementation boundary

Only read [Registry Index](https://doc.rust-lang.org/cargo/reference/registry-index.html) and [Registry Web API](https://doc.rust-lang.org/cargo/reference/registry-web-api.html) when implementing or operating a Cargo-compatible registry. Ordinary package consumers should not reproduce those protocols.

## Validation

```bash
cargo metadata --format-version 1 --locked
cargo fetch --locked
cargo package --list
```

For an air-gapped build, populate the intended sources first, disconnect or block the network in the test environment, and run with `--frozen`.
