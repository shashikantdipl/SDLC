-- Migration 010: Create all indexes for MCP tool, Dashboard, and pipeline queries
-- UP

-- === MCP Tool Query Indexes ===

-- I-020: list_agents — WHERE phase = $1 AND status = $2 ORDER BY name
CREATE INDEX idx_agents_phase_status ON agent_registry(phase, status, name);

-- I-040: get_cost_report — WHERE project_id = $1 AND recorded_at > $2
CREATE INDEX idx_cost_project_date ON cost_metrics(project_id, recorded_at DESC);

-- I-040: get_cost_report — GROUP BY agent_id for breakdown
CREATE INDEX idx_cost_agent_project ON cost_metrics(agent_id, project_id, recorded_at DESC);

-- I-042: query_audit_events — WHERE project_id = $1 AND severity >= $2
CREATE INDEX idx_audit_project_severity ON audit_events(project_id, severity, created_at DESC);

-- I-045: list_pending_approvals — WHERE status = 'pending'
CREATE INDEX idx_approvals_pending ON approval_requests(status, project_id, expires_at ASC)
    WHERE status = 'pending';

-- I-003: list_pipeline_runs — WHERE project_id = $1 AND status = $2
CREATE INDEX idx_pipelines_project_status ON pipeline_runs(project_id, status, started_at DESC);

-- I-060: search_exceptions — full-text search on title + rule
CREATE INDEX idx_exceptions_search ON knowledge_exceptions
    USING GIN(to_tsvector('english', title || ' ' || rule));

-- I-060: search_exceptions — WHERE tier = $1 AND active = TRUE
CREATE INDEX idx_exceptions_tier ON knowledge_exceptions(tier, active) WHERE active = TRUE;

-- Session context lookup
CREATE INDEX idx_session_lookup ON session_context(session_id, key);

-- Session context TTL cleanup
CREATE INDEX idx_session_expires ON session_context(expires_at) WHERE expires_at IS NOT NULL;

-- === Dashboard Query Indexes ===

-- Fleet Health page: active agents
CREATE INDEX idx_agents_active ON agent_registry(phase, name) WHERE status = 'active';

-- Cost Monitor: daily aggregation
CREATE INDEX idx_cost_daily ON cost_metrics(project_id, (date_trunc('day', recorded_at)));

-- Audit Log: recent errors
CREATE INDEX idx_audit_recent_errors ON audit_events(created_at DESC) WHERE severity IN ('error', 'critical');

-- MCP Monitoring Panel: recent calls
CREATE INDEX idx_mcp_calls_recent ON mcp_call_events(called_at DESC);

-- MCP Monitoring Panel: by server
CREATE INDEX idx_mcp_calls_server ON mcp_call_events(server_name, called_at DESC);

-- Approval Queue: history
CREATE INDEX idx_approvals_history ON approval_requests(decided_at DESC) WHERE status != 'pending';

-- === Pipeline and Internal Indexes ===

-- Pipeline steps: fetch all steps for a run
CREATE INDEX idx_steps_run_id ON pipeline_steps(run_id, step_number);

-- Pipeline checkpoints: by session
CREATE INDEX idx_checkpoints_session ON pipeline_checkpoints(session_id);

-- Audit: by session
CREATE INDEX idx_audit_session ON audit_events(session_id, created_at DESC);

-- Cost: by session
CREATE INDEX idx_cost_session ON cost_metrics(session_id);

-- MCP calls: by project
CREATE INDEX idx_mcp_calls_project ON mcp_call_events(project_id, called_at DESC) WHERE project_id IS NOT NULL;

-- DOWN
-- (Drop all indexes in reverse order)
-- DROP INDEX IF EXISTS idx_mcp_calls_project;
-- DROP INDEX IF EXISTS idx_cost_session;
-- DROP INDEX IF EXISTS idx_audit_session;
-- DROP INDEX IF EXISTS idx_checkpoints_session;
-- DROP INDEX IF EXISTS idx_steps_run_id;
-- DROP INDEX IF EXISTS idx_approvals_history;
-- DROP INDEX IF EXISTS idx_mcp_calls_server;
-- DROP INDEX IF EXISTS idx_mcp_calls_recent;
-- DROP INDEX IF EXISTS idx_audit_recent_errors;
-- DROP INDEX IF EXISTS idx_cost_daily;
-- DROP INDEX IF EXISTS idx_agents_active;
-- DROP INDEX IF EXISTS idx_session_expires;
-- DROP INDEX IF EXISTS idx_session_lookup;
-- DROP INDEX IF EXISTS idx_exceptions_tier;
-- DROP INDEX IF EXISTS idx_exceptions_search;
-- DROP INDEX IF EXISTS idx_pipelines_project_status;
-- DROP INDEX IF EXISTS idx_approvals_pending;
-- DROP INDEX IF EXISTS idx_audit_project_severity;
-- DROP INDEX IF EXISTS idx_cost_agent_project;
-- DROP INDEX IF EXISTS idx_cost_project_date;
-- DROP INDEX IF EXISTS idx_agents_phase_status;
