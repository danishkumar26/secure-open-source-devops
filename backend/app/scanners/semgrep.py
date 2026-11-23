"""Semgrep static application security testing (SAST) scanner wrapper."""

import json
import subprocess
from typing import TYPE_CHECKING

from .base import FindingDict, Scanner, finding

if TYPE_CHECKING:
    pass

# Semgrep exit codes: 0 = no findings, 1 = findings found, anything else
# is an execution error.
_SEMGREP_OK_EXIT_CODES = (0, 1)

# Shortcut: default ruleset (`--config auto`) and a single global timeout.
# Upgrade: configurable rulesets, paths, and per-repository timeout.
_SEMGREP_CONFIG = "auto"

# Semgrep severity names -> platform severity vocabulary.
_SEMGREP_SEVERITY = {"ERROR": "high", "WARNING": "medium", "INFO": "low"}


def _semgrep_severity(extra: dict) -> str:
    """Map a Semgrep severity to the platform severity vocabulary."""
    return _SEMGREP_SEVERITY.get(str(extra.get("severity") or "INFO").strip().upper(), "low")


class SemgrepScanner(Scanner):
    """Runs ``semgrep --json`` against a checked-out repository directory."""

    name = "semgrep"

    def __init__(self, timeout: float = 300.0) -> None:
        self.timeout = timeout

    def run(self, target: str) -> tuple[list[FindingDict], list[str]]:
        """``target`` is a directory; returns SAST findings."""
        findings: list[FindingDict] = []
        errors: list[str] = []
        try:
            result = subprocess.run(
                [
                    "semgrep",
                    "--json",
                    "--config",
                    _SEMGREP_CONFIG,
                    "--timeout",
                    f"{int(self.timeout)}",
                    target,
                ],
                capture_output=True,
                text=True,
                timeout=self.timeout + 60,
                check=False,
            )
        except FileNotFoundError:
            return findings, ["semgrep binary not found; install semgrep to enable SAST scanning"]
        except subprocess.TimeoutExpired as exc:
            return findings, [f"semgrep scan timed out after {self.timeout}s: {exc}"]
        # 0 and 1 both mean the scan ran; 1 means findings were found.
        if result.returncode not in _SEMGREP_OK_EXIT_CODES:
            return findings, [
                f"semgrep exited {result.returncode}: "
                f"{result.stderr.strip() or result.stdout.strip()}"
            ]
        try:
            data = json.loads(result.stdout or "{}")
        except json.JSONDecodeError as exc:
            return findings, [f"semgrep output is not valid JSON: {exc}"]
        for result_entry in data.get("results", []) or []:
            if not isinstance(result_entry, dict):
                continue
            extra = result_entry.get("extra") or {}
            start = result_entry.get("start")
            findings.append(
                finding(
                    tool=self.name,
                    severity=_semgrep_severity(extra),
                    title=result_entry.get("check_id") or "semgrep finding",
                    description=extra.get("message"),
                    file_path=result_entry.get("path"),
                    line_number=start.get("line") if isinstance(start, dict) else None,
                    is_redacted=False,
                    references=[],
                )
            )
        return findings, errors
