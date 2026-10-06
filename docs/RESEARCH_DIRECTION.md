# Research Direction: Detecting Security Behavior Drift

**Status as of 2026-10-04:** The repository contains an initial offline/imported-observation foundation. It does not yet collect authenticated runtime behavior, infer authorization policy from source, or prove a real target vulnerability.

## 1. Problem and motivation

AI-assisted web applications change quickly as developers request new features. A change that improves functionality can weaken an existing ownership or role check. This project will study whether a versioned security-behavior profile can make such authorization regressions visible across application revisions.

For this project, a **vibe-coded application** is a web application whose source or features were materially produced or modified with generative AI coding assistance. The label describes the development process; it is not itself a security property.

## 2. Security Behavior Baseline

A baseline is a versioned set of structured observations keyed by stable test-case IDs. An observation records the application/version, principal and role, action, resource and optional owner, endpoint/method, application state, expected and observed authorization outcomes, response facts, timestamp, and source/version references. Profiles are Pydantic JSON documents and receive content-derived identifiers.

The initial importer accepts JSON supplied by a researcher. It does not log in, call an application, switch identities, or issue requests. A deterministic configurable classifier can map imported status codes, response-body indicators, redirect destinations, and application-specific indicators to `allowed`, `denied`, or `unknown`. Ambiguous/no-match classifications remain `unknown`; HTTP status alone is not assumed to define authorization.

## 3. Security Behavior Drift

The comparator pairs cases by stable `case_id`. Denied-to-allowed is reported as a **security drift candidate**. Allowed-to-denied is reported as an observed change that may be a functionality regression. Changed expectations, new cases, removed cases, and unchanged cases are represented separately. A difference is not automatically called a vulnerability.

## 4. Static and runtime analysis

**Static authorization analysis — PLANNED.** A later controlled FastAPI/Python analyzer may extract candidate role, ownership, identity, permission, and authentication-dependency policies using deterministic AST analysis. It must label results as inferred policy, retain source references, and not make LLM security decisions.

**Runtime authorization analysis — BLOCKED BY SCOPE POLICY for automated collection.** Current project rules prohibit authenticated crawling, credential use, automated login/privilege switching, active exploitation, and mutation requests. Researchers may import observations that they collected separately under their approved study protocol. VibeTest itself does not contact the target in the research workflow.

## 5. Security behavior graph

The first graph is an in-memory Pydantic node/edge structure serialized to JSON. It represents applications, versions, principals, roles, actions, resources, endpoints, application states, expected/observed outcomes, authorization conditions, and evidence references. Graph differences compare semantic relationships while excluding version-membership metadata. The graph exists to expose changes in those relationships, not merely to render a visualization. No graph database is required.

## 6. Version comparison and verification

Profiles may record Git commit/branch references in `source_version` and `source_ref`. Version comparison creates candidates, then an optional verifier matches them against a **separately imported** observation set. `verified` means the supplied second observation reproduces the candidate outcome; the software cannot attest that collection was operationally independent or genuine. It does not issue an independent verification request.

## 7. AI/LLM role

The existing local Ollama integration remains limited to explanations in the legacy VibeTest finding pipeline. It does not classify outcomes, infer authorization policies, build graphs, compare versions, or decide whether a regression exists. Future interpretation experiments may add an LLM condition, but deterministic results must remain separately measurable.

## 8. Hypothesis and experimental methodology

Research hypothesis: comparing versioned authorization behavior profiles, optionally enriched by deterministic source-derived policy and graph relationships, can identify authorization behavior regressions introduced between application versions while preserving evidence for review. This is a hypothesis, not a proven result.

The initial method is offline: import V0 observations, build/save a baseline, import V1 observations, compare profiles and graphs, and optionally import a separate verification set. Included MiniShop JSON files are synthetic controlled fixtures showing this workflow; they are not measurements from a running application. The runner reports zero requests for imported-only experiments.

Later evaluation should include owner-only-to-public, role restriction, cross-user access, admin-function access, removed/weakened checks, unchanged authorization, and functional-only changes. Ground truth must be explicit. Dynamic-only, static+dynamic, graph, and LLM interpretation conditions can be compared once those components are permitted and implemented. Do not report accuracy numbers from the synthetic fixtures as research results.

## 9. Current status and limitations

**Implemented:** offline JSON importer; versioned behavior profile; deterministic response classifier; profile comparison; JSON graph build/load/save/diff; imported-observation verification status; CLI commands; illustrative MiniShop observations; unit tests.

**Partially implemented:** security behavior baseline and drift comparison, limited to supplied structured records; verification status over separately supplied records, without provenance attestation.

**Planned:** source-aware static authorization extraction; controlled MiniShop FastAPI app; larger scenario suite and real ground truth; git snapshot orchestration; further graph semantics; dashboard views; optional ablations.

**Blocked by scope policy:** VibeTest-driven authenticated runtime collection and independent active verification requests.

The original website scanner, crawler, detectors, reports, and dashboard remain available. Their findings are not automatically converted into behavior profiles and are not the research contribution.

## 10. Future work

After team and policy decisions, define a controlled owned application and safe study protocol; add AST-based policy candidates; import or collect permitted runtime evidence; align policies with observations; improve graph semantics; evaluate verification quality; expand reproducible version-pair benchmarks; and compare ablations. Do not integrate AI-generated code modification or active testing until the scope policy is formally revised.

## Offline first experiment

From the repository root:

```powershell
vibetest behavior-baseline eval/behavior/minishop_v0.json --out eval/behavior/out/v0.profile.json
vibetest behavior-baseline eval/behavior/minishop_v1.json --out eval/behavior/out/v1.profile.json
vibetest behavior-baseline eval/behavior/minishop_verification.json --out eval/behavior/out/verification.profile.json
vibetest experiment-run eval/behavior/out/v0.profile.json eval/behavior/out/v1.profile.json --verification eval/behavior/out/verification.profile.json --ground-truth eval/behavior/ground_truth.json --out eval/behavior/out/experiment.json
```

All inputs are local JSON fixtures. The commands make no target requests and use no credentials. Output is illustrative fixture processing, not an evaluation result.
