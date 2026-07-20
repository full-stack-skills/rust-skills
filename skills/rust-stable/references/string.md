# String & str Reference

> Based on `library/alloc/src/string.rs` and `library/core/src/str/` (official rust-lang/rust).

## String vs str

| Property | `String` | `&str` |
|----------|---------|-------|
| Memory | Owned, heap-allocated | Borrowed, anywhere |
| Mutable | Yes | No |
| Length | Runtime-dynamic | Fixed or slice |
| Usage | Building, modifying | Reading, parameters |

## String Creation & Mutation

```rust
let s = String::new();
let s = "hello".to_string();
let s = String::from("hello");

s.push('!');                             // append char
s.push_str(" world");                    // append &str
s.insert(0, 'H');                        // insert char at index
s.insert_str(5, " there");               // insert &str at index

// Concatenation
let s = s1 + &s2 + &s3;                  // s1 moved, rest referenced
let s = format!("{a}-{b}");              // no move, owned result

// Remove & truncate
s.pop();                                 // Option<char>
s.remove(5);                             // char at index (O(n))
s.truncate(10);                          // keep first 10 bytes
s.clear();
s.drain(3..6);                           // remove range → iterator
s.retain(|c| c != ' ');                  // remove spaces in-place
```

## str Methods

```rust
let s = "hello world";

// Search
s.contains("world");
s.find("wo");                            // Option<usize>
s.starts_with("he");
s.ends_with("ld");
s.is_empty();
s.len();                                 // byte length, not char count

// Slice
&s[0..5];                                // caution on char boundaries

// Split
s.split(' ');                            // iterator
s.split_whitespace();                    // split on any whitespace
s.lines();                               // split on '\n'
s.split_at(5);                           // (&str, &str)
s.splitn(2, ' ');

// Trim
s.trim();
s.trim_start();
s.trim_end();

// Transform
s.to_lowercase();
s.to_uppercase();
s.replacen("hello", "hi", 1);
// Iteration
for c in s.chars() { /* char */ }
for b in s.bytes() { /* u8 */ }
```

## Conversions

```rust
// &str → String
"hello".to_string();
String::from("hello");
"hello".into();

// String → &str
let s = String::from("hello");
let r: &str = &s;
let r: &str = s.as_str();

// Numbers ↔ String
let n: i32 = "42".parse().unwrap();
let s = 42.to_string();
```
