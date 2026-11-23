"""Scanner tests: external services and binaries are mocked, never called."""

import json

import httpx
import pytest
from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.finding import Finding
from app.models.repository import Repository
from app.models.scan import Scan, ScanStatus
from app.scanners.base import finding, normalize_severity
from app.scanners.gitleaks import GitleaksScanner
from app.scanners.osv import OsVScanner
from app.scanners.semgrep import SemgrepScanner
from app.scanners.trivy import TrivyScanner
from app.services.scanner_service import run_scan


@pytest.mark.parametrize(
    "value,expected",
    [
        ("CRITICAL", "critical"),
        ("High", "high"),
        ("medium", "medium"),
        ("Low", "low"),
        ("UNKNOWN", "low"),
        (None, "low"),
        ("bogus", "low"),
    ],
)
def test_normalize_severity_maps_unknown_to_low(value, expected):
    assert normalize_severity(value) == expected


def test_finding_defaults_redacted_false_and_empty_references():
    result = finding(tool="osv", severity="high", title="t")
    assert result["is_redacted"] is False
    assert result["references"] == []
    assert result["severity"] == "high"


class _FakeHttpxResponse:
    def __init__(self, payload, status_code=200):
        self.status_code = status_code
        self._payload = payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError("boom", request=None, response=self)

    def json(self):
        return self._payload


class _FakeHttpxClient:
    def __init__(self, *args, **kwargs):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def post(self, url, *, json=None, timeout=None):
        return _FakeHttpxResponse(self._payload)


def test_osv_scanner_parses_advisory(monkeypatch):
    payload = {
        "vulns": [
            {
                "id": "GHSA-xxxx-1234",
                "summary": "demo has a flaw",
                "details": "details here",
                "database": {"severity": [{"type": "HIGH", "score": 7.5}]},
                "affected": [
                    {
                        "package": {"name": "demo", "ecosystem": "PyPI"},
                        "ranges": [{"events": [{"introduced": "0", "fixed": "1.2.3"}]}],
                    }
                ],
                "references": [{"url": "https://osv.dev/v1/GHSA-xxxx-1234"}],
            }
        ]
    }
    monkeypatch.setattr(httpx, "Client", lambda *a, **k: _FakeHttpxClient())
    monkeypatch.setattr(
        _FakeHttpxClient,
        "post",
        lambda self, url, *, json=None, timeout=None: _FakeHttpxResponse(payload),
    )
    findings, errors = OsVScanner().run("demo==1.0.0")
    assert errors == []
    assert len(findings) == 1
    f = findings[0]
    assert f["tool"] == "osv"
    assert f["severity"] == "high"
    assert f["title"] == "GHSA-xxxx-1234"
    assert f["package_name"] == "demo"
    assert f["package_version"] == "1.0.0"
    assert f["fixed_version"] == "1.2.3"
    assert f["advisory_id"] == "GHSA-xxxx-1234"
    assert f["is_redacted"] is False
    assert f["references"] == ["https://osv.dev/v1/GHSA-xxxx-1234"]


def test_osv_scanner_handles_http_error(monkeypatch):
    monkeypatch.setattr(httpx, "Client", lambda *a, **k: _FakeHttpxClient())
    monkeypatch.setattr(
        _FakeHttpxClient,
        "post",
        lambda self, url, *, json=None, timeout=None: _FakeHttpxResponse({}, 502),
    )
    findings, errors = OsVScanner().run("demo==1.0.0")
    assert findings == []
    assert len(errors) == 1


def _make_subprocess_result(returncode=0, stdout="", stderr=""):
    result = type("Result", (), {})()
    result.returncode = returncode
    result.stdout = stdout
    result.stderr = stderr
    return result


def test_trivy_scanner_parses_vulnerability(monkeypatch):
    output = json.dumps(
        {
            "Results": [
                {
                    "Target": "/repo/requirements.txt",
                    "Vulnerabilities": [
                        {
                            "VulnerabilityID": "CVE-2026-0001",
                            "PkgName": "demo",
                            "InstalledVersion": "1.0.0",
                            "FixedVersion": "1.0.1",
                            "Severity": "CRITICAL",
                            "Title": "demo: flaw",
                            "Description": "a flaw",
                            "PrimaryPath": "/repo/requirements.txt",
                            "References": [{"url": "https://cve.org/CVE-2026-0001"}],
                        }
                    ],
                }
            ]
        }
    )
    monkeypatch.setattr(
        "app.scanners.trivy.subprocess.run", lambda *a, **k: _make_subprocess_result(stdout=output)
    )
    findings, errors = TrivyScanner().run("/repo")
    assert errors == []
    assert len(findings) == 1
    f = findings[0]
    assert f["tool"] == "trivy"
    assert f["severity"] == "critical"
    assert f["advisory_id"] == "CVE-2026-0001"
    assert f["package_name"] == "demo"
    assert f["package_version"] == "1.0.0"
    assert f["fixed_version"] == "1.0.1"
    assert f["file_path"] == "/repo/requirements.txt"
    assert f["references"] == ["https://cve.org/CVE-2026-0001"]


def test_trivy_scanner_missing_binary(monkeypatch):
    monkeypatch.setattr(
        "app.scanners.trivy.subprocess.run",
        lambda *a, **k: (_ for _ in ()).throw(FileNotFoundError("trivy")),
    )
    findings, errors = TrivyScanner().run("/repo")
    assert findings == []
    assert len(errors) == 1


def test_gitleaks_scanner_redacts_secrets(monkeypatch):
    output = json.dumps(
        [
            {
                "RuleID": "generic-api-key",
                "Secret": "sk_live_actual_secret_value_do_not_store",
                "File": "/repo/app/core/config.py",
                "StartLine": 12,
                "EndLine": 12,
            }
        ]
    )
    monkeypatch.setattr(
        "app.scanners.gitleaks.subprocess.run",
        lambda *a, **k: _make_subprocess_result(stdout=output),
    )
    findings, errors = GitleaksScanner().run("/repo")
    assert errors == []
    assert len(findings) == 1
    f = findings[0]
    assert f["tool"] == "gitleaks"
    assert f["severity"] == "high"
    assert f["is_redacted"] is True
    assert f["file_path"] == "/repo/app/core/config.py"
    assert f["line_number"] == 12
    assert f["description"] == "Secret detected (redacted)"
    assert "sk_live" not in json.dumps(f)


def test_gitleaks_scanner_missing_binary(monkeypatch):
    monkeypatch.setattr(
        "app.scanners.gitleaks.subprocess.run",
        lambda *a, **k: (_ for _ in ()).throw(FileNotFoundError("gitleaks")),
    )
    findings, errors = GitleaksScanner().run("/repo")
    assert findings == []
    assert len(errors) == 1


_TRIVY_FINDING = {
    "tool": "trivy",
    "severity": "critical",
    "title": "CVE-2026-0001 in demo",
    "description": "a flaw",
    "package_name": "demo",
    "package_version": "1.0.0",
    "fixed_version": "1.0.1",
    "advisory_id": "CVE-2026-0001",
    "file_path": "/repo/requirements.txt",
    "line_number": None,
    "is_redacted": False,
    "references": ["https://cve.org/CVE-2026-0001"],
}


def _fake_clone_run(cmd, **kwargs):
    return _make_subprocess_result(returncode=0)


def _install_service_fakes(monkeypatch):
    # Patch the real scanner classes: SCANNERS holds references to those
    # classes, so patching this module's attributes would have no effect.
    monkeypatch.setattr("app.services.scanner_service.subprocess.run", _fake_clone_run)
    monkeypatch.setattr(
        "app.scanners.trivy.TrivyScanner.run", lambda self, target: ([_TRIVY_FINDING], [])
    )
    monkeypatch.setattr("app.scanners.gitleaks.GitleaksScanner.run", lambda self, target: ([], []))


def _create_repo_and_scan(db, owner="owner", repo="repo"):
    repository = Repository(
        github_owner=owner,
        github_repo=repo,
        full_name=f"{owner}/{repo}",
        html_url=f"https://github.com/{owner}/{repo}",
    )
    db.add(repository)
    db.commit()
    db.refresh(repository)
    scan = Scan(repository_id=repository.id, status=ScanStatus.pending, trigger="manual")
    db.add(scan)
    db.commit()
    db.refresh(scan)
    return repository, scan


def test_run_scan_completes_and_stores_findings(monkeypatch):
    _install_service_fakes(monkeypatch)
    db = SessionLocal()
    try:
        repository, scan = _create_repo_and_scan(db)
        scan_id = scan.id
        repository_id = repository.id
    finally:
        db.close()

    run_scan(scan_id)

    db = SessionLocal()
    try:
        scan = db.get(Scan, scan_id)
        assert scan.status == ScanStatus.completed
        assert scan.started_at is not None
        assert scan.completed_at is not None
        assert scan.summary["finding_count"] == 1
        assert "clone" not in scan.summary["errors"]
        findings = db.execute(select(Finding).where(Finding.scan_id == scan_id)).scalars().all()
        assert len(findings) == 1
        finding_row = findings[0]
        assert finding_row.tool == "trivy"
        assert finding_row.severity == "critical"
        assert finding_row.package_name == "demo"
        assert finding_row.is_redacted is False
        repository = db.get(Repository, repository_id)
        assert repository.last_scanned_at is not None
    finally:
        db.close()


def test_run_scan_fails_when_clone_fails(monkeypatch):
    def failing_clone(cmd, **kwargs):
        return _make_subprocess_result(returncode=128, stderr="fatal: repository not found")

    monkeypatch.setattr("app.services.scanner_service.subprocess.run", failing_clone)

    db = SessionLocal()
    try:
        _repository, scan = _create_repo_and_scan(db, owner="nope", repo="nope")
        scan_id = scan.id
    finally:
        db.close()

    run_scan(scan_id)

    db = SessionLocal()
    try:
        scan = db.get(Scan, scan_id)
        assert scan.status == ScanStatus.failed
        assert "clone" in (scan.summary or {}).get("errors", {})
    finally:
        db.close()


def test_trigger_scan_queues_run_scan(client, monkeypatch):
    """POST /repositories/{id}/scans returns 202 and enqueues run_scan for
    the new scan record. (run_scan itself is covered by test_run_scan_*.)"""
    calls: list[int] = []
    monkeypatch.setattr("app.api.repositories.run_scan", lambda scan_id: calls.append(scan_id))
    response = client.post(
        "/repositories",
        json={
            "github_owner": "trigger-owner",
            "github_repo": "trigger-repo",
            "html_url": "https://github.com/trigger-owner/trigger-repo",
        },
    )
    assert response.status_code == 201, response.text
    repository_id = response.json()["id"]

    response = client.post(f"/repositories/{repository_id}/scans")
    assert response.status_code == 202, response.text
    assert calls == [response.json()["id"]]


def test_semgrep_scanner_parses_finding(monkeypatch):
    output = json.dumps(
        {
            "results": [
                {
                    "check_id": "python.requests.sast",
                    "path": "/repo/app/core/config.py",
                    "start": {"line": 12, "col": 1},
                    "extra": {"message": "Hardcoded secret detected", "severity": "ERROR"},
                }
            ]
        }
    )
    monkeypatch.setattr(
        "app.scanners.semgrep.subprocess.run",
        lambda *a, **k: _make_subprocess_result(stdout=output),
    )
    findings, errors = SemgrepScanner().run("/repo")
    assert errors == []
    assert len(findings) == 1
    f = findings[0]
    assert f["tool"] == "semgrep"
    assert f["severity"] == "high"
    assert f["title"] == "python.requests.sast"
    assert f["description"] == "Hardcoded secret detected"
    assert f["file_path"] == "/repo/app/core/config.py"
    assert f["line_number"] == 12
    assert f["is_redacted"] is False
    assert f["references"] == []


def test_semgrep_scanner_missing_binary(monkeypatch):
    monkeypatch.setattr(
        "app.scanners.semgrep.subprocess.run",
        lambda *a, **k: (_ for _ in ()).throw(FileNotFoundError("semgrep")),
    )
    findings, errors = SemgrepScanner().run("/repo")
    assert findings == []
    assert len(errors) == 1
