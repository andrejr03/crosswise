from __future__ import annotations

import subprocess
import sys
from pathlib import Path


REQUIRED_OUTPUTS = [
    "data/synthetic/fixtures_v1_0.json",
    "data/ground_truth/ground_truth_v1_0.json",
    "data/reconciliation/reconciliation_v1_0.json",
    "data/evaluation/evaluation_v1_0.json",
    "data/reliability/reliability_v1_0.json",
    "docs/evidence/CROSSWISE_LOCAL_EVIDENCE_REPORT_v1.0.md",
    "docs/evidence/crosswise_reviewer_v1_0.html",
    "docs/evidence/CROSSWISE_REVIEWER_DISCREPANCY_SHOWCASE.png",
]


def test_full_pipeline_script_runs_successfully_and_outputs_files() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    completed = subprocess.run(
        [sys.executable, "scripts/run_full_pipeline.py"],
        cwd=repo_root,
        check=True,
        text=True,
        capture_output=True,
    )

    assert "Crosswise full local pipeline completed successfully." in completed.stdout
    for relative_path in REQUIRED_OUTPUTS:
        assert (repo_root / relative_path).is_file()


def test_readme_contains_fresh_clone_quickstart_commands() -> None:
    readme = _readme_text()

    assert 'python3 -m pip install -e ".[dev]"' in readme
    assert "python3 scripts/generate_synthetic_data.py" in readme
    assert "python3 scripts/validate_fixtures.py" in readme
    assert "python3 scripts/run_reconciliation.py" in readme
    assert "python3 scripts/evaluate_reconciliation.py" in readme
    assert "python3 scripts/score_reliability.py" in readme
    assert "python3 scripts/generate_report.py" in readme
    assert "python3 scripts/generate_reviewer.py" in readme
    assert "python3 -m pytest" in readme


def test_readme_links_generated_evidence_and_reviewer() -> None:
    readme = _readme_text()

    assert "docs/evidence/CROSSWISE_LOCAL_EVIDENCE_REPORT_v1.0.md" in readme
    assert "docs/evidence/crosswise_reviewer_v1_0.html" in readme
    assert "docs/evidence/CROSSWISE_REVIEWER_DISCREPANCY_SHOWCASE.png" in readme
    assert "docs/evidence/INDEX.md" in readme


def test_readme_retains_synthetic_only_and_non_advice_statements() -> None:
    readme = _readme_text()

    assert "synthetic-data-only" in readme
    assert "Synthetic data only." in readme
    assert "No PII." in readme
    assert "No real invoices." in readme
    assert "No real company data." in readme
    assert "legal advice" in readme
    assert "financial advice" in readme
    assert "autonomous approval software" in readme


def _readme_text() -> str:
    repo_root = Path(__file__).resolve().parents[1]
    return (repo_root / "README.md").read_text(encoding="utf-8")
