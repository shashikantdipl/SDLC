-- Migration 008: Create pipeline_checkpoints table
-- UP
CREATE TABLE pipeline_checkpoints (
    id              BIGSERIAL PRIMARY KEY,
    run_id          UUID NOT NULL REFERENCES pipeline_runs(run_id) ON DELETE CASCADE,
    session_id      UUID NOT NULL,
    pipeline_name   VARCHAR(128) NOT NULL,
    last_step_number INTEGER NOT NULL CHECK (last_step_number >= 0),
    last_step_name  VARCHAR(128) NOT NULL,
    step_results    JSONB NOT NULL DEFAULT '{}',
    status          VARCHAR(32) NOT NULL DEFAULT 'in_progress'
                    CHECK (status IN ('in_progress', 'paused', 'completed', 'failed')),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_checkpoints_run ON pipeline_checkpoints(run_id);

COMMENT ON TABLE pipeline_checkpoints IS 'Pipeline execution checkpoints for resume-after-failure';

-- DOWN
-- DROP INDEX IF EXISTS idx_checkpoints_run;
-- DROP TABLE IF EXISTS pipeline_checkpoints;
