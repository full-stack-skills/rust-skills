# Unstable Cargo Features

Use nightly Cargo only when a stable workflow cannot meet the requirement and the experiment's risk is acceptable. Read the current [Unstable Features](https://doc.rust-lang.org/cargo/reference/unstable.html) page and linked tracking issue every time; names, syntax, defaults, and stabilization status can change.

## Activation forms

Cargo experiments can use different gates:

```toml
cargo-features = ["<manifest-feature>"]
```

```bash
cargo +nightly <command> -Z unstable-options <unstable-option>
cargo +nightly -Z <feature> <command>
cargo +nightly -Z help
```

```toml
[unstable]
<feature> = true
```

Do not mix these forms unless the feature documentation requires it.

## Evaluation checklist

Before recommending an experiment, record:

- exact nightly toolchain or date;
- unstable feature name and activation form;
- official tracking issue;
- supported host and target platforms;
- effect on manifests, lockfiles, cache layout, artifacts, or publication;
- stable fallback;
- removal or stabilization condition;
- CI job that proves the experimental path separately from stable support.

Pin nightly in `rust-toolchain.toml` or CI when reproducibility matters. Do not label a crate stable-compatible if its normal build requires nightly Cargo.

## Cargo lints versus rustc and Clippy lints

Keep these separate:

- `[lints.rust]` and `[lints.clippy]` configure rustc and Clippy lint levels through the manifest.
- Cargo's own `cargo::...` lint system and `[lints.cargo]` are documented in [Cargo Lints](https://doc.rust-lang.org/cargo/reference/lints.html) and may require nightly Cargo.

Route the policy choice and source-code lint remediation to `rust-style-clippy`; keep Cargo feature gating and manifest mechanics here.

## Common experiment categories

The unstable reference currently groups experiments around:

- resolver and feature behavior;
- build scripts and linking;
- output and artifact placement;
- compiler and standard-library builds;
- rustdoc output;
- manifest/profile extensions;
- metadata and build analysis;
- configuration, registries, and single-file scripts.

Do not mirror the full list locally because it changes frequently. Use the official list, then document only the selected experiment in the project.

## Exit strategy

When an experiment stabilizes:

1. identify the first stable Cargo version;
2. raise or document the required toolchain version if needed;
3. remove `+nightly`, `-Z`, `cargo-features`, or `[unstable]` gates;
4. rerun stable and MSRV validation;
5. delete obsolete fallback logic only after supported environments have migrated.
