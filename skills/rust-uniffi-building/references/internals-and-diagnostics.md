# UniFFI Internals and Diagnostics

Read this reference only when public configuration and type-model checks do not explain metadata, conversion, async, symbol, or runtime failures.

## Mental Model

UniFFI turns a declared component interface into:

1. Rust scaffolding and exported low-level functions;
2. metadata describing the component interface;
3. a binding intermediate representation;
4. language-specific rendered sources;
5. runtime conversion code that lifts foreign values into Rust and lowers Rust values back.

Debug the earliest incorrect layer rather than patching generated target-language code.

## Lifting, Lowering, and Serialization

- **Lift** converts a foreign representation into a Rust value.
- **Lower** converts a Rust value into the foreign representation.
- Compound values may be serialized through a Rust buffer according to UniFFI's internal contract.
- Custom types delegate through an underlying supported representation.

If a value corrupts or fails to decode:

1. confirm runtime and generated binding versions match;
2. reduce to the smallest failing type;
3. inspect field order, variant, optional/default, range, and custom conversion;
4. test the same value in every affected language;
5. compare debug and release behavior;
6. inspect FFI tracing only with sensitive-data controls.

Do not create an independent serializer that merely resembles UniFFI's internal format.

Official sources:

- [Lifting, Lowering, and Serialization](https://mozilla.github.io/uniffi-rs/latest/internals/lifting_and_lowering.html)
- [Ffi converter traits](https://mozilla.github.io/uniffi-rs/latest/internals/ffi_converter_traits.html)

## Call Directions

Foreign-to-Rust calls generally:

- lower arguments in generated foreign code;
- call exported Rust scaffolding;
- lift arguments into Rust;
- invoke the Rust function/method;
- lower return/error values;
- lift them in the foreign language.

Rust-to-foreign callbacks reverse that flow and add foreign object handles, callback registration, thread transitions, and exception mapping.

Use this direction model to locate:

- conversion failures before Rust logic runs;
- Rust panics or exported errors;
- callback handle/lifetime failures;
- foreign exceptions returning to Rust;
- leaks from incomplete buffer/handle cleanup.

Official sources:

- [Foreign to Rust calls](https://mozilla.github.io/uniffi-rs/latest/internals/rust_calls.html)
- [Rust to Foreign calls](https://mozilla.github.io/uniffi-rs/latest/internals/foreign_calls.html)

## Object References

Generated bindings coordinate foreign wrapper references with Rust object handles. Problems usually appear as:

- early release/use-after-close;
- reference cycles and leaks;
- duplicate wrappers with surprising identity;
- concurrent calls into unsynchronized state;
- finalizer work during runtime shutdown.

Instrument construction, clone/handle transfer, explicit close, callback registration, and drop with non-sensitive stable identifiers. Do not log raw pointer values as durable identities or expose them to consumers.

Official source: [Managing Object References](https://mozilla.github.io/uniffi-rs/latest/internals/object_references.html).

## Metadata, IR, and Rendering

If generation omits or misnames an item:

- confirm the item is compiled under the active features and `cfg`;
- confirm scaffolding/metadata is present in the exact final library;
- verify crate roots and component discovery;
- inspect the binding IR before blaming the renderer;
- compare language renderer behavior and config;
- avoid hand-editing generated sources as the fix.

Official sources:

- [Rendering Foreign Bindings](https://mozilla.github.io/uniffi-rs/latest/internals/rendering_foreign_bindings.html)
- [The UniFFI Bindings IR](https://mozilla.github.io/uniffi-rs/latest/internals/bindings_ir.html)
- [Bindings IR Pipeline](https://mozilla.github.io/uniffi-rs/latest/internals/bindings_ir_pipeline.html)

## Async Diagnostics

Async bridging introduces:

- a Rust future handle;
- poll/continuation plumbing;
- foreign executor integration;
- completion and cancellation state;
- return/error lifting.

For hangs:

1. verify the required runtime feature;
2. confirm the future is polled;
3. trace completion exactly once;
4. test cancellation at several poll points;
5. inspect detached child work;
6. verify foreign executor/task shutdown;
7. rule out locks held across `.await`.

Read the [async overview](https://mozilla.github.io/uniffi-rs/latest/internals/async-overview.html) and [async FFI details](https://mozilla.github.io/uniffi-rs/latest/internals/async-ffi.html) for the selected release.

## Release-Only and Loader Failures

When debug works but release fails, compare:

- crate features and target triples;
- `crate-type` and linker arguments;
- LTO, dead stripping, and symbol visibility;
- generated library filename/module map;
- signing, embedding, and runtime search paths;
- stale generated code or cached host packages;
- architecture slices and minimum OS versions.

Use native inspection tools appropriate to the platform, such as `nm`, `objdump`, `readelf`, `otool`, `lipo`, `file`, or platform package inspectors. Record commands and artifact hashes.

## Escalation Boundary

Escalate to `rust-unsafe-ffi` only when investigation reaches a hand-written ABI, raw pointer, allocator, unwinding, or manual layout invariant. UniFFI-generated unsafe internals should normally be diagnosed through locked upstream behavior rather than copied into application code.
