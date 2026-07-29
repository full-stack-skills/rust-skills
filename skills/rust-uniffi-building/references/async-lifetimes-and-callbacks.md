# Async, Lifetimes, and Callbacks

Read this reference before exporting async functions, objects with shared state, callback interfaces, or foreign traits.

## Ownership Across the Boundary

Foreign languages do not share Rust's lexical lifetime model. UniFFI converts values and tracks object handles, but the API still needs an explicit ownership contract.

For every exported value, decide:

- copied value versus Rust-owned identity;
- whether foreign code can retain it after the call;
- who releases it and whether release timing matters;
- whether calls may arrive concurrently;
- whether a callback can re-enter the same Rust object;
- what happens after cancellation or shutdown.

Do not expose borrowed Rust references as durable foreign objects. Prefer value records, owned strings/bytes, or reference-counted objects supported by UniFFI.

## Object Lifetimes

Generated bindings commonly wrap Rust objects with foreign runtime ownership:

- Rust object construction should return the ownership form required by the locked release, often `Arc<Self>`;
- foreign garbage collection or ARC controls wrapper release timing, not deterministic Rust scope exit;
- resources needing prompt close should expose an idempotent explicit shutdown/close method in addition to drop cleanup;
- methods after close should return a stable error;
- callback cycles can keep both sides alive;
- finalizers must not perform fragile blocking work.

Test:

- duplicate foreign references to one object;
- release in different orders;
- concurrent method calls;
- explicit close followed by drop;
- callback registration/unregistration;
- cycles and long-lived host objects.

## Threading and Reentrancy

Document for each export:

- permitted calling threads;
- internal synchronization;
- whether callbacks run inline, on a Rust worker, or through a foreign executor;
- whether foreign callbacks may call back into Rust;
- lock ordering and shutdown behavior.

Never invoke arbitrary foreign code while holding a Rust mutex unless the reentrancy and latency contract has been proven. Copy callback handles or state under the lock, release it, and then invoke when possible.

## Async Exports

UniFFI async support lowers a Rust future into a foreign-language async abstraction. Exact runtime features and generated behavior vary by release and language.

Before implementing:

- inspect whether the selected version requires a Tokio feature or runtime annotation;
- decide who owns the runtime;
- define cancellation semantics;
- define whether cancellation drops the future or only stops waiting;
- bound work spawned outside the returned future;
- ensure completion occurs exactly once;
- preserve exported error mapping.

Avoid detached work that outlives a cancelled foreign task without supervision. If an operation is not safely cancellable, document that cancellation only abandons the result and provide an explicit operation handle where needed.

Test:

- immediate and delayed success;
- each error variant;
- cancellation before poll, during I/O, and near completion;
- foreign task/Coroutine cancellation;
- runtime shutdown with in-flight calls;
- repeated cancellation and late callback behavior;
- no leaked Rust tasks or object handles.

Official sources:

- [Async/Future support](https://mozilla.github.io/uniffi-rs/latest/futures.html)
- [UniFFI Async Overview](https://mozilla.github.io/uniffi-rs/latest/internals/async-overview.html)
- [UniFFI Async FFI details](https://mozilla.github.io/uniffi-rs/latest/internals/async-ffi.html)

## Callback Interfaces

Callbacks reverse the direction of control. Define:

- registration and replacement policy;
- strong versus weak ownership;
- thread and executor used for invocation;
- ordering and concurrency;
- error/exception mapping;
- behavior after unregister, cancellation, or host shutdown;
- timeout/backpressure when foreign code is slow.

Do not assume callbacks are cheap or non-blocking. Bound callback rates and avoid unbounded queues. Treat foreign exceptions as part of the exported contract.

Test host implementations that:

- return normally;
- return errors where supported;
- throw/panic at the language boundary;
- re-enter Rust;
- block or respond slowly;
- unregister during invocation;
- disappear while Rust still holds a reference.

Official source: [Callback interfaces](https://mozilla.github.io/uniffi-rs/latest/types/callback_interfaces.html).

## Exported Traits and Foreign Traits

Separate these cases:

- a Rust trait exported as a UniFFI interface/object contract;
- behavior implemented in a foreign language and invoked from Rust;
- standard Rust traits exposed through UniFFI's supported mappings.

Verify object safety, supported method signatures, inheritance/implementation mapping in each language, and whether trait evolution is source- or binary-compatible for generated callers.

Official sources:

- [Traits with proc macros](https://mozilla.github.io/uniffi-rs/latest/proc_macro/traits.html)
- [Foreign traits](https://mozilla.github.io/uniffi-rs/latest/foreign_traits.html)
- [Exposing standard Rust traits](https://mozilla.github.io/uniffi-rs/latest/types/uniffi_traits.html)

## Completion Checklist

- Value and object ownership are explicit.
- Close/shutdown behavior is idempotent where deterministic release matters.
- Thread and reentrancy rules are documented.
- Async cancellation includes spawned-work behavior.
- Callback lifecycle, ordering, error, and backpressure policy are tested.
- Host-language tests prove the generated runtime behavior rather than only Rust internals.
