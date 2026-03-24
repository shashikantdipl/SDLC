-- Migration 002: Create cost_metrics table
-- UP
CREATE TABLE cost_metrics (
    id              BIGSERIAL PRIMARY KEY,
    agent_id        VARCHAR(64) NOT NULL REFERENCES agent_registry(agent_id),
    project_id      VARCHAR(64) NOT NULL,
    session_id      UUID NOT NULL,
    model           VARCHAR(64) NOT NULL,
    input_tokens    INTEGER NOT NULL DEFAULT 0 CHECK (input_tokens >= 0),
    output_tokens   INTEGER NOT NULL DEFAULT 0 CHECK (output_tokens >= 0),
    cost_usd        NUMERIC(10, 6) NOT NULL DEFAULT 0 CHECK (cost_usd >= 0),
    recorded_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE cost_metrics IS 'Per-invocation cost tracking for budget enforcement and reporting';

-- DOWN
-- DROP TABLE IF EXISTS cost_metrics;
