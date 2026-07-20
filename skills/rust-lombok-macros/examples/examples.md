# lombok-macros Execution Scenarios

## Reduce an internal DTO

User request:

> Replace these repetitive DTO getters and setters with lombok-macros. Let the String setter accept both `&str` and `String`.

Execution:

1. Check the locked version, edition, and project MSRV.
2. Record the existing method visibility, return types, and callers.
3. Derive only the `Getter` and `Setter` methods that callers need; do not default to `Data`.
4. Use the locked version's verified `type(Into<String>)` setter syntax.
5. Add caller-shaped contract tests and run fmt, check, test, and Clippy.

## Reject a broken domain model

User request:

> Remove the account's validating constructor and debit or credit methods. Derive Data and New so every field can be changed directly.

Do not implement the request literally. Explain that `Data` exposes setters and mutable getters while `New` performs no validation. Keep the handwritten `try_new`, `credit`, and `debit` domain operations. Consider a minimal `Getter` only for rule-free read-only fields, then add regression tests proving that invalid states remain unconstructible.

## Produce safe debug output

User request:

> Automatically derive Debug for this connection configuration, but never log its password or access token.

Use `CustomDebug` and add `#[debug(skip)]` to both fields. Test that final output contains neither the field names nor actual secrets. Do not also derive standard `Debug`, and do not use `DisplayDebug` to turn internal Debug output into user-facing error text.

## Correct an outdated tutorial

User request:

> Apply this tutorial that uses `#[derive(Lombok, Debug, Clone)]` and `lombok-macros = "latest"`.

Do not copy the snippet verbatim. Inspect the locked crate and explain that `2.0.32` has no `Lombok` derive and that `Debug` and `Clone` come from Rust itself. Add the dependency with `cargo add lombok-macros` or an explicit reviewed version, then choose `Getter` and `Setter` for the requested accessors. Use `Data` only if mutable getters are intentionally part of the contract. Compile the migrated example and test the exact generated method signatures.
