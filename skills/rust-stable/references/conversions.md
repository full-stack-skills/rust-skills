# Type Conversion

## Selection Rules

- Lossless, non-failing with clear semantics: Implement `From<T>` to automatically obtain `Into<U>`.
  ```rust
  impl From<i32> for String { ... } // Automatically implements Into<String>
  ```

- Possible failure: Implement `TryFrom<T>` and derive `TryInto<U>`.
  ```rust
  impl TryFrom<i32> for Result<u64, Error> { ... } // Derives TryInto<Result<u64, Error>>
  ```

- Borrowed views only: Use `AsRef<T>` / `AsMut<T>`.
  ```rust
  fn foo(s: &str) {}           // AsRef<str>
  fn bar(mut s: String) {}     // AsMut<String>
  ```

- Expensive copy or allocation: Prefix with `to_` and make the cost explicit.
  ```rust
  pub fn to_uppercase(&self) -> Result<String, Error> { ... }
  ```

- Cheap borrowed views: Use `as_*`.
  ```rust
  let s = str::from_utf8(data.as_slice())?; // as_str() / as_bytes() etc.
  ```

- Value narrowing (e.g., from large to small types): Prefer `TryFrom` over default `as`, which silently truncates and may hide semantic errors in business logic.
  ```rust
  let count: u64 = i32::from(10) // TryFrom<u32> for Result<u64, Error>; do not use as::<u64>.
  ```

## API Guidelines

- Generic entry points may accept `impl AsRef<Path>` or `impl Into<String>`, but avoid over-generalization that obscures error messages.
- When using the `?` operator with a conversion derived from `From`, preserve the original source type in errors:
  ```rust
  let path = std::fs::read_to_string(path)?; // Source is String, not Path
  ```

- FFI conversions and layout/pointer transformations should be delegated to `rust-unsafe-ffi`.

Official documentation: https://doc.rust-lang.org/std/convert/
