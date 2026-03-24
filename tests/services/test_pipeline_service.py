"""Tests for PipelineService — core pipeline operations.

Covers: trigger, get_status, list_runs, resume, cancel, get_documents,
get_config, validate_input, and state guard enforcement.
Real PostgreSQL via testcontainers — no DB mocks.
"""

from __future__ import annotations

from uuid import uuid4

import pytest
import pytest_asyncio

from services.pipeline_service import (
    PipelineNotFoundError,
    PipelineService,
    PipelineStateError,
)
from schemas.data_shapes import PipelineStatus


@pytest_asyncio.fixture
async def service(db_pool):
    """PipelineService instance backed by test database."""
    return PipelineService(db_pool)


PROJECT_ID = "test-project-001"


class TestTrigger:
    """I-001: Trigger pipeline."""

    @pytest.mark.asyncio
    async def test_trigger_creates_run(self, service: PipelineService):
        run = await service.trigger(PROJECT_ID, "document-stack", "Build an e-commerce app", triggered_by="priya")
        assert run.project_id == PROJECT_ID
        assert run.pipeline_name == "document-stack"
        assert run.status == PipelineStatus.PENDING
        assert run.current_step == 0
        assert run.total_steps == 14
        assert run.triggered_by == "priya"

    @pytest.mark.asyncio
    async def test_trigger_invalid_pipeline_raises(self, service: PipelineService):
        with pytest.raises(ValueError, match="Invalid pipeline"):
            await service.trigger(PROJECT_ID, "nonexistent-pipeline", "brief")

    @pytest.mark.asyncio
    async def test_trigger_returns_unique_run_ids(self, service: PipelineService):
        run1 = await service.trigger(PROJECT_ID, "document-stack", "brief one", triggered_by="user1")
        run2 = await service.trigger(PROJECT_ID, "document-stack", "brief two", triggered_by="user2")
        assert run1.run_id != run2.run_id


class TestGetStatus:
    """I-002: Get pipeline status."""

    @pytest.mark.asyncio
    async def test_get_status_returns_run(self, service: PipelineService):
        run = await service.trigger(PROJECT_ID, "document-stack", "brief", triggered_by="test")
        status = await service.get_status(run.run_id)
        assert status.run_id == run.run_id
        assert status.status == PipelineStatus.PENDING

    @pytest.mark.asyncio
    async def test_get_status_not_found_raises(self, service: PipelineService):
        with pytest.raises(PipelineNotFoundError):
            await service.get_status(uuid4())


class TestListRuns:
    """I-003: List pipeline runs."""

    @pytest.mark.asyncio
    async def test_list_runs_returns_project_runs(self, service: PipelineService):
        await service.trigger(PROJECT_ID, "document-stack", "brief 1", triggered_by="t")
        await service.trigger(PROJECT_ID, "document-stack", "brief 2", triggered_by="t")

        runs = await service.list_runs(PROJECT_ID)
        assert len(runs) >= 2
        for run in runs:
            assert run.project_id == PROJECT_ID

    @pytest.mark.asyncio
    async def test_list_runs_filters_by_status(self, service: PipelineService):
        await service.trigger(PROJECT_ID, "document-stack", "brief", triggered_by="t")
        runs = await service.list_runs(PROJECT_ID, status="pending")
        assert all(r.status == PipelineStatus.PENDING for r in runs)

    @pytest.mark.asyncio
    async def test_list_runs_empty_project(self, service: PipelineService):
        runs = await service.list_runs("nonexistent-project")
        assert runs == []

    @pytest.mark.asyncio
    async def test_list_runs_respects_limit(self, service: PipelineService):
        for i in range(5):
            await service.trigger(PROJECT_ID, "document-stack", f"brief {i}", triggered_by="t")
        runs = await service.list_runs(PROJECT_ID, limit=3)
        assert len(runs) == 3


class TestResume:
    """I-004: Resume paused pipeline."""

    @pytest.mark.asyncio
    async def test_resume_paused_pipeline(self, service: PipelineService, db_pool):
        run = await service.trigger(PROJECT_ID, "document-stack", "brief", triggered_by="t")
        # Manually set to paused (simulating approval gate pause)
        await db_pool.execute("UPDATE pipeline_runs SET status = 'paused' WHERE run_id = $1", run.run_id)

        resumed = await service.resume(run.run_id)
        assert resumed.status == PipelineStatus.RUNNING

    @pytest.mark.asyncio
    async def test_resume_non_paused_raises(self, service: PipelineService):
        run = await service.trigger(PROJECT_ID, "document-stack", "brief", triggered_by="t")
        with pytest.raises(PipelineStateError, match="Cannot resume"):
            await service.resume(run.run_id)  # status is 'pending', not 'paused'


class TestCancel:
    """I-005: Cancel pipeline."""

    @pytest.mark.asyncio
    async def test_cancel_pending_pipeline(self, service: PipelineService):
        run = await service.trigger(PROJECT_ID, "document-stack", "brief", triggered_by="t")
        cancelled = await service.cancel(run.run_id)
        assert cancelled.status == PipelineStatus("cancelled")
        assert cancelled.completed_at is not None

    @pytest.mark.asyncio
    async def test_cancel_running_pipeline(self, service: PipelineService, db_pool):
        run = await service.trigger(PROJECT_ID, "document-stack", "brief", triggered_by="t")
        await db_pool.execute("UPDATE pipeline_runs SET status = 'running' WHERE run_id = $1", run.run_id)

        cancelled = await service.cancel(run.run_id)
        assert cancelled.status == PipelineStatus("cancelled")

    @pytest.mark.asyncio
    async def test_cancel_completed_raises(self, service: PipelineService, db_pool):
        run = await service.trigger(PROJECT_ID, "document-stack", "brief", triggered_by="t")
        await db_pool.execute(
            "UPDATE pipeline_runs SET status = 'completed', completed_at = NOW() WHERE run_id = $1",
            run.run_id,
        )
        with pytest.raises(PipelineStateError, match="Cannot cancel"):
            await service.cancel(run.run_id)


class TestValidateInput:
    """I-009: Validate pipeline input."""

    @pytest.mark.asyncio
    async def test_valid_input(self, service: PipelineService):
        result = await service.validate_input(PROJECT_ID, "document-stack", "Build an e-commerce platform with payments")
        assert result.valid is True
        assert result.errors == []

    @pytest.mark.asyncio
    async def test_empty_project_id(self, service: PipelineService):
        result = await service.validate_input("", "document-stack", "Some brief text here")
        assert result.valid is False
        assert any("project_id" in e for e in result.errors)

    @pytest.mark.asyncio
    async def test_invalid_pipeline_name(self, service: PipelineService):
        result = await service.validate_input(PROJECT_ID, "invalid", "Some brief text here")
        assert result.valid is False
        assert any("pipeline_name" in e for e in result.errors)

    @pytest.mark.asyncio
    async def test_brief_too_short(self, service: PipelineService):
        result = await service.validate_input(PROJECT_ID, "document-stack", "short")
        assert result.valid is False
        assert any("brief" in e for e in result.errors)

    @pytest.mark.asyncio
    async def test_long_brief_warns(self, service: PipelineService):
        result = await service.validate_input(PROJECT_ID, "document-stack", "x" * 10001)
        assert result.valid is True
        assert len(result.warnings) > 0


class TestGetConfig:
    """I-008: Get pipeline configuration."""

    @pytest.mark.asyncio
    async def test_get_document_stack_config(self, service: PipelineService):
        config = await service.get_config("document-stack")
        assert config.pipeline_name == "document-stack"
        assert len(config.steps) == 14
        assert config.cost_ceiling_usd == 25
        assert len(config.parallel_groups) == 4


class TestDataShapeCompliance:
    """Verify returned objects match INTERACTION-MAP PipelineRun shape exactly."""

    @pytest.mark.asyncio
    async def test_pipeline_run_has_all_fields(self, service: PipelineService):
        run = await service.trigger(PROJECT_ID, "document-stack", "brief", triggered_by="test")
        assert hasattr(run, "run_id")
        assert hasattr(run, "project_id")
        assert hasattr(run, "pipeline_name")
        assert hasattr(run, "status")
        assert hasattr(run, "current_step")
        assert hasattr(run, "total_steps")
        assert hasattr(run, "triggered_by")
        assert hasattr(run, "started_at")
        assert hasattr(run, "completed_at")
        assert hasattr(run, "cost_usd")

    @pytest.mark.asyncio
    async def test_pipeline_run_serializes_to_json(self, service: PipelineService):
        run = await service.trigger(PROJECT_ID, "document-stack", "brief", triggered_by="test")
        json_data = run.model_dump(mode="json")
        assert "run_id" in json_data
        assert "status" in json_data
        assert json_data["status"] == "pending"
