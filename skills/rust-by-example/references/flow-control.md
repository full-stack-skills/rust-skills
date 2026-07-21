# Flow Control

> Concrete patterns for `if let`, `while let`, `match`, `loop` with labels, `break` with values, and `let else`. For exhaustive language semantics, see `rust-stable`.

## 1. `if let` — single-pattern destructure

```rust
fn main() {
    let opt: Option<i32> = Some(7);
    if let Some(n) = opt {
        println!("got {n}");
    } else {
        println!("none");
    }
}
```

**When to use:** exactly one variant matters and the rest collapse to "else". Use `match` when two or more branches do different things.

## 2. `while let` — loop until `None` / pattern fails

```rust
fn main() {
    let mut xs = vec![1, 2, 3];
    while let Some(x) = xs.pop() {
        println!("{x}");
    }
}
```

Roughly equivalent to `loop { match xs.pop() { Some(x) => ..., None => break } }` but shorter. Watch for infinite loops if the iterator does not progress.

## 3. `match` with `@`-binding, guards, ranges, and `_`

```rust
#[derive(Debug)]
struct Point { x: i32, y: i32 }

fn describe(p: Point) {
    match p {
        Point { x: 0, y }      => println!("on y-axis at {y}"),
        Point { x, y: 0 }      => println!("on x-axis at {x}"),
        p @ Point { x: 10..=20, .. } => println!("in x-band: {p:?}"),
        Point { x, y } if x.abs() == y.abs() => println!("diagonal"),
        _ => println!("elsewhere"),
    }
}

fn main() {
    describe(Point { x: 0, y: 5 });
    describe(Point { x: 15, y: 7 });
    describe(Point { x: -2, y: 2 });
}
```

- `@` binds the whole value while also sub-matching a field.
- Guards (`if cond`) run after the match; they can shadow variables and reference bindings from the arm.
- Ranges (`a..=b`) only work for `PartialOrd + RangeBounds`-friendly types (numeric, char, not floats).

## 4. `loop` with labels

```rust
fn main() {
    let mut grid = [[0u8; 3]; 3];
    'outer: for r in 0..3 {
        for c in 0..3 {
            if r == 1 && c == 1 {
                break 'outer;              // exits the outer loop
            }
            grid[r][c] = 1;
        }
    }
    assert_eq!(grid[1][1], 0);
}
```

Labels work on `loop`, `while`, `while let`, and `for`. Use `'name:` (single-quote prefix) and `break 'name` / `continue 'name`.

## 5. `break` returning a value

```rust
fn first_even(xs: &[i32]) -> Option<i32> {
    for &x in xs {
        if x % 2 == 0 { return Some(x); }
    }
    None
}

fn find_with_loop(xs: &[i32]) -> Option<i32> {
    let mut i = 0;
    let found = loop {
        if i >= xs.len() { break None; }
        if xs[i] % 2 == 0 { break Some(xs[i]); }
        i += 1;
    };
    found
}

fn main() {
    assert_eq!(first_even(&[1, 3, 4, 5]), Some(4));
    assert_eq!(find_with_loop(&[1, 3, 4]), Some(4));
}
```

A `loop` expression has the type of its `break` values. Prefer `for` + early `return` over explicit indexed `loop` when possible.

## 6. Early return

```rust
fn parse_pair(s: &str) -> Option<(i32, i32)> {
    let (a, b) = s.split_once(',')?;
    Some((a.trim().parse().ok()?, b.trim().parse().ok()?))
}
```

Use `?` on `Option`/`Result` to return early. Avoid nested `match` pyramids.

## 7. `let else` — Rust 1.65+

```rust
// Requires Rust 1.65 or newer.
fn must_parse(s: &str) -> i32 {
    let n: i32 = s.parse() else {
        panic!("not an int");
    };
    n + 1
}

fn unwrap_or_continue(items: &[Option<i32>]) -> Vec<i32> {
    let mut out = Vec::new();
    for item in items {
        let Some(x) = item else { continue; };
        out.push(x);
    }
    out
}
```

`let PATTERN = EXPR else { diverge };` is sugar for an early-`return`/`break`/`continue`/`panic` destructure. Cleaner than `if let ... else { return }`.

## `match` vs `if let` vs `let else`

| Pattern | Use when |
|--------|----------|
| `match` | Two or more distinct arms, or exhaustiveness matters |
| `if let P = e { .. } else { .. }` | Single happy-path + fallback |
| `let P = e else { diverge };` | Refute and bail out, then continue linearly |
| `while let P = e { .. }` | Iterate a fallible producer |

## Reference

- [Rust by Example — if let](https://doc.rust-lang.org/rust-by-example/flow_control/if_let.html)
- [Rust by Example — while let](https://doc.rust-lang.org/rust-by-example/flow_control/while_let.html)
- [Rust by Example — match](https://doc.rust-lang.org/rust-by-example/flow_control/match.html)
- [Rust by Example — Loops](https://doc.rust-lang.org/rust-by-example/flow_control/loop.html)
- [let else stabilization (1.65)](https://blog.rust-lang.org/2022/11/03/Rust-1.65.0.html)
