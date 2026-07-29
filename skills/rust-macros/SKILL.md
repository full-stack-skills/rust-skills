---
name: rust-macros
description: Design, name, implement, debug, test, and review Rust declarative and procedural macros, including macro_rules matchers and repetition, hygiene, $crate paths, derive, attribute and function-like macros, proc-macro crate naming, syn parsing, quote generation, diagnostics, cargo-expand, doctests, and trybuild. Use when users need compile-time code generation, a Rust DSL, or guidance choosing -derive versus -macros; keep ordinary trait, generic, or handwritten APIs outside macros unless generation has a clear maintenance benefit.
---

# Rust Macros

Use macros for syntax transformation or mechanical generation that functions, traits, generics, and build scripts cannot express cleanly. Keep the generated API smaller and more stable than the macro implementation.

## Scope and Routing

Use this skill for `macro_rules!`, declarative DSLs, derive macros, attribute macros, function-like procedural macros, parsing, token generation, hygiene, diagnostics, and expansion tests.

Route ordinary generic design to `rust-stable`, crate layout and proc-macro companion crates to `rust-workspace`, feature and publishing policy to `rust-cargo-build`, compile-fail strategy to `rust-testing`, use of the third-party Lombok-like derives to `rust-lombok-macros`, and UniFFI export/derive usage plus generated foreign bindings to `rust-uniffi-building`.

## Workflow

### 1. Prove a macro is the right boundary

Write representative invocations and expected expansions first. Prefer a function, trait, derive already provided by the ecosystem, or small handwritten implementation when it keeps diagnostics and navigation clearer. Define supported syntax, edition, MSRV, generated names, visibility, error cases, and semver surface.

### 2. Choose the smallest macro category

| Need | Mechanism |
|---|---|
| Repeat or match Rust token patterns | `macro_rules!` |
| Implement a trait for an annotated type | derive procedural macro |
| Transform an annotated item | attribute procedural macro |
| Parse a custom token invocation | function-like procedural macro |

Use a dedicated `proc-macro = true` crate for procedural macros. Put shared runtime traits and types in a normal library crate so generated code does not depend on private proc-macro implementation details.

### 3. Name procedural-macro crates by their public surface

Treat the suffix as an API promise, not a compiler requirement:

| Public macro surface | Preferred package suffix | Examples |
|---|---|---|
| Only `#[proc_macro_derive]` entry points | `-derive` or the established family spelling such as `_derive` | `serde_derive` |
| A broader suite, especially attribute or function-like macros, or mixed macro kinds | `-macros` | `tokio-macros`, `actix-macros` |
| Unclear or unspecified macro scope | Avoid singular `-macro`; choose a more descriptive name | — |

Choose `-derive` when every public entry point is a derive macro. The crate may expose several closely related derives; the deciding factor is macro kind, not the exact count. Choose `-macros` when the crate exposes attribute macros, function-like macros, mixed macro kinds, or intentionally serves as the package family's general macro collection.

Do not publish both `<name>-derive` and `<name>-macros` by default. A single proc-macro crate can register any number of derive, attribute, and function-like macros. Prefer one of these layouts:

```text
<name>            # public runtime API or facade; may re-export macros
<name>-derive     # derive-only proc-macro crate
```

```text
<name>            # public runtime API or facade; may re-export macros
<name>-macros     # general proc-macro collection
<name>-macro-core # optional normal library for parsing and generation logic
```

Split `-derive` and `-macros` into separate published crates only when users can adopt them independently and the split materially reduces dependencies or compile time, separates release or compatibility policies, or isolates distinct ownership boundaries. Keep their exported macro names and responsibilities non-overlapping. Do not split merely by macro kind or for naming symmetry.

Before publishing, also:

- Follow the separator already used by the crate family; Cargo package names may contain `-` or `_`, while Rust crate identifiers normalize hyphens to underscores.
- Prefer a facade crate and feature-gated re-exports when most users should not depend on the implementation crate directly.
- Treat a published crate rename as a migration with ecosystem and semver cost; choose the intended long-term scope early, but do not claim planned macro kinds before they exist.

### 4. Implement declarative macros hygienically

```rust
#[macro_export]
macro_rules! string_list {
    ($($value:expr),* $(,)?) => {{
        let mut output = ::std::vec::Vec::new();
        $(output.push(::std::string::ToString::to_string(&$value));)*
        output
    }};
}
```

- Put specific matcher arms before general arms.
- Use the correct fragment specifier such as `expr`, `ident`, `ty`, `pat`, `item`, `meta`, `path`, or `tt`.
- Support an optional trailing separator only when the public syntax intends it.
- Use `$crate` for paths into the defining crate.
- Avoid repeated evaluation, hidden moves, surprising control flow, and identifiers that collide with caller code.
- Avoid quadratic TT munchers for large inputs; prefer repetitions or procedural parsing when token volume matters.

### 5. Parse procedural macros structurally

```rust
use proc_macro::TokenStream;
use quote::quote;
use syn::{parse_macro_input, DeriveInput};

#[proc_macro_derive(Describe)]
pub fn derive_describe(input: TokenStream) -> TokenStream {
    let input = parse_macro_input!(input as DeriveInput);
    let name = input.ident;
    quote! {
        impl Describe for #name {
            fn type_name() -> &'static str {
                stringify!(#name)
            }
        }
    }
    .into()
}
```

- Parse with `syn` or a purpose-built parser rather than token strings.
- Preserve spans and combine `syn::Error` values so users receive multiple useful diagnostics.
- Generate paths that work after dependency renaming when the public contract requires it.
- Preserve generics, lifetimes, const parameters, where clauses, attributes, and visibility.
- Do not panic on invalid user input; emit compile errors at the relevant span.

### 6. Test the public expansion contract

Use several layers:

```bash
cargo fmt --all --check
cargo check --workspace --all-targets --all-features
cargo test --workspace --all-targets --all-features
cargo clippy --workspace --all-targets --all-features -- -D warnings
cargo expand --package example-crate
```

- Runtime and doctest cases prove successful generated behavior.
- `trybuild` or equivalent UI tests lock accepted and rejected syntax plus diagnostics.
- Expansion snapshots are review aids, not the only correctness gate.
- Test generic, lifetime, visibility, renamed-dependency, no-std, feature, and edition combinations that the macro claims to support.

Nightly `trace_macros!` is an optional diagnostic tool, not a stable default.

Read [Macro Reference](references/references.md) for matcher and procedural-macro details. Read [Execution Scenarios](examples/examples.md) for representative requests.

## Review Checklist

- Could a function, trait, or derive replace the macro?
- Is caller input evaluated exactly as documented?
- Are `$crate`, spans, generics, and visibility handled correctly?
- Can invalid input trigger a proc-macro panic?
- Does generated unsafe code expose a documented safe contract?
- Are compile-fail diagnostics tested without overspecifying unstable wording?
- Does the generated public API create an intentional semver commitment?

## Completion Criteria

- Define supported syntax and expected expansion before implementation.
- Use the smallest suitable macro category.
- Preserve hygiene, spans, generics, visibility, and edition compatibility.
- Cover successful expansions and rejected syntax with caller-shaped tests.
- Pass formatting, check, tests, and Clippy on supported configurations.

## Upstream Sources

- [The Rust Book: Macros](https://doc.rust-lang.org/book/ch20-05-macros.html)
- [Rust Reference: Macros By Example](https://doc.rust-lang.org/reference/macros-by-example.html)
- [Rust Reference: Procedural Macros](https://doc.rust-lang.org/reference/procedural-macros.html)
- [syn](https://docs.rs/syn/)
- [quote](https://docs.rs/quote/)

## Data Privacy

This skill does not collect, store, or transmit user data. Generated code may embed input literals, so review expansion output for secrets before publishing artifacts.
