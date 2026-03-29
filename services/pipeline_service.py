"""PipelineService — Business logic for pipeline operations.

Implements interactions: I-001 through I-009 from INTERACTION-MAP.
Called by: MCP agents-server tools, REST /api/v1/pipelines/* routes.
Never import from mcp_servers/ or api/.

Data shapes returned: PipelineRun, PipelineDocument, PipelineConfig, ValidationResult
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from pathlib import Path
from uuid import UUID, uuid4

import asyncpg

from schemas.data_shapes import (
    PipelineConfig,
    PipelineDocument,
    PipelineRun,
    PipelineStatus,
    ValidationResult,
)


# Valid pipeline names
VALID_PIPELINES = {"document-stack", "feature-development", "bug-fix", "hotfix", "security-patch"}

# Default pipeline config (in production, loaded from teams/*.yaml)
DEFAULT_PIPELINE_CONFIG = PipelineConfig(
    pipeline_name="document-stack",
    steps=[
        # Pre-Phase + Phase A (Steps 0-3)
        "D0-brd", "D1-roadmap", "D2-prd", "D3-arch",
        # Phase B — Decomposition (Steps 4-6)
        "D4-features", "D5-quality", "D6-security",
        # Phase C — Interface Design (Steps 7-9)
        "D7-interaction", "D8-mcp", "D9-design",
        # Phase D — Data & Build-Facing (Steps 10-15)
        "D10-data", "D11-api", "D12-user-stories", "D13-backlog", "D14-claude", "D15-enforce",
        # Phase E — Operations, Safety & Compliance (Steps 16-21)
        "D16-infra", "D17-migration", "D18-testing", "D19-fault-tolerance", "D20-guardrails", "D21-compliance",
    ],
    cost_ceiling_usd=Decimal("45.00"),
    parallel_groups=[
        ["D1-roadmap", "D2-prd"],       # Phase A: ROADMAP ‖ PRD
        ["D8-mcp", "D9-design"],         # Phase C: MCP-TOOL-SPEC ‖ DESIGN-SPEC
        ["D17-migration", "D18-testing"],# Phase E: MIGRATION ‖ TESTING
    ],
    gate_types={
        "D6-security": "quality_gate",   # After decomposition, before interface design
        "D7-interaction": "quality_gate", # INTERACTION-MAP gates parallel MCP+DESIGN
        "D11-api": "quality_gate",       # After data model, before build-facing docs
        "D19-fault-tolerance": "quality_gate",  # After infra, before safety docs
    },
)


class PipelineNotFoundError(Exception):
    """Raised when a pipeline run_id does not exist."""

    def __init__(self, run_id: UUID) -> None:
        self.run_id = run_id
        super().__init__(f"Pipeline run not found: {run_id}")


class PipelineStateError(Exception):
    """Raised when an operation is invalid for the current pipeline state."""

    def __init__(self, run_id: UUID, current_status: str, attempted_action: str) -> None:
        self.run_id = run_id
        self.current_status = current_status
        self.attempted_action = attempted_action
        super().__init__(
            f"Cannot {attempted_action} pipeline {run_id}: current status is '{current_status}'"
        )


class PipelineService:
    """Pipeline execution management.

    All methods return INTERACTION-MAP data shapes.
    State guards enforce valid transitions (can't cancel completed, etc.).
    """

    def __init__(self, db: asyncpg.Pool) -> None:
        self._db = db

    async def trigger(
        self,
        project_id: str,
        pipeline_name: str,
        brief: str,
        triggered_by: str = "system",
    ) -> PipelineRun:
        """I-001: Trigger a new pipeline run.

        Creates a pipeline_runs record with status='pending'.
        Creates pipeline_steps records for each step in the pipeline.
        """
        if pipeline_name not in VALID_PIPELINES:
            raise ValueError(f"Invalid pipeline: {pipeline_name}. Valid: {VALID_PIPELINES}")

        config = self._get_config(pipeline_name)
        run_id = uuid4()

        row = await self._db.fetchrow(
            """
            INSERT INTO pipeline_runs (run_id, project_id, pipeline_name, status, current_step, total_steps, triggered_by)
            VALUES ($1, $2, $3, 'pending', 0, $4, $5)
            RETURNING run_id, project_id, pipeline_name, status, current_step, total_steps,
                      triggered_by, started_at, completed_at, cost_usd
            """,
            run_id,
            project_id,
            pipeline_name,
            len(config.steps),
            triggered_by,
        )

        return self._row_to_pipeline_run(row)

    async def get_status(self, run_id: UUID) -> PipelineRun:
        """I-002: Get the current status of a pipeline run."""
        row = await self._db.fetchrow(
            """
            SELECT run_id, project_id, pipeline_name, status, current_step, total_steps,
                   triggered_by, started_at, completed_at, cost_usd
            FROM pipeline_runs WHERE run_id = $1
            """,
            run_id,
        )
        if row is None:
            raise PipelineNotFoundError(run_id)
        return self._row_to_pipeline_run(row)

    async def list_runs(
        self,
        project_id: str,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[PipelineRun]:
        """I-003: List pipeline runs for a project, optionally filtered by status."""
        if status:
            rows = await self._db.fetch(
                """
                SELECT run_id, project_id, pipeline_name, status, current_step, total_steps,
                       triggered_by, started_at, completed_at, cost_usd
                FROM pipeline_runs
                WHERE project_id = $1 AND status = $2
                ORDER BY started_at DESC
                LIMIT $3 OFFSET $4
                """,
                project_id,
                status,
                limit,
                offset,
            )
        else:
            rows = await self._db.fetch(
                """
                SELECT run_id, project_id, pipeline_name, status, current_step, total_steps,
                       triggered_by, started_at, completed_at, cost_usd
                FROM pipeline_runs
                WHERE project_id = $1
                ORDER BY started_at DESC
                LIMIT $2 OFFSET $3
                """,
                project_id,
                limit,
                offset,
            )
        return [self._row_to_pipeline_run(row) for row in rows]

    async def resume(self, run_id: UUID) -> PipelineRun:
        """I-004: Resume a paused pipeline from its checkpoint."""
        current = await self.get_status(run_id)
        if current.status != PipelineStatus.PAUSED:
            raise PipelineStateError(run_id, current.status.value, "resume")

        row = await self._db.fetchrow(
            """
            UPDATE pipeline_runs SET status = 'running', updated_at = NOW()
            WHERE run_id = $1
            RETURNING run_id, project_id, pipeline_name, status, current_step, total_steps,
                      triggered_by, started_at, completed_at, cost_usd
            """,
            run_id,
        )
        return self._row_to_pipeline_run(row)

    async def cancel(self, run_id: UUID) -> PipelineRun:
        """I-005: Cancel a running or paused pipeline."""
        current = await self.get_status(run_id)
        if current.status not in (PipelineStatus.RUNNING, PipelineStatus.PAUSED, PipelineStatus.PENDING):
            raise PipelineStateError(run_id, current.status.value, "cancel")

        row = await self._db.fetchrow(
            """
            UPDATE pipeline_runs SET status = 'cancelled', completed_at = NOW(), updated_at = NOW()
            WHERE run_id = $1
            RETURNING run_id, project_id, pipeline_name, status, current_step, total_steps,
                      triggered_by, started_at, completed_at, cost_usd
            """,
            run_id,
        )
        return self._row_to_pipeline_run(row)

    async def get_documents(self, run_id: UUID) -> list[PipelineDocument]:
        """I-006: Get all generated documents for a completed pipeline run."""
        await self.get_status(run_id)  # Verify run exists

        rows = await self._db.fetch(
            """
            SELECT step_number, step_name, agent_id, output_key, quality_score,
                   token_count, completed_at
            FROM pipeline_steps
            WHERE run_id = $1 AND status = 'completed' AND output_key IS NOT NULL
            ORDER BY step_number
            """,
            run_id,
        )

        documents = []
        for row in rows:
            documents.append(PipelineDocument(
                document_name=row["step_name"],
                document_number=row["step_number"],
                content="",  # Content lives in filesystem; loaded separately
                agent_id=row["agent_id"],
                generated_at=row["completed_at"] or datetime.now(),
                quality_score=float(row["quality_score"]) if row["quality_score"] else None,
            ))
        return documents

    async def get_config(self, pipeline_name: str) -> PipelineConfig:
        """I-008: Get pipeline configuration (steps, parallel groups, gates)."""
        return self._get_config(pipeline_name)

    async def validate_input(
        self, project_id: str, pipeline_name: str, brief: str
    ) -> ValidationResult:
        """I-009: Validate pipeline input before triggering."""
        errors: list[str] = []
        warnings: list[str] = []

        if not project_id or not project_id.strip():
            errors.append("project_id is required")
        if pipeline_name not in VALID_PIPELINES:
            errors.append(f"Invalid pipeline_name: '{pipeline_name}'. Valid: {sorted(VALID_PIPELINES)}")
        if not brief or len(brief.strip()) < 10:
            errors.append("brief must be at least 10 characters")
        if brief and len(brief) > 10000:
            warnings.append("brief exceeds 10000 characters; may increase cost")

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )

    async def update_step_status(
        self,
        run_id: UUID,
        step_number: int,
        status: str,
        output_key: str | None = None,
        quality_score: float | None = None,
        cost_usd: Decimal | None = None,
        error_message: str | None = None,
    ) -> None:
        """Internal: Update a pipeline step's status (called by orchestrator)."""
        await self._db.execute(
            """
            UPDATE pipeline_steps SET
                status = $3,
                output_key = COALESCE($4, output_key),
                quality_score = COALESCE($5, quality_score),
                cost_usd = COALESCE($6, cost_usd),
                error_message = $7,
                completed_at = CASE WHEN $3 IN ('completed', 'failed') THEN NOW() ELSE completed_at END,
                started_at = CASE WHEN $3 = 'running' AND started_at IS NULL THEN NOW() ELSE started_at END
            WHERE run_id = $1 AND step_number = $2
            """,
            run_id,
            step_number,
            status,
            output_key,
            quality_score,
            cost_usd,
            error_message,
        )

    async def update_run_progress(
        self, run_id: UUID, current_step: int, status: str, cost_usd: Decimal | None = None
    ) -> None:
        """Internal: Update pipeline run progress (called by orchestrator)."""
        await self._db.execute(
            """
            UPDATE pipeline_runs SET
                current_step = $2,
                status = $3,
                cost_usd = COALESCE($4, cost_usd),
                completed_at = CASE WHEN $3 IN ('completed', 'failed', 'cancelled') THEN NOW() ELSE completed_at END
            WHERE run_id = $1
            """,
            run_id,
            current_step,
            status,
            cost_usd,
        )

    def _get_config(self, pipeline_name: str) -> PipelineConfig:
        """Load pipeline config. In production, reads from teams/*.yaml."""
        if pipeline_name == "document-stack":
            return DEFAULT_PIPELINE_CONFIG
        # For other pipelines, return a minimal config
        return PipelineConfig(
            pipeline_name=pipeline_name,
            steps=["step-1", "step-2"],
            cost_ceiling_usd=Decimal("10.00"),
            parallel_groups=[],
            gate_types={},
        )

    @staticmethod
    def _row_to_pipeline_run(row: asyncpg.Record) -> PipelineRun:
        """Convert a DB row to PipelineRun data shape."""
        return PipelineRun(
            run_id=row["run_id"],
            project_id=row["project_id"],
            pipeline_name=row["pipeline_name"],
            status=PipelineStatus(row["status"]),
            current_step=row["current_step"],
            total_steps=row["total_steps"],
            triggered_by=row["triggered_by"],
            started_at=row["started_at"],
            completed_at=row["completed_at"],
            cost_usd=Decimal(str(row["cost_usd"])),
        )
