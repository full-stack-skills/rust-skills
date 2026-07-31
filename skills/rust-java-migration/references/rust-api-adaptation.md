# Rust API and JavaBean Property Adaptation

Use an idiomatic Rust API for Rust callers while preserving JavaBean or dynamic
property semantics at the compatibility boundary.

## Normative source and scope

Use the locally installed `rust-api-design` skill as the primary post-migration
API authority, especially Rust API Guidelines `C-GETTER`, `C-CONV`,
`C-CONVERT`, `C-ITER`, and `C-STRUCT-FIELD`. This reference applies those rules
to Java-source parity work: preserve the Java behavior, but do not make JavaBean
spelling the Rust public API.

This migration skill keeps `set_name(value)` as its explicit house convention
for controlled mutation. Do not add a second fluent setter merely to satisfy a
different style preference; choose one project convention and apply it
consistently.

## Rust API conventions

| Java shape | Rust starting point |
|---|---|
| trivial public bean field | public field only when invariants and API evolution permit |
| `getName()` | `name()` returning a borrow where possible |
| `setName(value)` | `set_name(value)` with the original validation and side effects |
| mutable field access | `name_mut()` only when it cannot bypass invariants |
| ownership extraction | `into_name()` or `into_inner()` |
| `isEnabled()` / boolean getter | `is_enabled()`, `has_value()`, or another semantic predicate |
| builder setter | chainable `UserBuilder::new().name("Tom").build()` |

Do not generate `get_name()` merely for name parity. `get_*` is allowed only
for a genuine lookup operation, such as a map-like `get(key)` that may not find
an entry. Preserve visibility, null/default behavior, validation, exceptions,
caching, lazy computation, synchronization, observability, and other side
effects.

Treat public fields as a stable API commitment. Keep a field private whenever
future validation, synchronization, lazy state, or field evolution is likely;
do not offer `name_mut()` when mutable access would bypass the same invariant.

## Conversion and collection rules

Do not turn a Java conversion helper into an arbitrary accessor name. Use the
following Rust contract and keep Java error behavior where it remains public:

| Need | Rust form |
|---|---|
| cheap borrowed inspection | `as_name()` or `AsRef<T>` |
| new value from `&self` | `to_name()` |
| consume the value | `into_name()` / `into_inner()` |
| cheap lossless conversion | `impl From<T>` (which provides `Into`) |
| cheap fallible conversion | `impl TryFrom<T>` / `TryInto<T>` |
| collection traversal | `iter()`, `iter_mut()`, and `IntoIterator` where appropriate |

Do not implement `Deref` or `DerefMut` merely to emulate Java inheritance or
delegate a wrapper's API. Prefer explicit methods, traits, or composition.

## Mapping form versus completion state

Record API shape separately from evidence status:

| Mapping form | Meaning |
|---|---|
| `DIRECT` | The Java responsibility maps directly to an idiomatic Rust API without a compatibility adapter |
| `ADAPTED` | Rust uses an idiomatic API while an adapter preserves a Java-facing, script-facing, wire, reflection, or framework contract |

`ADAPTED` never means complete. A row still needs a factual state such as
`MISSING`, `PARTIAL`, `UNVERIFIED`, or `IMPLEMENTED`.

## QLExpress-style property compatibility

Keep two layers:

```text
Java getName()/setName()
    -> semantic contract
Rust name()/set_name()
    -> NativeRegistry/member resolver
script user.name / user.name = "Tom"
```

The Rust type should not expose `get_name()` just so the script resolver can
find it. Register the script property explicitly:

```rust
registry.register_property(
    "name",
    |user: &User| Value::from(user.name()),
    |user: &mut User, value| user.set_name(value.try_into()?),
)?;
```

Treat `NativeRegistry` as the QLExpress example; use the target project's actual
registry/member-resolver abstraction elsewhere.

Preserve and test:

- Java resolution precedence among a field, `getXxx()`, boolean `isXxx()`, and
  `setXxx()`;
- read-only, write-only, aliases, inheritance/trait exposure, and visibility;
- getter/setter validation, side effects, errors, synchronization, and caching;
- script reads such as `user.name` and writes such as
  `user.name = "Tom"`;
- Rust-native calls such as `user.name()` and `user.set_name(value)`;
- identical error categories and observable mutation for both access paths.

Record the Java accessor signatures, Rust API, compatibility registration,
mapping form `ADAPTED`, factual completion state, and dual-layer tests in the
four migration documents.
