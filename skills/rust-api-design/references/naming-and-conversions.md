# Naming and Conversions — Deep Dive

Companion to `SKILL.md` §1 and §2. Covers the trickier cases that don't fit a one-line rule.

## Naming: Special Cases

### Units in names

When a value has implicit units, encode them in the name:

```rust
// ✅ Units are explicit
pub fn timeout_millis(&self) -> u64 { /* */ }
pub fn resize_to_pixels(&self, w: u32, h: u32) { /* */ }
const MAX_RETRY_COUNT: u32 = 5;

// ❌ Ambiguous
pub fn timeout(&self) -> u64 { /* */ }   // ms? s? ns?
```

### Predicate methods: `is_`/`has_`/`should_`

Boolean predicates use `is_`/`has_`/`contains_`/`should_`:

```rust
pub fn is_empty(&self) -> bool { /* */ }
pub fn has_payload(&self) -> bool { /* */ }
pub fn contains_key(&self, k: &str) -> bool { /* */ }
pub fn should_retry(&self) -> bool { /* */ }
```

`is_` is the default. `has_` for ownership. `contains_` for collections.

### Constructors: `new`/`from_X`/`with_X`

| Pattern | Convention | Example |
|---------|-----------|---------|
| Default constructor | `new` | `Foo::new()` |
| From another type | `from_X` | `Foo::from_bytes(b)` |
| With config | `with_X` | `Foo::with_capacity(16)` |
| Fallible | `parse` or `try_from_X` | `Foo::parse(s)` |
| Empty/zero | `empty` | `String::empty()` |

Avoid `Foo::create()` — `new` is the convention.

### Avoid `make_` and `set_`

```rust
// ❌ Java/Python style
pub fn make_request(&self) -> Request { /* */ }
pub fn set_timeout(&mut self, t: u64) { /* */ }

// ✅ Rust style
pub fn build_request(&self) -> Request { /* */ }   // or new_request
pub fn timeout(&mut self, t: u64) { /* */ }        // setter == field name
```

## Conversions: The Decision Tree

```
I want to convert from T to U.
   │
   ├─ Is it cheap and lossless?
   │     ├─ Yes → impl From<T> for U
   │     └─ No → fall through
   │
   ├─ Is it cheap and fallible?
   │     └─ impl TryFrom<T> for U
   │
   ├─ Is it expensive and infallible?
   │     └─ Provide `U::from_T(t: T) -> U` method
   │
   ├─ Is it expensive and fallible?
   │     └─ Provide `U::parse(t: &T) -> Result<U, Error>` method
   │
   └─ Just borrowing for inspection?
         └─ impl AsRef<U> for T  (and Borrow<U> if Eq/Hash semantics)
```

## `From` vs `Into`

Rust's blanket impl provides `Into` for free:

```rust
impl From<Foo> for Bar { fn from(f: Foo) -> Self { /* */ } }
// Gives you:
let b: Bar = foo.into();
let b = Bar::from(foo);
```

**Rule**: impl `From`, never `Into`. The blanket impl does the rest.

## `AsRef` vs `Borrow`

```rust
// AsRef: cheap view. Eq/Hash need NOT agree.
impl AsRef<str> for Email {
    fn as_ref(&self) -> &str { &self.0 }
}

// Borrow: cheap view. Eq/Hash MUST agree with the target.
impl Borrow<str> for Email {
    fn borrow(&self) -> &str { &self.0 }
}
```

Use `Borrow` only when you want `HashMap<Email, V>` to be lookupable by `&str`:

```rust
let mut map: HashMap<Email, V> = HashMap::new();
map.get("user@example.com");  // requires Borrow<str>
```

Otherwise `AsRef` is enough.

## `TryFrom`/`TryInto`

```rust
impl TryFrom<&str> for Email {
    type Error = EmailError;
    fn try_from(s: &str) -> Result<Self, Self::Error> {
        if s.contains('@') { Ok(Email(s.into())) }
        else { Err(EmailError::Invalid) }
    }
}

// Caller:
let email = Email::try_from("user@example.com")?;
let email: Email = "user@example.com".try_into()?;
```

## The `Deref` Anti-Pattern (in detail)

`Deref` is for smart pointers — types whose entire purpose is to delegate to an inner value (`Box`, `Rc`, `Arc`, `String`, `Vec`, `Cow`). When you impl `Deref` on a non-pointer type, you trigger **deref coercion**, which:

1. **Hides method resolution**: `my_client.send()` might call `HttpClient::send` because `MyClient: Deref<Target = HttpClient>`. The reader has to know this.
2. **Breaks `&self` resolution**: methods on the inner type see `&self` as the inner type, not the wrapper.
3. **Couples the API**: every public method on the inner becomes public on the wrapper, even ones you didn't intend.

### Real-world example (anonymized)

```rust
// ❌ A framework wraps an executor and uses Deref
pub struct Framework { inner: Executor }
impl Deref for Framework {
    type Target = Executor;
    fn deref(&self) -> &Executor { &self.inner }
}

// Users see Framework::spawn, Framework::block_on, etc.
// The framework author never "added" these methods.

// ✅ Use composition + delegation
pub struct Framework { inner: Executor }
impl Framework {
    pub fn executor(&self) -> &Executor { &self.inner }
    // Only the methods you want are exposed.
}
```

## Iterator Naming for Collections

```rust
struct Stack<T> { items: Vec<T> }

impl<T> Stack<T> {
    pub fn iter(&self) -> std::slice::Iter<'_, T> { self.items.iter() }
    pub fn iter_mut(&mut self) -> std::slice::IterMut<'_, T> { self.items.iter_mut() }
}

impl<T> IntoIterator for Stack<T> {
    type Item = T;
    type IntoIter = std::vec::IntoIter<T>;
    fn into_iter(self) -> Self::IntoIter { self.items.into_iter() }
}

impl<'a, T> IntoIterator for &'a Stack<T> {
    type Item = &'a T;
    type IntoIter = std::slice::Iter<'a, T>;
    fn into_iter(self) -> Self::IntoIter { self.items.iter() }
}

impl<'a, T> IntoIterator for &'a mut Stack<T> {
    type Item = &'a mut T;
    type IntoIter = std::slice::IterMut<'a, T>;
    fn into_iter(self) -> Self::IntoIter { self.items.iter_mut() }
}
```

If you provide `iter()` and `iter_mut()`, also impl `IntoIterator` for `&T` and `&mut T`. Users expect both forms.

## Anti-Pattern: Auto-Trait Sprawl

Don't reflexively derive every trait:

```rust
// ❌ Cargo-cult
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash, Default)]
pub struct Handler { /* */ }

// Some of these may not make sense:
// - Copy if Handler owns a file descriptor (double-close bug)
// - Hash if Handler's identity is its FD (FDs get reused)
// - Default if there's no natural "empty" handler
```

Ask: would this trait compose correctly with the type's invariants? If unsure, drop it.

## Source

- [Rust API Guidelines — Naming](https://rust-lang.github.io/api-guidelines/naming.html)
- [Rust API Guidelines — Interoperability](https://rust-lang.github.io/api-guidelines/interoperability.html)
- [Rust API Guidelines — Conversions](https://rust-lang.github.io/api-guidelines/interoperability.html#c-conv)
- [`Deref` polymorphism](https://rust-unofficial.github.io/patterns/anti_patterns/deref.html)
