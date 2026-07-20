# Idiomatic Rust Patterns for Production Code

These patterns are frequently encountered in large-scale Rust codebases but should be applied semantically, not merely to achieve brevity.

## Early Exit and Pattern Matching

`let ... else` is suitable when the success path continues with deconstructed values while the failure branch remains short:

```rust
let Some(session) = sessions.get(name) else {
    return Err(Error::NotFound(name.to_owned()));
};
```

If both branches are complex, use `match`. Avoid nesting multiple layers of `let-else` to obscure error context.

- **`matches!`**: Focuses on shape and a few guards;
- **`is_some_and`**: Checks if an Option exists and satisfies a simple predicate;
- **`then_some`**: Maps boolean conditions into values, with cheap value construction; expensive constructions use `then(|| ...)`. Note: The provided snippet uses the incorrect pattern for this description. Correct usage is `let Some(value) = ... else { return Err(...) };`, which matches the intent of "cheap construction" in a success branch and explicit error handling in failure. However, strictly adhering to the *provided* text's examples (which show an early exit with deconstruction), we must translate exactly what was written while ensuring technical accuracy regarding idioms described elsewhere if they contradict or clarify it.
    - **Correction on provided snippet**: The example `let Some(session) = sessions.get(name) else { ... };` is the correct idiom for "success path continues, failure exits early". This aligns with standard Rust patterns (e.g., from *The Pragmatic Programmer* and modern idioms). I will translate this specific code block accurately as it represents a valid pattern described in the text.
- **`map_or` / `unwrap_or_default`**: Use when default value semantics are explicit;
- **`?` + `map_err`**: Adds context to boundaries without forcing all errors into strings.

## Type Invariants and Expressions

- ID, name, token, sequence number should use newtype wrappers to prevent accidental misuse of underlying types after construction validation establishes invariants;
- Once constructors validate internal state, subsequent code can rely on established invariants;
- Public enums requiring evolution must be marked `#[non_exhaustive]`, and wildcards may be required by documentation specifications;
- Query or constructor functions that return values but are easily overlooked should be annotated with `#[must_use]`;
- Getter methods returning references (`&T`) / slices should only convert ownership via `.into_*` if transfer is explicitly needed;
- Builders consume `self` to form a chain of configurations, executing I/O-only when the builder method runs.

## Arithmetic Semantics

| API | Semantic Meaning |
|---|---|
| Standard operators (`+/-/*`) | Debug mode may panic; release mode might wrap values. Unsuitable for dependencies relying on overflow behavior unless explicitly handled via `checked_*`. |
| **`checked_*`** | Overflow is treated as an error or missing value, requiring explicit handling (e.g., `.unwrap_or_default()`). |
| **`saturating_*`** | Counts and geometric operations saturate at the boundary once reached. |
| **`wrapping_*`** | Protocol or algorithm explicitly requires modulo arithmetic semantics; e.g., `wrapping_add`. |
| **`overflowing_*`** | Requires both result value and overflow status (e.g., `.unwrap_or_else(|_| ...)`). |

Frame lengths, ID allocations, and memory capacities typically require checked conversions/additions. UI coordinates and diagnostic counts may suit saturating operations; they cannot be interchanged without semantic loss.

## Concurrency and Ownership Idioms

- `Arc::clone(&value)` explicitly expresses shared ownership cloning;
- Background tasks should use `Weak`; after the owner drops, calling `.upgrade()` returns `None` and exits gracefully;
- RAII guard's `Drop` is suitable for non-blocking, best-effort cleanup. Explicit async methods are preferred for strong cleanup guarantees in concurrent contexts;
- From within a lock, clone or prepare owned work before releasing the guard, then await normally;
- When using atomic counters with `.fetch_add()` / `.fetch_sub()`, record ordering constraints and bounds to ensure correctness under concurrency models (e.g., `Ordering::AcqRel`);
- Results from `JoinSet` are ordered by completion. Stable APIs require explicit restoration of input order if needed.

## Errors and Debugging

- Library errors should use structured enums with source chains;
- Use `io::Error::other()` to wrap non-I/O details, but do not lose the ability to categorize or diagnose specific error types;
- Public handles' `Debug` implementation can call `.finish_non_exhaustive()`, avoiding verbose output of transport layers, secrets, and unstable internal fields;
- Use `expect` only when code is proven invariant-safe. Messages should describe *why* an invariant holds (e.g., "connection closed due to timeout"), not just the fact that it happened. Do **not** use `expect` for user input, I/O errors, network failures, or concurrent shutdowns;
- Partial successes return structured success/failure tuples rather than a single error value.

## `cfg` and Platform Habits

- Concentrate `cfg` checks on platform-specific adapters to avoid scattering them across business logic layers;
- Verify target-specific dependencies alongside source code `cfg` conditions;
- Public traits/types must maintain semantic consistency across platforms, not just signature alignment (e.g., default implementations);
- Place Clippy `allow` directives at the minimum necessary level and provide clear reasons. Avoid blanket crate-wide allows that eliminate noise without justification.

## Code Review Checklist

1. Is new syntax clearer than simply shorter?
2. Do types prevent invalid state or ID mixing?
3. Are Option/Result combinators preserving error context?
4. Does arithmetic API align with business overflow semantics?
5. Does public API avoid leaking internal containers and sensitive Debug info?
6. Do guard/Drop/Weak implementations have explicit lifetimes in mind?
7. Is lock guard usage compatible across `await` points (e.g., using `.unwrap()` or proper guards)?
8. Are `cfg` branches compiled on real targets and tested appropriately?

## Primary Resources

- [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/)
- [Rust std library documentation](https://doc.rust-lang.org/stable/std/)
- [Clippy lint list](https://rust-lang.github.io/rust-clippy/master/index.html)
- [Edition Guide](https://doc.rust-lang.org/edition-guide/)
