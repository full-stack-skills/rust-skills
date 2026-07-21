//! Display impls for AST nodes — kept in a sibling file to avoid bloating `ast.rs`.

use super::{Expr, Module};
use std::fmt;

impl fmt::Display for Expr {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Expr::Atom(s) => write!(f, "{s}"),
        }
    }
}

impl fmt::Display for Module {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        for (i, expr) in self.expressions().iter().enumerate() {
            if i > 0 {
                write!(f, " ")?;
            }
            write!(f, "{expr}")?;
        }
        Ok(())
    }
}
