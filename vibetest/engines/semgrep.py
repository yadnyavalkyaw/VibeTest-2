"""Semgrep adapter for source code scanning.

This adapter runs Semgrep with a curated set of rules and converts the JSON output
into VibeTest Finding objects.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import List

from ..schemas.artifacts import Artifact
from ..schemas.findings import Finding, SourceEngine, Severity
from ..core.context import ScanContext


def run_semgrep(
    target_path: Path,
    ctx: ScanContext,
    rules_dir: Path | None = None,
) -> List[Finding]:
    """Run Semgrep against a target path and return findings.

    Args:
        target_path: The path to the source code directory or file.
        ctx: ScanContext for consent checking (though for local files, consent may not apply).
        rules_dir: Optional path to a directory of Semgrep rules.

    Returns:
        List of Finding objects.
    """
    # Build the Semgrep command
    cmd = ["semgrep", "--json", "--quiet"]
    if rules_dir:
        cmd.extend(["--config", str(rules_dir)])
    cmd.append(str(target_path))

    # Run Semgrep
    timeout = getattr(ctx, "config", {}).get("semgrep_timeout", 120) if hasattr(ctx, "config") else 120
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError:
        # Semgrep not installed
        return []
    except subprocess.TimeoutExpired:
        # Timeout
        return []

    if result.returncode not in (0, 1):  # Semgrep returns 1 when findings are found
        # Other errors
        return []

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return []

    findings: List[Finding] = []
    for result in data.get("results", []):
        # Map Semgrep severity to our Severity
        semgrep_severity = result.get("extra", {}).get("severity", "info").lower()
        severity_map = {
            "critical": Severity.CRITICAL,
            "high": Severity.HIGH,
            "medium": Severity.MEDIUM,
            "low": Severity.LOW,
            "info": Severity.INFO,
            "note": Severity.INFO,
            "warning": Severity.LOW,  # sometimes used
            "error": Severity.HIGH,
        }
        severity = severity_map.get(semgrep_severity, Severity.INFO)

        # Build evidence
        evidence = []
        if "path" in result:
            evidence.append(
                {
                    "url": f"file://{result['path']}",
                    "snippet": result.get("extra", {}).get("lines", ""),
                    "detail": result.get("extra", {}).get("message", ""),
                }
            )
        if "start" in result and "end" in result:
            # Add line numbers to detail if available
            start_line = result["start"].get("line")
            end_line = result["end"].get("line")
            if start_line is not None and end_line is not None:
                detail = f"Lines {start_line}-{end_line}"
                if evidence:
                    evidence[0]["detail"] = (evidence[0]["detail"] + "; " + detail) if evidence[0]["detail"] else detail
                else:
                    evidence.append(
                        {
                            "url": f"file://{result.get('path', '')}",
                            "snippet": "",
                            "detail": detail,
                        }
                    )

        check_id = result.get("check_id", "semgrep-finding")
        category = check_id.replace("/", ".").split(".")[-1]
        finding = Finding(
            detector_id="semgrep",
            category=category,
            severity=severity,
            confidence=0.85,  # Semgrep rules are generally reliable, but we don't know exact confidence
            title=result.get("extra", {}).get("message", "Semgrep finding"),
            evidence=evidence,
            remediation_hint=result.get("extra", {}).get("fix", ""),
            source_engine=SourceEngine.SEMGREP,
        )
        findings.append(finding)

    return findings