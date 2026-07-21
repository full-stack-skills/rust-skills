//! `golden-crate-discovery` — a minimal crate demonstrating the dependency-
//! selection decision tree that `rust-crate-discovery` recommends.
//!
//! Real evaluation is done by `scripts/crate_eval.py` (Python, networked).
//! This crate shows the Rust-side decision: when to add a dependency vs
//! implement yourself, and how to encode the chosen crate's metadata.

use std::fmt;

/// A dependency recommendation produced by the evaluation flow.
///
/// Mirrors the output of `crate_eval.py eval <name>` — grade, score,
/// subscores, red flags, and a final recommendation string.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Recommendation {
    pub name: String,
    pub grade: Grade,
    pub score: u8,
    pub red_flags: Vec<String>,
    pub verdict: Verdict,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Grade {
    A,
    B,
    C,
    D,
    F,
}

impl fmt::Display for Grade {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str(match self {
            Grade::A => "A",
            Grade::B => "B",
            Grade::C => "C",
            Grade::D => "D",
            Grade::F => "F",
        })
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Verdict {
    Recommended,
    LikelySuitable,
    Acceptable,
    Caution,
    Block,
    Risky,
}

impl fmt::Display for Verdict {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str(match self {
            Verdict::Recommended => "RECOMMENDED",
            Verdict::LikelySuitable => "LIKELY SUITABLE",
            Verdict::Acceptable => "ACCEPTABLE",
            Verdict::Caution => "CAUTION",
            Verdict::Block => "BLOCK",
            Verdict::Risky => "RISKY",
        })
    }
}

impl Recommendation {
    /// Construct from raw score + red flags; grade and verdict derived.
    pub fn from_score(name: impl Into<String>, score: u8, red_flags: Vec<String>) -> Self {
        let grade = match score {
            85..=u8::MAX => Grade::A,
            70..=84 => Grade::B,
            55..=69 => Grade::C,
            40..=54 => Grade::D,
            _ => Grade::F,
        };
        let has_advisory = red_flags
            .iter()
            .any(|f| f.to_lowercase().contains("advisory"));
        let has_stale = red_flags.iter().any(|f| {
            let l = f.to_lowercase();
            l.contains("no release") || l.contains("last github commit")
        });
        let verdict = if has_advisory {
            Verdict::Block
        } else if has_stale {
            Verdict::Caution
        } else {
            match grade {
                Grade::A => Verdict::Recommended,
                Grade::B => Verdict::LikelySuitable,
                Grade::C => Verdict::Acceptable,
                Grade::D | Grade::F => Verdict::Risky,
            }
        };
        Self {
            name: name.into(),
            grade,
            score,
            red_flags,
            verdict,
        }
    }

    /// True if the recommendation is safe to adopt without further review.
    pub fn is_adoptable(&self) -> bool {
        matches!(
            self.verdict,
            Verdict::Recommended | Verdict::LikelySuitable | Verdict::Acceptable
        )
    }
}

/// Decision: should you add a dependency, or implement yourself?
pub enum DepDecision {
    /// Add the dependency — it scores well and fits.
    Add { crate_name: String },
    /// Implement yourself — the need is small or no suitable crate exists.
    Implement,
    /// Block — unresolved advisory or critical concern.
    Block { reason: String },
}

/// Apply the decision rule: if a recommended crate exists with score >= 70
/// and no blocking red flags, add it. Otherwise implement yourself.
pub fn decide(rec: &Recommendation) -> DepDecision {
    if rec.red_flags.iter().any(|f| {
        let l = f.to_lowercase();
        l.contains("advisory") || l.contains("no source repository")
    }) {
        return DepDecision::Block {
            reason: rec.red_flags.join("; "),
        };
    }
    if rec.score >= 70 && rec.is_adoptable() {
        DepDecision::Add {
            crate_name: rec.name.clone(),
        }
    } else {
        DepDecision::Implement
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn grade_a_with_no_flags_is_recommended() {
        let rec = Recommendation::from_score("serde", 97, vec![]);
        assert_eq!(rec.grade, Grade::A);
        assert_eq!(rec.verdict, Verdict::Recommended);
        assert!(rec.is_adoptable());
    }

    #[test]
    fn grade_a_with_advisory_blocks() {
        let rec = Recommendation::from_score(
            "vulnerable-crate",
            90,
            vec!["1 RustSec advisory: RUSTSEC-2024-0001".to_string()],
        );
        assert_eq!(rec.verdict, Verdict::Block);
        assert!(!rec.is_adoptable());
    }

    #[test]
    fn grade_c_is_acceptable() {
        let rec = Recommendation::from_score("niche-crate", 60, vec![]);
        assert_eq!(rec.grade, Grade::C);
        assert_eq!(rec.verdict, Verdict::Acceptable);
    }

    #[test]
    fn grade_d_is_risky() {
        let rec = Recommendation::from_score("sketchy", 45, vec![]);
        assert_eq!(rec.grade, Grade::D);
        assert_eq!(rec.verdict, Verdict::Risky);
    }

    #[test]
    fn stale_crate_gets_caution() {
        let rec =
            Recommendation::from_score("old-crate", 75, vec!["no release in 800 days".to_string()]);
        assert_eq!(rec.grade, Grade::B);
        assert_eq!(rec.verdict, Verdict::Caution);
    }

    #[test]
    fn decide_adds_high_scoring_clean_crate() {
        let rec = Recommendation::from_score("tokio", 95, vec![]);
        match decide(&rec) {
            DepDecision::Add { crate_name } => assert_eq!(crate_name, "tokio"),
            _ => panic!("expected Add"),
        }
    }

    #[test]
    fn decide_implements_when_low_score() {
        let rec = Recommendation::from_score("unknown", 35, vec![]);
        assert!(matches!(decide(&rec), DepDecision::Implement));
    }

    #[test]
    fn decide_blocks_on_advisory() {
        let rec = Recommendation::from_score(
            "x",
            90,
            vec!["RustSec advisory: RUSTSEC-2024-0001".to_string()],
        );
        assert!(matches!(decide(&rec), DepDecision::Block { .. }));
    }

    #[test]
    fn decide_blocks_on_no_repo() {
        let rec = Recommendation::from_score("x", 80, vec!["no source repository".to_string()]);
        assert!(matches!(decide(&rec), DepDecision::Block { .. }));
    }

    #[test]
    fn grade_display_works() {
        assert_eq!(format!("{}", Grade::A), "A");
        assert_eq!(format!("{}", Grade::F), "F");
    }
}
