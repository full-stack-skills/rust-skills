# Trait Design Patterns

## Trait with default methods

```rust
trait Greeter {
    fn greet(&self) -> String;
    fn greet_loudly(&self) -> String {
        format!("{}!!!", self.greet())
    }
}

struct Person { name: String }
impl Greeter for Person {
    fn greet(&self) -> String { format!("Hello, {}", self.name) }
}
```

## Trait as function parameter

```rust
fn print_greeter(g: &impl Greeter) {
    println!("{}", g.greet());
}

fn print_greeter_generic<T: Greeter>(g: &T) {
    println!("{}", g.greet());
}
```

## Trait objects

```rust
struct Button { label: String }
struct TextField { placeholder: String }

trait Widget { fn render(&self); }
impl Widget for Button { fn render(&self) { /* ... */ } }
impl Widget for TextField { fn render(&self) { /* ... */ } }

fn render_all(widgets: Vec<Box<dyn Widget>>) {
    for w in &widgets { w.render(); }
}
```
