"""Tests for pipeline REST API routes.

Routes are thin wrappers around PipelineService.
Mock the service (tested separately with real DB in Phase 2).
Test: request parsing, service delegation, response envelope, error codes.
"""
import pytest
from aiohttp import web
from unittest.mock import AsyncMock, patch
from uuid import uuid4
from decimal import Decimal
from datetime import datetime, timezone

from api.app import create_app
from schemas.data_shapes import (
    PipelineRun,
    PipelineStatus,
    PipelineConfig,
    PipelineDocument,
    ValidationResult,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
API_KEY = "dev-api-key"
AUTH_HEADERS = {"X-API-Key": API_KEY}

RUN_ID = uuid4()
NOW = datetime.now(timezone.utc)


def _make_run(**overrides) -> PipelineRun:
    defaults = dict(
        run_id=RUN_ID,
        project_id="proj-1",
        pipeline_name="document-stack",
        status=PipelineStatus.PENDING,
        current_step=0,
        total_steps=22,
        triggered_by="tester",
        started_at=NOW,
        completed_at=None,
        cost_usd=Decimal("0.00"),
    )
    defaults.update(overrides)
    return PipelineRun(**defaults)


@pytest.fixture
async def app():
    """Create app without real DB — services will be mocked per-test."""
    application = await create_app(db_pool=None)
    return application


@pytest.fixture
async def client(aiohttp_client, app):
    """aiohttp test client."""
    return await aiohttp_client(app)


# ---------------------------------------------------------------------------
# I-001  POST /api/v1/pipelines — trigger pipeline
# ---------------------------------------------------------------------------
class TestTriggerPipeline:

    @pytest.mark.asyncio
    async def test_trigger_returns_201_with_pipeline_run(self, client, app):
        mock_svc = AsyncMock()
        mock_svc.trigger.return_value = _make_run()
        app["pipeline_service"] = mock_svc

        resp = await client.post(
            "/api/v1/pipelines",
            json={"pipeline_name": "document-stack", "project_id": "proj-1", "brief": "", "triggered_by": "tester"},
            headers=AUTH_HEADERS,
        )
        assert resp.status == 201
        body = await resp.json()
        assert "data" in body
        assert body["data"]["run_id"] == str(RUN_ID)
        assert body["data"]["status"] == "pending"
        mock_svc.trigger.assert_called_once_with(
            pipeline_name="document-stack",
            project_id="proj-1",
            brief="",
            triggered_by="tester",
        )

    @pytest.mark.asyncio
    async def test_trigger_passes_params(self, client, app):
        mock_svc = AsyncMock()
        mock_svc.trigger.return_value = _make_run()
        app["pipeline_service"] = mock_svc

        resp = await client.post(
            "/api/v1/pipelines",
            json={
                "pipeline_name": "document-stack",
                "project_id": "proj-1",
                "brief": "Build a todo app",
                "triggered_by": "tester",
            },
            headers=AUTH_HEADERS,
        )
        assert resp.status == 201
        mock_svc.trigger.assert_called_once_with(
            pipeline_name="document-stack",
            project_id="proj-1",
            brief="Build a todo app",
            triggered_by="tester",
        )


# ---------------------------------------------------------------------------
# I-003  GET /api/v1/pipelines — list pipelines
# ---------------------------------------------------------------------------
class TestListPipelines:

    @pytest.mark.asyncio
    async def test_list_returns_200_with_runs(self, client, app):
        mock_svc = AsyncMock()
        mock_svc.list_runs.return_value = [
            _make_run(run_id=uuid4()),
            _make_run(run_id=uuid4()),
        ]
        app["pipeline_service"] = mock_svc

        resp = await client.get(
            "/api/v1/pipelines?project_id=proj-1",
            headers=AUTH_HEADERS,
        )
        assert resp.status == 200
        body = await resp.json()
        assert "data" in body
        assert len(body["data"]) == 2
        assert "meta" in body
        mock_svc.list_runs.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_passes_query_params(self, client, app):
        mock_svc = AsyncMock()
        mock_svc.list_runs.return_value = []
        app["pipeline_service"] = mock_svc

        resp = await client.get(
            "/api/v1/pipelines?project_id=proj-1&status=running&limit=5&offset=10",
            headers=AUTH_HEADERS,
        )
        assert resp.status == 200
        mock_svc.list_runs.assert_called_once_with(
            project_id="proj-1",
            status="running",
            limit=5,
            offset=10,
        )

    @pytest.mark.asyncio
    async def test_list_defaults_limit_offset(self, client, app):
        mock_svc = AsyncMock()
        mock_svc.list_runs.return_value = []
        app["pipeline_service"] = mock_svc

        resp = await client.get(
            "/api/v1/pipelines",
            headers=AUTH_HEADERS,
        )
        assert resp.status == 200
        mock_svc.list_runs.assert_called_once_with(
            project_id=None,
            status=None,
            limit=20,
            offset=0,
        )

    @pytest.mark.asyncio
    async def test_list_meta_contains_limit_offset(self, client, app):
        mock_svc = AsyncMock()
        mock_svc.list_runs.return_value = []
        app["pipeline_service"] = mock_svc

        resp = await client.get(
            "/api/v1/pipelines?limit=10&offset=5",
            headers=AUTH_HEADERS,
        )
        body = await resp.json()
        assert body["meta"]["limit"] == 10
        assert body["meta"]["offset"] == 5


# ---------------------------------------------------------------------------
# I-002  GET /api/v1/pipelines/{run_id} — get pipeline status
# ---------------------------------------------------------------------------
class TestGetPipelineStatus:

    @pytest.mark.asyncio
    async def test_get_status_returns_200(self, client, app):
        mock_svc = AsyncMock()
        mock_svc.get_status.return_value = _make_run()
        app["pipeline_service"] = mock_svc

        resp = await client.get(
            f"/api/v1/pipelines/{RUN_ID}",
            headers=AUTH_HEADERS,
        )
        assert resp.status == 200
        body = await resp.json()
        assert body["data"]["run_id"] == str(RUN_ID)
        mock_svc.get_status.assert_called_once_with(run_id=RUN_ID)

    @pytest.mark.asyncio
    async def test_get_status_not_found_returns_404(self, client, app):
        from services.pipeline_service import PipelineNotFoundError

        mock_svc = AsyncMock()
        missing_id = uuid4()
        mock_svc.get_status.side_effect = PipelineNotFoundError(
            f"Pipeline run {missing_id} not found"
        )
        app["pipeline_service"] = mock_svc

        resp = await client.get(
            f"/api/v1/pipelines/{missing_id}",
            headers=AUTH_HEADERS,
        )
        assert resp.status == 404
        body = await resp.json()
        assert body["error"]["code"] == "PIPELINE_NOT_FOUND"


# ---------------------------------------------------------------------------
# I-004  POST /api/v1/pipelines/{run_id}/resume
# ---------------------------------------------------------------------------
class TestResumePipeline:

    @pytest.mark.asyncio
    async def test_resume_returns_200(self, client, app):
        mock_svc = AsyncMock()
        mock_svc.resume.return_value = _make_run(status=PipelineStatus.RUNNING)
        app["pipeline_service"] = mock_svc

        resp = await client.post(
            f"/api/v1/pipelines/{RUN_ID}/resume",
            headers=AUTH_HEADERS,
        )
        assert resp.status == 200
        body = await resp.json()
        assert body["data"]["status"] == "running"
        mock_svc.resume.assert_called_once_with(run_id=RUN_ID)

    @pytest.mark.asyncio
    async def test_resume_invalid_state_returns_409(self, client, app):
        from services.pipeline_service import PipelineStateError

        mock_svc = AsyncMock()
        mock_svc.resume.side_effect = PipelineStateError(
            run_id=RUN_ID,
            current_status="pending",
            attempted_action="resume",
        )
        app["pipeline_service"] = mock_svc

        resp = await client.post(
            f"/api/v1/pipelines/{RUN_ID}/resume",
            headers=AUTH_HEADERS,
        )
        assert resp.status == 409
        body = await resp.json()
        assert body["error"]["code"] == "PIPELINE_STATE_ERROR"


# ---------------------------------------------------------------------------
# I-005  POST /api/v1/pipelines/{run_id}/cancel
# ---------------------------------------------------------------------------
class TestCancelPipeline:

    @pytest.mark.asyncio
    async def test_cancel_returns_200(self, client, app):
        mock_svc = AsyncMock()
        mock_svc.cancel.return_value = _make_run(
            status=PipelineStatus.FAILED, completed_at=NOW,
        )
        app["pipeline_service"] = mock_svc

        resp = await client.post(
            f"/api/v1/pipelines/{RUN_ID}/cancel",
            headers=AUTH_HEADERS,
        )
        assert resp.status == 200
        body = await resp.json()
        assert body["data"]["completed_at"] is not None
        mock_svc.cancel.assert_called_once_with(run_id=RUN_ID)

    @pytest.mark.asyncio
    async def test_cancel_completed_returns_409(self, client, app):
        from services.pipeline_service import PipelineStateError

        mock_svc = AsyncMock()
        mock_svc.cancel.side_effect = PipelineStateError(
            run_id=RUN_ID,
            current_status="completed",
            attempted_action="cancel",
        )
        app["pipeline_service"] = mock_svc

        resp = await client.post(
            f"/api/v1/pipelines/{RUN_ID}/cancel",
            headers=AUTH_HEADERS,
        )
        assert resp.status == 409
        body = await resp.json()
        assert body["error"]["code"] == "PIPELINE_STATE_ERROR"


# ---------------------------------------------------------------------------
# I-009  POST /api/v1/pipelines/validate
# ---------------------------------------------------------------------------
class TestValidatePipelineInput:

    @pytest.mark.asyncio
    async def test_validate_valid_input(self, client, app):
        mock_svc = AsyncMock()
        mock_svc.validate_input.return_value = ValidationResult(
            valid=True, errors=[], warnings=[],
        )
        app["pipeline_service"] = mock_svc

        resp = await client.post(
            "/api/v1/pipelines/validate",
            json={"pipeline_name": "document-stack", "project_id": "proj-1", "brief": "Build an app"},
            headers=AUTH_HEADERS,
        )
        assert resp.status == 200
        body = await resp.json()
        assert body["data"]["valid"] is True
        mock_svc.validate_input.assert_called_once_with(
            project_id="proj-1",
            pipeline_name="document-stack",
            brief="Build an app",
        )

    @pytest.mark.asyncio
    async def test_validate_invalid_input(self, client, app):
        mock_svc = AsyncMock()
        mock_svc.validate_input.return_value = ValidationResult(
            valid=False,
            errors=["pipeline_name 'bad' is not valid"],
            warnings=[],
        )
        app["pipeline_service"] = mock_svc

        resp = await client.post(
            "/api/v1/pipelines/validate",
            json={"pipeline_name": "bad", "project_id": "proj-1", "brief": ""},
            headers=AUTH_HEADERS,
        )
        assert resp.status == 200
        body = await resp.json()
        assert body["data"]["valid"] is False
        assert len(body["data"]["errors"]) == 1


# ---------------------------------------------------------------------------
# I-008  GET /api/v1/pipelines/config/{pipeline_name}
# ---------------------------------------------------------------------------
class TestGetPipelineConfig:

    @pytest.mark.asyncio
    async def test_get_config_returns_200(self, client, app):
        mock_svc = AsyncMock()
        mock_svc.get_config.return_value = PipelineConfig(
            pipeline_name="document-stack",
            steps=["00-ROADMAP", "01-PRD"],
            cost_ceiling_usd=Decimal("25.00"),
            parallel_groups=[["00-ROADMAP"], ["01-PRD"]],
            gate_types={"01-PRD": "auto"},
        )
        app["pipeline_service"] = mock_svc

        resp = await client.get(
            "/api/v1/pipelines/config/document-stack",
            headers=AUTH_HEADERS,
        )
        assert resp.status == 200
        body = await resp.json()
        assert body["data"]["pipeline_name"] == "document-stack"
        mock_svc.get_config.assert_called_once_with(
            pipeline_name="document-stack",
        )


# ---------------------------------------------------------------------------
# I-006  GET /api/v1/pipelines/{run_id}/documents
# ---------------------------------------------------------------------------
class TestGetPipelineDocuments:

    @pytest.mark.asyncio
    async def test_get_documents_returns_list(self, client, app):
        mock_svc = AsyncMock()
        mock_svc.get_documents.return_value = [
            PipelineDocument(
                document_name="00-ROADMAP",
                document_number=0,
                content="# Roadmap",
                agent_id="roadmap-agent",
                generated_at=NOW,
                quality_score=0.95,
            ),
        ]
        app["pipeline_service"] = mock_svc

        resp = await client.get(
            f"/api/v1/pipelines/{RUN_ID}/documents",
            headers=AUTH_HEADERS,
        )
        assert resp.status == 200
        body = await resp.json()
        assert len(body["data"]) == 1
        assert body["data"][0]["document_name"] == "00-ROADMAP"
        mock_svc.get_documents.assert_called_once_with(run_id=RUN_ID)


# ---------------------------------------------------------------------------
# I-007  POST /api/v1/pipelines/{run_id}/steps/{step}/retry
# ---------------------------------------------------------------------------
class TestRetryStep:

    @pytest.mark.asyncio
    async def test_retry_step_returns_200(self, client, app):
        mock_svc = AsyncMock()
        mock_svc.update_step_status.return_value = None
        mock_svc.get_status.return_value = _make_run(status=PipelineStatus.RUNNING)
        app["pipeline_service"] = mock_svc

        resp = await client.post(
            f"/api/v1/pipelines/{RUN_ID}/steps/03-CLAUDE/retry",
            headers=AUTH_HEADERS,
        )
        assert resp.status == 200
        mock_svc.update_step_status.assert_called_once_with(run_id=RUN_ID, step="03-CLAUDE", status="pending")
        mock_svc.get_status.assert_called_once_with(run_id=RUN_ID)


# ---------------------------------------------------------------------------
# Auth: 401 / 403
# ---------------------------------------------------------------------------
class TestAuthMiddleware:

    @pytest.mark.asyncio
    async def test_missing_api_key_returns_401(self, client, app):
        resp = await client.get("/api/v1/pipelines")
        assert resp.status == 401
        body = await resp.json()
        assert body["error"]["code"] == "UNAUTHORIZED"

    @pytest.mark.asyncio
    async def test_wrong_api_key_returns_403(self, client, app):
        resp = await client.get(
            "/api/v1/pipelines",
            headers={"X-API-Key": "wrong-key"},
        )
        assert resp.status == 403
        body = await resp.json()
        assert body["error"]["code"] == "FORBIDDEN"


# ---------------------------------------------------------------------------
# Response envelope structure
# ---------------------------------------------------------------------------
class TestResponseEnvelope:

    @pytest.mark.asyncio
    async def test_success_envelope_has_data_and_meta(self, client, app):
        mock_svc = AsyncMock()
        mock_svc.list_runs.return_value = []
        app["pipeline_service"] = mock_svc

        resp = await client.get(
            "/api/v1/pipelines",
            headers=AUTH_HEADERS,
        )
        body = await resp.json()
        assert "data" in body
        assert "meta" in body
        assert "request_id" in body["meta"]
        assert "timestamp" in body["meta"]

    @pytest.mark.asyncio
    async def test_error_envelope_has_error_and_meta(self, client, app):
        from services.pipeline_service import PipelineNotFoundError

        mock_svc = AsyncMock()
        mock_svc.get_status.side_effect = PipelineNotFoundError("not found")
        app["pipeline_service"] = mock_svc

        resp = await client.get(
            f"/api/v1/pipelines/{uuid4()}",
            headers=AUTH_HEADERS,
        )
        body = await resp.json()
        assert "error" in body
        assert "code" in body["error"]
        assert "message" in body["error"]
        assert "meta" in body
        assert "request_id" in body["meta"]
        assert "timestamp" in body["meta"]
