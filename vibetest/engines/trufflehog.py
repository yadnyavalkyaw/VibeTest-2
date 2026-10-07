"""TruffleHog adapter for secret detection in Git repositories and filesystems.

This adapter runs TruffleHog against a target path/repo and converts JSON output
into VibeTest Finding objects.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import List

from ..schemas.findings import Finding, SourceEngine, Severity
from ..core.context import ScanContext


def run_trufflehog(
    target: str,
    ctx: ScanContext,
    scan_args: List[str] | None = None,
) -> List[Finding]:
    """Run TruffleHog against a target and return findings.

    Args:
        target: The repository URL, path, or file to scan.
        ctx: ScanContext for timeout configuration.
        scan_args: Additional TruffleHog scan arguments.

    Returns:
        List of Finding objects.
    """
    # Build the TruffleHog command
    cmd = ["trufflehog", "scan", "--json", target]
    if scan_args:
        cmd.extend(scan_args)

    # Run TruffleHog
    timeout = getattr(ctx, "config", {}).get("trufflehog_timeout", 300) if hasattr(ctx, "config") else 300
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError:
        # TruffleHog not installed
        return []
    except subprocess.TimeoutExpired:
        # Timeout
        return []

    if result.returncode != 0:
        # Error
        return []

    findings: List[Finding] = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            continue

        # TruffleHog JSON output structure varies; handle common formats
        if isinstance(data, dict) and data.get("Type") == "Secrets":
            secret_type = data.get("DetectorType", "unknown-secret")
            severity = _map_trufflehog_severity(secret_type)

            # Build evidence
            evidence = []
            if data.get("Raw"):
                evidence.append(
                    {
                        "url": data.get("SourceURL", ""),
                        "snippet": _redact_secret(data.get("Raw", "")),
                        "detail": f"Detected by {data.get('DetectorType', 'unknown')} detector",
                    }
                )

            finding = Finding(
                detector_id=f"trufflehog-{secret_type}",
                category="secret-exposure",
                cwe_id="CWE-798",
                owasp_2025="A07:2025",
                severity=severity,
                confidence=0.9,
                title=f"Hardcoded secret detected ({secret_type})",
                evidence=evidence,
                remediation_hint="Remove the secret from the source and rotate it immediately.",
                source_engine=SourceEngine.TRUFFLEHOG,
            )
            findings.append(finding)

    return findings


def _map_trufflehog_severity(detector_type: str) -> Severity:
    """Map TruffleHog detector types to VibeTest severity levels."""
    high_detectors = {"aws", "gcp", "azure", "private-key", "github-pat", "gitlab-pat"}
    if detector_type.lower() in high_detectors:
        return Severity.CRITICAL
    return Severity.HIGH


def _redact_secret(raw: str) -> str:
    """Redact the secret value, showing only a prefix."""
    if len(raw) <= 12:
        return raw[:4] + "***"
    return raw[:8] + "***" + raw[-4:] if len(raw) > 12 else raw[:4] + "***"