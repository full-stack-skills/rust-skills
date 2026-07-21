# rust-module-layout — References

Deep technical material on Rust module layout decisions.

## Files

| File | Topic |
|------|-------|
| [refactoring-flat-lib-rs.md](refactoring-flat-lib-rs.md) | Step-by-step migration of an "index + glob re-export" lib.rs to a curated facade |
| [large-crate-layout.md](large-crate-layout.md) | Worked 50-file example of a large crate's directory tree |
| [modernizing-mod-rs.md](modernizing-mod-rs.md) | Mechanical migration from `foo/mod.rs` to `foo.rs + foo/` |
| [coming-from-java-python.md](coming-from-java-python.md) | Mental model translation: Java packages / Python modules → Rust modules |
| [facade-design.md](facade-design.md) | Public facade design (C-REEXPORT, C-HIERARCHY) |
| [naming.md](naming.md) | Module and item naming conventions |
| [visibility-and-privacy.md](visibility-and-privacy.md) | Complete visibility model with edge cases |
| [module-resolution.md](module-resolution.md) | How the compiler resolves `mod foo;` to a file path; `#[path]` attribute |

## When to Read What

- **Refactoring an existing crate** → `refactoring-flat-lib-rs.md` + relevant sections in SKILL.md
- **Starting a large new crate** → `large-crate-layout.md` + `facade-design.md`
- **Coming from another language** → `coming-from-java-python.md`
- **Confused about visibility** → `visibility-and-privacy.md`
- **Choosing module names** → `naming.md`
- **Understanding how `mod foo;` finds files** → `module-resolution.md`
