# Traits and Generics

## Model Selection

- Compile-time polymorphism with performance priority: use generic `T: Trait`.
- Runtime heterogeneous collections or plugin boundaries: use `dyn Trait`.
- Callers require a single associated result type.
- Multiple result types are needed for the same implementation: use generic parameters.
- Composing multiple independent capabilities requires small traits + blanket impls.

## API Rules

- Place constraints as close to their usage points as possible, avoiding overly broad bounds.
- Keep public traits minimal; utility methods can provide default implementations.
- Consider impacts on SemVer and expressiveness before exposing `impl Trait`.
- Use newtypes to comply with the orphan rule and encapsulate external type semantics.
- trait objects require object safety; generic methods or those returning `Self` typically need a `where Self: Sized` clause or refactoring.
- Unstable language features must be explicitly targeted at nightly builds and cannot appear in stable examples.

## Common Validation

```bash
cargo check --all-targets --all-features
cargo test --doc
cargo semver-checks check-release
```

The last command requires a third-party tool; execute only if the project has adopted it or user permission is granted to install.

Official sources:

- https://doc.rust-lang.org/book/ch10-02-traits.html
- https://doc.rust-lang.org/reference/items/traits.html
- https://rust-lang.github.io/api-guidelines/
