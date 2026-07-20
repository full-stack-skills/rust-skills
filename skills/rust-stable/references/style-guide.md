# Rust Style Guide

## Naming Conventions

- Types and traits: `UpperCamelCase` (e.g., `MyType`, `MyTrait`)
- Functions, methods, modules, and variables: `snake_case` (e.g., `my_function`, `my_module_name`)
- Constants and statics: `SCREAMING_SNAKE_CASE` (e.g., `MY_CONSTANT`, `STATIC_VAR`)
  - Constructors typically use the keyword `new`.
  - Conversion methods follow patterns like `from_*`, `into_*`, `as_*`, or `to_*`.

## Modules and API Surface

- Organize modules by domain capability rather than splitting them into individual struct/trait/impl files.
- Default visibility is private; public APIs are limited to stable, intentionally maintained interfaces.
- Re-export major public types from the crate root to avoid deep internal paths in user dependencies.
- Write documentation for public errors, panics, unsafe code, and platform-specific limitations using rustdoc chapters.
- Prefer writing examples as executable doctests instead of inline comments or standalone test files.

## Formatting and Linting

```bash
cargo fmt --all --check
cargo clippy --workspace --all-targets --all-features -- -D warnings
```

Do not globally `allow` lint rules solely to suppress them; record why they are inapplicable and restrict the scope of any allowed exceptions.

More advanced lints, edition migrations, and error code analysis should be handled by the dedicated tooling: [rust-style-clippy](https://github.com/rust-lang/style-guide).

Official source: https://doc.rust-lang.org/style-guide/
