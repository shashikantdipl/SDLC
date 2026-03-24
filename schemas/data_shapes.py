"""Shared data shapes — Single source of truth.

These Pydantic models match the 22 data shapes from INTERACTION-MAP (Doc 6).
Imported by: services/, mcp_servers/, api/routes/.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


# --- Enums ---

class PipelineStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEGRADED = "degraded"
    ERROR = "error"


class AgentPhase(str, Enum):
    GOVERN = "govern"
    DESIGN = "design"
    BUILD = "build"
    TEST = "test"
    DEPLOY = "deploy"
    OPERATE = "operate"
    OVERSIGHT = "oversight"


class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    TIMEOUT = "timeout"


class KnowledgeTier(str, Enum):
    UNIVERSAL = "universal"
    STACK = "stack"
    CLIENT = "client"


class MaturityLevel(str, Enum):
    APPRENTICE = "apprentice"
    JOURNEYMAN = "journeyman"
    PROFESSIONAL = "professional"
    EXPERT = "expert"


class BudgetScope(str, Enum):
    FLEET = "fleet"
    PROJECT = "project"
    AGENT = "agent"


# --- Data Shapes (22 total, from INTERACTION-MAP) ---

class PipelineRun(BaseModel):
    """Shape: PipelineRun — Used by I-001, I-002, I-003, I-004, I-005."""
    run_id: UUID
    project_id: str
    pipeline_name: str
    status: PipelineStatus
    current_step: int
    total_steps: int
    triggered_by: str
    started_at: datetime
    completed_at: datetime | None = None
    cost_usd: Decimal = Decimal("0.00")


class PipelineDocument(BaseModel):
    """Shape: PipelineDocument — Used by I-006."""
    document_name: str
    document_number: int
    content: str
    agent_id: str
    generated_at: datetime
    quality_score: float | None = None


class AgentSummary(BaseModel):
    """Shape: AgentSummary — Used by I-020 (list_agents)."""
    agent_id: str
    name: str
    phase: AgentPhase
    archetype: str
    model: str
    status: AgentStatus
    active_version: str
    maturity: MaturityLevel


class AgentDetail(BaseModel):
    """Shape: AgentDetail — Used by I-021 (get_agent)."""
    agent_id: str
    name: str
    phase: AgentPhase
    archetype: str
    model: str
    status: AgentStatus
    active_version: str
    canary_version: str | None = None
    canary_traffic_pct: int = 0
    previous_version: str | None = None
    maturity: MaturityLevel
    daily_cost_usd: Decimal = Decimal("0.00")
    invocations_today: int = 0
    last_invoked_at: datetime | None = None
    description: str = ""


class AgentHealth(BaseModel):
    """Shape: AgentHealth — Used by I-023."""
    agent_id: str
    status: AgentStatus
    last_heartbeat: datetime | None = None
    error_rate_1h: float = 0.0
    avg_latency_ms: float = 0.0
    invocations_1h: int = 0


class AgentVersion(BaseModel):
    """Shape: AgentVersion — Used by I-024, I-025, I-026."""
    agent_id: str
    active_version: str
    canary_version: str | None = None
    canary_traffic_pct: int = 0
    previous_version: str | None = None
    updated_at: datetime


class AgentMaturity(BaseModel):
    """Shape: AgentMaturity — Used by I-027."""
    agent_id: str
    maturity: MaturityLevel
    golden_tests_passed: int
    adversarial_tests_passed: int
    total_invocations: int
    avg_quality_score: float
    promoted_at: datetime | None = None


class AgentInvocationResult(BaseModel):
    """Shape: AgentInvocationResult — Used by I-022."""
    invocation_id: UUID
    agent_id: str
    status: str
    output: str
    cost_usd: Decimal
    duration_ms: int
    quality_score: float | None = None


class CostBreakdownItem(BaseModel):
    """Sub-shape for CostReport breakdown."""
    label: str
    cost_usd: Decimal
    invocations: int
    percentage: float


class CostReport(BaseModel):
    """Shape: CostReport — Used by I-040."""
    scope: BudgetScope
    scope_id: str
    period_days: int
    total_cost_usd: Decimal
    breakdown: list[CostBreakdownItem] = []
    generated_at: datetime


class BudgetStatus(BaseModel):
    """Shape: BudgetStatus — Used by I-041."""
    scope: BudgetScope
    scope_id: str
    budget_usd: Decimal
    spent_usd: Decimal
    remaining_usd: Decimal
    utilization_pct: float
    period: str


class CostAnomaly(BaseModel):
    """Shape: CostAnomaly — Used by I-048."""
    anomaly_id: UUID
    agent_id: str
    project_id: str
    expected_cost_usd: Decimal
    actual_cost_usd: Decimal
    deviation_pct: float
    detected_at: datetime
    severity: Severity


class AuditEvent(BaseModel):
    """Shape: AuditEvent — Used by I-042."""
    event_id: UUID
    agent_id: str
    project_id: str
    session_id: UUID | None = None
    action: str
    severity: Severity
    message: str
    details: dict | None = None
    pii_detected: bool = False
    created_at: datetime


class AuditSummary(BaseModel):
    """Shape: AuditSummary — Used by I-043."""
    total_events: int
    by_severity: dict[str, int]
    by_agent: dict[str, int]
    period_start: datetime
    period_end: datetime
    total_cost_usd: Decimal


class AuditReport(BaseModel):
    """Shape: AuditReport — Used by I-044."""
    report_id: UUID
    generated_at: datetime
    period_start: datetime
    period_end: datetime
    total_events: int
    events: list[AuditEvent]
    format: str = "json"


class ApprovalRequest(BaseModel):
    """Shape: ApprovalRequest — Used by I-045."""
    approval_id: UUID
    session_id: UUID
    pipeline_name: str
    step_id: str
    summary: str
    status: ApprovalStatus
    approver_channel: str | None = None
    requested_at: datetime
    expires_at: datetime
    decision_by: str | None = None
    decision_comment: str | None = None
    decided_at: datetime | None = None


class ApprovalResult(BaseModel):
    """Shape: ApprovalResult — Used by I-046, I-047."""
    approval_id: UUID
    status: ApprovalStatus
    decision_by: str
    decision_comment: str | None = None
    decided_at: datetime


class KnowledgeException(BaseModel):
    """Shape: KnowledgeException — Used by I-060, I-061, I-062, I-063."""
    exception_id: str
    title: str
    rule: str
    severity: Severity
    tier: KnowledgeTier
    stack_name: str | None = None
    client_id: str | None = None
    active: bool = False
    fire_count: int = 0
    created_by: str
    created_at: datetime


class FleetHealth(BaseModel):
    """Shape: FleetHealth — Used by I-080."""
    total_agents: int
    healthy: int
    degraded: int
    error: int
    inactive: int
    fleet_cost_today_usd: Decimal
    fleet_budget_remaining_usd: Decimal
    agents: list[AgentHealth] = []


class McpServerStatus(BaseModel):
    """Shape: McpServerStatus — Used by I-081."""
    server_name: str
    status: str
    uptime_seconds: int
    tools_registered: int
    resources_registered: int
    error_rate_1h: float
    avg_latency_ms: float


class McpCallEvent(BaseModel):
    """Shape: McpCallEvent — Used by I-082."""
    call_id: UUID
    server_name: str
    tool_name: str
    client_id: str | None = None
    project_id: str | None = None
    input_summary: str
    status: str
    duration_ms: int
    cost_usd: Decimal
    called_at: datetime


class PipelineConfig(BaseModel):
    """Shape: PipelineConfig — Used by I-008."""
    pipeline_name: str
    steps: list[str]
    cost_ceiling_usd: Decimal
    parallel_groups: list[list[str]]
    gate_types: dict[str, str]


class ValidationResult(BaseModel):
    """Shape: ValidationResult — Used by I-009."""
    valid: bool
    errors: list[str] = []
    warnings: list[str] = []
