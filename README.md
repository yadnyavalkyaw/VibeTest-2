# VibeTest

**An authorization-gated, read-only security scanner for "vibe-coded" web applications.**

VibeTest crawls a website you own (or a public GitHub repository), checks it for the
security mistakes AI-assisted apps actually make, and reports each one in plain English
with **evidence** and a **fix suggestion** — aimed at a non-expert owner, not a
professional pentester.

| | |
|---|---|
| **Stage** | Phase 1 — scan → detect → report (auto-fix is future work) |
| **Type** | University final-year major project, team of 3, one semester |
| **Stack** | Python 3.12+, Typer CLI, FastAPI local dashboard, SQLite, Jinja2 reports |
| **Cost** | Zero. Every dependency and service is free/open-source. |
| **Checks** | 10 detectors, 1 technology fingerprinter |
| **Tests** | 124 pytest tests, all passing |
| **Evaluation** | 5 owned fixtures, 20 ground-truth categories, precision/recall/F1 = 1.00 |

---

## Table of contents

1. [Why this project exists](#why-this-project-exists)
2. [What it checks](#what-it-checks)
3. [What it deliberately does *not* do](#what-it-deliberately-does-not-do)
4. [Quick start (run it on your machine)](#quick-start-run-it-on-your-machine)
5. [Optional components](#optional-components)
6. [Try it in 60 seconds](#try-it-in-60-seconds)
7. [Demo targets included in the repo](#demo-targets-included-in-the-repo)
8. [CLI reference](#cli-reference)
9. [Local dashboard](#local-dashboard)
10. [Configuration](#configuration-vibetesttoml)
11. [Evaluation harness](#evaluation-harness)
12. [Running the tests](#running-the-tests)
13. [Project layout](#project-layout)
14. [Security model (the four hard rules)](#security-model-the-four-hard-rules)
15. [Limitations and roadmap](#limitations-and-roadmap)
16. [Troubleshooting](#troubleshooting)
17. [Documentation map](#documentation-map)

---

## Why this project exists

Apps built quickly with AI assistants and shipped to free hosting (Vercel, Netlify,
Render) have a very consistent weakness profile. In practice the same handful of
mistakes show up again and again:

- an `.env` file or a **service-role key committed into the shipped JavaScript bundle**
- a **backend database readable by anyone** (Supabase RLS switched off — the
  CVE-2025-48757 pattern — or open Firebase Realtime Database rules)
- **missing security headers** (CSP, HSTS, `X-Frame-Options`, …)
- **source maps and dev builds** left switched on in production
- **known-vulnerable npm packages** loaded by the site
- project files that should never have been deployed at all (`.git/`, backups, configs)

The person who owns such an app is usually a beginner, has no security background, and
cannot afford a commercial scanner or a consultant. Existing tools are either noisy,
expensive, or need expertise to interpret. VibeTest is deliberately narrow: it checks
exactly this class of real-world failure, for free, read-only, and explains the result in
language a non-expert can act on.

## What it checks

| Detector | What it finds | Real-world example |
|---|---|---|
| `headers` | Missing or weak HTTP security headers (CSP, HSTS, `X-Frame-Options`, `X-Content-Type-Options`, referrer policy) | Site can be framed or downgraded without warning |
| `exposed_files` | Reachable sensitive files: `.env`, `.git/HEAD`, configs, dumps | `/.env` served as plain text → full secret leak |
| `secrets_bundle` | Secrets embedded in the site's own JavaScript bundles, with JWT role decoding for Supabase keys | A `service_role` key shipped in `app.js` → full database read/write |
| `source_maps` | Published `*.map` files | Source maps expose the entire original source tree |
| `debug_config` | Development/debug build markers in production assets | React/Vite dev bundles with source paths and test config |
| `deps_osv` | Known CVEs in the JS packages the site actually loads (free [OSV.dev](https://osv.dev) lookups, no API key) | `@babel/core@7.28.5` → GHSA-4x5r-pxfx-6jf8, fixed in 7.29.6+ |
| `supabase_rls` | Tables readable **without any authentication** (flagship check) | `profiles` table readable with the public anon key |
| `firebase_rules` | Realtime Database readable by unauthenticated clients | `/.json` returns live data instead of a permission error |
| `repo_sensitive_files` | Secrets committed into a **public GitHub repository** (repo mode) | `.env` and `serviceAccountKey.json` in a public repo |
| `repo_deps` | Vulnerable package versions pinned in lockfiles (repo mode) | Old `lodash` / `minimist` in `package-lock.json` |

Plus:

- **Technology fingerprinter** — recognises framework, hosting platform and backend
  services from headers, HTML and bundles.
- **Plain-English explanations** — every finding gets a "what this means / why it matters
  / how to fix it" explanation. Deterministic templates by default, optional local LLM
  (Ollama) with `--llm`.
- **Self-contained HTML report** — one file, no external assets, includes evidence.
- **PDF export** — same report as a downloadable A4 PDF.
- **Local dashboard** — scan history, severity overview, finding cards, report view.
- **Two target modes** — a live URL, or a public GitHub repository (static analysis).

## What it deliberately does *not* do

Being explicit about this matters: VibeTest is an **exposure-surface and misconfiguration
scanner**, not a network scanner and not an exploitation tool.

| Layer | Typical tools | VibeTest |
|---|---|---|
| Open ports, service/OS fingerprinting | nmap, masscan | **No** — and it is the right call: an app on Vercel/Netlify has no ports of its own. Port scanning it would scan the *platform's* shared edge, not the app, and would break the platform's terms. |
| TLS certificates / protocol config | testssl.sh, sslyze | **No** (planned; the finding category already exists) |
| HTTP security headers | securityheaders.com, ZAP | **Yes** |
| Cookie flags (`Secure`/`HttpOnly`/`SameSite`) | ZAP, Burp | **No** (planned) |
| CORS misconfiguration | custom scripts, Burp | **No** (planned) |
| Deployment/config leaks, source maps, debug builds | manual | **Yes** |
| Dependency CVEs (SCA) | npm audit, Dependabot | **Yes** (OSV.dev) |
| Backend-as-a-Service access control (Supabase/Firebase) | few tools cover this | **Yes** — this is the project's niche |
| Login/auth flows, business logic, IDOR | Burp, manual pentest | **No** |
| Injection testing (SQLi/XSS payloads), exploitation | sqlmap, ZAP active scan | **No, by design** — the tool never sends attack payloads |
| Static code analysis (taint analysis) | Semgrep, CodeQL | **No** (repo mode = committed secrets + pinned CVE versions) |
| Automatic remediation | — | **No** (explicitly out of scope for Phase 1) |

VibeTest is **complementary** to nmap/ZAP/Burp, not a replacement. On the app class it
targets, it finds the things those tools usually miss (leaked keys, open serverless
databases) without generating noise.

---

## Quick start (run it on your machine)

Everything below is also the recommended way to run the project **on someone else's
computer** (teammate, lab machine, evaluator's laptop). Nothing is machine-specific: the
configuration uses relative paths, and all per-machine data (virtualenv, scan database,
generated reports) is git-ignored.

### 0. Prerequisites

| Requirement | Notes |
|---|---|
| **Python 3.12 or newer** | Hard requirement (`pyproject.toml` → `requires-python`). Check with `python --version`. |
| **Git** (optional) | Only for `git clone` — you can also download a ZIP from the repo page. |
| **Internet** | Needed once for `pip install`, and later for OSV.dev lookups and GitHub downloads. Localhost scanning itself works offline. |

### 1. Get the code

```bash
git clone https://github.com/sudhendrak04/VibeTest.git
cd VibeTest
```

### 2. Create a virtual environment and install

**Windows (PowerShell / CMD):**

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

**macOS / Linux:**

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e ".[dev]"
```

The `dev` extra adds `pytest`. The project is installed in **editable** mode, so
`vibetest` becomes a command inside `.venv\Scripts` (Windows) or `.venv/bin`
(macOS/Linux).

> **PowerShell tip:** you do **not** need to activate the virtualenv. Calling the
> executables by full path (`.venv\Scripts\vibetest.exe`) works and avoids the
> "running scripts is disabled" execution-policy error entirely. If you prefer to
> activate: `.venv\Scripts\Activate.ps1` (and `.\.venv\Scripts\Activate.ps1` in
> PowerShell), then just use `vibetest` and `python`.

### 3. Verify the installation

```powershell
.venv\Scripts\python.exe -m pytest -q
```

Expected: **`124 passed`** (takes ~10 s). If you skipped the optional Playwright extra,
you will see `123 passed, 1 skipped` — that single skip is the real-Chromium PDF test.

### 4. Run your first scan

```powershell
# Terminal 1 — serve the included demo site
python -m http.server 8125 --bind 127.0.0.1 --directory targets\demo_site

# Terminal 2 — scan it
.venv\Scripts\vibetest.exe scan http://127.0.0.1:8125/ --out reports\demo_site.html
```

You should see a severity-sorted table of findings, the detected technology, and a
self-contained HTML report written to `reports/demo_site.html`. Open it in a browser.

### 5. (Optional) Start the dashboard

```powershell
.venv\Scripts\vibetest.exe serve
```

Open **http://127.0.0.1:8000** — paste a URL or a `github.com/owner/repo` reference,
tick the authorization box, and scan. History and reports are stored in a local SQLite
file (`vibetest.db`).

> **Always run commands from the repository root.** `vibetest.toml` is read from the
> current working directory.

### Copying the project to another machine instead of cloning

Copy the folder across, but **delete `.venv` first** — virtualenvs are not portable.
Everything else travels fine. Never commit your own `vibetest.db` or `reports/`
(they are git-ignored, which is why the clone will not contain them).

---

## Optional components

VibeTest runs with **only** Python. Three external pieces are *soft dependencies*: if
they are missing, the tool degrades gracefully and tells you what it skipped.

| Component | Install (free) | What it adds | Behaviour without it |
|---|---|---|---|
| **Playwright** (recommended) | `pip install -e ".[dev,crawl]"` then `python -m playwright install chromium` (~350 MB) | Renders JavaScript-built SPAs (finds keys that only exist after JS runs) **and** powers PDF export | Keeps the raw HTML; PDF button falls back to the browser's print dialog; 1 test skips |
| **Katana** | Prebuilt binary from [ProjectDiscovery releases](https://github.com/projectdiscovery/katana/releases), or `go install github.com/projectdiscovery/katana/cmd/katana@latest`; then ensure `katana` is on `PATH` or set `katana_bin` in `vibetest.toml` | Crawls the site to discover more pages/endpoints | Falls back to fetching the entry page only |
| **Ollama** | Install [Ollama](https://ollama.com), `ollama pull qwen2.5:3b`, then set `ollama_model` in `vibetest.toml` to a tag you have | AI-written explanations via `--llm` | Deterministic template explanations (the default) |

Notes:

- On Linux, Playwright may also need system libraries: `python -m playwright install-deps`.
- The committed `vibetest.toml` references the Ollama models installed on the original
  author's machine (`qwen2.5:3b` / `mistral:latest`). On a different machine, either
  change those two lines to tags you have, or simply keep using templates — the fallback
  is automatic.
- PDF export and SPA rendering share the same `[crawl]` extra.
- Ollama explanation results are cached per finding in `.llm_cache.json` (safe to delete;
  a warm cache turns a multi-minute explanation pass into seconds).

---

## Try it in 60 seconds

The repository ships with five **deliberately vulnerable, owned** demo targets — no
third-party site is ever contacted.

```powershell
# 1) Static site: leaked keys in the bundle, reachable .env, source map, dev build, CVEs
python -m http.server 8125 --bind 127.0.0.1 --directory targets\demo_site
.venv\Scripts\vibetest.exe scan http://127.0.0.1:8125/

# 2) Single-page app: the planted secrets are injected by JavaScript,
#    so they are INVISIBLE without rendering (5 findings) and appear WITH it (9 findings)
python -m http.server 8131 --bind 127.0.0.1 --directory targets\demo_spa
.venv\Scripts\vibetest.exe scan http://127.0.0.1:8131/ --no-render   # shell only
.venv\Scripts\vibetest.exe scan http://127.0.0.1:8131/               # with rendering

# 3) Supabase-style backend: public anon key + a table with RLS switched off
python targets\demo_supabase\mock_server.py
.venv\Scripts\vibetest.exe scan http://127.0.0.1:8127/

# 4) Firebase-style backend: open Realtime Database rules (CRITICAL)
python targets\demo_firebase\mock_server.py
.venv\Scripts\vibetest.exe scan http://127.0.0.1:8128/

# 5) GitHub repo mode against the included mock GitHub server
python tools\mock_github.py
.venv\Scripts\vibetest.exe scan-repo demo-org/demo-app --github-base http://127.0.0.1:8130
```

`python tools\mock_ollama.py` starts a fake Ollama server if you want to exercise the
`--llm` code path without installing a model.

## Demo targets included in the repo

| Fixture | How to serve | What it demonstrates |
|---|---|---|
| `targets/demo_site` | `python -m http.server 8125 --bind 127.0.0.1 --directory targets\demo_site` | Leaked secrets in JS, exposed `.env`, source map, dev-build marker, vulnerable deps |
| `targets/demo_spa` | `python -m http.server 8131 --bind 127.0.0.1 --directory targets\demo_spa` | Why SPA rendering matters (needs `[crawl]`) |
| `targets/demo_supabase` | `python targets\demo_supabase\mock_server.py` (port 8127) | Supabase anon key in public + RLS missing on a table; anon key itself must **not** be reported |
| `targets/demo_firebase` | `python targets\demo_firebase\mock_server.py` (port 8128) | Open Realtime Database rules |
| `targets/demo_repo` | via `tools/mock_github.py` (port 8130) | Repo mode: committed `.env` + service-account key, secrets, vulnerable lockfile versions |

## CLI reference

```
vibetest scan <url>        Scan a live website (must be allowlisted/authorized)
vibetest scan-repo <repo>  Statically analyse a PUBLIC GitHub repository
vibetest targets           Show the allowlist
vibetest serve             Start the local dashboard
```

**`scan` options**

| Option | Meaning |
|---|---|
| `--allow HOST` | Add a hostname to the allowlist for this run only (repeatable) |
| `--no-llm` / `--llm` | Template explanations (default) or local Ollama explanations (auto-fallback) |
| `--no-probes` | Fully passive scan: skip the gentle unauthenticated probe checks |
| `--no-render` | Skip headless rendering of JavaScript-built pages |
| `--out PATH` | Write a self-contained HTML report |
| `--no-db` | Do not persist the scan to SQLite |

**`scan-repo` options**: `--branch`, `--github-base`, `--llm/--no-llm`, `--out`, `--no-db`

**`serve` options**: `--port` (default 8000), `--db`

Examples:

```powershell
# scan a site you own
vibetest scan https://our-planted-app.vercel.app --allow our-planted-app.vercel.app

# scan a public repository: passive static analysis, no live requests
# to the deployed site (any public repo works — try your own)
vibetest scan-repo owner/public-repository

# passive-only, no database write, HTML report
vibetest scan http://127.0.0.1:8125/ --no-probes --no-db --out reports/site.html
```

Exit codes: `0` success, `1` download failure, `2` refused (target not authorized).

## Local dashboard

`vibetest serve` → <http://127.0.0.1:8000> (bound to `127.0.0.1` only).

- Accepts a **website URL** or a **public GitHub repository** reference (auto-detected),
  and shows which mode was used.
- Every scan requires ticking the **explicit authorization checkbox**; without it the
  request is refused (HTTP 403). The confirmed host is allowlisted for that run only.
- Background jobs with live progress, scan history, severity overview, finding cards,
  report view, and **Download PDF**.
- Read-only after scanning: it never offers a "fix this" button (out of scope).

## Configuration (`vibetest.toml`)

Shipped in the repository root and read from the current working directory. The most
important keys:

| Key | Default | Meaning |
|---|---|---|
| `allowed_targets` | `["localhost", "127.0.0.1"]` | **Consent allowlist.** The scanner hard-refuses anything else. Add only targets you own or have permission to test. |
| `enable_probes` | `true` | Gentle unauthenticated probes (exposed files, Supabase/Firebase reads). `false` = fully passive. |
| `katana_bin` | `"katana"` | Path/name of the Katana binary if it is not on `PATH`. |
| `max_pages`, `katana_depth`, `katana_rate_limit` | 20 / 2 / 10 | Crawl breadth and politeness. |
| `render_spa`, `max_render_pages` | `true` / 5 | Headless rendering of JavaScript apps. |
| `osv_api_url` | OSV.dev query endpoint | Set to `""` to disable all external lookups (fully offline). |
| `ollama_model`, `ollama_fallback_model`, `ollama_api_url` | `qwen2.5:3b`, `mistral:latest`, `http://127.0.0.1:11434` | Local LLM explanation layer. **Change the model names to match the models you actually installed.** |
| `database_path` | `vibetest.db` | Local scan history. |
| `llm_cache_path` | `.llm_cache.json` | Per-finding explanation cache. |

## Evaluation harness

```powershell
.venv\Scripts\python.exe eval\harness.py
```

The harness starts each owned fixture, scans it, and compares the findings against
hand-written ground truth in `eval/targets.yaml`:

- `expect:` categories that **must** fire (drives recall),
- `forbid_categories` / `forbid_title_contains` — checks that must **not** fire
  (precision guardrails; any violation fails the run with exit code 1),
- every browser request inside the harness is still consent-gated, and the run asserts
  zero constraint violations.

Latest recorded results (`eval/results.md`):

| Target | Findings | TP | FP | FN | Violations | Precision | Recall | F1 |
|---|---|---|---|---|---|---|---|---|
| demo_site | 15 | 7 | 0 | 0 | 0 | 1.00 | 1.00 | 1.00 |
| demo_supabase | 6 | 2 | 0 | 0 | 0 | 1.00 | 1.00 | 1.00 |
| demo_firebase | 6 | 2 | 0 | 0 | 0 | 1.00 | 1.00 | 1.00 |
| demo_spa | 9 | 4 | 0 | 0 | 0 | 1.00 | 1.00 | 1.00 |
| demo_repo | 9 | 5 | 0 | 0 | 0 | 1.00 | 1.00 | 1.00 |

**Overall (category level): precision 1.00, recall 1.00, F1 1.00, 0 constraint
violations across 20 ground-truth categories.**

Notes: `demo_site` and `demo_repo` need internet (OSV.dev); the `demo_spa` target is
skipped with a note if Playwright is not installed.

## Running the tests

```powershell
.venv\Scripts\python.exe -m pytest -q            # 124 tests
.venv\Scripts\python.exe -m pytest -q tests/test_supabase_rls.py   # one area
```

The suite is hermetic — **no test contacts a real external site**. Every network call is
either faked in-process (`tests/fake_http.py`) or pointed at the local mock servers
(`tools/mock_github.py`, `tools/mock_ollama.py`); hostnames like `osv.test` and
`gh.test` are fake bases. Expected findings per detector are asserted explicitly in the
test files, so a behaviour change fails loudly instead of silently drifting.

## Project layout

```
vibetest/
  cli.py                 Typer CLI: scan / scan-repo / targets / serve
  config.py              vibetest.toml loading (Pydantic settings)
  core/                  consent gate, orchestrator, SQLite store, repo-mode scan
  acquisition/           crawler, Katana, Playwright rendering, JS bundles, GitHub download
  detectors/             one file per vulnerability class + registry (10 detectors)
  analysis/              aggregation, severity/CWE/OWASP mapping
  reporting/             HTML report, PDF export, LLM explanation layer
  schemas/               Artifact / Finding / ScanResult (the binding team contract)
  web/                   FastAPI dashboard (localhost-only)
targets/                 deliberately vulnerable OWNED demo targets
tools/                   mock GitHub + mock Ollama servers for development
eval/                    evaluation harness, ground truth, results
tests/                   124 pytest tests
docs/ARCHITECTURE.md     architecture detail
graphify-out/            generated code knowledge graph (queryable)
```

## Security model (the four hard rules)

1. **Authorization gate.** Nothing is scanned unless the target is on the explicit
   allowlist (`vibetest.toml`), passed via `--allow`, or confirmed in the dashboard.
   The refusal happens *before* any request leaves the machine. Repo mode is passive
   static analysis of **public repositories only** and never contacts a deployed site.
2. **Read-only and gentle.** Passive checks plus gentle unauthenticated GET probes
   (a fixed list of well-known paths, one row per Supabase table, one Firebase root
   read). No payloads, no writes, no login attempts, no fuzzing, no port scanning.
3. **Deterministic core.** Same target → same findings. The LLM may only touch the
   explanation layer, never detection.
4. **Zero budget.** Free and open-source tooling only.

Only scan systems you own or have explicit written permission to test. See
`PENDING.md` for the project's legal note.

## Limitations and roadmap

Honest gaps (also tracked in `PROGRESS.md` / `PENDING.md`):

- **Not implemented yet:** Firestore rule checks (Realtime Database rules are done),
  client-side-only authorization hints, cookie-flag checks (`Secure`/`HttpOnly`/
  `SameSite`), CORS misconfiguration checks, TLS/certificate configuration checks.
- **By design, not planned for Phase 1:** authenticated crawling, injection/exploitation
  testing, infrastructure/port scanning, automatic remediation.
- **Known UI gap:** each finding stores a `confidence` value, but the report and
  dashboard do not yet display it.
- Evidence quality depends on the target: a key only present after login, or a database
  that only misbehaves for authenticated users, will not be visible to an
  unauthenticated read-only scan.

## Troubleshooting

| Symptom | Cause and fix |
|---|---|
| `REFUSED: ... not authorized` (exit code 2) | The target is not on the allowlist. Add it to `vibetest.toml` or pass `--allow <host>` — only for systems you own/own permission for. |
| `python --version` is 3.11 or older | VibeTest needs **3.12+**. Install a newer Python and re-create the venv. |
| PowerShell: "running scripts is disabled" | Don't activate the venv — call `.venv\Scripts\vibetest.exe` and `.venv\Scripts\python.exe` directly. |
| `123 passed, 1 skipped` | Expected without the optional Playwright extra. Install `[crawl]` + `playwright install chromium` for 124. |
| Ollama not running / model not found | Explanations fall back to templates automatically. To use the LLM: start Ollama, `ollama pull <model>`, and set `ollama_model` in `vibetest.toml`. |
| Only one page was scanned | Katana is not installed or not on `PATH`. Install it or set `katana_bin` to its full path. |
| SPA secrets not detected | Headless rendering is unavailable or the page needs interaction. Install Playwright; compare with `--no-render`. |
| `Address already in use` | Another process holds the port. Use `vibetest serve --port 8100` or a different fixture port. |
| OSV lookups fail / offline | Expected without internet. Set `osv_api_url = ""` to disable external lookups cleanly. |
| `LF will be replaced by CRLF` warnings on Windows | Cosmetic line-ending notice from Git on Windows. Ignore it. |
| Config changes seem ignored | `vibetest.toml` is read from the **current working directory** — run commands from the repository root. |
| Scan of a real site finds nothing | Common causes: the site is behind a login, the CDN strips headers, or the vulnerable code is in a bundle the crawler never reached. Cross-check with `--out` and the report evidence. |

## Documentation map

| File | What it is for |
|---|---|
| `docs/ARCHITECTURE.md` | How the pipeline fits together, module by module |
| `PROJECTS.md` | Full decision log — what was decided, why, and what was rejected |
| `PROGRESS.md` | Plain-language implementation log (updated after every session) |
| `PROBLEMS.md` | Real problems the team hit and how they were fixed |
| `PENDING.md` | Deferred tasks, target acquisition, legal note |
| `AGENTS.md` | Conventions, hard constraints, architecture contract |
| `targets/README.md` | What each demo target contains and why it is intentionally vulnerable |
| `eval/results.md` | Latest harness results |
| `graphify-out/GRAPH_REPORT.md` | Generated code knowledge graph / architecture map |

### Optional developer tooling: the knowledge graph

The repo ships a generated code graph (`graphify-out/`). It is not needed to run or test
VibeTest, but it makes code questions much faster. Install the CLI with
`uv tool install graphifyy` (or `pip install graphifyy`), then e.g.
`graphify query "how does the consent gate work"`, `graphify path <A> <B>`,
`graphify explain <concept>`, and `graphify update .` after changing code.

---

## Team and license

Built by a team of three as a final-year major project (see `AGENTS.md` for roles and
workflow).

This is an academic coursework repository. **No open-source license has been chosen
yet** — please ask before reusing the code or the demo targets. The demo targets under
`targets/` are intentionally vulnerable fixtures owned by this project; the `.env` files
and keys committed there are fake and exist only to be detected.
