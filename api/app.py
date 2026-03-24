"""REST API application — aiohttp on port 8080.

Wraps shared services for programmatic access and dashboard data.
Every endpoint calls a shared service method (no business logic here).
"""
from __future__ import annotations
from aiohttp import web
import asyncpg

from api.middleware.error_handler import error_middleware
from api.middleware.auth import auth_middleware
from api.routes import pipelines, agents, cost, audit, approvals, knowledge, health


async def create_app(db_pool: asyncpg.Pool | None = None) -> web.Application:
    """Create and configure the aiohttp application."""
    app = web.Application(middlewares=[error_middleware, auth_middleware])

    # Store DB pool for service creation
    app["db_pool"] = db_pool

    # Initialize services
    if db_pool:
        from services.pipeline_service import PipelineService
        from services.agent_service import AgentService
        from services.cost_service import CostService
        from services.audit_service import AuditService
        from services.approval_service import ApprovalService
        from services.knowledge_service import KnowledgeService
        from services.health_service import HealthService
        from services.session_service import SessionService

        app["pipeline_service"] = PipelineService(db_pool)
        app["agent_service"] = AgentService(db_pool)
        app["cost_service"] = CostService(db_pool)
        app["audit_service"] = AuditService(db_pool)
        app["approval_service"] = ApprovalService(db_pool)
        app["knowledge_service"] = KnowledgeService(db_pool)
        app["health_service"] = HealthService(db_pool)
        app["session_service"] = SessionService(db_pool)

    # Register routes
    pipelines.setup_routes(app)
    agents.setup_routes(app)
    cost.setup_routes(app)
    audit.setup_routes(app)
    approvals.setup_routes(app)
    knowledge.setup_routes(app)
    health.setup_routes(app)

    return app
