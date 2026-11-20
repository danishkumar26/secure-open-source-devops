"""Database connectivity and model tests."""

from sqlalchemy import text

from app.models.finding import Finding, Severity
from app.models.repository import Repository
from app.models.scan import Scan, ScanStatus


def test_tables_exist(db_session):
    """All expected tables are present."""
    tables = {
        row[0]
        for row in db_session.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
    }
    assert {"repositories", "scans", "findings"} <= tables


def test_repository_crud(db_session):
    repo = Repository(
        github_owner="danishkumar26",
        github_repo="secure-open-source-devops",
        full_name="danishkumar26/secure-open-source-devops",
        html_url="https://github.com/danishkumar26/secure-open-source-devops",
        description="A DevSecOps platform.",
    )
    db_session.add(repo)
    db_session.commit()
    db_session.refresh(repo)

    assert repo.id is not None
    assert repo.created_at is not None

    fetched = db_session.get(Repository, repo.id)
    assert fetched.full_name == "danishkumar26/secure-open-source-devops"

    fetched.description = "Updated description"
    db_session.commit()
    assert db_session.get(Repository, repo.id).description == "Updated description"

    db_session.delete(fetched)
    db_session.commit()
    assert db_session.get(Repository, repo.id) is None


def test_scan_and_finding_lifecycle(db_session):
    repo = Repository(
        github_owner="owner",
        github_repo="repo",
        full_name="owner/repo",
        html_url="https://github.com/owner/repo",
    )
    db_session.add(repo)
    db_session.commit()

    scan = Scan(repository_id=repo.id, status=ScanStatus.running, trigger="manual")
    db_session.add(scan)
    db_session.commit()

    finding = Finding(
        scan_id=scan.id,
        tool="osv",
        severity=Severity.high,
        title="Vulnerable dependency",
        description="example-package is affected by CVE-EXAMPLE.",
        package_name="example-package",
        package_version="1.0.0",
        fixed_version="1.0.1",
        advisory_id="CVE-EXAMPLE",
        references=["https://osv.dev/v1/CVE-EXAMPLE"],
    )
    db_session.add(finding)
    db_session.commit()

    assert finding.id is not None
    assert scan.findings[0].title == "Vulnerable dependency"

    scan.status = ScanStatus.completed
    db_session.commit()
    assert db_session.get(Scan, scan.id).status == ScanStatus.completed
