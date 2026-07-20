# Ownership & Borrow Checker Patterns

## NLL — non-lexical lifetimes

```rust
let mut v = vec![1, 2, 3];
let r = &v[0];             // borrow starts
println!("{r}");           // borrow ends here — before &mut
v.push(4);                 // OK: borrow already ended
```

## Split borrows

```rust
struct Point { x: i32, y: i32 }

let mut p = Point { x: 1, y: 2 };
let rx = &p.x;             // borrow p.x
let ry = &mut p.y;         // borrow p.y — OK, separate fields
println!("{rx}, {ry}");
```

## Temporary scope for &mut

```rust
let mut data = vec![1, 2, 3];
let last = {
    let r = data.last_mut().unwrap();
    *r += 1;
    *r                          // copy out
};                              // &mut borrow ends here
data.push(last);                // OK now
```
