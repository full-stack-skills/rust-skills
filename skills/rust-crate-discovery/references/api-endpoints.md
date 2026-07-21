# API Endpoints Reference

> Reference companion to [`SKILL.md`](../SKILL.md). The authoritative caller is
> [`scripts/crate_eval.py`](../scripts/crate_eval.py) (`fetch_*` functions). If
> the tool and this doc disagree, the **script is authoritative**.

The tool queries four sources. None are paid, but three reject requests
without a `User-Agent` header.

| Source    | Base URL                   | Auth           | Rate limit (anon)   | Used for                       |
|-----------|----------------------------|----------------|:-------------------:|--------------------------------|
| crates.io | `https://crates.io/api/v1` | none           | ~1 req/sec          | search, metadata, downloads    |
| docs.rs   | `https://docs.rs`          | none           | generous            | documentation build presence   |
| GitHub    | `https://api.github.com`   | optional token | 60 req/hour         | stars, contributors, last push |
| RustSec   | `https://rustsec.org`      | none           | generous            | security advisories            |

---

## crates.io API

The primary source — a JSON REST API under the
[data-access policy](https://crates.io/data-access). Download counts, version
history, license, repository, and description all come from here.

### Requirements

```http
GET https://crates.io/api/v1/...
User-Agent: rust-crate-discovery-agent/1.0 (https://github.com/full-stack-skills/rust-skills)
Accept: application/json
```

- **`User-Agent` is mandatory** — omitting it (or sending a generic library UA)
  returns HTTP 403. crates.io asks that the UA identify the tool and a contact URL.
- **No token** required for read-only public endpoints; a token raises the
  rate limit but the script does not send one.
- **Rate limit ~1 req/sec anonymous.** The script spaces multi-crate runs with
  `time.sleep(0.2)` (see `cmd_compare`) and inserts `time.sleep(0.1)` between
  GitHub/RustSec sub-fetches.

### Endpoints used

**Search** — `GET /crates?q=<query>&per_page=<N>&category=<C>`

- `q` URL-encoded search terms (matches name, description, keywords).
- `per_page` capped at 100 by the tool (`min(limit, 100)`).
- `category` optional, e.g. `database`, `web-programming::http-client`.

Returns `{ "crates": [ {...} ], "meta": { "total": N } }`. Consumed per-crate
fields: `id`, `description`, `max_version`, `downloads`,
`recent_downloads`, `updated_at` (rendered in the search table).

**Crate detail** — `GET /crates/<name>`

The richest endpoint; drives `fetch_crates_io_detail()`. Returns
`{ "crate": {...}, "versions": [ {...} ] }`. The `crate` object fields consumed
(mapped onto `CrateSignals`):

```text
description, repository, homepage, documentation, keywords, categories,
license, max_version, newest_version, rust_version, downloads,
recent_downloads, created_at, updated_at, exact_match
```

`version_count` is derived as `len(versions)`.

**Version-specific** — `GET /crates/<name>/<version>` *(not currently called)*

Per-version `license`, `features`, `yanked`, `rust_version`. Not used today (the
script takes `max_version` from the detail endpoint); documented for future
feature work (yank detection, feature-gate inspection).

**Owners** — `GET /crates/<name>/owners` *(not currently called)*

Maintainer list. Not used; bus-factor detection currently relies on GitHub
contributor counts instead.

### Rate-limit mitigation & errors

- Space requests 100–200 ms apart (the tool does this for you).
- For bulk runs, prefer `compare` (handles spacing) over a shell loop of `eval`.
- On 429s, slow down or request a crates.io token and inject an
  `Authorization` header (requires a small script edit).
- HTTP 404 on `/crates/<name>` → `fetch_crates_io_detail` returns `None`; the
  CLI prints "Crate '<name>' not found" and exits 1. Other HTTP errors
  propagate (unlike the GitHub/RustSec best-effort fetchers, which swallow).

---

## docs.rs

The canonical Rust crate documentation host. It builds docs on publish, so a
successful build is strong evidence the crate compiles and exposes a
documented API. **No official JSON API** for build status — the tool probes.

### Probe

```http
HEAD https://docs.rs/crate/<name>/
HEAD https://docs.rs/crate/<name>/<version>/
User-Agent: rust-crate-discovery-agent/1.0 (...)
```

- HTTP 200 → `(present=True, status="ok")`.
- HTTP 404 → `(present=False, status="unknown")`.
- HTTP 5xx/other → `(present=True, status="unknown")` — grants benefit of the
  doubt so a docs.rs outage doesn't penalize the crate.
- Network exception → `(present=False, status="unknown")`.

### What it tells us

The 7-point documentation sub-score hinges on this probe (see
[scoring-rubric.md](scoring-rubric.md#documentation-15)). A 404 is the single
largest documentation deduction.

### Limitations

- docs.rs builds **on publish**, so there is a lag of minutes (longer for large
  crates) between a crates.io release and its docs. A brand-new release may
  transiently show "no docs".
- A failed build (platform-specific dependency, feature issue) means no docs.rs
  entry even though the crate is real — check the repo's own rendered docs.
- Build *status* (ok vs failed) isn't reliably distinguishable via HEAD alone;
  the script records `"unknown"` for any non-200/non-404 case.

---

## GitHub API

Community signals (stars, contributors) and the last-commit recency signal.
GitHub has the strictest anonymous rate limit of the four sources.

### Requirements

```http
GET https://api.github.com/...
User-Agent: rust-crate-discovery-agent/1.0 (...)
Accept: application/json
```

- **`User-Agent` mandatory** — omitting it returns HTTP 403.
- **Rate limit**: 60 req/hour anonymous, 5,000/hour with a token
  (`Authorization: Bearer <token>`).
- The script does **not** send a token by default. To raise the limit:

  ```bash
  export GITHUB_TOKEN=ghp_your_personal_access_token
  ```

  …and edit `_get`/`fetch_github` to attach the header. (Token usage is out of
  scope for the bundled script but documented for bulk-evaluation operators.)

### Extracting owner/repo

The script parses the crates.io `repository` URL via `_gh_owner_repo`:

```python
_gh_owner_repo("https://github.com/rbatis/rbatis")  → ("rbatis", "rbatis")
```

Trailing slashes and `.git` suffixes are stripped. Non-`github.com` URLs
(GitLab, sourcehut, self-hosted) return `None` and GitHub signals are silently
skipped (stars/contributors/last_commit stay 0). **Known limitation:** a
GitLab-hosted crate scores lower on Community regardless of real popularity.

### Endpoints used

**Repository metadata** — `GET /repos/<owner>/<repo>`

Returns `stargazers_count`, `forks_count`, `open_issues_count`, `pushed_at`.
Mapped: stars → `github_stars`, forks → `github_forks`, open issues →
`github_open_issues`, `pushed_at` (truncated to `YYYY-MM-DD`) →
`github_last_commit`.

**Contributor count** — `GET /repos/<owner>/<repo>/contributors?per_page=1&anon=true`

Total count is read from the `Link` response header (GitHub paginates
contributors): parse `page=N>; rel="last"`. If no `rel="last"` link (small
repos), count the JSON body length instead.

```http
Link: <...?page=42>; rel="last", <...?page=1>; rel="first"
→ github_contributors = 42
```

`per_page=1` minimizes payload; `anon=true` includes anonymous contributors. On
any exception, `github_contributors` stays 0 — which can *falsely* trigger the
single-maintainer red flag. If you suspect rate-limiting, re-run with
`GITHUB_TOKEN` set.

### Rate-limit mitigation

- `--skip-github` skips both calls (faster, but Community → 0/10 and
  Maintenance loses the commit-recency sub-signal).
- `compare` of many crates uses ~2 GitHub calls each; 30 crates hits the
  anonymous hourly ceiling.
- On 403 (rate limited), fetchers swallow the exception and leave signals at 0
  rather than crashing the whole evaluation.

---

## RustSec Advisory Database

Tracks known Rust ecosystem vulnerabilities. Unlike the other sources, it has
**no stable per-crate JSON API** — the tool scrapes the HTML package page.

### Probe

```http
GET https://rustsec.org/packages/<crate>.html
User-Agent: rust-crate-discovery-agent/1.0 (...)
```

The body is regex-scanned for advisory IDs: `re.findall(r"RUSTSEC-\d{4}-\d{2,6}", body)`.
Each unique ID becomes `{"id": "RUSTSEC-YYYY-NNNN",
"url": "https://rustsec.org/advisories/RUSTSEC-YYYY-NNNN.html"}`.

- Page contains "No advisories" or "404" → empty list (no known advisories, or
  not in the DB).
- Any HTTP error → empty list (treated as "none found", *not* "safe").

### Related URLs (manual follow-up)

| Resource                | URL                                                        |
|-------------------------|------------------------------------------------------------|
| Per-package page        | `https://rustsec.org/packages/<crate>.html`                |
| Per-advisory page       | `https://rustsec.org/advisories/<RUSTSEC-YYYY-NNNN>.html`  |
| Advisory DB repo (TOML) | `https://github.com/rustsec/advisory-db`                   |

### Authoritative alternative: `cargo audit`

The scrape is a *convenience* signal. For authoritative results run
[`cargo audit`](https://github.com/rustsec/rustsec/tree/main/cargo-audit)
against a real `Cargo.lock`:

```bash
cargo install cargo-audit
cargo audit
```

It reads the same advisory-db but resolves your *exact* locked versions,
including transitive dependencies. The scrape-based check cannot see transitive
advisories — always run `cargo audit` as the final pre-shipping gate.

### Programmatic alternative: advisory-db TOML

For programmatic use without scraping, clone
[rustsec/advisory-db](https://github.com/rustsec/advisory-db) and read the TOML
files under `crates/<name>/`. Each is one advisory with structured fields
(`id`, `package`, `date`, `versions`, `patched_versions`, `severity`). More
robust than HTML scraping but requires a local clone.

---

## Data freshness

| Source    | Freshness                                                                |
|-----------|--------------------------------------------------------------------------|
| crates.io | Real-time — counters and metadata update on publish.                     |
| docs.rs   | Builds on publish; lag of minutes (longer for large crates).             |
| GitHub    | Real-time — `pushed_at`, stars, contributors update immediately.         |
| RustSec   | Advisory DB updated as CVEs are filed; may lag upstream disclosure by days-weeks. |

> **Security lag caveat:** advisories are filed *after* a disclosure. A crate
> with no advisory today may have an undisclosed vulnerability. Absence of a
> flag is not proof of safety — pair this check with `cargo audit` in CI.

## Common failure modes

| Symptom                              | Likely cause                    | Mitigation                          |
|--------------------------------------|---------------------------------|-------------------------------------|
| 403 from crates.io                   | Missing/blocked `User-Agent`    | Confirm the script's UA is intact   |
| 403 from GitHub, stars=0             | Anonymous rate limit exhausted  | Set `GITHUB_TOKEN` or `--skip-github` |
| All GitHub signals 0 on a known repo | Non-`github.com` `repository`   | Manual lookup; known limitation     |
| Advisory list always empty           | rustsec.org markup changed      | Fall back to `cargo audit`          |
| docs.rs "present" during an outage   | 5xx grants benefit of the doubt | Re-check after outage clears        |
| Intermittent timeouts                | Network/upstream slowness       | Raise `--timeout` (edit `_get`)     |

## Upstream sources

- [crates.io data access policy & API](https://crates.io/data-access)
- [docs.rs](https://docs.rs) / [docs.rs source](https://github.com/rust-lang/docs.rs)
- [GitHub REST API reference](https://docs.github.com/en/rest)
- [GitHub rate limits](https://docs.github.com/en/rest/overview/resources-in-the-rest-api#rate-limiting)
- [RustSec Advisory Database](https://rustsec.org/)
- [rustsec/advisory-db repository](https://github.com/rustsec/advisory-db)
- [cargo-audit](https://github.com/rustsec/rustsec/tree/main/cargo-audit)
