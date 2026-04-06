-- Migration 004: Create pipeline_runs and pipeline_steps tables
-- UP
CREATE TABLE pipeline_runs (
    id              BIGSERIAL PRIMARY KEY,
    run_id          UUID NOT NULL DEFAULT gen_random_uuid() UNIQUE,
    project_id      VARCHAR(64) NOT NULL,
    pipeline_name   VARCHAR(128) NOT NULL,
    status          VARCHAR(16) NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending', 'running', 'paused', 'completed', 'failed', 'cancelled')),
    current_step    INTEGER NOT NULL DEFAULT 0 CHECK (current_step >= 0),
    total_steps     INTEGER NOT NULL DEFAULT 22 CHECK (total_steps > 0),
    triggered_by    VARCHAR(128) NOT NULL DEFAULT 'system',
    error_message   TEXT,
    started_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at    TIMESTAMPTZ,
    cost_usd        NUMERIC(10, 6) NOT NULL DEFAULT 0 CHECK (cost_usd >= 0),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE pipeline_steps (
    id              BIGSERIAL PRIMARY KEY,
    run_id          UUID NOT NULL REFERENCES pipeline_runs(run_id) ON DELETE CASCADE,
    step_number     INTEGER NOT NULL CHECK (step_number >= 0),
    step_name       VARCHAR(128) NOT NULL,
    agent_id        VARCHAR(64) NOT NULL REFERENCES agent_registry(agent_id),
    status          VARCHAR(16) NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending', 'running', 'completed', 'failed', 'skipped')),
    input_key       VARCHAR(128),
    output_key      VARCHAR(128),
    quality_score   NUMERIC(4, 3) CHECK (quality_score >= 0 AND quality_score <= 1),
    token_count     INTEGER DEFAULT 0 CHECK (token_count >= 0),
    error_message   TEXT,
    started_at      TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    cost_usd        NUMERIC(10, 6) NOT NULL DEFAULT 0 CHECK (cost_usd >= 0),
    UNIQUE (run_id, step_number)
);

COMMENT ON TABLE pipeline_runs IS 'Top-level pipeline execution records';
COMMENT ON TABLE pipeline_steps IS 'Individual step execution within a pipeline run';

-- DOWN
-- DROP TABLE IF EXISTS pipeline_steps;
-- DROP TABLE IF EXISTS pipeline_runs;
