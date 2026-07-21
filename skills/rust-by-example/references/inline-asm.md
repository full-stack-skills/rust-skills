# Inline Assembly

> Patterns for `core::arch::asm!` / `core::arch::global_asm!`: operand kinds, clobbers, options, and platform gating. Inline asm is rare; reach for it only in kernels, embedded, or proven hot paths. For deeper unsafe discussion, see `unsafe.md`.

## When to use

| Situation | Inline asm? |
|-----------|-------------|
| Hot intrinsic the compiler already lowers (`u64::leading_zeros`) | No |
| Single CPU instruction with no Rust equivalent (`cpuid`, `rdtsc`) | Yes |
| Kernel context switch, custom calling convention | Yes |
| Embedded: wait-for-interrupt, `wfi` | Yes |
| Writing a generic algorithm | No |

Inline asm bypasses the optimizer's understanding of the code. Always benchmark before and after.

## Syntax overview

`asm!` takes a template string (one instruction per line or `;`), operands, options. Template uses `{0}`, `{name}` placeholders like `format!`.

```rust
use core::arch::asm;

#[cfg(target_arch = "x86_64")]
fn halt() {
    unsafe {
        asm!("hlt", options(nostack, preserves_flags));
    }
}
```

Always gate by `target_arch` — asm is architecture-specific. Compiling this on ARM will fail without the `#[cfg]`.

## Operand kinds

```rust
use core::arch::asm;

#[cfg(target_arch = "x86_64")]
fn add_via_asm(a: u64, b: u64) -> u64 {
    let out: u64;
    unsafe {
        asm!(
            "add {res}, {lhs}",
            "add {res}, {rhs}",
            res = out(reg) out,         // out: any register, written
            lhs = in(reg) a,            // in: any register, read
            rhs = in(reg) b,
            options(pure, nomem, nostack),
        );
    }
    out
}
```

| Kind | Meaning |
|------|---------|
| `in(reg) x` | Place `x` in some register, read-only |
| `out(reg) x` | Output: written back into `x` |
| `inout(reg) x` | Same register read and written |
| `inlateout(reg) x` | Like `inout` but allocator may reuse |
| `const X` | Immediate value substituted into template |
| `sym FOO` | Symbol reference (function / static) |
| `label NAME` | Jump label (`asm!` 1.67+) |

Constraint templates: `reg` (any), `mem` (memory operand), `const` (compile-time int), specific regs like `in("eax") x`.

## Named placeholders and formatting

```rust
use core::arch::asm;

#[cfg(target_arch = "x86_64")]
fn read_timestamp() -> u64 {
    let lo: u32;
    let hi: u32;
    unsafe {
        asm!(
            "rdtsc",
            "mov {lo}, eax",
            "mov {hi}, edx",
            lo = out(reg) lo,
            hi = out(reg) hi,
            options(nostack, preserves_flags),
        );
    }
    ((hi as u64) << 32) | (lo as u64)
}
```

Numbers (`{0}`) and names (`{lo}`) both work. Names make multi-instruction blocks far easier to read.

## Clobbers

If your asm touches registers or memory not declared as operands, you must tell the compiler.

```rust
use core::arch::asm;

#[cfg(target_arch = "x86_64")]
fn hot_call() {
    unsafe {
        asm!(
            "call my_init",                // hypothetical external symbol
            lateout("rax") _,              // clobbered, value discarded
            lateout("rcx") _,
            lateout("rdx") _,
            out("xmm0") _,                 // clobbers SIMD register
        );
    }
}
```

Use `lateout(reg) _` (or named register form) to declare a register clobbered. The `_` discards the output value. Memory clobbers are automatic unless `nomem` is set.

## Options

| Option | Meaning |
|--------|---------|
| `pure` | Output depends only on inputs; allows CSE and dead-code elimination |
| `nomem` | Does not access memory (enables reordering) |
| `nostack` | Does not push to the stack |
| `preserves_flags` | Does not modify CPU flags |
| `noreturn` | Never returns (e.g. `unreachable`) |
| `readonly` | Reads memory but does not write |
| `raw_sym` | Allows unresolved `sym` |
| `may_unwind` | May unwind the stack |

`options(pure, nomem, preserves_flags, nostack)` is the common set for a pure intrinsic; the optimizer can move, hoist, or delete the block.

## `global_asm!` — module-level assembly

```rust
use core::arch::global_asm;

#[cfg(target_arch = "x86_64")]
global_asm!(
    ".global my_fast_add",
    "my_fast_add:",
    "lea rax, [rdi + rsi]",
    "ret",
);

extern "C" { fn my_fast_add(a: u64, b: u64) -> u64; }
```

`global_asm!` defines assembly at module level (e.g. for naked functions, hand-rolled entry points). For inline use inside a function, prefer `asm!`.

## A complete, gated, safe wrapper

```rust
/// Reads the CPU timestamp counter. Returns `None` on non-x86_64.
pub fn timestamp() -> Option<u64> {
    #[cfg(target_arch = "x86_64")]
    {
        use core::arch::asm;
        let lo: u32;
        let hi: u32;
        // SAFETY: rdtsc is privileged-safe on x86_64; we read general
        // registers and let the compiler restore them.
        unsafe {
            asm!(
                "rdtsc",
                "mov {lo}, eax",
                "mov {hi}, edx",
                lo = out(reg) lo,
                hi = out(reg) hi,
                options(nostack, preserves_flags),
            );
        }
        Some(((hi as u64) << 32) | (lo as u64))
    }
    #[cfg(not(target_arch = "x86_64"))]
    None
}
```

This pattern — `#[cfg(target_arch = ...)]` + tight `unsafe` block + `// SAFETY:` comment + safe public wrapper — is the right shape for almost all inline asm in a Rust crate.

## Common pitfalls

| Pitfall | Fix |
|---------|-----|
| Compiles on x86, fails on ARM | Gate with `#[cfg(target_arch = "...")]` |
| Compiler reorders asm past a side effect | Drop `nomem` / `preserves_flags` |
| Wrong clobber list → corrupt registers | Declare every register you touch |
| Use `eax` as `out` then read `rax` | Use the right width (`eax` vs `rax`) |
| `sym foo` not found | `foo` must be a `fn` or `static` reachable at that point |

## Reference

- [Rust by Example — Inline assembly](https://doc.rust-lang.org/rust-by-example/unsafe/asm.html)
- [The Rust Reference — Inline assembly](https://doc.rust-lang.org/reference/inline-assembly.html)
- [std::arch::asm](https://doc.rust-lang.org/core/arch/macro.asm.html)
- [RFC 2873 — Inline assembly](https://rust-lang.github.io/rfcs/2873-inline-asm.html)
- [The Rustonomicon](https://doc.rust-lang.org/nomicon/)
