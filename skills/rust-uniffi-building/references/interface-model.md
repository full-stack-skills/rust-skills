# UniFFI Interface Model

Read this reference when choosing UDL versus procedural macros or designing exported types. Verify syntax against the locked UniFFI release and the [official type-model documentation](https://mozilla.github.io/uniffi-rs/latest/types/namespace.html).

## Strategy Decision

### Procedural macros

Prefer macros when Rust should remain the only interface source and all required constructs are supported. Typical entry points include:

- `#[uniffi::export]` for functions, impl blocks, and traits;
- `#[derive(uniffi::Record)]` for value records;
- `#[derive(uniffi::Enum)]` for enums;
- `#[derive(uniffi::Error)]` for exported error types;
- `#[derive(uniffi::Object)]` for reference-counted objects;
- `uniffi::custom_type!` or `uniffi::custom_newtype!` for conversions;
- `uniffi::setup_scaffolding!()` once in a macro-only crate.

Advantages:

- avoids duplicating signatures in Rust and UDL;
- preserves Rust-side navigation and conditional compilation;
- makes source changes and exported metadata reviewable together.

Costs:

- feature availability and syntax can change by release;
- target-language behavior still requires the general type-model docs;
- macro diagnostics may hide the generated ABI layer.

### UDL

Prefer UDL when an existing schema is authoritative, a language-neutral review surface is required, or the selected UniFFI release does not support a construct through macros.

Treat UDL as a public schema:

- namespace and crate naming must remain stable;
- every referenced type must be declared or imported;
- overload-like designs must use explicit exported names;
- defaults, optional values, errors, and docstrings belong to the compatibility contract;
- generated scaffolding must be rebuilt whenever the UDL changes.

### Mixed mode

Use mixed mode only for migration or a concrete feature gap. The UDL must remain valid on its own, and types referenced from UDL must be declared there. Keep macro-only additions in separate impl blocks and make the Rust crate name match the UDL namespace.

## Type Selection

| Rust/API intent | UniFFI shape | Review questions |
|---|---|---|
| Immutable data transfer | Record | Are all fields stable, bounded, and meaningful in each target language? |
| Closed alternatives | Enum | Is adding a variant compatible with every generated language? |
| Expected failure | Error enum | Are variants actionable and free of sensitive internal details? |
| Identity/shared state | Object | Who owns references, which methods mutate state, and is access thread-safe? |
| Behavior supplied by foreign code | Callback interface/trait | Which thread calls it, can it re-enter Rust, and how is it unregistered? |
| Domain wrapper | Custom type/newtype | Is conversion total, validated, and versioned? |
| Type from another crate | External/remote type | Which crate owns metadata and configuration discovery? |
| Large binary payload | Byte buffer | What are size limits, copy costs, and zero-length semantics? |

## Built-In Values

Confirm the selected release's supported scalar widths and host mappings. In general:

- use explicit integer widths rather than platform-sized integers;
- distinguish optional values from empty strings, zero, or empty collections;
- bound strings, sequences, maps, and byte buffers before allocation;
- do not expose borrowed references as if host code could retain them;
- define timestamp and duration semantics explicitly, including range and precision;
- avoid nested or recursive structures that are expensive or unsupported in target generators.

## Records and Enums

Records cross the boundary by value. Avoid putting mutable identity, file handles, connections, or unbounded graphs into records.

For enums:

- decide whether foreign callers must handle unknown future variants;
- avoid renaming variants without an explicit migration;
- separate data-bearing variants from error semantics when target-language ergonomics suffer;
- test every variant in every generated language, not just Rust pattern matches.

## Objects

Objects represent Rust-owned identity exposed through a foreign reference:

- construct them through exported constructors;
- return the ownership form required by the selected version, commonly `Arc<Self>`;
- make interior mutation and synchronization explicit;
- avoid holding foreign callbacks while invoking user code under a lock;
- test destruction, repeated calls after cancellation, concurrent calls, and callback cycles;
- do not assume the foreign garbage collector promptly releases Rust resources.

## Errors

Use exported errors for expected domain and input failures. Keep panics for defects and prevent them from becoming the routine error channel.

Define:

- stable variants or codes;
- target-language message policy;
- whether fields contain safe user-facing data;
- conversion from private internal errors;
- compatibility behavior when adding or removing variants.

Do not expose file paths, SQL, credentials, internal URLs, backtraces, or implementation types in generated exceptions.

## Custom, External, and Remote Types

Use custom conversion only when a supported wire shape can faithfully represent the domain type:

- validate during lifting from foreign values;
- make lowering deterministic;
- preserve range, precision, normalization, and error behavior;
- test invalid and boundary values;
- document which crate owns the conversion metadata.

External and remote types require dependency and configuration discovery to agree. Verify crate names, UDL imports where relevant, Cargo features, and `[crate-roots]` or cargo metadata.

## Naming and Exclusion

Treat generated names as public APIs:

- inspect Kotlin, Swift, Python, and Ruby spellings after rename rules;
- avoid collisions introduced by target-language casing;
- use explicit exclusion for Rust APIs that should not cross the boundary;
- keep docstrings free of Rust-only assumptions;
- test reserved words and acronym normalization in every claimed language.

## Review Checklist

- Is the interface strategy singular and justified?
- Does every exported type have a supported, bounded representation?
- Are identity and value semantics separated?
- Are errors explicit and safe?
- Can foreign code retain, call, or release each object safely?
- Are custom conversions total and tested?
- Do naming and evolution rules work in every target language?

## Official Sources

- [Namespace](https://mozilla.github.io/uniffi-rs/latest/types/namespace.html)
- [Built-in types](https://mozilla.github.io/uniffi-rs/latest/types/builtin_types.html)
- [Enumerations](https://mozilla.github.io/uniffi-rs/latest/types/enumerations.html)
- [Records](https://mozilla.github.io/uniffi-rs/latest/types/records.html)
- [Interfaces, Objects, and Traits](https://mozilla.github.io/uniffi-rs/latest/types/interfaces.html)
- [Custom types](https://mozilla.github.io/uniffi-rs/latest/types/custom_types.html)
- [Remote and External types](https://mozilla.github.io/uniffi-rs/latest/types/remote_ext_types.html)
- [Procedural macros](https://mozilla.github.io/uniffi-rs/latest/proc_macro/index.html)
