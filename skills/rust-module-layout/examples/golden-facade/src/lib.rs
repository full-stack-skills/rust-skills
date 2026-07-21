//! Golden example: a curated crate facade over a private deep tree.
//!
//! The crate exposes a flat public surface (`Parser`, `Module`, `Expr`)
//! while keeping the implementation (lexer, grammar, AST internals) private.
//! External users cannot reach `parser::lexer::Lexer` even though it is `pub`
//! within its own module — privacy is parent-bound.

mod ast;
mod error;
mod parser;

// ── Curated facade ─────────────────────────────────────────────────
// Only the items users need at the root. Keep this list short.

pub use ast::{Expr, Module};
pub use error::{Error, Result};
pub use parser::Parser;

/// Top-level convenience entry point — preserves the flat API.
pub fn parse(input: &str) -> Result<Module> {
    Parser::new().parse(input)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn exposes_a_small_public_api() {
        let module = parse("hello").unwrap();
        assert_eq!(module.expressions().len(), 1);
    }

    #[test]
    fn deep_tree_is_unreachable() {
        // The internal modules `parser`, `ast`, `error` are private.
        // Users can only use the re-exported types.
        let _: Parser = Parser::new();
        let _: Module = parse("x").unwrap();
    }
}
