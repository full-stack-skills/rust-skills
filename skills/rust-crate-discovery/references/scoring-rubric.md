# Scoring Rubric

> Reference companion to [`SKILL.md`](../SKILL.md). The authoritative
> implementation is [`scripts/crate_eval.py`](../scripts/crate_eval.py) — the
> `score_*` functions. If this document and the script disagree, **the script
> wins**. Tune weights there, not here.

## Overview

Every crate becomes a **0–100 score** across six weighted dimensions favoring
*health signals* over *fitness signals*: a high score means "alive and safe to
depend on", not "does what you need". Fitness is a separate manual check.

| Dimension        | Weight | What it measures                          | Primary data source         |
|------------------|:------:|-------------------------------------------|-----------------------------|
| Adoption         | 30     | Is anyone actually using this?            | crates.io downloads         |
| Maintenance      | 25     | Is it being actively cared for?           | crates.io + GitHub          |
| Documentation    | 15     | Can a new user learn it?                  | docs.rs + crates.io fields  |
| Maturity         | 15     | Is the API stable and settled?            | crates.io age + version     |
| Community        | 10     | Is there a contributor base (bus factor)? | GitHub stars + contributors |
| License          | 5      | Is the license adoptable?                 | crates.io license field     |
| **Total**        | **100**|                                           |                             |

### Grade bands

| Grade | Score    | Verdict                                              |
|:-----:|:--------:|------------------------------------------------------|
| A     | ≥ 85     | Excellent — recommended                              |
| B     | 70–84    | Good — likely suitable                               |
| C     | 55–69    | Acceptable — verify fit                              |
| D     | 40–54    | Risky — investigate before use                       |
| F     | < 40     | Avoid — significant concerns                         |

The score never reaches 100 for a crate with *any* missing signal (no repo,
no docs, pre-1.0, copyleft license): a perfect score requires positive
evidence across all six dimensions.

---

## The log-scale helper

Most adoption/community signals use `_log_scale(value, midpoint, max_score)`:

```text
value == 0           → 0
value <= midpoint    → max_score * 0.5 * log10(value+1) / log10(midpoint+1)
value  > midpoint    → max_score * 0.5 + 0.5*max_score * log10(value/midpoint + 1) / log10(10)
```

**The midpoint earns ~half the max score, not the full max.** The full max is
reached around **10× the midpoint**. This compresses the top end so `serde`
(100M+ downloads) does not make every other crate look dead.

```text
log_scale(   500, 50_000, 15) =  4
log_scale( 5_000, 50_000, 15) =  5
log_scale(50_000, 50_000, 15) =  7   ← midpoint ≈ half
log_scale(100_000, 50_000, 15)= 11
log_scale(500_000, 50_000, 15)= 15   ← full max near 10× midpoint
```

A linear scale would give a 50k-download crate ~0.015/30 against `serde`'s
saturated 30; the log scale makes the mid-range meaningful and the top end
bounded.

---

## Adoption (30)

**Measures** whether real users depend on this crate. Downloads are the
strongest available production-use proxy (crates.io records every registry
resolution). Split into two sub-signals so a once-popular-but-now-dead crate
cannot hide behind historical totals.

| Sub-signal                 | Weight | Midpoint | Max reached near |
|----------------------------|:------:|:--------:|:---------------:|
| All-time downloads         | 15     | 50,000   | 500,000          |
| Recent (90-day) downloads  | 15     | 5,000    | 50,000           |

**Key signals**: `sig.downloads`, `sig.recent_downloads` (crates.io).

```text
score_adoption = min(30,
    log_scale(downloads,        50_000, 15)
  + log_scale(recent_downloads,  5_000, 15)
)
```

**Worked example** — a crate with 100,000 all-time downloads and 10,000
downloads in the last 90 days:

```text
log_scale(100_000, 50_000, 15) = 11
log_scale( 10_000,  5_000, 15) = 11
adoption = min(30, 11 + 11) = 22 / 30
```

A recent:all-time ratio above ~33% additionally emits the *strong recent
adoption* positive note.

**Edge cases**:
- 0 downloads → 0 points (brand-new or yanked crate).
- Very high all-time, near-zero recent → ~15/30; flags the crate as
  stale-but-historically-used. The maintenance dimension then drives the red flag.
- The 90-day window smooths day-of-publish spikes.

---

## Maintenance (25)

**Measures** ongoing care. A crate can be "done" (mature, no updates needed)
or "dead" (abandoned, bugs unfixed); this dimension combines **three**
independent signals to separate them. No single signal suffices: a
release-focused crate may not push to `git` often, and a git-active crate may
not cut a release often. Combining `updated_at` (release cadence),
`version_count` (release history), and `github_last_commit` (development
activity) catches both gaps.

| Sub-signal                       | Weight | Logic (days since)                      |
|----------------------------------|:------:|-----------------------------------------|
| Last crates.io update            | 12     | <90d → 12, <365d → 8, <730d → 4, else 0 |
| Version count                    | 8      | log-scale, midpoint 20                  |
| Last GitHub commit               | 5      | <30d → 5, <180d → 3, <365d → 1, else 0  |

**Key signals**: `sig.updated_at`, `sig.version_count`, `sig.github_last_commit`.
Version count uses `log_scale(version_count, 20, 8)`: 5→2, 20→4 (midpoint),
50→6, 200→8.

**Edge cases**:
- `updated_at` older than 730 days → 0 release-recency points *and* a "no
  release in N days" red flag (see [red-flags.md](red-flags.md)).
- `--skip-github` drops the GitHub-commit sub-signal (max becomes 20/25).
- A mature crate that simply doesn't need releases (e.g. `libc`) scores low on
  update-recency but high on version-count and overall maturity — read the
  *combined* dimension, not one sub-signal.

---

## Documentation (15)

**Measures** whether a new user can actually learn the crate. This is a flat
boolean checklist, not a log scale — docs either exist or they don't.

| Sub-signal                | Weight | Condition                                       |
|---------------------------|:------:|-------------------------------------------------|
| docs.rs build present     | 7      | HEAD request to docs.rs returns 200             |
| Description > 30 chars    | 3      | `sig.description` non-trivial                   |
| Documentation URL exists  | 3      | `sig.documentation` is an https URL             |
| Repository URL exists     | 2      | `sig.repository` non-empty                      |

**Key signals**: `sig.docs_rs_present`, `sig.description`,
`sig.documentation`, `sig.repository`.

**Edge cases**:
- A crate with a README but no docs.rs build loses 7 points — the strongest
  single deduction here, usually a failed docs.rs build (platform or feature
  issue).
- The description check is a crude proxy; a one-word description ("cache")
  scores 0 even when accurate.
- The docs.rs check is a HEAD probe; if docs.rs is down, the tool returns
  `("unknown")` and grants benefit of the doubt (see [api-endpoints.md](api-endpoints.md)).

---

## Maturity (15)

**Measures** whether the API has settled. Age alone is weak (a five-year-old
wrapper around an unstable 0.x API is common), so we combine age with version
stability and repository presence.

| Sub-signal                  | Weight | Logic                          |
|-----------------------------|:------:|--------------------------------|
| Age (since `created_at`)    | 6      | >3y → 6, >1y → 4, >90d → 2     |
| Stable version (≥ 1.0.0)    | 5      | major ≥ 1 → 5; major == 0 → 2  |
| Has source repository       | 4      | `sig.repository` non-empty     |

**Key signals**: `sig.created_at`, `sig.max_version`, `sig.repository`.

**Edge cases**:
- A pre-1.0 crate that is 4 years old still gets only 2/5 on the version
  signal — pre-1.0 implies *no semver stability guarantee*, penalized
  regardless of calendar age.
- `max_version` is parsed by splitting on `.` and reading the first integer;
  non-numeric pre-release metadata is ignored. An unparseable version (rare)
  scores 0 on the version sub-signal but keeps age + repo points.
- A crate can be mature (15/15) and still unmaintained — the dimensions are
  independent by design.

---

## Community (10)

**Measures** the contributor base, which proxies bus factor. One maintainer
means one bus; twenty means a project can survive attrition. Both sub-signals
use the log-scale helper (midpoints 500 stars / 10 contributors).

| Sub-signal            | Weight | Midpoint | Max reached near |
|-----------------------|:------:|:--------:|:---------------:|
| GitHub stars          | 6      | 500      | 5,000            |
| GitHub contributors   | 4      | 10       | 100              |

**Key signals**: `sig.github_stars`, `sig.github_contributors`.

**Edge cases**:
- `--skip-github` zeroes both sub-signals (community → 0/10).
- Contributor count is derived from the GitHub `Link` header pagination
  (`per_page=1&anon=true`); for repos with no GitHub URL it is 0.
- Stars lag real adoption — that is why Community is weighted only 10 vs
  Adoption's 30.
- A single-contributor crate with low adoption additionally triggers the
  *bus-factor* red flag.

---

## License (5)

**Measures** whether the license is adoptable under typical commercial/OSS
policy — the only dimension with hard categorical thresholds rather than a
continuous scale.

| Category            | Score | Licenses                                                   |
|---------------------|:-----:|------------------------------------------------------------|
| Permissive          | 5     | MIT, Apache-2.0, BSD-3-Clause, ISC, 0BSD, Zlib, Unicode-* |
| Weak copyleft       | 3     | MPL, LGPL                                                  |
| Strong copyleft     | 1     | GPL, AGPL, SSPL                                            |
| Unknown / missing   | 2     | empty or unrecognized                                      |

**Key signal**: `sig.license`. SPDX `OR`/`AND` expressions are split; any
permissive constituent grants 5 points (`MIT OR Apache-2.0` → 5). Dual `OR`
favors the most permissive term; `AND` (conjunction) is also split
(conservative). `Unicode-DFS-2016` and `Unicode-3.0` are explicitly permissive.

**Edge case — missing vs copyleft**: missing license scores *higher* (2) than
strong copyleft (1) because "unknown" is neutral pending investigation, whereas
copyleft is a known constraint. But missing license independently triggers a
medium-severity red flag (see [red-flags.md](red-flags.md)) — treat the 2 as
"neutral score, but investigate".

---

## Recommendation logic

The recommendation string is derived from grade + red flags, not the raw score:

```text
grade A, no advisory     → RECOMMENDED — strong fit, low risk
grade B, no advisory     → LIKELY SUITABLE — verify fit for your use case
grade C                  → ACCEPTABLE — investigate specific concerns
any grade + advisory     → BLOCK — unresolved security advisory
grade D + stale          → CAUTION — appears unmaintained
otherwise                → RISKY — significant concerns
```

A security advisory always overrides the grade to `BLOCK` regardless of the
numeric score — the single most important override rule.

---

## Tuning the weights

All weights are magic numbers in the `score_*` functions of
[`scripts/crate_eval.py`](../scripts/crate_eval.py). To re-tune: edit the
literal (e.g. `score += 12` in `score_maintenance`), update the matching
`max_for` entry in `format_score_human` so the bar-chart denominator stays
accurate, then re-run `eval` on known crates to sanity-check.

| Want more weight on…     | Bump                       | Side effect                                |
|--------------------------|----------------------------|--------------------------------------------|
| Bleeding-edge crates     | lower Adoption midpoint    | inflates marginal crates                   |
| Conservative picks       | raise Adoption midpoint    | penalizes genuinely good new crates        |
| Bus-factor sensitivity   | raise Community weight     | demotes single-author but high-quality libs|

Security is already absolute via the advisory→`BLOCK` override. **Do not** edit
this markdown to change behavior — the script is authoritative; if you change
it, update the tables here to match.

---

## Known limitations

- **Downloads can be gamed** — CI pipelines, Docker rebuilds, mirror
  duplication inflate counts.
- **GitHub stars lag real adoption** — heavily-used library crates may have
  surprisingly few stars.
- **New crates have a cold-start problem** — a week-old crate with perfect docs
  and a clean license can still score C because adoption/community are near
  zero. Check the maintainer's track record instead.
- **Private / internal crates are not scored** — invisible to this tool.
- **docs.rs and RustSec are scrape/probe-based** — no first-class JSON API for
  either; checks can break if those sites change layout.
- **Score ≠ fitness** — a crate can score A and be the wrong tool.

## Upstream sources

- [crates.io data access policy](https://crates.io/data-access) — download counts, version metadata
- [docs.rs](https://docs.rs) — documentation build status, version presence
- [GitHub REST API](https://docs.github.com/en/rest) — stars, contributors, last commit
- [RustSec Advisory Database](https://rustsec.org/) — known vulnerabilities
- [SPDX license list](https://spdx.org/licenses/) — license identifier semantics
