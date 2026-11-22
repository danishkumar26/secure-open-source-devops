"""Trivy filesystem vulnerability scanner wrapper."""

import json
import subprocess
from typing import TYPE_CHECKING

from .base import FindingDict, Scanner, finding

if TYPE_CHECKING:
    pass


class TrivyScanner(Scanner):
    """Runs ``trivy fs`` against a checked-out repository directory."""

    name = "trivy"

    def __init__(self, timeout: float = 300.0, skip_dirs: str = ".git") -> None:
        self.timeout = timeout
        self.skip_dirs = skip_dirs

    def run(self, target: str) -> tuple[list[FindingDict], list[str]]:
        findings: list[FindingDict] = []
        errors: list[str] = []
        try:
            result = subprocess.run(
                [
                    "trivy",
                    "fs",
                    "--format",
                    "json",
                    "--timeout",
                    f"{int(self.timeout)}s",
                    "--skip-dirs",
                    self.skip_dirs,
                    target,
                ],
                capture_output=True,
                text=True,
                timeout=self.timeout + 60,
                check=False,
            )
        except FileNotFoundError:
            return findings, [
                "trivy binary not found; install trivy to enable filesystem vulnerability scanning"
            ]
        except subprocess.TimeoutExpired as exc:
            return findings, [f"trivy scan timed out after {self.timeout}s: {exc}"]
        # Trivy exits 0 when nothing is found, 1 when vulnerabilities exist,
        # anything else is an execution error.
        if result.returncode not in (0, 1):
            return findings, [
                f"trivy exited {result.returncode}: "
                f"{result.stderr.strip() or result.stdout.strip()}"
            ]
        try:
            data = json.loads(result.stdout or "{}")
        except json.JSONDecodeError as exc:
            return findings, [f"trivy output is not valid JSON: {exc}"]
        for result_entry in data.get("Results", []) or []:
            findings.extend(
                finding(
                    tool=self.name,
                    severity=vuln.get("Severity", "UNKNOWN"),
                    title=vuln.get("Title") or vuln.get("VulnerabilityID") or "trivy finding",
                    description=vuln.get("Description"),
                    package_name=vuln.get("PkgName"),
                    package_version=vuln.get("InstalledVersion"),
                    fixed_version=vuln.get("FixedVersion"),
                    advisory_id=vuln.get("VulnerabilityID"),
                    file_path=vuln.get("PrimaryPath") or result_entry.get("Target"),
                    references=[
                        ref.get("url", "")
                        for ref in vuln.get("References", []) or []
                        if isinstance(ref, dict) and ref.get("url")
                    ],
                )
                for vuln in result_entry.get("Vulnerabilities", []) or []
            )
        return findings, errors
