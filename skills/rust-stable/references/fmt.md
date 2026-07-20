# Formatting Reference

> Based on `library/core/src/fmt/` (official rust-lang/rust).

## Format String Syntax

```rust
// Positional
format!("{} {}", "hello", "world");               // "hello world"
format!("{0} {1}", "a", "b");                     // "a b"
format!("{1} {0}", "a", "b");                     // "b a"

// Named (2021+)
let name = "Alice";
format!("Hello, {name}!");                         // "Hello, Alice!"

// Formatting traits
format!("{:?}", vec![1, 2]);                      // Debug: "[1, 2]"
format!("{:#?}", vec![1, 2]);                     // Pretty Debug
format!("{:p}", &x);                               // Pointer
format!("{:b}", 10);                               // Binary: "1010"
format!("{:o}", 10);                               // Octal: "12"
format!("{:x}", 255);                              // Lower Hex: "ff"
format!("{:X}", 255);                              // Upper Hex: "FF"
format!("{:e}", 1000.0);                           // Scientific: "1e3"
format!("{:E}", 1000.0);                           // Scientific Upper: "1E3"

// Width & alignment
format!("{:10}", "hi");                            // "hi        " (right, width 10)
format!("{:<10}", "hi");                           // "hi        " (left)
format!("{:^10}", "hi");                           // "    hi    " (center)
format!("{:>10}", "hi");                           // "        hi" (right)
format!("{:.>10}", "hi");                          // "........hi" (fill '.')

// Numeric formatting
format!("{:05}", 42);                              // "00042" (zero-pad)
format!("{:+.3}", 3.14159);                        // "+3.142" (sign + 3 decimals)
format!("{:.2}", 3.14159);                         // "3.14" (2 decimals)
format!("{:#x}", 255);                             // "0xff" (0x prefix)
format!("{:#X}", 255);                             // "0xFF"
```

## Custom Display & Debug

```rust
use std::fmt;

struct Point { x: i32, y: i32 }

impl fmt::Display for Point {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "({}, {})", self.x, self.y)
    }
}

impl fmt::Debug for Point {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.debug_struct("Point")
            .field("x", &self.x)
            .field("y", &self.y)
            .finish()
    }
}
```
