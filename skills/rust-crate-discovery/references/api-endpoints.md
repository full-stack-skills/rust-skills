# API Endpoints Reference

> Reference companion to [`SKILL.md`](../SKILL.md). The authoritative caller is
> [`scripts/crate_eval.py`](../scripts/crate_eval.py) (functions `fetch_*`).
> This document lists every external endpoint the tool touches, the required
> headers, rate limits, and the response fields actually consumed. If the tool
> and this doc disagree, the **script is authoritative**.

The tool queries four data sources. None of them are paid, but three require a
`User-Agent` header or they reject the request.

| Source    | Base URL                       | Auth         | Rate limit (anonymous) | Used for                       |
|-----------|--------------------------------|--------------|:----------------------:|--------------------------------|
| crates.io | `https://crates.io/api/v1`     | none         | ~1 req/sec             | search, metadata, downloads    |
| docs.rs   | `https://docs.rs`              | none         | generous               | documentation build presence   |
| GitHub    | `https://api.github.com`       | optional token | 60 req/hour          | stars, contributors, last push |
| RustSec   | `https://rustsec.org`          | none         | generous               | security advisories            |

---

## crates.io API

The primary source. crates.io publishes a JSON REST API documented under their
[data-access policy](https://crates.io/data-access). Download counts, version
history, license, repository, and description all come from here.

### Requirements

```http
GET https://crates.io/api/v1/...
User-Agent: rust-crate-discovery-agent/1.0 (https://github.com/full-stack-skills/rust-skills)
Accept: application/json
```

- **`User-Agent` is mandatory.** Requests without it (or with a generic
  library UA) are rejected with HTTP 403. crates.io asks that the UA identify
  the tool and include a contact URL.
- **No API token** is required for read-only public endpoints. A token raises
  the rate limit but the script does not use one.
- **Rate limit**: approximately 1 request/sec anonymous. The script spaces
  multi-crate evaluations with `time.sleep(0.2)` (see `cmd_compare`) and
  inserts `time.sleep(0.1)` between GitHub/RustSec sub-fetches.

### Endpoints used

#### Search crates

```http
GET /crates?q=<query>&per_page=<N>&category=<C>
```

- `q` — search terms (URL-encoded); matches name, description, keywords.
- `per_page` — capped at 100 by the tool (`min(limit, 100)`).
- `category` — optional; e.g. `database`, `web-programming::http-client`.

```json
{
  "crates": [
    {
      "id": "sea-orm",
      "name": "sea-orm",
      "description": "...",
      "max_version": "1.1.0",
      "downloads": 1843566,
      "recent_downloads": 244103,
      "updated_at": "2026-06-18T..."
    }
  ],
  "meta": { "total": 42 }
}
```

Consumed fields: `id`, `description`, `max_version`, `downloads`,
`recent_downloads`, `updated_at` (rendered in the search table).

#### Crate detail

```http
GET /crates/<name>
```

Returns the full crate object plus an embedded `versions[]` array. This is the
single richest endpoint and drives `fetch_crates_io_detail()`.

```json
{
  "crate": {
    "name": "rbatis",
    "description": "...",
    "repository": "https://github.com/rbatis/rbatis",
    "homepage": "...",
    "documentation": "https://docs.rs/rbatis",
    "keywords": ["orm", "sql"],
    "categories": ["database"],
    "license": "Apache-2.0",
    "max_version": "4.9.6",
    "newest_version": "4.9.6",
    "rust_version": "1.75",
    "downloads": 657356,
    "recent_downloads": 19938,
    "created_at": "2019-...",
    "updated_at": "2026-...",
    "exact_match": true
  },
  "versions": [ { "num": "4.9.6", ... }, ... ]
}
```

Consumed fields (mapped onto `CrateSignals`): `description`, `repository`,
`homepage`, `documentation`, `keywords`, `categories`, `license`,
`max_version`, `newest_version`, `rust_version`, `downloads`,
`recent_downloads`, `created_at`, `updated_at`, `exact_match`, and
`len(versions)` for `version_count`.

#### Version-specific (not currently called)

```http
GET /crates/<name>/<version>
```

Returns per-version metadata: `license`, `features`, `yanked`, `rust_version`.
The script does **not** call this today (it uses `max_version` from the detail
endpoint), but it is documented here for future feature work (e.g. yank
detection, feature-gate inspection).

#### Owners (not currently called)

```http
GET /crates/<name>/owners
```

Returns the maintainer list. Not called by the current tool; bus-factor
detection currently relies on GitHub contributor counts instead. Documented for
completeness.

### Rate-limit mitigation

- The tool spaces requests 100–200 ms apart via `time.sleep`.
- For bulk evaluation of many crates, prefer `compare` (which handles spacing)
  over a shell loop of `eval` calls.
- If you hit 429s, slow down or request a crates.io API token and inject it
  via the `Authorization` header (requires a small script edit).

### Error handling

- HTTP 404 on `/crates/<name>` → `fetch_crates_io_detail` returns `None`; the
  CLI prints "Crate '<name>' not found on crates.io" and exits 1.
- Other HTTP errors propagate as exceptions (no silent swallow on crates.io
  paths, unlike the GitHub/RustSec best-effort fetchers).

---

## docs.rs

docs.rs is the canonical host for Rust crate documentation. It builds docs on
publish, so a successful build is strong evidence the crate compiles and
exposes a documented API. There is **no official JSON API** for build status;
the tool probes the URL directly.

### Probe

```http
HEAD https://docs.rs/crate/<name>/
HEAD https://docs.rs/crate/<name>/<version>/
User-Agent: rust-crate-discovery-agent/1.0 (...)
```

- HTTP 200 → docs built; `(present=True, status="ok")`.
- HTTP 404 → no build; `(present=False, status="unknown")`.
- HTTP 5xx or other → docs.rs is having issues; the tool grants benefit of the
  doubt: `(present=True, status="unknown")`. This avoids penalizing a crate
  during a docs.rs outage.
- Network exception → `(present=False, status="unknown")`.

### What it tells us

The 7-point documentation sub-score hinges entirely on this probe (see
[scoring-rubric.md](scoring-rubric.md#documentation-15)). A 404 here is the
single largest documentation deduction.

### Limitations

- docs.rs builds docs **on publish**, so there is a lag of minutes (occasionally
  longer for large crates) between a release appearing on crates.io and its
  docs being available. A brand-new release may transiently show "no docs".
- A failed build (e.g. due to a platform-specific dependency) means docs.rs has
  no entry even though the crate is real. Check the repo's own rendered docs.
- Build *status* (ok vs. failed) is not reliably distinguishable via HEAD
  alone; the script records `"unknown"` for any non-200/non-404 case.

---

## GitHub API

Used for community signals (stars, contributors) and the last-commit recency
signal. GitHub has the strictest anonymous rate limit of the four sources.

### Requirements

```http
GET https://api.github.com/...
User-Agent: rust-crate-discovery-agent/1.0 (...)
Accept: application/json
```

- **`User-Agent` is mandatory.** Omitting it returns HTTP 403.
- **Rate limit**: 60 requests/hour anonymous, 5,000/hour with a token
  (authenticated via `Authorization: Bearer <token>`).
- The script does **not** send a token by default. To raise the limit:

  ```bash
  export GITHUB_TOKEN=ghp_your_personal_access_token
  ```

  …and edit `_get`/`fetch_github` to attach the header. (Token usage is out of
  scope for the bundled script but documented here for operators running bulk
  evaluations.)

### Extracting owner/repo

The script parses the crates.io `repository` URL:

```python
_gh_owner_repo("https://github.com/rbatis/rbatis")  → ("rbatis", "rbatis")
```

- Trailing slashes and `.git` suffixes are stripped.
- Non-`github.com` URLs (GitLab, sourcehut, self-hosted) return `None` and
  GitHub signals are silently skipped (stars/contributors/last_commit stay 0).
  This is a known limitation: a GitLab-hosted crate will score lower on
  Community regardless of real popularity.

### Endpoints used

#### Repository metadata

```http
GET /repos/<owner>/<repo>
```

```json
{
  "stargazers_count": 2103,
  "forks_count": 312,
  "open_issues_count": 87,
  "pushed_at": "2026-07-15T..."
}
```

Consumed fields: `stargazers_count` → `github_stars`, `forks_count` →
`github_forks`, `open_issues_count` → `github_open_issues`, `pushed_at`
(truncated to `YYYY-MM-DD`) → `github_last_commit`.

#### Contributor count

```http
GET /repos/<owner>/<repo>/contributors?per_page=1&anon=true
```

The total contributor count is read from the `Link` response header (GitHub
paginates contributors). The script parses `page=N>; rel="last"` from `Link`;
if no `rel="last"` link is present (small repos), it counts the JSON body
length instead.

```http
Link: <...?page=42>; rel="last", <...?page=1>; rel="first"
→ github_contributors = 42
```

- `per_page=1` minimizes payload size; only the header is needed.
- `anon=true` includes anonymous (unauthenticated) contributors in the count.
- On any exception, `github_contributors` stays 0 — which can falsely trigger
  the single-maintainer red flag. If you suspect rate-limiting, re-run with
  `GITHUB_TOKEN` set.

### Rate-limit mitigation

- `--skip-github` skips both calls entirely (faster, but Community → 0/10 and
  Maintenance loses the commit-recency sub-signal).
- For `compare` of many crates, expect ~2 GitHub calls per crate; 30 crates
  hits the anonymous hourly ceiling.
- On 403 (rate limited), the fetchers swallow the exception and leave signals
  at 0 rather than crashing the whole evaluation.

---

## RustSec Advisory Database

RustSec tracks known vulnerabilities in the Rust ecosystem. Unlike the other
three sources, it has **no stable per-crate JSON API** — the tool scrapes the
HTML package page.

### Probe

```http
GET https://rustsec.org/packages/<crate>.html
User-Agent: rust-crate-discovery-agent/1.0 (...)
```

The response body is regex-scanned for advisory IDs:

```python
re.findall(r"RUSTSEC-\d{4}-\d{2,6}", body)
```

Each unique ID becomes an entry in `sig.advisories`:

```python
{"id": "RUSTSEC-2024-0344",
 "url": "https://rustsec.org/advisories/RUSTSEC-2024-0344.html"}
```

- A page containing "No advisories" or "404" → empty list (crate has no known
  advisories, or isn't in the DB).
- Any HTTP error → empty list (treated as "no advisories found", not "safe").

### Related URLs (for manual follow-up)

| Resource                           | URL                                                     |
|------------------------------------|---------------------------------------------------------|
| Per-package page                   | `https://rustsec.org/packages/<crate>.html`             |
| Per-advisory page                  | `https://rustsec.org/advisories/<RUSTSEC-YYYY-NNNN>.html` |
| Advisory DB repo (TOML)            | `https://github.com/rustsec/advisory-db`                |

### Authoritative alternative: `cargo audit`

The scrape is a *convenience* signal. For authoritative results, run
[`cargo audit`](https://github.com/rustsec/rustsec/tree/main/cargo-audit)
locally against a real `Cargo.lock`:

```bash
cargo install cargo-audit
cargo audit
```

`cargo audit` reads the same advisory-db but resolves against your *exact*
locked versions, including transitive dependencies the top-level crate pulls
in. The scrape-based check in this tool cannot see transitive advisories —
always run `cargo audit` as the final gate before shipping.

### Programmatic alternative: advisory-db TOML

For programmatic use without scraping, clone
[rustsec/advisory-db](https://github.com/rustsec/advisory-db) and read the
TOML files directly under `crates/<name>/`. Each file is one advisory with
structured fields (`id`, `package`, `date`, `versions`, `aliases`,
`patched_versions`, `severity`). This is more robust than HTML scraping but
requires a local clone.

---

## Data freshness

| Source    | Freshness                                                        |
|-----------|------------------------------------------------------------------|
| crates.io | Real-time — download counters and metadata update on publish.    |
| docs.rs   | Builds on publish; lag of minutes (longer for large crates).     |
| GitHub    | Real-time — `pushed_at` and stars/contributors update immediately. |
| RustSec   | Advisory DB updated as CVEs are filed; may lag upstream disclosure by days to weeks. |

> **Security lag caveat**: RustSec advisories are filed by maintainers and
> researchers after a disclosure. A crate with *no* advisory today may have
> an undisclosed vulnerability. Absence of a flag is not proof of safety —
> pair this tool's check with `cargo audit` in CI.

## Common failure modes and mitigations

| Symptom                                | Likely cause                          | Mitigation                          |
|----------------------------------------|---------------------------------------|-------------------------------------|
| 403 from crates.io                     | Missing/blocked `User-Agent`          | Confirm the script's UA is intact   |
| 403 from GitHub, stars=0               | Anonymous rate limit exhausted        | Set `GITHUB_TOKEN` or use `--skip-github` |
| All GitHub signals 0 on a known repo   | Non-`github.com` `repository` URL     | Manual lookup; known limitation     |
| Advisory list always empty             | rustsec.org markup changed            | Fall back to `cargo audit`          |
| docs.rs "present" during an outage     | 5xx path grants benefit of the doubt  | Re-check after outage clears        |
| Intermittent timeouts                  | Network or upstream slowness          | Raise `--timeout` (edit `_get`)     |

## Upstream sources

- [crates.io data access policy & API](https://crates.io/data-access)
- [docs.rs](https://docs.rs) / [docs.rs source](https://github.com/rust-lang/docs.rs)
- [GitHub REST API reference](https://docs.github.com/en/rest)
- [GitHub rate limits](https://docs.github.com/en/rest/overview/resources-in-the-rest-api#rate-limiting)
- [RustSec Advisory Database](https://rustsec.org/)
- [rustsec/advisory-db repository](https://github.com/rustsec/advisory-db)
- [cargo-audit](https://github.com/rustsec/rustsec/tree/main/cargo-audit)
