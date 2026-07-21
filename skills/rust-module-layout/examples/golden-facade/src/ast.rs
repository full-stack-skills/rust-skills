//! AST subdomain — public types re-exported at the crate root.

mod print; // src/ast/print.rs — Display impl lives separately

pub use self::expr::Expr;
pub use self::module::Module;

mod expr {
    /// Public AST node — part of the curated facade.
    #[derive(Debug, Clone, PartialEq, Eq)]
    pub enum Expr {
        Atom(String),
    }
}

mod module {
    use super::Expr;

    /// Public AST root — part of the curated facade.
    #[derive(Debug, Clone, PartialEq, Eq)]
    pub struct Module {
        expressions: Vec<Expr>,
    }

    impl Module {
        pub(crate) fn new(expressions: Vec<Expr>) -> Self {
            Self { expressions }
        }

        pub fn expressions(&self) -> &[Expr] {
            &self.expressions
        }
    }
}
