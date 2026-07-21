//! The highest-level crate: a binary entry point.
//!
//! Depends on both `my-core` and `my-net` — both directions allowed
//! (binary ─► library).

use my_core::Version;
use my_net::user_agent;

fn main() {
    let version = Version::new(0, 1, 0);
    println!("{}", user_agent("my-cli", version));
}
