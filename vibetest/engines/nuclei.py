"""Nuclei adapter for safe template scanning.

This adapter runs Nuclei with a curated set of safe tags (exposure, misconfiguration, etc.)
and converts the JSONL output into VibeTest Finding objects.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import List

from ..schemas.artifacts import Artifact
from ..schemas.findings import Finding, SourceEngine, Severity
from ..core.context import ScanContext


def run_nuclei(
    target: str,
    ctx: ScanContext,
    templates_dir: Path | None = None,
    safe_tags: List[str] | None = None,
) -> List[Finding]:
    """Run Nuclei against a target and return findings.

    Args:
        target: The URL or file to scan.
        ctx: ScanContext for consent checking and HTTP client.
        templates_dir: Optional path to a directory of Nuclei templates.
        safe_tags: List of Nuclei template tags to consider safe (default: exposure, misconfiguration, technology, info).

    Returns:
        List of Finding objects.
    """
    if safe_tags is None:
        safe_tags = ["exposure", "misconfiguration", "technology", "info"]

    # Build the Nuclei command
    cmd = ["nuclei", "-target", target, "-jsonl", "-tags", ",".join(safe_tags)]
    if templates_dir:
        cmd.extend(["-t", str(templates_dir)])

    # Run Nuclei
    timeout = getattr(ctx, "config", {}).get("nuclei_timeout", 300) if hasattr(ctx, "config") else 300
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError:
        # Nuclei not installed
        return []
    except subprocess.TimeoutExpired:
        # Timeout
        return []

    findings: List[Finding] = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            continue

        # Map Nuclei severity to our Severity
        nuclei_severity = data.get("severity", "info").lower()
        severity_map = {
            "critical": Severity.CRITICAL,
            "high": Severity.HIGH,
            "medium": Severity.MEDIUM,
            "low": Severity.LOW,
            "info": Severity.INFO,
            "unknown": Severity.INFO,
        }
        severity = severity_map.get(nuclei_severity, Severity.INFO)

        # Build evidence
        evidence = []
        if "matched-at" in data:
            evidence.append(
                {
                    "url": data["matched-at"],
                    "snippet": data.get("extracted-results", ""),
                    "detail": data.get("description", ""),
                }
            )

        # Create Finding
        finding = Finding(
            detector_id="nuclei",
            category=data.get("template-id", "nuclei-finding"),
            severity=severity,
            confidence=0.8,  # Nuclei templates are community vetted, but we don't know exact confidence
            title=data.get("info", {}).get("name", "Nuclei finding"),
            evidence=evidence,
            remediation_hint=data.get("info", {}).get("remediation", ""),
            source_engine=SourceEngine.NUCLEI,
        )
        findings.append(finding)

    return findings