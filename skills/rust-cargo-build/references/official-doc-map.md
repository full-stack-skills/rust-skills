# Official Cargo Documentation Map

Use this file to find the authoritative Cargo page before answering version-sensitive questions. The canonical URLs follow the current stable Cargo release; compare the installed `cargo --version` with the [Cargo changelog](https://doc.rust-lang.org/cargo/CHANGELOG.html) when a field, flag, default, or command may be newer than the project's toolchain.

## Documentation layers

| Layer | Use it for | Official entry |
|---|---|---|
| Getting Started | Install Cargo and create the first package | [Getting Started](https://doc.rust-lang.org/cargo/getting-started/) |
| Cargo Guide | Task-oriented onboarding and everyday workflows | [Cargo Guide](https://doc.rust-lang.org/cargo/guide/) |
| Cargo Reference | Exact manifest, resolver, configuration, registry, and build semantics | [Cargo Reference](https://doc.rust-lang.org/cargo/reference/) |
| Cargo Commands | CLI flags, selectors, output, and side effects | [Cargo Commands](https://doc.rust-lang.org/cargo/commands/) |
| Changelog | Stabilization dates, changed defaults, regressions, and removals | [Cargo Changelog](https://doc.rust-lang.org/cargo/CHANGELOG.html) |
| Unstable Reference | Nightly-only `cargo-features`, `-Z`, and `[unstable]` behavior | [Unstable Features](https://doc.rust-lang.org/cargo/reference/unstable.html) |
| FAQ and glossary | Resolve terminology and common operational questions | [FAQ](https://doc.rust-lang.org/cargo/faq.html), [Glossary](https://doc.rust-lang.org/cargo/appendix/glossary.html) |
| Git authentication | Diagnose Git dependency and proxy authentication | [Git Authentication](https://doc.rust-lang.org/cargo/appendix/git-authentication.html) |

## Cargo Guide

| Topic | Official page | Local guidance |
|---|---|---|
| Why Cargo exists | [Why Cargo Exists](https://doc.rust-lang.org/cargo/guide/why-cargo-exists.html) | `cargo-guide-workflow.md` |
| Create and initialize packages | [Creating a New Package](https://doc.rust-lang.org/cargo/guide/creating-a-new-project.html) | `cargo-guide-workflow.md` |
| Work on an existing package | [Working on an Existing Package](https://doc.rust-lang.org/cargo/guide/working-on-an-existing-project.html) | `cargo-guide-workflow.md` |
| Add dependencies | [Dependencies](https://doc.rust-lang.org/cargo/guide/dependencies.html) | `dependencies-features-resolver.md` |
| Conventional package layout | [Package Layout](https://doc.rust-lang.org/cargo/guide/project-layout.html) | `manifest-targets.md` |
| Manifest versus lockfile | [Cargo.toml vs Cargo.lock](https://doc.rust-lang.org/cargo/guide/cargo-toml-vs-cargo-lock.html) | `cargo-guide-workflow.md` |
| Tests | [Tests](https://doc.rust-lang.org/cargo/guide/tests.html) | Route test design to `rust-testing` |
| Continuous integration | [Continuous Integration](https://doc.rust-lang.org/cargo/guide/continuous-integration.html) | `cargo-guide-workflow.md` |
| Publish to crates.io | [Publishing on crates.io](https://doc.rust-lang.org/cargo/reference/publishing.html) | `publishing.md` |
| Cargo Home | [Cargo Home](https://doc.rust-lang.org/cargo/guide/cargo-home.html) | `build-cache-diagnostics.md` |
| Build performance | [Optimizing Build Performance](https://doc.rust-lang.org/cargo/guide/build-performance.html) | `profiles.md`, `build-cache-diagnostics.md` |

## Cargo Reference

| Topic | Official page | Local guidance or owner |
|---|---|---|
| Manifest format | [Manifest Format](https://doc.rust-lang.org/cargo/reference/manifest.html) | `manifest-targets.md` |
| Cargo targets | [Cargo Targets](https://doc.rust-lang.org/cargo/reference/cargo-targets.html) | `manifest-targets.md` |
| Rust version/MSRV | [Rust Version](https://doc.rust-lang.org/cargo/reference/rust-version.html) | `manifest-targets.md` |
| Workspaces | [Workspaces](https://doc.rust-lang.org/cargo/reference/workspaces.html) | `workspaces.md` |
| Dependency declarations | [Specifying Dependencies](https://doc.rust-lang.org/cargo/reference/specifying-dependencies.html) | `dependencies-features-resolver.md` |
| Dependency overrides | [Overriding Dependencies](https://doc.rust-lang.org/cargo/reference/overriding-dependencies.html) | `dependencies-features-resolver.md` |
| Source replacement | [Source Replacement](https://doc.rust-lang.org/cargo/reference/source-replacement.html) | `registries-authentication.md` |
| Dependency resolution | [Dependency Resolution](https://doc.rust-lang.org/cargo/reference/resolver.html) | `dependencies-features-resolver.md` |
| Features | [Features](https://doc.rust-lang.org/cargo/reference/features.html) | `dependencies-features-resolver.md` |
| Feature patterns | [Features Examples](https://doc.rust-lang.org/cargo/reference/features-examples.html) | `dependencies-features-resolver.md` |
| Profiles | [Profiles](https://doc.rust-lang.org/cargo/reference/profiles.html) | `profiles.md` |
| Cargo configuration | [Configuration](https://doc.rust-lang.org/cargo/reference/config.html) | `configuration-environment.md` |
| Environment variables | [Environment Variables](https://doc.rust-lang.org/cargo/reference/environment-variables.html) | `configuration-environment.md` |
| Build scripts | [Build Scripts](https://doc.rust-lang.org/cargo/reference/build-scripts.html) | `build-scripts.md` |
| Build-script patterns | [Build Script Examples](https://doc.rust-lang.org/cargo/reference/build-script-examples.html) | `build-scripts.md` |
| Build cache and output layout | [Build Cache](https://doc.rust-lang.org/cargo/reference/build-cache.html) | `build-cache-diagnostics.md` |
| Package ID specifications | [Package ID Specifications](https://doc.rust-lang.org/cargo/reference/pkgid-spec.html) | `metadata-automation.md` |
| External Cargo tools | [External Tools](https://doc.rust-lang.org/cargo/reference/external-tools.html) | `metadata-automation.md` |
| Registries | [Registries](https://doc.rust-lang.org/cargo/reference/registries.html) | `registries-authentication.md` |
| Registry authentication | [Registry Authentication](https://doc.rust-lang.org/cargo/reference/registry-authentication.html) | `registries-authentication.md` |
| Credential providers | [Credential Provider Protocol](https://doc.rust-lang.org/cargo/reference/credential-provider-protocol.html) | `registries-authentication.md` |
| Running a registry | [Running a Registry](https://doc.rust-lang.org/cargo/reference/running-a-registry.html) | Read only when implementing or operating a registry |
| Registry index | [Registry Index](https://doc.rust-lang.org/cargo/reference/registry-index.html) | Operate here only when implementing a registry |
| Registry Web API | [Registry Web API](https://doc.rust-lang.org/cargo/reference/registry-web-api.html) | Operate here only when implementing a registry |
| SemVer compatibility | [SemVer Compatibility](https://doc.rust-lang.org/cargo/reference/semver.html) | Route decisions to `rust-semver` |
| Future incompatibility reports | [Future Incompat Report](https://doc.rust-lang.org/cargo/reference/future-incompat-report.html) | `build-cache-diagnostics.md` |
| Build timings | [Reporting Build Timings](https://doc.rust-lang.org/cargo/reference/timings.html) | `build-cache-diagnostics.md` |
| Cargo lints | [Cargo Lints](https://doc.rust-lang.org/cargo/reference/lints.html) | `unstable-features.md`; route rustc/Clippy policy to `rust-style-clippy` |
| Unstable Cargo features | [Unstable Features](https://doc.rust-lang.org/cargo/reference/unstable.html) | `unstable-features.md` |

## Command groups

| Group | Official page | Local guidance |
|---|---|---|
| General commands | [General Commands](https://doc.rust-lang.org/cargo/commands/general-commands.html) | `cargo-command-map.md` |
| Build commands | [Build Commands](https://doc.rust-lang.org/cargo/commands/build-commands.html) | `cargo-command-map.md` |
| Manifest commands | [Manifest Commands](https://doc.rust-lang.org/cargo/commands/manifest-commands.html) | `cargo-command-map.md` |
| Package commands | [Package Commands](https://doc.rust-lang.org/cargo/commands/package-commands.html) | `cargo-command-map.md` |
| Publishing commands | [Publishing Commands](https://doc.rust-lang.org/cargo/commands/publishing-commands.html) | `cargo-command-map.md`, `publishing.md` |
| Report commands | [Report Commands](https://doc.rust-lang.org/cargo/commands/report-commands.html) | `cargo-command-map.md`, `build-cache-diagnostics.md` |
| Deprecated and removed commands | [Deprecated and Removed](https://doc.rust-lang.org/cargo/commands/deprecated-and-removed.html) | Use only for migration or historical diagnosis |

## Version-check rule

1. Run `cargo --version`.
2. Open the current stable page for the intended behavior.
3. Check the changelog or a version-specific Rust documentation snapshot when the project's Cargo is older.
4. Mark nightly-only behavior explicitly and read its tracking issue.
5. Record a stable fallback whenever production use depends on an experiment.
