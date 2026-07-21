# Anti-Pattern Catalog (Before/After Refactors)

Each anti-pattern shows the violation and the idiomatic fix. Use as a checklist when reviewing a public API.

## 1. `get_X` Accessor

```rust
// ❌
pub struct Buffer { data: Vec<u8> }
impl Buffer {
    pub fn get_data(&self) -> &[u8] { &self.data }
    pub fn get_length(&self) -> usize { self.data.len() }
}

// ✅
impl Buffer {
    pub fn data(&self) -> &[u8] { &self.data }
    pub fn len(&self) -> usize { self.data.len() }
    pub fn is_empty(&self) -> bool { self.data.is_empty() }
}
```

## 2. Bool Parameter

```rust
// ❌
pub fn search(query: &str, case_sensitive: bool, whole_word: bool) -> Vec<Match> { /* */ }
search("foo", true, false);  // ??

// ✅
pub enum CaseSensitivity { Sensitive, Insensitive }
pub enum WordBoundary { WholeWord, Substring }

pub fn search(
    query: &str,
    case: CaseSensitivity,
    boundary: WordBoundary,
) -> Vec<Match> { /* */ }

search("foo", CaseSensitivity::Sensitive, WordBoundary::Substring);
```

## 3. `unwrap` in Public API

```rust
// ❌
pub fn parse_config(text: &str) -> Config {
    let parsed: serde_json::Value = serde_json::from_str(text).unwrap();
    Config {
        name: parsed["name"].as_str().unwrap().to_string(),
        retries: parsed["retries"].as_u64().unwrap() as u32,
    }
}

// ✅
#[derive(Debug, thiserror::Error)]
pub enum ConfigError {
    #[error("invalid JSON: {0}")] Json(#[from] serde_json::Error),
    #[error("missing or invalid field: {field}")] MissingField { field: &'static str },
}

pub fn parse_config(text: &str) -> Result<Config, ConfigError> {
    let parsed: serde_json::Value = serde_json::from_str(text)?;
    let name = parsed["name"].as_str()
        .ok_or(ConfigError::MissingField { field: "name" })?;
    let retries = parsed["retries"].as_u64()
        .ok_or(ConfigError::MissingField { field: "retries" })? as u32;
    Ok(Config { name: name.to_string(), retries })
}
```

## 4. `String`/`Vec` Inputs

```rust
// ❌
pub fn process_request(method: String, headers: Vec<(String, String)>) -> Response { /* */ }
// Forces caller to allocate.

// ✅
pub fn process_request(
    method: &str,
    headers: impl IntoIterator<Item = (impl AsRef<str>, impl AsRef<str>)>,
) -> Response { /* */ }

// Caller can use &str or String:
process_request("GET", [("Accept", "application/json")]);
process_request(method_string, headers_vec);
```

## 5. Unsealed Extension Trait

```rust
// ❌
pub trait Logger {
    fn log(&self, msg: &str);
    // Tomorrow: add fn log_level(&self, level: Level, msg: &str);
    // → every downstream impl breaks
}

// ✅ Sealed
mod private { pub trait Sealed {} }
pub trait Logger: private::Sealed {
    fn log(&self, msg: &str);
}

pub struct StdoutLogger;
impl private::Sealed for StdoutLogger {}
impl Logger for StdoutLogger { fn log(&self, msg: &str) { /* */ } }
```

## 6. Missing `#[non_exhaustive]` on Error

```rust
// ❌
pub enum Error { Io(io::Error), Parse(ParseError) }
// Adding Error::Timeout later is a breaking change — downstream match lacks `_`.

// ✅
#[non_exhaustive]
pub enum Error { Io(io::Error), Parse(ParseError) }
// Downstream match must have `_`, so adding Error::Timeout is non-breaking.
```

## 7. Missing Newtype

```rust
// ❌ Argument-order bug waiting to happen
pub fn transfer(amount: u64, from: u64, to: u64) { /* */ }
transfer(100, 42, 99);  // OK
transfer(100, 99, 42);  // accidentally swaps accounts

// ✅ Newtypes
pub struct UserId(pub u64);
pub struct AccountId(pub u64);
pub struct Cents(pub u64);

pub fn transfer(amount: Cents, from: AccountId, to: AccountId) { /* */ }
transfer(Cents(100), AccountId(42), AccountId(99));   // types checked
```

## 8. `Debug` Leaking Secrets

```rust
// ❌
#[derive(Debug)]
pub struct Credentials {
    pub api_key: String,
    pub secret: String,
}

let c = Credentials { api_key: "sk-1234".into(), secret: "shhh".into() };
println!("{:?}", c);  // Credentials { api_key: "sk-1234", secret: "shhh" }

// ✅ Manual Debug
pub struct Credentials {
    pub api_key: String,
    pub secret: String,
}

impl std::fmt::Debug for Credentials {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("Credentials")
            .field("api_key", &"[redacted]")
            .field("secret", &"[redacted]")
            .finish()
    }
}

println!("{:?}", c);  // Credentials { api_key: "[redacted]", secret: "[redacted]" }
```

## 9. `Deref` Polymorphism

```rust
// ❌ Using Deref to "inherit" methods
pub struct SmartClient { inner: reqwest::Client }
impl Deref for SmartClient {
    type Target = reqwest::Client;
    fn deref(&self) -> &Self::Target { &self.inner }
}
// Users now see SmartClient::get, SmartClient::post, etc. — none of which you "wrote".

// ✅ Composition + explicit delegation
pub struct SmartClient { inner: reqwest::Client }

impl SmartClient {
    pub fn inner(&self) -> &reqwest::Client { &self.inner }

    // Delegate only the methods you want
    pub fn get(&self, url: impl AsRef<str>) -> reqwest::RequestBuilder {
        self.inner.get(url.as_ref())
    }
}
```

## 10. `transmute` for Casts

```rust
// ❌ Unsound — bit reinterpretation
let bytes: [u8; 4] = [0x12, 0x34, 0x56, 0x78];
let value: u32 = unsafe { std::mem::transmute(bytes) };

// ✅ Safe, endian-explicit
let value: u32 = u32::from_ne_bytes(bytes);   // native endian
let value: u32 = u32::from_le_bytes(bytes);   // explicit little-endian
let value: u32 = u32::from_be_bytes(bytes);   // explicit big-endian

// ❌ Unsound — type erasure
let ptr: *const u8 = &byte;
let value: usize = unsafe { std::mem::transmute(ptr) };

// ✅ Safe pointer-to-int
let value: usize = ptr as usize;
```

## 11. Cargo-Cult Trait Derive

```rust
// ❌
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Default)]
pub struct FileHandle { fd: i32 }
// Copy on a FD is a double-close bug.
// Hash on a FD is wrong (FDs get reused).
// Default doesn't exist (what's the "empty" FD?).

// ✅
#[derive(Debug)]
pub struct FileHandle { fd: i32 }

impl Drop for FileHandle {
    fn drop(&mut self) {
        // close(self.fd) — single close
    }
}
```

## 12. Unnamed Output Type

```rust
// ❌
pub fn get_config() -> Result<std::collections::HashMap<String, String>, ConfigError> { /* */ }
// Caller has to read docs to know key structure.

// ✅
pub struct Config { entries: std::collections::HashMap<String, String> }

impl Config {
    pub fn get(&self, key: &str) -> Option<&str> { self.entries.get(key).map(|s| s.as_str()) }
    pub fn iter(&self) -> impl Iterator<Item = (&String, &String)> { self.entries.iter() }
}

pub fn load_config() -> Result<Config, ConfigError> { /* */ }
```

## Source

All patterns cross-referenced from the [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/checklist.html) checklist.
