"""Local Markdown report generation for Crosswise evidence outputs."""

from crosswise.reporting.local_report import (
    DEFAULT_OUTPUT_PATH,
    REQUIRED_OUTPUT_PATHS,
    generate_local_evidence_report,
    load_required_outputs,
    render_local_evidence_report,
    write_local_evidence_report,
)

__all__ = [
    "DEFAULT_OUTPUT_PATH",
    "REQUIRED_OUTPUT_PATHS",
    "generate_local_evidence_report",
    "load_required_outputs",
    "render_local_evidence_report",
    "write_local_evidence_report",
]
