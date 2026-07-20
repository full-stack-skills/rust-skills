# lombok-macros 2.0.32 Reference

This reference is derived from the crates.io `2.0.32` package's `src/lib.rs`, attribute parser, and code generator. Recheck the source and compile tests after upgrading. Do not treat this file as documentation that automatically follows the latest release.

## Version facts

- Dependency: `lombok-macros = "=2.0.32"`
- Import path: `lombok_macros`
- Crate type: procedural macro
- Crate edition: 2024
- Declared MSRV: none
- Features: none
- License: MIT
- Derives: `Getter`, `GetterMut`, `Setter`, `Data`, `New`, `CustomDebug`, `DisplayDebug`, and `DisplayDebugFormat`
- Not included: Builder, Default, Clone, Eq, Hash, Serialize, or Deserialize

## Common outdated or misleading snippets

Translate examples by behavior, not by annotation name:

| Snippet or claim | `2.0.32` interpretation |
|---|---|
| `#[derive(Lombok)]` | Unsupported. Select `Getter`, `GetterMut`, `Setter`, or `Data`. |
| `lombok-macros = "latest"` | Invalid dependency guidance. Use `cargo add lombok-macros` or a reviewed semver requirement. |
| “The crate generates Clone” | Incorrect. `Clone` is a standard Rust derive. |
| “The crate generates Debug” | Only `CustomDebug` is crate-provided; ordinary `Debug` is a standard Rust derive. |
| “DisplayDebug generates Debug and Display” | Incorrect. It implements `Display` using an available `Debug` representation. |
| “No overhead” | Too broad. There is no helper runtime API to call, but macro expansion adds compile-time work and generated methods can clone, panic, or widen APIs. |

When correcting an old example, preserve the intended caller contract and compile it against the project's locked version. Do not mechanically replace `Lombok` with `Data`: `Data` also enables mutable getters and setters for annotated fields and may expose more capability than the old code intended.

## Getter

Use the `#[get(...)]` field attribute. Named fields generate `get_<field>`; tuple fields generate `get_<index>`.

| Attribute | Return value | Notes |
|---|---|---|
| `#[get(pub)]` | Usually `&T` | Visibility also supports `pub(crate)`, `pub(super)`, and `private` |
| `#[get(pub, type(clone))]` | `T` | Calls `clone`; its cost is part of the API contract |
| `#[get(pub, type(copy))]` | `T` | The field must support copying |
| `#[get(pub, type(deref))]` | Inner `T` | Panics for Option and Result; normally avoid it |

For `Option<T>` and `Result<T, E>`, the default reference mode generates a normal getter that clones the container, calls `unwrap()`, and returns `T`. It also generates a `try_get_<field>` method. This is not a failure-preserving borrowed accessor. Prefer explicit production APIs:

```rust
fn value(&self) -> Option<&str> {
    self.value.as_deref()
}

fn result(&self) -> Result<&Value, &Error> {
    self.result.as_ref()
}
```

`type(deref)` explicitly panics on `None` and `Err`. For `Box<T>`, it can attempt to move from borrowed content. Consider it only after compiling and behavior-testing the exact field type.

Part of the crate documentation also shows `#[get(pub, clone)]`, `copy`, and `deref` shorthand. The `2.0.32` parser sets its return strategy only from `type(...)`; use the source-verified forms in the table.

## GetterMut

Use `#[get_mut(pub)]` to generate `get_mut_<field>(&mut self) -> &mut T`. It also supports `pub(crate)`, `pub(super)`, and `private`.

The method exposes the entire field as a mutable reference, allowing changes that the macro cannot observe. Restrict it to data carriers without cross-field invariants, auditing, or normalization requirements.

## Setter

Use `#[set(...)]` to generate `set_<field>(&mut self, val: ...) -> &mut Self`, which supports chaining.

```rust
#[set(pub)]                         // original field type
#[set(pub, type(Into<String>))]     // impl Into<String>
#[set(pub, type(AsRef<str>))]       // impl AsRef<str>, followed by to_owned
#[set(pub, type(AsRef<[u8]>))]      // impl AsRef<[u8]>, followed by to_owned
```

Visibility supports `pub`, `pub(crate)`, `pub(super)`, and `private`. Conversion improves call ergonomics but does not add validation. Keep a handwritten named method when assignment requires validation, normalization, event emission, or cache invalidation.

## Data

`Data` combines `Getter`, `GetterMut`, and `Setter` processing and recognizes `#[get(...)]`, `#[get_mut(...)]`, and `#[set(...)]`. It does not replace `Debug`, `Clone`, `New`, or a builder.

Because all three accessor categories can widen the API surface, start with separate minimal derives. Use `Data` only when the selected fields genuinely require the corresponding read, write, and mutable-borrow capabilities.

## New

Control constructor visibility on the type:

```rust
#[derive(New)]
#[new(pub(crate))]
struct Request {
    id: u64,
    #[new(skip)]
    retries: usize,
}
```

- Generates an associated `new` function that is public by default.
- Uses non-skipped fields as parameters in declaration order.
- Initializes `#[new(skip)]` fields with `Default::default()`; their types must implement `Default`.
- Performs no validation and cannot replace `try_new`, parsing, range checks, or cross-field invariants.

## CustomDebug

`#[derive(CustomDebug)]` generates `Debug`. Add `#[debug(skip)]` to fields that must be omitted. It supports structs and enums.

Security constraints:

- Explicitly skip tokens, passwords, keys, cookies, and personal data.
- Test that `format!("{value:?}")` contains neither the field name nor its value.
- Review every newly added field; the macro is not an automatic redaction system.
- Do not also derive the standard `Debug` implementation.

## DisplayDebug and DisplayDebugFormat

- `DisplayDebug` implements `Display` using `{:?}`.
- `DisplayDebugFormat` implements `Display` using `{:#?}`.

Both require `Debug`. Restrict them to internal diagnostics. Do not use them for user-facing errors, CLI output, protocol messages, or persisted text because Debug reveals structure and is not a stable presentation contract. Even with `CustomDebug`, test the final Display output for sensitive types.

## Visibility and semver

Generated methods participate in module privacy and public APIs exactly like handwritten methods. Changing `private` to `pub(crate)` or `pub`, changing a borrowed return into clone or copy, or adding a setter or mutable getter changes caller capabilities and may alter a library's semver surface. Lock signatures with downstream-caller tests before upgrading.
