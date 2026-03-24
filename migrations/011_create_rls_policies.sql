-- Migration 011: Row-Level Security policies for multi-tenant isolation
-- UP

-- Enable RLS on multi-tenant tables
ALTER TABLE cost_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE pipeline_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE approval_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE session_context ENABLE ROW LEVEL SECURITY;
ALTER TABLE mcp_call_events ENABLE ROW LEVEL SECURITY;

-- Force RLS for table owners too (defense in depth)
ALTER TABLE cost_metrics FORCE ROW LEVEL SECURITY;
ALTER TABLE pipeline_runs FORCE ROW LEVEL SECURITY;
ALTER TABLE audit_events FORCE ROW LEVEL SECURITY;
ALTER TABLE approval_requests FORCE ROW LEVEL SECURITY;
ALTER TABLE session_context FORCE ROW LEVEL SECURITY;
ALTER TABLE mcp_call_events FORCE ROW LEVEL SECURITY;

-- === Project-Scoped Policies ===

CREATE POLICY cost_metrics_project_isolation ON cost_metrics
    USING (project_id = current_setting('app.current_project_id', TRUE))
    WITH CHECK (project_id = current_setting('app.current_project_id', TRUE));

CREATE POLICY pipeline_runs_project_isolation ON pipeline_runs
    USING (project_id = current_setting('app.current_project_id', TRUE))
    WITH CHECK (project_id = current_setting('app.current_project_id', TRUE));

CREATE POLICY audit_events_project_isolation ON audit_events
    FOR SELECT
    USING (
        project_id = current_setting('app.current_project_id', TRUE)
        OR project_id IS NULL
    );

CREATE POLICY audit_events_insert ON audit_events
    FOR INSERT
    WITH CHECK (TRUE);

CREATE POLICY approval_requests_project_isolation ON approval_requests
    USING (project_id = current_setting('app.current_project_id', TRUE))
    WITH CHECK (project_id = current_setting('app.current_project_id', TRUE));

CREATE POLICY mcp_call_events_project_isolation ON mcp_call_events
    USING (
        project_id = current_setting('app.current_project_id', TRUE)
        OR project_id IS NULL
    )
    WITH CHECK (TRUE);

-- === Session-Scoped Policies ===

CREATE POLICY session_context_session_isolation ON session_context
    USING (session_id = current_setting('app.current_session_id', TRUE)::UUID)
    WITH CHECK (session_id = current_setting('app.current_session_id', TRUE)::UUID);

-- DOWN
-- DROP POLICY IF EXISTS session_context_session_isolation ON session_context;
-- DROP POLICY IF EXISTS mcp_call_events_project_isolation ON mcp_call_events;
-- DROP POLICY IF EXISTS approval_requests_project_isolation ON approval_requests;
-- DROP POLICY IF EXISTS audit_events_insert ON audit_events;
-- DROP POLICY IF EXISTS audit_events_project_isolation ON audit_events;
-- DROP POLICY IF EXISTS pipeline_runs_project_isolation ON pipeline_runs;
-- DROP POLICY IF EXISTS cost_metrics_project_isolation ON cost_metrics;
-- ALTER TABLE mcp_call_events DISABLE ROW LEVEL SECURITY;
-- ALTER TABLE session_context DISABLE ROW LEVEL SECURITY;
-- ALTER TABLE approval_requests DISABLE ROW LEVEL SECURITY;
-- ALTER TABLE audit_events DISABLE ROW LEVEL SECURITY;
-- ALTER TABLE pipeline_runs DISABLE ROW LEVEL SECURITY;
-- ALTER TABLE cost_metrics DISABLE ROW LEVEL SECURITY;
