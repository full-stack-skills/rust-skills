---
name: rust-unsafe-ffi
description: Design, implement, audit, and test unsafe Rust and foreign-function boundaries, including raw pointers, validity and aliasing invariants, MaybeUninit, layout, Pin, manual Send and Sync, allocators, C ABI declarations, callbacks, ownership transfer, unwinding, and Edition 2024 unsafe syntax. Use when safe Rust cannot express the required memory or ABI operation; require minimal unsafe blocks, explicit safety contracts, safe wrappers, Miri where applicable, and real platform integration tests.
---

# Rust Unsafe and FFI

Treat `unsafe` as a proof obligation. An unsafe block permits specific operations; it does not relax validity, aliasing, initialization, lifetime, data-race, layout, or ABI requirements.

## Scope and Routing

Use this skill for raw pointers, `NonNull`, unsafe functions and traits, unions, `MaybeUninit`, `ManuallyDrop`, layout, pinning, allocators, manual `Send` or `Sync`, C ABI bindings, callbacks, handles, and ownership transfer.

Route ordinary ownership design to `rust-stable`, concurrent architecture to `rust-concurrency`, UniFFI-generated multi-language bindings to `rust-uniffi-building`, general build scripts to `rust-cargo-build`, and review reporting to `rust-code-review`.

## Workflow

### 1. Justify and isolate unsafe operations

Identify the operation safe Rust cannot express. Prefer an audited crate or standard-library abstraction when it preserves the required behavior. Keep unsafe blocks small and enable:

```rust
#![deny(unsafe_op_in_unsafe_fn)]
```

An `unsafe fn` must still place each unsafe operation in an explicit `unsafe {}` block. Expose a safe wrapper only when it can establish and preserve every invariant internally.

### 2. Write the safety contract before code

Document:

- pointer provenance, non-nullness, alignment, and dereferenceable byte range;
- initialization and validity requirements for the pointee type;
- aliasing and mutation rules for the full access duration;
- lifetime and ownership transfer, including who destroys or frees values;
- thread-safety and reentrancy requirements;
- ABI, layout, calling convention, integer width, and error conventions;
- panic or foreign-exception behavior across the boundary.

Use `# Safety` documentation for unsafe public APIs and `// SAFETY:` comments at proof sites.

### 3. Implement raw-memory operations conservatively

```rust
pub unsafe fn read_i32(ptr: *const i32) -> i32 {
    // SAFETY: The caller guarantees that ptr is aligned, initialized,
    // dereferenceable for one i32, and not concurrently mutated.
    unsafe { ptr.read() }
}
```

- Use `ptr.add` only within the same allocated object or one-past it.
- Distinguish aligned and unaligned reads; never create a reference to an unaligned packed field.
- Use `MaybeUninit<T>` while values may be uninitialized, and track exactly which elements were initialized before drop or `assume_init`.
- Prefer `from_ne_bytes`, pointer casts with checked layout, or explicit field conversion over `transmute`.
- Do not use `ManuallyDrop` to hide ownership ambiguity or double-drop risk.

### 4. Define layout and pinning precisely

- Use `#[repr(C)]` for C-compatible struct layout and explicit reprs for shared enums.
- Use `#[repr(transparent)]` only when its documented field restrictions hold.
- Treat padding as potentially uninitialized; do not serialize a struct by copying its raw bytes.
- `Pin<P>` protects the pointee only under the pinning contract. It does not make ordinary `Unpin` data immovable and does not by itself make a self-reference sound.
- Prefer established projection helpers or structural pinning patterns over raw self-referential pointers.

### 5. Build a narrow FFI boundary

Edition 2024 requires unsafe extern blocks and unsafe attributes where applicable:

```rust
use std::ffi::{c_char, CStr};

unsafe extern "C" {
    fn foreign_name() -> *const c_char;
}

pub fn name() -> Option<String> {
    // SAFETY: The foreign contract promises either null or a valid,
    // NUL-terminated string that remains alive for this call.
    let ptr = unsafe { foreign_name() };
    (!ptr.is_null()).then(|| {
        // SAFETY: Non-nullness and termination follow from the contract above.
        unsafe { CStr::from_ptr(ptr) }.to_string_lossy().into_owned()
    })
}
```

- Use `std::ffi` C types or generated bindings, not assumed Rust integer widths.
- Convert nullable pointers, lengths, ownership, and error codes at one boundary.
- Prevent unwinding across a C ABI unless the selected ABI explicitly permits it; catch panics at callbacks when necessary.
- Make callback lifetime, thread, cancellation, and unregister behavior explicit.
- Pair allocation and deallocation in the same allocator domain.

### 6. Verify the proof

Run applicable gates:

```bash
cargo fmt --all --check
cargo check --workspace --all-targets --all-features
cargo test --workspace --all-targets --all-features
cargo clippy --workspace --all-targets --all-features -- -D warnings
cargo miri test
```

Also use sanitizers or Valgrind where supported, ABI layout assertions, C-side integration tests, multiple optimization levels, and every supported operating system and architecture. Miri does not execute arbitrary foreign code, so isolate or mock the external call while testing the Rust-side memory contract.

Read [Unsafe and FFI Reference](references/references.md) for memory-type details. Read [Execution Scenarios](examples/examples.md) for representative boundaries.

## Review Checklist

- Is unsafe necessary, minimal, and locally justified?
- Does each safety contract cover validity, aliasing, lifetime, layout, and concurrency?
- Can a safe caller violate the wrapper's assumptions?
- Are partial initialization and failure cleanup correct?
- Are ownership and deallocation symmetric across FFI?
- Can panic or foreign unwinding cross the ABI boundary?
- Are manual `Send` and `Sync` implementations proven for every field and callback?
- Do tests exercise null, empty, maximum, misaligned, error, callback, and shutdown paths?

## Completion Criteria

- Document every caller and implementation safety obligation.
- Keep unsafe blocks minimal and safe wrappers impossible to misuse from safe Rust.
- Verify ABI types, layout, ownership, error, and unwinding behavior.
- Run Miri where applicable and real platform tests for the external boundary.
- Record any property that could not be verified locally.

## Upstream Sources

- [Rustonomicon](https://doc.rust-lang.org/nomicon/)
- [Rust Reference: Unsafe](https://doc.rust-lang.org/reference/unsafe-keyword.html)
- [Rust Reference: Type Layout](https://doc.rust-lang.org/reference/type-layout.html)
- [std::ptr](https://doc.rust-lang.org/std/ptr/)
- [std::mem](https://doc.rust-lang.org/std/mem/)
- [std::ffi](https://doc.rust-lang.org/std/ffi/)
- [Miri](https://github.com/rust-lang/miri)

## Data Privacy

This skill does not collect, store, or transmit user data. Do not send proprietary headers, generated bindings, crash dumps, or memory contents to external services without authorization.
