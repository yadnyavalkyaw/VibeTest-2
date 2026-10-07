"""Unit tests for external tool adapters (Nuclei, Semgrep, TruffleHog)."""
import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

from vibetest.core.context import ScanContext
from vibetest.engines.nuclei import run_nuclei
from vibetest.engines.semgrep import run_semgrep
from vibetest.engines.trufflehog import run_trufflehog
from vibetest.schemas.findings import FindingStatus, Severity, SourceEngine


def _mock_ctx() -> ScanContext:
    mock_gate = MagicMock()
    mock_gate.is_allowed.return_value = True
    mock_settings = MagicMock()
    ctx = ScanContext(
        settings=mock_settings,
        gate=mock_gate,
    )
    ctx.config = {"nuclei_timeout": 5, "semgrep_timeout": 5, "trufflehog_timeout": 5}
    return ctx


def test_nuclei_missing_binary_returns_empty():
    ctx = _mock_ctx()
    with patch("subprocess.run", side_effect=FileNotFoundError):
        findings = run_nuclei("https://example.com", ctx)
        assert findings == []


def test_nuclei_parses_jsonl_output():
    ctx = _mock_ctx()
    sample_nuclei_output = json.dumps({
        "template-id": "exposed-env-file",
        "info": {
            "name": "Environment Variables Exposure",
            "remediation": "Do not expose .env files to the public.",
        },
        "severity": "critical",
        "matched-at": "https://example.com/.env",
        "extracted-results": "DB_PASSWORD=secret",
        "description": "Found accessible environment file",
    })
    mock_proc = MagicMock(stdout=sample_nuclei_output, returncode=0)
    with patch("subprocess.run", return_value=mock_proc):
        findings = run_nuclei("https://example.com", ctx)
        assert len(findings) == 1
        f = findings[0]
        assert f.detector_id == "nuclei"
        assert f.severity == Severity.CRITICAL
        assert f.source_engine == SourceEngine.NUCLEI
        assert f.title == "Environment Variables Exposure"
        assert len(f.evidence) == 1
        assert f.evidence[0].url == "https://example.com/.env"
        assert f.evidence[0].snippet == "DB_PASSWORD=secret"


def test_semgrep_missing_binary_returns_empty():
    ctx = _mock_ctx()
    with patch("subprocess.run", side_effect=FileNotFoundError):
        findings = run_semgrep(Path("/fake/path"), ctx)
        assert findings == []


def test_semgrep_parses_json_output():
    ctx = _mock_ctx()
    sample_semgrep_output = json.dumps({
        "results": [
            {
                "check_id": "rules.security.hardcoded-jwt",
                "path": "src/auth.js",
                "start": {"line": 14},
                "end": {"line": 15},
                "extra": {
                    "severity": "ERROR",
                    "message": "Potential hardcoded secret or token detected",
                    "lines": "const token = 'eyJhbGci...';",
                    "fix": "Use process.env.TOKEN",
                },
            }
        ]
    })
    mock_proc = MagicMock(stdout=sample_semgrep_output, returncode=1)
    with patch("subprocess.run", return_value=mock_proc):
        findings = run_semgrep(Path("/fake/path"), ctx)
        assert len(findings) == 1
        f = findings[0]
        assert f.detector_id == "semgrep"
        assert f.severity == Severity.HIGH
        assert f.source_engine == SourceEngine.SEMGREP
        assert f.category == "hardcoded-jwt"
        assert len(f.evidence) == 1
        assert "src/auth.js" in f.evidence[0].url
        assert "Lines 14-15" in f.evidence[0].detail


def test_trufflehog_missing_binary_returns_empty():
    ctx = _mock_ctx()
    with patch("subprocess.run", side_effect=FileNotFoundError):
        findings = run_trufflehog("https://github.com/example/repo", ctx)
        assert findings == []


def test_trufflehog_parses_json_output_and_redacts():
    ctx = _mock_ctx()
    sample_truffle_output = json.dumps({
        "Type": "Secrets",
        "DetectorType": "AWS",
        "Raw": "AKIAIOSFODNN7EXAMPLE",
        "SourceURL": "https://github.com/example/repo/blob/main/config.json",
    })
    mock_proc = MagicMock(stdout=sample_truffle_output, returncode=0)
    with patch("subprocess.run", return_value=mock_proc):
        findings = run_trufflehog("https://github.com/example/repo", ctx)
        assert len(findings) == 1
        f = findings[0]
        assert f.detector_id == "trufflehog-AWS"
        assert f.severity == Severity.CRITICAL
        assert f.source_engine == SourceEngine.TRUFFLEHOG
        assert f.category == "secret-exposure"
        assert len(f.evidence) == 1
        # Raw secret must be redacted
        assert "***" in f.evidence[0].snippet
        assert "AKIAIOSFODNN7EXAMPLE" not in f.evidence[0].snippet
