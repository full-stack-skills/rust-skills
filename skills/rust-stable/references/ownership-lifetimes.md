# Ownership, Borrowing, and Lifetimes

## Decision Order

1. Does the value need to live across scopes?
2. Is the caller still required to use it?
3. Should it be modified?
4. Are multiple owners or cross-thread sharing required?

Prioritize based on:
- Read-only observation: `&T`
- Exclusive modification: `&mut T`
- Transfer responsibility: `T` (move)
- Shared ownership: single-threaded `Rc<T>`, multi-threaded `Arc<T>`
- Internal mutability: `Cell<T>`, `RefCell<T>`, or synchronization primitives

## API Design

- Input accepts borrows; output returns owned values, which is the most common and composable boundary.
- Prefer text input as `&str`; convert to `String` only when necessary for storage.
- For collections, prefer slices or iterators over forcing callers to construct `Vec`.
- Lifetimes describe reference relationships but do not extend actual lifetimes.
- Before returning references, prove that the data is owned by the caller and has a clear single source of origin.

## Common Fixes

- Local temporary values cannot be returned: return an owned value or require the caller to provide storage.
- Overlapping mutable and immutable borrows: narrow borrow scopes first; extract required data before modification.
- Closure escaping current scope: choose `move` based on responsibility, then evaluate clone costs.
- Modifying collections during iteration: collect changes beforehand using `retain`, `drain`, or the entry API.
- Self-referential requirements: prefer re-designing structures; if fixed addresses are needed, use `rust-unsafe-ffi` to handle `Pin`s and safety invariants.

## Verification

Do not rely solely on compilation success. Continue checking:
- Does cloning mask ownership design issues?
- Are references cross-threaded, across await boundaries, or exposed via FFI?
- Do drop orders affect locks, files, transactions, and temporary directories?
- Is the public API unnecessarily exposing lifetime parameters?

Official source: https://doc.rust-lang.org/book/ch04-00-understanding-ownership.html
