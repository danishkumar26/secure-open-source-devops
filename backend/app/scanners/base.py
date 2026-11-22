"""Shared scanner base types and result normalization helpers."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


class ScannerError(Exception):
    """Raised when a scanner invocation fails."""


# Normalized finding dicts mirror the columns of app.models.Finding so the
# scanner service can store scanner output without an extra translation layer.
FindingDict = dict[str, object]

SEVERITY_MAP = {
    "CRITICAL": "critical",
    "HIGH": "high",
    "MEDIUM": "medium",
    "LOW": "low",
    "UNKNOWN": "low",
}


def normalize_severity(value: str | None) -> str:
    """Map a scanner severity string to the platform severity vocabulary.

    Anything unrecognized becomes ``low`` so scanner output changes can never
    crash ingestion or insert an invalid enum value.
    """
    return SEVERITY_MAP.get((value or "").strip().upper(), "low")


def finding(
    *,
    tool: str,
    severity: str,
    title: str,
    description: str | None = None,
    package_name: str | None = None,
    package_version: str | None = None,
    fixed_version: str | None = None,
    advisory_id: str | None = None,
    file_path: str | None = None,
    line_number: int | None = None,
    is_redacted: bool = False,
    references: list[str] | None = None,
) -> FindingDict:
    """Build a normalized finding dict."""
    return {
        "tool": tool,
        "severity": normalize_severity(severity),
        "title": title,
        "description": description,
        "package_name": package_name,
        "package_version": package_version,
        "fixed_version": fixed_version,
        "advisory_id": advisory_id,
        "file_path": file_path,
        "line_number": line_number,
        "is_redacted": is_redacted,
        "references": references or [],
    }


class Scanner:
    """Base class for security scanner integrations.

    Subclasses set ``name`` and implement ``run(target)`` returning
    ``(findings, errors)``. The service wraps every scanner call so one
    failing scanner never aborts a whole scan.
    """

    name: str = "scanner"

    def run(self, target: str) -> tuple[list[FindingDict], list[str]]:
        """Run the scanner against ``target``.

        Returns the normalized findings and any non-fatal errors.
        """
        raise NotImplementedError
