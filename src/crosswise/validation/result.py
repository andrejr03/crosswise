"""Validation result structures for Crosswise fixture checks."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ValidationIssue:
    check: str
    message: str
    collection: str | None = None
    record_id: str | None = None
    field: str | None = None

    def format(self) -> str:
        parts = [self.check]
        if self.collection:
            parts.append(self.collection)
        if self.record_id:
            parts.append(self.record_id)
        if self.field:
            parts.append(self.field)
        return f"{' | '.join(parts)}: {self.message}"


@dataclass
class ValidationReport:
    passed_checks: list[str] = field(default_factory=list)
    failures: list[ValidationIssue] = field(default_factory=list)
    warnings: list[ValidationIssue] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return not self.failures

    def pass_check(self, check: str) -> None:
        self.passed_checks.append(check)

    def fail(
        self,
        check: str,
        message: str,
        collection: str | None = None,
        record_id: str | None = None,
        field: str | None = None,
    ) -> None:
        self.failures.append(
            ValidationIssue(
                check=check,
                message=message,
                collection=collection,
                record_id=record_id,
                field=field,
            )
        )

    def warn(
        self,
        check: str,
        message: str,
        collection: str | None = None,
        record_id: str | None = None,
        field: str | None = None,
    ) -> None:
        self.warnings.append(
            ValidationIssue(
                check=check,
                message=message,
                collection=collection,
                record_id=record_id,
                field=field,
            )
        )
