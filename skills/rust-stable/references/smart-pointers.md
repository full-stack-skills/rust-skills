# Smart Pointers Reference

> Based on `library/alloc/src/boxed.rs`, `library/alloc/src/rc.rs`, `library/alloc/src/sync.rs` (official rust-lang/rust).

## Box<T>

```rust
let b = Box::new(42);                   // heap allocation
let list = Box::new(Node { val: 1, next: None });  // recursive type

// Deref coercion: &Box<T> → &T
fn takes_ref(x: &i32) {}
takes_ref(&b);

// Box<dyn Trait>
let obj: Box<dyn Iterator<Item = i32>> = Box::new(0..10);

// From raw parts (unsafe)
let raw = Box::into_raw(b);
unsafe { Box::from_raw(raw); }
```

## Rc<T> (single-threaded)

```rust
use std::rc::Rc;

let rc = Rc::new(5);
let rc2 = Rc::clone(&rc);               // +1 ref count

println!("{}", Rc::strong_count(&rc));  // 2

// Weak to break cycles
use std::rc::Weak;
let weak = Rc::downgrade(&rc);
let upgraded = weak.upgrade();          // Option<Rc<T>>
```

## Arc<T> (multi-threaded)

```rust
use std::sync::Arc;
use std::thread;

let arc = Arc::new(vec![1, 2, 3]);
let mut handles = vec![];

for _ in 0..10 {
    let arc = Arc::clone(&arc);
    handles.push(thread::spawn(move || {
        println!("{:?}", *arc);
    }));
}
```

## Cell & RefCell

```rust
use std::cell::{Cell, RefCell};

// Cell — for Copy types only
let cell = Cell::new(42);
cell.set(100);
let val = cell.get();
cell.replace(50);
let old = cell.take();                  // replaces with Default

// RefCell — runtime borrow checking
let refcell = RefCell::new(vec![1, 2, 3]);
refcell.borrow_mut().push(4);           // panics if already borrowed
if let Some(mut ref_mut) = refcell.try_borrow_mut().ok() {
    ref_mut.push(5);
}

// OnceCell — single initialization
use std::cell::OnceCell;
let cell = OnceCell::new();
cell.set("hello").unwrap();
assert_eq!(cell.get(), Some(&"hello"));
```

## Deref & Drop

```rust
use std::ops::{Deref, DerefMut};
use std::fmt;

struct MyBox<T>(T);

impl<T> Deref for MyBox<T> {
    type Target = T;
    fn deref(&self) -> &T { &self.0 }
}

impl<T> DerefMut for MyBox<T> {
    fn deref_mut(&mut self) -> &mut T { &mut self.0 }
}

impl<T: fmt::Display> fmt::Display for MyBox<T> {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "MyBox({})", self.0)
    }
}

// Drop — resource cleanup
impl<T> Drop for MyBox<T> {
    fn drop(&mut self) { println!("dropping MyBox"); }
}
```
