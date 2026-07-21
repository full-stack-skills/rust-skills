//! Parser subdomain — sub-facade over the lexer and grammar.
//!
//! This file is the modern-layout equivalent of `parser/mod.rs`:
//! `parser.rs` + `parser/` directory coexist.

mod grammar;
mod lexer; // src/parser/lexer.rs // src/parser/grammar.rs

pub(crate) use grammar::Grammar;

pub struct Parser {
    grammar: Grammar,
}

impl Parser {
    pub fn new() -> Self {
        Self {
            grammar: Grammar::new(),
        }
    }

    pub fn parse(&self, input: &str) -> crate::Result<crate::ast::Module> {
        let tokens = lexer::tokenize(input);
        self.grammar.parse(&tokens)
    }
}

impl Default for Parser {
    fn default() -> Self {
        Self::new()
    }
}
