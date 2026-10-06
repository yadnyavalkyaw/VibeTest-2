"""VibeTest CLI (Typer). Primary delivery format — see PROJECTS.md §5."""
from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from .config import load_settings
from .core.consent import ConsentDenied, ConsentGate
from .core.orchestrator import run_scan
from .core.repo_scan import run_repo_scan
from .core.store import Store
from .reporting.html_report import render_report
from .schemas.scan import ScanResult
from .research.behavior.baseline import load_observations, load_profile, save_profile
from .research.behavior.comparator import compare_profiles, verify_candidates
from .research.behavior.models import OutcomeClassifier
from .research.experiment import run_imported_experiment
from .research.graph.builder import build_graph
from .research.graph.diff import diff_profiles
from .research.graph.serializer import save_graph

app = typer.Typer(
    help="VibeTest — authorization-gated security scanner for vibe-coded web apps.",
    no_args_is_help=True,
)
console = Console()

_SEVERITY_STYLE = {
    "critical": "bold red",
    "high": "red",
    "medium": "yellow",
    "low": "cyan",
    "info": "dim",
}


def _print_findings(result: ScanResult) -> None:
    table = Table(title=f"VibeTest scan — {result.target_url}")
    for col in ("Severity", "Title", "Category", "CWE", "OWASP"):
        table.add_column(col)
    for f in result.findings:
        table.add_row(
            f.severity.value.upper(),
            f.title,
            f.category,
            f.cwe_id or "-",
            f.owasp_2025 or "-",
            style=_SEVERITY_STYLE.get(f.severity.value, ""),
        )
    console.print(table)
    tech = result.artifact.tech
    known = [part for part in [tech.framework, tech.hosting, *tech.backend_services] if part]
    if known:
        console.print(f"Detected technology: {' · '.join(known)}")
    console.print(f"{len(result.findings)} finding(s). Scan id: {result.scan_id}")


def _write_report(result: ScanResult, out: Path | None) -> None:
    if out is not None:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render_report(result), encoding="utf-8")
        console.print(f"HTML report written to {out}")


@app.command()
def scan(
    url: str = typer.Argument(..., help="Target URL. MUST be on the allowlist (owned/authorized only)."),
    allow: list[str] = typer.Option([], "--allow", help="Add a hostname to the allowlist for this run."),
    no_llm: bool = typer.Option(True, "--no-llm/--llm", help="Template explanations (default) or local Ollama model (falls back to templates if unavailable)."),
    no_probes: bool = typer.Option(False, "--no-probes", help="Passive-only scan: skip gentle probe checks (exposed files, ...)."),
    no_render: bool = typer.Option(False, "--no-render", help="Skip headless rendering of JavaScript-built pages."),
    out: Path | None = typer.Option(None, "--out", help="Write a self-contained HTML report to this path."),
    no_db: bool = typer.Option(False, "--no-db", help="Do not persist the scan to SQLite."),
) -> None:
    settings = load_settings()
    if no_probes:
        settings = settings.model_copy(update={"enable_probes": False})
    if no_render:
        settings = settings.model_copy(update={"render_spa": False})
    if not no_llm:
        console.print(
            f"[dim]LLM explanations: local Ollama model '{settings.ollama_model}' "
            "(template fallback if unavailable).[/]"
        )
    gate = ConsentGate([*settings.allowed_targets, *allow])
    store = None if no_db else Store(settings.database_path)
    try:
        result = run_scan(url, settings=settings, gate=gate, no_llm=no_llm, store=store)
    except ConsentDenied as exc:
        console.print(f"[bold red]REFUSED:[/] {exc}")
        raise typer.Exit(code=2) from exc

    _print_findings(result)
    _write_report(result, out)


@app.command("scan-repo")
def scan_repo(
    repo: str = typer.Argument(..., help="owner/name or a github.com URL. PUBLIC repositories only (static analysis)."),
    branch: str | None = typer.Option(None, "--branch", help="Branch to download (default: main, then master)."),
    github_base: str | None = typer.Option(None, "--github-base", help="GitHub base URL override (for mirrors/testing)."),
    no_llm: bool = typer.Option(True, "--no-llm/--llm", help="Template explanations (default) or local Ollama model."),
    out: Path | None = typer.Option(None, "--out", help="Write a self-contained HTML report to this path."),
    no_db: bool = typer.Option(False, "--no-db", help="Do not persist the scan to SQLite."),
) -> None:
    """Scan a PUBLIC GitHub repository (static analysis — no live testing)."""
    settings = load_settings()
    if not no_llm:
        console.print(
            f"[dim]LLM explanations: local Ollama model '{settings.ollama_model}' "
            "(template fallback if unavailable).[/]"
        )
    store = None if no_db else Store(settings.database_path)
    try:
        result = run_repo_scan(
            repo,
            settings=settings,
            branch=branch,
            github_base=github_base,
            no_llm=no_llm,
            store=store,
        )
    except ValueError as exc:
        console.print(f"[bold red]INVALID REPOSITORY:[/] {exc}")
        raise typer.Exit(code=2) from exc
    except RuntimeError as exc:
        console.print(f"[bold red]DOWNLOAD FAILED:[/] {exc}")
        raise typer.Exit(code=1) from exc

    _print_findings(result)
    _write_report(result, out)


@app.command()
def targets() -> None:
    """List the allowlisted (owned/authorized) targets."""
    settings = load_settings()
    console.print("Allowlisted targets (owned/authorized only):")
    for t in settings.allowed_targets:
        console.print(f"  • {t}")


@app.command("behavior-baseline")
def behavior_baseline(
    input_file: Path = typer.Argument(..., exists=True, readable=True, help="Imported observation JSON; no target requests are made."),
    out: Path = typer.Option(..., "--out", help="Write the versioned behavior profile JSON."),
    classifier: Path | None = typer.Option(None, "--classifier", help="Optional deterministic outcome-rule JSON."),
) -> None:
    """Build a behavior profile from supplied/imported observations only."""
    try:
        rules = OutcomeClassifier.model_validate_json(classifier.read_text(encoding="utf-8")) if classifier else None
        profile = load_observations(input_file, classifier=rules)
        save_profile(profile, out)
    except (ValueError, OSError) as exc:
        console.print(f"[bold red]IMPORT FAILED:[/] {exc}")
        raise typer.Exit(code=2) from exc
    console.print(f"Imported {len(profile.observations)} observations for {profile.application_id}@{profile.version_id}.")
    console.print(f"Profile: {profile.profile_id} → {out}")


@app.command("behavior-compare")
def behavior_compare(
    baseline_file: Path = typer.Argument(..., exists=True, readable=True),
    current_file: Path = typer.Argument(..., exists=True, readable=True),
    out: Path = typer.Option(..., "--out", help="Write comparison JSON."),
    graph_out: Path | None = typer.Option(None, "--graph-out", help="Optionally write graph-diff JSON."),
) -> None:
    """Compare two saved offline behavior profiles."""
    try:
        baseline, current = load_profile(baseline_file), load_profile(current_file)
        result = compare_profiles(baseline, current)
        delta = diff_profiles(baseline, current)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(result.model_dump_json(indent=2) + "\n", encoding="utf-8")
        if graph_out:
            graph_out.parent.mkdir(parents=True, exist_ok=True)
            graph_out.write_text(delta.model_dump_json(indent=2) + "\n", encoding="utf-8")
    except (ValueError, OSError) as exc:
        console.print(f"[bold red]COMPARISON FAILED:[/] {exc}")
        raise typer.Exit(code=2) from exc
    console.print(f"{len(result.regression_candidates)} security drift candidate(s) in {baseline.version_id} → {current.version_id}.")
    console.print(f"Comparison: {out}")


@app.command("behavior-verify")
def behavior_verify(
    baseline_file: Path = typer.Argument(..., exists=True, readable=True),
    current_file: Path = typer.Argument(..., exists=True, readable=True),
    verification_file: Path = typer.Argument(..., exists=True, readable=True, help="Separately imported observations; no verification requests are made."),
    out: Path = typer.Option(..., "--out", help="Write the comparison with supplied-observation verification statuses."),
) -> None:
    """Verify candidates against a separately supplied observation profile."""
    try:
        baseline, current = load_profile(baseline_file), load_profile(current_file)
        verification = load_profile(verification_file)
        result = verify_candidates(compare_profiles(baseline, current), verification)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(result.model_dump_json(indent=2) + "\n", encoding="utf-8")
    except (ValueError, OSError) as exc:
        console.print(f"[bold red]VERIFICATION FAILED:[/] {exc}")
        raise typer.Exit(code=2) from exc
    verified = sum(1 for item in result.regression_candidates if item.verification and item.verification.status.value == "verified")
    console.print(f"{verified} candidate(s) reproduced in separately supplied observations; collection is not attested.")
    console.print(f"Result: {out}")


@app.command("graph-build")
def graph_build(
    profile_file: Path = typer.Argument(..., exists=True, readable=True),
    out: Path = typer.Option(..., "--out", help="Write JSON graph."),
) -> None:
    """Build a JSON behavior graph from a saved profile."""
    try:
        graph = build_graph(load_profile(profile_file))
        save_graph(graph, out)
    except (ValueError, OSError) as exc:
        console.print(f"[bold red]GRAPH BUILD FAILED:[/] {exc}")
        raise typer.Exit(code=2) from exc
    console.print(f"Wrote {len(graph.nodes)} node(s) and {len(graph.edges)} edge(s) to {out}.")


@app.command("experiment-run")
def experiment_run(
    baseline_file: Path = typer.Argument(..., exists=True, readable=True),
    current_file: Path = typer.Argument(..., exists=True, readable=True),
    out: Path = typer.Option(..., "--out", help="Write structured experiment result JSON."),
    verification_file: Path | None = typer.Option(None, "--verification", help="Optional separately supplied verification observation JSON."),
    ground_truth_file: Path | None = typer.Option(None, "--ground-truth", help="Optional JSON object mapping case_id to true/false regression labels."),
) -> None:
    """Run a local experiment over imported observation files (request_count=0)."""
    import json

    try:
        baseline, current = load_profile(baseline_file), load_profile(current_file)
        verification = load_profile(verification_file) if verification_file else None
        ground_truth = json.loads(ground_truth_file.read_text(encoding="utf-8")) if ground_truth_file else None
        if ground_truth is not None and not isinstance(ground_truth, dict):
            raise ValueError("ground truth must be a JSON object mapping case ids to booleans")
        result = run_imported_experiment(baseline, current, verification, ground_truth=ground_truth)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(result.model_dump_json(indent=2) + "\n", encoding="utf-8")
    except (ValueError, OSError) as exc:
        console.print(f"[bold red]EXPERIMENT FAILED:[/] {exc}")
        raise typer.Exit(code=2) from exc
    console.print(f"Imported-observation experiment: {result.drift_candidates} candidate(s), {result.verified_regressions} verified in supplied data, 0 requests.")
    console.print(f"Result: {out}")


@app.command()
def serve(
    port: int = typer.Option(8000, "--port", help="Port to serve on (localhost only)."),
    db: Path | None = typer.Option(None, "--db", help="SQLite database path (default: from vibetest.toml)."),
) -> None:
    """Local dashboard: start consent-gated scans and browse past results."""
    import uvicorn

    from .web.app import create_app

    settings = load_settings()
    db_path = str(db) if db is not None else settings.database_path
    console.print(f"VibeTest dashboard on [bold]http://127.0.0.1:{port}/[/] — Ctrl+C to stop")
    uvicorn.run(create_app(db_path), host="127.0.0.1", port=port, log_level="warning")


if __name__ == "__main__":
    app()
