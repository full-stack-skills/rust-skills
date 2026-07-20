# Adoption, Migration, and Review Checklist

## Decide before adopting

1. Is the type only a data carrier where every constructible and mutable state is valid?
2. Do existing methods perform validation, normalization, logging, event emission, cache invalidation, or security checks?
3. Do callers require a reference, an owned value, or a mutable reference? Is cloning acceptable?
4. Which methods must be public? Can they remain private or `pub(crate)`?
5. Does the type contain credentials, personal data, or business secrets?
6. Can the project's declared MSRV compile the locked version?
7. Do contract tests and real callers exercise the generated API?

Keep a method handwritten whenever a macro cannot express one of its invariants or side effects. The objective is to remove mechanical code, not to maximize derive usage.

## Migrate handwritten methods

Replace methods incrementally:

1. Record the old signature, visibility, ownership, panic or error behavior, and side effects.
2. Add caller-level tests for the old contract.
3. Replace one capability at a time, such as Getter before considering Setter.
4. Compile every supported target and feature combination, then run downstream or integration tests.
5. Run `cargo tree -i lombok-macros` to confirm the selected version and source.
6. Delete the handwritten method only after proving behavioral equivalence.

Do not expose an unchecked generic setter merely to remove a five-line validating method. Domain actions such as `activate`, `change_email`, or `reserve` communicate rules more clearly than `set_status`.

## Review the change

### API surface

- Has `Data` generated setters or mutable getters that no caller needs?
- Is visibility minimal? Has a public library evaluated generated methods as semver API?
- Did a getter change unexpectedly between borrowing and cloning or copying?
- Is the `New` parameter order clear and stable? Will adding a field break callers?

### Correctness

- Does a default `Option` or `Result` getter, or `type(deref)`, introduce a panic?
- Is a `new(skip)` default a real business default instead of a silently fabricated state?
- Can a setter or mutable getter bypass range, state-machine, or cross-field invariants?
- Does an `Into` or `AsRef` setter convert into the actual field type?

### Security and observability

- Does Debug or Display contain credentials, tokens, cookies, personal data, or internal errors?
- Does a negative `#[debug(skip)]` test confirm that both the field name and value are absent?
- Is Debug-backed Display being used as user, protocol, or persistence output?

### Dependency maintenance

- Does `Cargo.lock` match the docs.rs version used during implementation?
- Because the crate declares no MSRV, has the project run it on the minimum supported toolchain?
- Does an upgrade recompile generated-API tests instead of relying only on a changelog?
- Does the dependency pass project policy such as `cargo deny check`?

## Recommended test shape

```rust
#[test]
fn generated_api_keeps_the_contract() {
    let mut value = Config::new("worker".to_owned(), 4);
    assert_eq!(value.get_name(), "worker");
    assert_eq!(value.get_workers(), 4);

    value.set_name("batch").set_workers(8);
    assert_eq!(value.get_name(), "batch");
    assert_eq!(value.get_workers(), 8);
}

#[test]
fn debug_redacts_secret() {
    let output = format!("{:?}", secret_value());
    assert!(!output.contains("token"));
    assert!(!output.contains("actual-secret"));
}
```

For a public library, also use a separate downstream crate or compile test so that access to private fields in unit tests does not hide a visibility regression.
