# Cargo Command Map

Select commands by task and side effect. Read the linked command page for its complete package, target, feature, profile, target-triple, output, and manifest-selection options. Use `cargo help <command>` to match the installed Cargo version.

## General and build commands

| Command | Use | Important side effect or route | Official page |
|---|---|---|---|
| `cargo` | Show command overview or execute a selected subcommand | Global options affect command execution; read installed help | [cargo](https://doc.rust-lang.org/cargo/commands/cargo.html) |
| `cargo help` | Read installed command help | No project mutation | [cargo help](https://doc.rust-lang.org/cargo/commands/cargo-help.html) |
| `cargo version` | Report Cargo version | Use before version-gated advice | [cargo version](https://doc.rust-lang.org/cargo/commands/cargo-version.html) |
| `cargo check` | Type-check without final code generation | May resolve dependencies or update the lockfile unless constrained | [cargo check](https://doc.rust-lang.org/cargo/commands/cargo-check.html) |
| `cargo build` | Compile selected artifacts | Writes build artifacts and may update the lockfile | [cargo build](https://doc.rust-lang.org/cargo/commands/cargo-build.html) |
| `cargo run` | Build and execute a binary/example | Executes project code; pass program arguments after `--` | [cargo run](https://doc.rust-lang.org/cargo/commands/cargo-run.html) |
| `cargo test` | Build and run test targets | Executes project and test code; route test design to `rust-testing` | [cargo test](https://doc.rust-lang.org/cargo/commands/cargo-test.html) |
| `cargo bench` | Build and run benchmark targets | Executes benchmark code; usually uses the bench profile | [cargo bench](https://doc.rust-lang.org/cargo/commands/cargo-bench.html) |
| `cargo doc` | Build rustdoc output | Writes `target/doc`; route documentation design to `rust-documentation` | [cargo doc](https://doc.rust-lang.org/cargo/commands/cargo-doc.html) |
| `cargo clean` | Remove Cargo build artifacts | Destructive; resolve the exact target directory and selection first | [cargo clean](https://doc.rust-lang.org/cargo/commands/cargo-clean.html) |
| `cargo fetch` | Pre-fetch dependencies | Network and cache side effects; useful before offline builds | [cargo fetch](https://doc.rust-lang.org/cargo/commands/cargo-fetch.html) |
| `cargo fix` | Apply compiler suggestions | Modifies source files; require a clean or safely understood worktree | [cargo fix](https://doc.rust-lang.org/cargo/commands/cargo-fix.html) |
| `cargo fmt` | Run rustfmt through Cargo | May modify source unless `--check`; route policy to `rust-style-clippy` | [cargo fmt](https://doc.rust-lang.org/cargo/commands/cargo-fmt.html) |
| `cargo clippy` | Run Clippy through Cargo | Route lint policy to `rust-style-clippy` | [cargo clippy](https://doc.rust-lang.org/cargo/commands/cargo-clippy.html) |
| `cargo miri` | Run code in the Miri interpreter when the component/toolchain supports it | Executes under an interpreter; verify installation and route unsafe-behavior analysis appropriately | [cargo miri](https://doc.rust-lang.org/cargo/commands/cargo-miri.html) |
| `cargo rustc` | Pass extra options to one selected rustc target | Avoid as persistent configuration when manifest/config fields exist | [cargo rustc](https://doc.rust-lang.org/cargo/commands/cargo-rustc.html) |
| `cargo rustdoc` | Pass extra options to one selected rustdoc target | Route documentation intent to `rust-documentation` | [cargo rustdoc](https://doc.rust-lang.org/cargo/commands/cargo-rustdoc.html) |

## Manifest and dependency commands

| Command | Use | Important side effect | Official page |
|---|---|---|---|
| `cargo add` | Add or update a direct dependency declaration | Modifies `Cargo.toml` and usually `Cargo.lock` | [cargo add](https://doc.rust-lang.org/cargo/commands/cargo-add.html) |
| `cargo remove` | Remove a direct dependency declaration | Modifies `Cargo.toml` and usually `Cargo.lock` | [cargo remove](https://doc.rust-lang.org/cargo/commands/cargo-remove.html) |
| `cargo info` | Inspect package metadata and features | May update registry cache | [cargo info](https://doc.rust-lang.org/cargo/commands/cargo-info.html) |
| `cargo generate-lockfile` | Generate or refresh lockfile resolution | Writes `Cargo.lock` | [cargo generate-lockfile](https://doc.rust-lang.org/cargo/commands/cargo-generate-lockfile.html) |
| `cargo update` | Update resolved versions within requirements | Writes `Cargo.lock`; scope with package ID specs where possible | [cargo update](https://doc.rust-lang.org/cargo/commands/cargo-update.html) |
| `cargo locate-project` | Locate a manifest or workspace root | No mutation | [cargo locate-project](https://doc.rust-lang.org/cargo/commands/cargo-locate-project.html) |
| `cargo metadata` | Emit machine-readable workspace and graph data | May resolve/fetch unless locked, frozen, offline, or `--no-deps` | [cargo metadata](https://doc.rust-lang.org/cargo/commands/cargo-metadata.html) |
| `cargo pkgid` | Resolve a package ID specification | No intended project mutation | [cargo pkgid](https://doc.rust-lang.org/cargo/commands/cargo-pkgid.html) |
| `cargo tree` | Inspect dependency and feature edges | No manifest mutation; may resolve the graph | [cargo tree](https://doc.rust-lang.org/cargo/commands/cargo-tree.html) |
| `cargo vendor` | Copy registry and Git sources into a directory source | Writes vendored files and prints source config | [cargo vendor](https://doc.rust-lang.org/cargo/commands/cargo-vendor.html) |

## Package and installation commands

| Command | Use | Important side effect | Official page |
|---|---|---|---|
| `cargo new` | Create a new package directory | Creates files and may initialize version control | [cargo new](https://doc.rust-lang.org/cargo/commands/cargo-new.html) |
| `cargo init` | Initialize the current directory as a package | Creates files in an existing directory | [cargo init](https://doc.rust-lang.org/cargo/commands/cargo-init.html) |
| `cargo search` | Search a registry | Network request; select alternate registry explicitly | [cargo search](https://doc.rust-lang.org/cargo/commands/cargo-search.html) |
| `cargo install` | Build and install binary crates | Downloads, compiles, and writes installed executables | [cargo install](https://doc.rust-lang.org/cargo/commands/cargo-install.html) |
| `cargo uninstall` | Remove Cargo-installed executables | Destructive; confirm the package and installation root | [cargo uninstall](https://doc.rust-lang.org/cargo/commands/cargo-uninstall.html) |

## Publishing and reports

| Command | Use | Important side effect | Official page |
|---|---|---|---|
| `cargo package` | Assemble and verify a publishable archive | Writes package artifacts; inspect with `--list` first | [cargo package](https://doc.rust-lang.org/cargo/commands/cargo-package.html) |
| `cargo publish` | Upload a package version | Irreversible publication; require explicit registry and authorization | [cargo publish](https://doc.rust-lang.org/cargo/commands/cargo-publish.html) |
| `cargo login` / `logout` | Configure or remove registry credentials | Modifies credential state | [cargo login](https://doc.rust-lang.org/cargo/commands/cargo-login.html), [cargo logout](https://doc.rust-lang.org/cargo/commands/cargo-logout.html) |
| `cargo owner` | Change registry package owners | External authorization change | [cargo owner](https://doc.rust-lang.org/cargo/commands/cargo-owner.html) |
| `cargo yank` | Change whether a published version is selected by new resolution | External registry mutation; does not delete the version | [cargo yank](https://doc.rust-lang.org/cargo/commands/cargo-yank.html) |
| `cargo report future-incompatibilities` | Explain dependency warnings that may become hard errors | Reads saved build reports | [cargo report](https://doc.rust-lang.org/cargo/commands/cargo-report.html) |

## Common selection discipline

- Use `--manifest-path` when the working directory is ambiguous.
- Select workspace packages deliberately with `--workspace`, `--package`, `--exclude`, or `--members`-equivalent command options where supported.
- Select targets explicitly when a package has multiple binaries, examples, tests, or benches.
- Treat `--all-features` as a requested combination, not proof that all feature combinations work.
- Use `--locked`, `--offline`, or `--frozen` according to the required lockfile and network policy.
- Put arguments for the built program or test harness after `--`.
