"""Repository, scan, and finding API routes."""

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Path, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.finding import Finding
from app.models.repository import Repository
from app.models.scan import Scan
from app.schemas.error import ErrorResponse
from app.schemas.finding import FindingRead
from app.schemas.repository import RepositoryCreate, RepositoryRead
from app.schemas.scan import ScanCreate, ScanRead
from app.services.scanner_service import run_scan

router = APIRouter()


@router.post(
    "",
    response_model=RepositoryRead,
    status_code=status.HTTP_201_CREATED,
    responses={409: {"model": ErrorResponse}},
)
def create_repository(repository: RepositoryCreate, db: Session = Depends(get_db)):
    """Register a repository for monitoring."""
    full_name = f"{repository.github_owner}/{repository.github_repo}"
    existing = db.execute(
        select(Repository).where(Repository.full_name == full_name)
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Repository '{full_name}' is already being monitored.",
        )
    db_repository = Repository(
        github_owner=repository.github_owner,
        github_repo=repository.github_repo,
        full_name=full_name,
        html_url=str(repository.html_url),
        description=repository.description,
        default_branch=repository.default_branch,
        is_private=repository.is_private,
    )
    db.add(db_repository)
    db.commit()
    db.refresh(db_repository)
    return db_repository


@router.get("", response_model=list[RepositoryRead])
def list_repositories(db: Session = Depends(get_db)):
    """List all monitored repositories."""
    return db.execute(select(Repository).order_by(Repository.created_at.desc())).scalars().all()


@router.get("/{repository_id}", response_model=RepositoryRead)
def get_repository(repository_id: int = Path(..., ge=1), db: Session = Depends(get_db)):
    """Get a single monitored repository by ID."""
    repository = db.get(Repository, repository_id)
    if repository is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repository not found")
    return repository


@router.delete("/{repository_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_repository(repository_id: int = Path(..., ge=1), db: Session = Depends(get_db)):
    """Stop monitoring a repository and delete its scans and findings."""
    repository = db.get(Repository, repository_id)
    if repository is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repository not found")
    db.delete(repository)
    db.commit()
    return


@router.post(
    "/{repository_id}/scans", response_model=ScanRead, status_code=status.HTTP_202_ACCEPTED
)
def trigger_scan(
    background_tasks: BackgroundTasks,
    repository_id: int = Path(..., ge=1),
    scan_in: ScanCreate | None = None,
    db: Session = Depends(get_db),
):
    """Queue a security scan for a repository.

    Scanners (Trivy, Gitleaks, OSV) run in a background task after the
    response is sent; the scan record transitions pending -> running ->
    completed/failed and its findings are stored.
    """
    repository = db.get(Repository, repository_id)
    if repository is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repository not found")
    trigger = scan_in.trigger if scan_in else "manual"
    db_scan = Scan(repository_id=repository_id, status="pending", trigger=trigger)
    db.add(db_scan)
    db.commit()
    db.refresh(db_scan)
    if background_tasks is not None:
        background_tasks.add_task(run_scan, db_scan.id)
    return db_scan


@router.get("/{repository_id}/scans", response_model=list[ScanRead])
def list_scans(repository_id: int = Path(..., ge=1), db: Session = Depends(get_db)):
    """List scan history for a repository."""
    repository = db.get(Repository, repository_id)
    if repository is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repository not found")
    return (
        db.execute(
            select(Scan)
            .where(Scan.repository_id == repository_id)
            .order_by(Scan.started_at.desc().nullslast())
        )
        .scalars()
        .all()
    )


@router.get("/{repository_id}/scans/{scan_id}/findings", response_model=list[FindingRead])
def list_findings(
    repository_id: int = Path(..., ge=1),
    scan_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
):
    """List findings for a scan."""
    scan = db.get(Scan, scan_id)
    if scan is None or scan.repository_id != repository_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found")
    return (
        db.execute(
            select(Finding).where(Finding.scan_id == scan_id).order_by(Finding.created_at.desc())
        )
        .scalars()
        .all()
    )
