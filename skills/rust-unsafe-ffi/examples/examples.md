# Unsafe & FFI Examples

## Raw pointer dereference
```rust
let mut x = 42u32;
let ptr = &mut x as *mut u32;
unsafe {
    *ptr = 100;
}
assert_eq!(x, 100);
```

## FFI: calling C strlen
```rust
use std::ffi::CString;

unsafe extern "C" { fn strlen(s: *const i8) -> usize; }

fn safe_len(s: &str) -> usize {
    let c = CString::new(s).unwrap();
    unsafe { strlen(c.as_ptr()) }
}
```

## MaybeUninit
```rust
use std::mem::MaybeUninit;

let mut val = MaybeUninit::<String>::uninit();
val.write("hello".to_string());
let s = unsafe { val.assume_init() };
```
