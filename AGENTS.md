# Project Identity

Crosswise is an AI document reconciliation project focused on:

- structured document records
- invoice / purchase order / receipt reconciliation
- discrepancy detection
- field-level reliability
- evidence-backed decisions
- human-review workflows

# Repository Source of Truth

Primary planning references:

- `docs/plans/CROSSWISE_PROJECT_SYNTHESIS_AND_FOUNDATION_v1.0.md`
- `docs/plans/CROSSWISE_SLICE_0_TECHNICAL_CONTRACT_AND_SYSTEM_SPECIFICATION_v1.0.md`

Agents must read these before major work.

# Git Policy

Agents must never:

- create branches
- switch branches
- rename branches
- delete branches
- merge branches
- rebase branches
- alter remotes

unless explicitly instructed by the repository owner.

Default behavior:

Work only on the currently checked-out branch.

# Commit Policy

Agents must never:

- run `git add`
- run `git commit`
- run `git push`
- run `git tag`

unless explicitly instructed.

Always stop after implementation, validation, evidence, and `git status --short`.

# Data Policy

Crosswise must remain:

- synthetic-data-first
- no PII
- no real invoices
- no real company data
- no real supplier data
- no payment information
- no tax identifiers
- no bank details

# Scope Control

Agents must not introduce:

- OCR
- live APIs
- real documents
- deployment infrastructure
- payment workflows
- accounting logic
- legal advice
- tax advice
- financial advice
- autonomous actions

unless a future approved planning document explicitly authorizes them.

# Prototype Policy

The file:

`assets/prototypes/crosswise-prototype.zip`

is a preserved design artifact.

Agents must not:

- overwrite it
- regenerate it
- replace it
- delete it

unless explicitly instructed.

# Documentation Policy

When creating new planning artifacts:

Store them under:

`docs/plans/`

Evidence:

`docs/evidence/`

Reviews:

`docs/reviews/`

# Implementation Policy

Agents must follow the approved slice sequence.

Current state:

Completed:

- Foundation
- Slice 0
- Slice 1

Do not skip directly to advanced features.

Respect approved scope boundaries.

# Validation Policy

Before stopping, agents should:

- run relevant tests
- report validation results
- report created/modified files
- report `git status --short`

# Communication Policy

Be concise.
Do not create unnecessary plans.
Do not re-open settled project decisions.
Do not rename Crosswise.
Do not revisit project selection.
