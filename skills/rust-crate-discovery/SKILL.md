---
name: rust-crate-discovery
description: Discover, evaluate, score, and compare Rust crates for adoption — search crates.io, fetch metadata from 4 sources (crates.io API, docs.rs, GitHub API, RustSec advisory DB), apply a weighted 0-100 scoring model across adoption/maintenance/documentation/maturity/community/license, flag red concerns (unmaintained, advisories, no docs, single-maintainer), and recommend the best fit. Use when users ask "which crate should I use for X", "is this crate maintained/safe/popular", "compare these 3 crates", or need to pick a dependency before adoption; hand post-adoption governance (cargo-deny, license policy, advisory response) to rust-dependencies, semver and breaking-change classification to rust-semver, and manifest mechanics to rust-cargo-build.
---

# Rust Crate Discovery and Evaluation

> Authority: [crates.io API](https://crates.io/data-access), [docs.rs](https://docs.rs), [GitHub REST API](https://docs.github.com/en/rest), [RustSec Advisory Database](https://rustsec.org/).

This skill owns the **discovery + evaluation phase** before a crate enters your `Cargo.toml`. It uses a bundled Python tool (`scripts/crate_eval.py`) to fetch signals from 4 sources and produce a weighted 0-100 score with a letter grade (A/B/C/D/F), red-flag list, and a recommendation. It does **not** own post-adoption governance (`rust-dependencies`), manifest mechanics (`rust-cargo-build`), or semver (`rust-semver`).

## Capability Boundaries

### ✅ Strengths
1. Search crates.io by keyword, category, or name — returns ranked candidates
2. Evaluate a single crate in depth: fetch metadata from crates.io + docs.rs + GitHub + RustSec
3. Compare 2+ crates side-by-side with subscore breakdown
4. Score each crate 0-100 across 6 dimensions: adoption (30), maintenance (25), documentation (15), maturity (15), community (10), license (5)
5. Flag red concerns: stale, advisories, no docs, low adoption with churn, single-maintainer bus factor, no source repo, license missing
6. Recommend the best fit, surfacing blocking concerns before the user adopts
7. Output as human-readable report or machine-readable JSON (for agent consumption)

### ⚠️ Prerequisites
1. Network access (the tool fetches from crates.io, docs.rs, GitHub, RustSec)
2. Python 3.9+ (no external pip packages — stdlib only)

### ❌ Out of Scope
1. Post-adoption governance (cargo-deny config, license policy, advisory response workflow) → `rust-dependencies`
2. Cargo.toml field semantics → `rust-cargo-build`
3. Semver and breaking-change classification → `rust-semver`
4. Which std type to use instead of a crate → `rust-stdlib`

## Data Privacy

This skill makes outbound HTTP requests to crates.io, docs.rs, GitHub, and RustSec. The User-Agent identifies the tool. No user data is collected or transmitted beyond the crate name in the URL path (which is public registry data). For private/proprietary crate names, prefer manual review.

---

# The Evaluation Tool — `scripts/crate_eval.py`

A stdlib-only Python script. Three subcommands:

```bash
# Search candidates
python3 scripts/crate_eval.py search "orm"
python3 scripts/crate_eval.py search "http client" --limit 5
python3 scripts/crate_eval.py search "logging" --category "development-tools::debugging"

# Evaluate one crate in depth
python3 scripts/crate_eval.py eval rbatis
python3 scripts/crate_eval.py eval rbatis --json          # machine-readable
python3 scripts/crate_eval.py eval rbatis -v              # show raw signals
python3 scripts/crate_eval.py eval rbatis --skip-github   # faster, less signal

# Compare multiple candidates
python3 scripts/crate_eval.py compare rbatis diesel sea-orm sqlx
```

## Workflow

1. **Search** — `search "<domain keyword>"` to surface candidates. Inspect the top 5-10 by downloads and recency.
2. **Shortlist** — pick 2-4 names with non-trivial adoption (≥1k downloads) and recent activity.
3. **Compare** — `compare <names...>` to get the side-by-side scorecard.
4. **Investigate red flags** — for the top pick, read the red-flag list. Block on security advisories; investigate stale or single-maintainer concerns.
5. **Verify fit** — the score measures *health*, not *fitness*. Read the crate's docs, check its API shape (`rust-api-design` lens), confirm it covers your use case.
6. **Hand off** — once adopted, set up `cargo-deny` (`rust-dependencies`) and pin version policy (`rust-semver`).

## Reading the output

```
=== rbatis === A (92/100) — RECOMMENDED — strong fit, low risk
  version 4.9.6  |  657,356 downloads (19,938 recent)  |  license: Apache-2.0
  Subscores:
    adoption        █████████████░░░░░░░░░░░░  27/30
    maintenance     ████████████░░░░░░░░░░░░░  25/25
    ...
  Red flags:
    ! license not declared
```

- **Grade + score** — at-a-glance health
- **Subscores** — which dimensions are strong/weak
- **Notes** (`+`) — positive signals
- **Red flags** (`!`) — concerns to investigate before adopting
- **Recommendation** — verdict (RECOMMENDED / LIKELY SUITABLE / ACCEPTABLE / CAUTION / BLOCK / RISKY)

---

# Scoring Model

| Dimension | Max | What it measures | Key signals |
|-----------|-----|------------------|-------------|
| **Adoption** | 30 | Is anyone using this? | all-time downloads, recent (90-day) downloads |
| **Maintenance** | 25 | Is it actively maintained? | last crates.io update, version count, GitHub last commit |
| **Documentation** | 15 | Can users learn it? | docs.rs build, description, docs URL, repo link |
| **Maturity** | 15 | Is the API stable? | age, stable version ≥1.0, has repo |
| **Community** | 10 | Is there a contributor base? | GitHub stars, contributors |
| **License** | 5 | Is it permissive? | permissive (MIT/Apache/BSD) preferred; copyleft penalized |
| **Total** | 100 | | |

## Grade bands

| Grade | Score | Meaning |
|-------|-------|---------|
| **A** | ≥85 | Excellent — recommended |
| **B** | 70-84 | Good — likely suitable |
| **C** | 55-69 | Acceptable — verify fit |
| **D** | 40-54 | Risky — investigate before use |
| **F** | <40 | Avoid — significant concerns |

See `references/scoring-rubric.md` for the full formula and signal weights.

---

# Red Flags Catalog

The tool surfaces specific concerns. Always read these before adopting.

| Flag | Severity | Action |
|------|---------|--------|
| RustSec advisory | **Block** | Pin to fixed version or pick alternative |
| No release in >12 months | High | Check if abandoned; consider fork or alternative |
| Last GitHub commit >6 months | High | Activity may have moved elsewhere |
| No docs.rs build | Medium | API docs may be missing; check manually |
| License not declared | Medium | Treat as proprietary; cannot use without clarification |
| Low adoption with many versions | Medium | Churn without traction; investigate quality |
| Pre-1.0 with 20+ versions | Medium | API likely unstable across minor bumps |
| Single maintainer + low adoption | Medium | Bus factor risk; consider backing up or forking |
| No source repository | High | Cannot audit; avoid |

See `references/red-flags.md` for the full catalog and decision guidance.

---

# Decision Shortcuts

| Question | Answer |
|---------|--------|
| Which crate for X? | `search "X"`, then `compare` top 3-4 |
| Is this crate safe? | `eval <name>`; check red flags for advisories |
| Is it maintained? | `eval <name>`; check maintenance subscore + last update |
| Is the API stable? | `eval <name>`; check maturity subscore + version ≥1.0 |
| What's the license? | `eval <name>`; appears in signals |
| A vs B vs C? | `compare A B C`; pick highest score without blocking red flags |
| Score says A but it doesn't fit my use case | Trust the fit check over the score — score measures health, not fitness |

## When the score is misleading

- **Niche crates** — a domain-specific crate may have low downloads but be the only option. Score will understate; rely on manual review.
- **New crates** — recent releases have low adoption signals; check maintainer track record instead.
- **Forks** — a fork may have few downloads but be the maintained successor. Check the parent crate's status.
- **Internal/private crates** — not on crates.io; this tool won't help. Use manual review.

---

## Resources

- [Scoring Rubric](references/scoring-rubric.md) — full formula, log-scale parameters, subscore breakdowns
- [Red Flags Catalog](references/red-flags.md) — full flag list with severity and action
- [API Endpoints Reference](references/api-endpoints.md) — the 4 data sources and their endpoints
- [Evaluation Workflow Examples](examples/evaluation-examples.md) — worked scenarios (ORM choice, HTTP client, logging)
- [`scripts/crate_eval.py`](scripts/crate_eval.py) — the evaluation tool (run with `python3`)

## Upstream Sources

- [crates.io API](https://crates.io/data-access) — search, crate metadata, version downloads
- [docs.rs](https://docs.rs) — documentation build status, version presence
- [GitHub REST API](https://docs.github.com/en/rest) — stars, contributors, last commit, open issues
- [RustSec Advisory Database](https://rustsec.org/) — known vulnerabilities
- [crates.io-index](https://github.com/rust-lang/crates.io-index) — registry index (alternative to API)
