//! The highest-level binary crate.

use my_core::Version;
use my_net::user_agent;

fn main() {
    let version = Version::new(0, 1, 0);
    println!("{}", user_agent("my-cli", version));
}
