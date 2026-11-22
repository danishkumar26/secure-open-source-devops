"""OSV.dev vulnerability query scanner."""

import httpx

from .base import FindingDict, Scanner, finding, normalize_severity

OSV_API_URL = "https://api.osv.dev/v1/query"

# Shortcut: only the PyPI ecosystem is supported and only requirements.txt
# pins are queried (parsed by the scanner service). Upgrade: parse other
# lockfiles (package.json, go.mod, Cargo.toml) and map their ecosystems.
ECOSYSTEM = "PyPI"
_MAX_PACKAGES = 25


class OsVScanner(Scanner):
    """Queries the OSV API for vulnerabilities affecting a package version."""

    name = "osv"

    def __init__(self, timeout: float = 30.0) -> None:
        self.timeout = timeout

    def run(self, target: str) -> tuple[list[FindingDict], list[str]]:
        """``target`` is ``package==version``; returns OSV advisories."""
        findings: list[FindingDict] = []
        errors: list[str] = []
        if "==" not in target:
            return findings, [f"invalid osv target: {target!r}"]
        package, version = target.split("==", 1)
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    OSV_API_URL,
                    json={"package": {"name": package, "ecosystem": ECOSYSTEM}, "version": version},
                )
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPError as exc:
            return findings, [f"osv query failed for {package} {version}: {exc}"]
        findings.extend(
            finding(
                tool=self.name,
                severity=self._severity(vuln),
                title=vuln.get("id") or "OSV advisory",
                description=vuln.get("summary") or vuln.get("details"),
                package_name=package,
                package_version=version,
                fixed_version=self._fixed_version(vuln),
                advisory_id=vuln.get("id"),
                references=[
                    ref.get("url", "")
                    for ref in vuln.get("references", []) or []
                    if isinstance(ref, dict) and ref.get("url")
                ],
            )
            for vuln in data.get("vulns", []) or []
        )
        return findings, errors

    @staticmethod
    def _severity(vuln: dict) -> str:
        severities = vuln.get("database", {}).get("severity", []) or []
        if severities:
            return normalize_severity(severities[0].get("type"))
        return "low"

    @staticmethod
    def _fixed_version(vuln: dict) -> str | None:
        for affected in vuln.get("affected", []) or []:
            for rng in affected.get("ranges", []) or []:
                for event in rng.get("events", []) or []:
                    if isinstance(event, dict) and "fixed" in event:
                        return event["fixed"]
        return None
