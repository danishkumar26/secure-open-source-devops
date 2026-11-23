"""Orchestrates security scans: clone, run scanners, store results.

Called as a FastAPI background task after a scan record is created, so the
API returns 202 immediately while scanners run. Uses its own database
session because the request session is closed by the time this executes.
"""

import os
import re
import subprocess
import tempfile
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.finding import Finding
from app.models.repository import Repository
from app.models.scan import Scan, ScanStatus
from app.scanners.base import Scanner
from app.scanners.gitleaks import GitleaksScanner
from app.scanners.osv import OsVScanner
from app.scanners.semgrep import SemgrepScanner
from app.scanners.trivy import TrivyScanner

# Shortcut: one fixed clone timeout for every repository. Upgrade: make it
# configurable per repository or scale with repository size.
_CLONE_TIMEOUT = 300
_MAX_PACKAGES = 25

_REQUIREMENTS_RE = re.compile(r"^\s*([A-Za-z0-9_.\-]+)\s*==\s*([A-Za-z0-9_.\+]+)\s*$")

# Repo-level scanners run on the checked-out repository. OSV is run per
# package parsed from requirements.txt (Day 4 scope; dependency analysis is
# Day 5).
SCANNERS: list[type[Scanner]] = [TrivyScanner, GitleaksScanner, SemgrepScanner]


def _parse_requirements_packages(path: str) -> list[tuple[str, str]]:
    """Return ``(package, version)`` pins from a requirements.txt file.

    Shortcut: pins with extras, environment markers, or URLs are ignored.
    Upgrade: delegate to a real requirements/lockfile parser.
    """
    packages: list[tuple[str, str]] = []
    try:
        with open(path, encoding="utf-8") as handle:
            for line in handle:
                match = _REQUIREMENTS_RE.match(line)
                if match:
                    packages.append((match.group(1), match.group(2)))
                    if len(packages) >= _MAX_PACKAGES:
                        break
    except OSError:
        return []
    return packages


def _store_findings(db: Session, scan: Scan, findings: list[dict]) -> None:
    for item in findings:
        db.add(
            Finding(
                scan_id=scan.id,
                tool=str(item.get("tool", "")),
                severity=item["severity"],
                title=str(item.get("title") or ""),
                description=item.get("description"),
                package_name=item.get("package_name"),
                package_version=item.get("package_version"),
                fixed_version=item.get("fixed_version"),
                advisory_id=item.get("advisory_id"),
                file_path=item.get("file_path"),
                line_number=item.get("line_number"),
                is_redacted=bool(item.get("is_redacted", False)),
                references=item.get("references") or [],
            )
        )


def run_scan(scan_id: int) -> None:
    """Run all enabled scanners for ``scan_id`` and persist the results.

    One scanner failing never aborts the scan: per-scanner errors are
    recorded in ``scan.summary`` and ingestion continues.
    """
    db: Session = SessionLocal()
    try:
        scan = db.get(Scan, scan_id)
        if scan is None:
            return
        repository = db.get(Repository, scan.repository_id)
        if repository is None:
            return

        scan.status = ScanStatus.running
        scan.started_at = datetime.now(UTC)
        db.commit()

        findings: list[dict] = []
        errors: dict[str, str] = {}

        with tempfile.TemporaryDirectory(prefix="secure-devops-scan-") as workdir:
            clone_path = os.path.join(workdir, "repo")
            clone = subprocess.run(
                ["git", "clone", "--depth", "1", repository.html_url, clone_path],
                capture_output=True,
                text=True,
                timeout=_CLONE_TIMEOUT,
            )
            if clone.returncode != 0:
                errors["clone"] = (
                    clone.stderr.strip()
                    or clone.stdout.strip()
                    or f"git clone exited {clone.returncode}"
                )
            else:
                for scanner_class in SCANNERS:
                    scanner = scanner_class()
                    try:
                        scanner_findings, scanner_errors = scanner.run(clone_path)
                        findings.extend(scanner_findings)
                        if scanner_errors:
                            errors[scanner.name] = "; ".join(scanner_errors)
                    except Exception as exc:  # one scanner must not abort the scan
                        errors[scanner.name] = f"{type(exc).__name__}: {exc}"
                # OSV needs package metadata, which is not available until
                # dependency analysis (Day 5). Query OSV for the pinned
                # packages in requirements.txt as a scoped integration.
                for package, version in _parse_requirements_packages(
                    os.path.join(clone_path, "requirements.txt")
                ):
                    try:
                        osv_findings, osv_errors = OsVScanner().run(f"{package}=={version}")
                        findings.extend(osv_findings)
                        if osv_errors:
                            errors[f"{OsVScanner.name}:{package}"] = "; ".join(osv_errors)
                    except Exception as exc:
                        errors[f"{OsVScanner.name}:{package}"] = f"{type(exc).__name__}: {exc}"

        _store_findings(db, scan, findings)

        now = datetime.now(UTC)
        scan.completed_at = now
        scan.summary = {
            "scanners": [scanner.name for scanner in SCANNERS] + [OsVScanner.name],
            "errors": errors,
            "finding_count": len(findings),
        }
        repository.last_scanned_at = now
        # A scan that produced no results because everything errored failed;
        # partial scanner errors with findings are still completed.
        scan.status = ScanStatus.failed if errors and not findings else ScanStatus.completed
        db.commit()
    except Exception as exc:  # orchestration failure: keep the scan record, mark failed
        scan = db.get(Scan, scan_id)
        if scan is not None:
            scan.status = ScanStatus.failed
            scan.error_message = f"{type(exc).__name__}: {exc}"
            db.commit()
    finally:
        db.close()
