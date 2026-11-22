"""Gitleaks secret detection scanner wrapper."""

import json
import subprocess
from typing import TYPE_CHECKING

from .base import FindingDict, Scanner, finding

if TYPE_CHECKING:
    pass


class GitleaksScanner(Scanner):
    """Runs ``gitleaks detect`` against a checked-out repository directory.

    Secret values are never stored: findings are redacted and only the file
    path, line, rule and title are kept.
    """

    name = "gitleaks"

    def __init__(self, timeout: float = 300.0) -> None:
        self.timeout = timeout

    def run(self, target: str) -> tuple[list[FindingDict], list[str]]:
        findings: list[FindingDict] = []
        errors: list[str] = []
        try:
            result = subprocess.run(
                [
                    "gitleaks",
                    "detect",
                    "--source",
                    target,
                    "--format",
                    "json",
                    "--no-banner",
                    "--exit-code",
                    "0",
                ],
                capture_output=True,
                text=True,
                timeout=self.timeout + 60,
                check=False,
            )
        except FileNotFoundError:
            return findings, [
                "gitleaks binary not found; install gitleaks to enable secret detection"
            ]
        except subprocess.TimeoutExpired as exc:
            return findings, [f"gitleaks scan timed out after {self.timeout}s: {exc}"]
        # --exit-code 0 makes gitleaks exit 0 even when leaks are found; any
        # other non-zero exit is an execution error.
        if result.returncode != 0:
            return findings, [
                f"gitleaks exited {result.returncode}: "
                f"{result.stderr.strip() or result.stdout.strip()}"
            ]
        try:
            leaks = json.loads(result.stdout or "[]")
        except json.JSONDecodeError as exc:
            return findings, [f"gitleaks output is not valid JSON: {exc}"]
        if not isinstance(leaks, list):
            return findings, ["gitleaks output is not a list of leaks"]
        for leak in leaks:
            if not isinstance(leak, dict):
                continue
            findings.append(
                finding(
                    tool=self.name,
                    severity="high",
                    title=str(leak.get("RuleID") or "secret detected"),
                    description="Secret detected (redacted)",
                    file_path=leak.get("File") or leak.get("path"),
                    line_number=leak.get("StartLine") or leak.get("start_line"),
                    advisory_id=str(leak.get("RuleID") or ""),
                    is_redacted=True,
                    references=[],
                )
            )
        return findings, errors
