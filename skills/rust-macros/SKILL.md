---
name: rust-macros
description: Design, implement, debug, test, and review Rust declarative and procedural macros, including macro_rules matchers and repetition, hygiene, $crate paths, derive, attribute and function-like macros, syn parsing, quote generation, diagnostics, cargo-expand, doctests, and trybuild. Use when users need compile-time code generation or a Rust DSL; keep ordinary trait, generic, or handwritten APIs outside macros unless generation has a clear maintenance benefit.
---

# Rust Macros

Use macros for syntax transformation or mechanical generation that functions, traits, generics, and build scripts cannot express cleanly. Keep the generated API smaller and more stable than the macro implementation.

## Scope and Routing

Use this skill for `macro_rules!`, declarative DSLs, derive macros, attribute macros, function-like procedural macros, parsing, token generation, hygiene, diagnostics, and expansion tests.

Route ordinary generic design to `rust-stable`, crate layout and proc-macro companion crates to `rust-project-structure`, feature and publishing policy to `rust-cargo-build`, compile-fail strategy to `rust-testing`, and use of the third-party Lombok-like derives to `rust-lombok-macros`.

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

### 3. Implement declarative macros hygienically

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

### 4. Parse procedural macros structurally

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

### 5. Test the public expansion contract

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
