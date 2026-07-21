# Rust API Guidelines Review Checklist

A reviewer-facing checklist that turns the [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/) into concrete, diff-shaped signals. Use it during the review step after you have already traced behavior through boundaries (Workflow step 3) and before you write performance findings (Workflow step 4). The four chapters below correspond to the four most common sources of API-level regressions in real Rust PRs: Dependability, Type safety, Interoperability, and Future-proofing.

Each rule lists:

- **Rule** — the canonical `C-*` id from the API Guidelines.
- **Look for** — text patterns, AST shapes, or visibility cues that appear in diffs.
- **Severity** — `Major` (changes behavior, breaks soundness, or leaks panics onto callers), `Minor` (clear API hygiene issue with low blast radius), or `Nit` (style or documentation polish). Map these onto the review finding's severity field.
- **Suggested comment** — a starting point. Always tailor it to the actual call site and attach the tightest file/line range.

Only raise a finding when the pattern is on the public API surface (anything reachable from outside the crate, including via trait impls, macros, or serialized output), or when the change plausibly affects a caller. Internal helpers, `#[cfg(test)]` modules, and benchmarks are out of scope for these rules unless they hide a bug.

## How to use this checklist

1. Open the diff and the surrounding file. Determine visibility of every touched item.
2. For each chapter below, scan the diff for the "Look for" patterns.
3. For every match, confirm the failure path with a concrete caller (real or hypothetical) before writing it up. Do not flag patterns you cannot defend.
4. Pick the suggested comment that matches the situation, edit it to reference the actual symbol, and attach severity + location.
5. If the design decision is larger than a comment (e.g. re-deriving traits across the crate, rethinking an error model, sealing a trait family), route the request to `rust-api-design` instead of asking for an inline rewrite.

## Dependability

Public APIs must not panic on inputs a reasonable caller will pass, and unsafe type punning must be justified.

| Rule | Look for | Severity | Suggested comment |
|------|---------|---------|-------------------|
| C-PANIC | `panic!()`, `.unwrap()`, `.expect()`, `unreachable!()`, `unimplemented!()`, `todo!()`, slice/array indexing `x[i]`, `assert!()`/`assert_eq!()` inside `pub fn`/`pub method` bodies that accept caller-supplied input | Major | "This panics on caller input. Return `Result<T, E>` (or guard with a checked accessor) so callers can react; see C-PANIC." |
| C-UNWRAP | `something.parse().unwrap()`, `serde_json::from_str(s).unwrap()`, `lock().unwrap()`, `recv().unwrap()` in non-test code paths reachable from a public entry point | Major | "Use `?` or surface a typed error; `.unwrap()` here turns a recoverable failure into a process abort." |
| C-TRANSMUTE | `unsafe { std::mem::transmute(_) }`, `unsafe { std::mem::transmute_copy(_) }` used for type punning between same-size types | Major | "Avoid `transmute` for type punning. Prefer `from_ne_bytes`/`from_le_bytes`, a `From`/`TryFrom` impl, or an `as` cast. If the transmute is sound, document the layout invariant it relies on." |
| C-EXPECT-DEBUG | `.expect("...")` whose message echoes a `Debug` of user data | Minor | "Avoid interpolating untrusted data into panic messages; it can leak through logs and `Display` chains." |

### Worked examples (Dependability)

```rust
// BEFORE — C-PANIC, Major
pub fn decode(buf: &[u8]) -> Frame {
    let len = u32::from_be_bytes([buf[0], buf[1], buf[2], buf[3]]);
    let body = &buf[4..4 + len as usize]; // panics if buf is short or len overflows
    Frame::parse(body).unwrap()
}

// AFTER
pub fn decode(buf: &[u8]) -> Result<Frame, DecodeError> {
    let (head, rest) = buf.split_first_chunk::<4>()
        .ok_or(DecodeError::ShortHeader)?;
    let len = u32::from_be_bytes(*head) as usize;
    let body = rest.get(..len).ok_or(DecodeError::ShortBody)?;
    Frame::parse(body)
}
```

## Type safety

Prefer types that make invalid states unrepresentable over `bool` parameters and bare primitive IDs.

| Rule | Look for | Severity | Suggested comment |
|------|---------|---------|-------------------|
| C-BOOL | `pub fn` with two or more `bool` parameters, or a single `bool` whose name is not self-describing at the call site (`set_flag(true, false)`, `render(win, true, false, false)`) | Minor | "Multiple `bool` params are unreadable at call sites. Introduce enums (`Mode::Visible`, `Mode::Hidden`) or a builder." |
| C-NEWTYPE | `pub fn` that takes several bare integers (`u64`, `u32`, `AccountId`) where two arguments are interchangeable by type, e.g. `transfer(amount: u64, from: u64, to: u64)` | Minor | "Wrap these in newtypes (`Amount`, `AccountId`) to prevent argument-order and unit bugs." |
| C-VALIDATE-ARGS | `pub fn` that accepts a primitive and immediately `debug_assert!`s an invariant | Minor | "Encode the invariant in the type (a constructor returning `Result<NewType, _>`) so callers cannot bypass it." |

### Worked example (Type safety)

```rust
// BEFORE — C-BOOL, Minor
pub fn render(widget: &Widget, show_border: bool, active: bool, focused: bool);

// render(w, true, false, true) — what does the third bool mean?

// AFTER
pub enum Border { Hidden, Visible }
pub enum Focus { Inactive, Active, Focused }
pub fn render(widget: &Widget, border: Border, focus: Focus);
```

## Interoperability

Public types should play nicely with the rest of the ecosystem: derivable common traits, idiomatic conversions, and no `Deref` abuse.

| Rule | Look for | Severity | Suggested comment |
|------|---------|---------|-------------------|
| C-COMMON-TRAITS | `pub struct`/`pub enum` without `#[derive(Debug)]`; public error types without `Clone`/`PartialEq`/`Eq` where users need to compare or retry | Minor | "Add `#[derive(Debug, Clone, PartialEq)]` (and `Eq` if partial equality is total) so callers can log, retry, and assert on this type." |
| C-DEBUG | `impl Debug for X` that prints `***` or redacts entire fields without a `non_exhaustive` note | Minor | "If `Debug` must redact, document it in the type doc so users do not rely on the shape for logging." |
| C-CONVERT | `impl From<T> for U` where the conversion can fail silently, or `impl Deref`/`impl DerefMut` on a non-smart-pointer type to reuse methods | Major | "`Deref` is for smart pointers. Using it for reuse makes the type implicitly coercible and hides method resolution; prefer composition, an `as_inner()` accessor, or explicit forwarding methods." |
| C-ITER | `pub fn` returning `Vec<T>` when the caller only iterates, or `impl Iterator` without `DoubleEndedIterator`/`ExactSizeIterator` where it is cheap to provide | Minor | "Return `impl Iterator<Item = T>` (and implement `ExactSizeIterator`/`DoubleEndedIterator` where the source supports it) so callers avoid the intermediate allocation." |
| C-SERDE | `pub` types with hand-rolled `Serialize`/`Deserialize` whose wire format differs from the derive output | Minor | "Document the wire shape and version compatibility; derive-based round-trips should produce identical bytes." |

### Worked example (Interoperability)

```rust
// BEFORE — C-CONVERT, Major
pub struct HttpClient { inner: reqwest::Client, base: Url }
impl Deref for HttpClient {
    type Target = reqwest::Client;
    fn deref(&self) -> &Self::Target { &self.inner }
}

// AFTER — explicit accessor
impl HttpClient {
    pub fn inner(&self) -> &reqwest::Client { &self.inner }
    pub fn base(&self) -> &Url { &self.base }
}
```

## Future-proofing

Public traits and enums that are intended to grow must give themselves room to do so without a semver break.

| Rule | Look for | Severity | Suggested comment |
|------|---------|---------|-------------------|
| C-SEALED | A `pub trait` that adds new methods, has no default impls, and is documented or commented as "extension point" or "users may implement", with no seal (private/`#[doc(hidden)]` supertrait) | Minor | "Seal this trait (e.g. via a private supertrait or `#[doc(hidden)] mod private`) so adding a method is non-breaking. If users are expected to implement it, document the contract and consider a `default` method instead." |
| C-NON-EXHAUSTIVE | `pub enum` (especially error types and configuration enums) in a library crate without `#[non_exhaustive]` | Minor | "Add `#[non_exhaustive]` so adding a variant is not a breaking change and downstream `_ =>` arms compile." |
| C-STRUCT-UPDATE | `pub struct` with many public fields that callers construct via `Struct { ..Default::default() }` | Nit | "If callers rely on struct-update syntax, document the field set as part of the API or move construction behind a builder." |
| C-PRIVATE-IMPL | `pub trait` where the only `impl`s in the crate are private or `#[cfg(test)]` | Nit | "If this trait exists only for internal abstraction, mark it `pub(crate)` to avoid an accidental public API commitment." |

### Worked example (Future-proofing)

```rust
// BEFORE — C-SEALED, Minor
pub trait Extension {
    fn name(&self) -> &str;
    fn init(&mut self, ctx: &Context);
    // Adding `fn shutdown(&mut self)` here is a breaking change
    // because every downstream impl must add the method.
}

// AFTER — sealed
mod private {
    pub trait Sealed {}
}

pub trait Extension: private::Sealed {
    fn name(&self) -> &str;
    fn init(&mut self, ctx: &Context);
    // New default methods can be added freely.
}
```

## Severity calibration

When in doubt about severity:

- Start at `Major` when any of these hold:
  - the pattern can panic, abort, deadlock, or return a wrong result on reachable input;
  - it is `unsafe` and unsoundness is plausible;
  - it changes serialization, ABI, MSRV, or a public signature in a semver-breaking way.
- Use `Minor` when the change compiles and runs correctly but creates a clear ergonomic, ergonomic, or maintenance burden (unreadable call sites, missing `Debug`, hidden `Deref` chains).
- Reserve `Nit` for documentation gaps and style preferences. Never escalate a Nit to block a PR.

## False positives (when not to flag)

These patterns look like violations but are usually fine. Verify before commenting.

- `.unwrap()` / `.expect()` inside `#[cfg(test)]` modules, `#[tokio::test]` bodies, and `benches/` are the idiomatic way to fail tests. Do not flag them.
- `.unwrap()` on values the type system guarantees are infallible at that call site (e.g. `Regex::new(literal_constant).unwrap()`) is acceptable. Confirm the guarantee is structural, not just "I think so".
- `panic!()` in `From<...>::from`, `Deref`, `Drop`, `PartialOrd`, `Hash`, and other trait bodies that the standard library documents as infallible is acceptable when the precondition is documented.
- `transmute` in FFI shims, `repr(transparent)` newtype wrappers, and `bytemuck`-style layout conversions is acceptable if the layout invariant is documented and a `SAFETY:` comment is present.
- `bool` parameters in binary operators (`BitAnd`, `BitOr`), builder terminators (`.build(true)`), or single-argument setters named `enabled`/`visible` are usually readable.
- Sealed supertraits that look unused but are imported from another crate: check whether the crate exports the seal intentionally before asking for removal.

## Routing

| When the review surfaces... | Route to |
|-----------------------------|----------|
| A request to redesign trait families, error taxonomies, or builder patterns | `rust-api-design` |
| An `unsafe` soundness question beyond layout/redaction | `rust-unsafe-ffi` |
| A lock-ordering, cancellation, or executor-blocking concern | `rust-concurrency` |
| A formatting, naming, or Clippy-policy question | `rust-style-clippy` |
| A missing-test or test-design question | `rust-testing` |

Always include the rule id (e.g. `C-PANIC`), the diff hunk, and the failing caller path when routing, so the downstream skill does not need to re-derive the context.

## Reference

- Source: <https://rust-lang.github.io/api-guidelines/>
- Rule id conventions follow the upstream `C-*` naming.
- This checklist is a reviewer aid, not an automated lint. Pair it with `cargo clippy --workspace --all-targets --all-features -- -D warnings` for the mechanical subset.
