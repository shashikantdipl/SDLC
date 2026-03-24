-- Migration 007: Create approval_requests table
-- UP
CREATE TABLE approval_requests (
    approval_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id      UUID NOT NULL,
    run_id          UUID REFERENCES pipeline_runs(run_id) ON DELETE SET NULL,
    project_id      VARCHAR(64),
    pipeline_name   VARCHAR(128) NOT NULL,
    step_number     INTEGER NOT NULL CHECK (step_number >= 0),
    step_name       VARCHAR(128) NOT NULL,
    summary         TEXT NOT NULL,
    risk_level      VARCHAR(16) NOT NULL DEFAULT 'medium'
                    CHECK (risk_level IN ('low', 'medium', 'high', 'critical')),
    status          VARCHAR(16) NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending', 'approved', 'rejected', 'expired', 'escalated')),
    context         JSONB DEFAULT '{}',
    approver_channel VARCHAR(256),
    decision_by     VARCHAR(128),
    decision_comment TEXT,
    requested_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    decided_at      TIMESTAMPTZ,
    expires_at      TIMESTAMPTZ NOT NULL
);

ALTER TABLE approval_requests
    ADD CONSTRAINT chk_rejection_comment CHECK (
        status != 'rejected' OR decision_comment IS NOT NULL
    );

COMMENT ON TABLE approval_requests IS 'Human approval gate requests for pipeline steps';

-- DOWN
-- DROP TABLE IF EXISTS approval_requests;
