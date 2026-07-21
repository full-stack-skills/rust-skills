//! Grammar rules — implementation detail of `parser`. Not exported externally.

use crate::Result;
use crate::ast::{Expr, Module};

pub(crate) struct Grammar;

impl Grammar {
    pub(crate) fn new() -> Self {
        Self
    }

    pub(crate) fn parse(&self, tokens: &[String]) -> Result<Module> {
        let exprs: Vec<Expr> = tokens.iter().map(|t| Expr::Atom(t.clone())).collect();
        Ok(Module::new(exprs))
    }
}
