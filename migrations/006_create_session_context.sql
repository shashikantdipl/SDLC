-- Migration 006: Create session_context table
-- BLOCKING: The 12-doc pipeline cannot run without this table.
-- UP
CREATE TABLE session_context (
    id              BIGSERIAL PRIMARY KEY,
    session_id      UUID NOT NULL,
    key             VARCHAR(128) NOT NULL,
    value           JSONB NOT NULL,
    written_by      VARCHAR(64) NOT NULL,
    written_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ttl_seconds     INTEGER NOT NULL DEFAULT 86400 CHECK (ttl_seconds > 0),
    expires_at      TIMESTAMPTZ GENERATED ALWAYS AS (written_at + (ttl_seconds || ' seconds')::INTERVAL) STORED,
    UNIQUE (session_id, key)
);

COMMENT ON TABLE session_context IS 'Session key-value store for inter-agent context passing within pipeline runs';
COMMENT ON COLUMN session_context.ttl_seconds IS 'Time-to-live in seconds. Default 86400 (24 hours). Expired rows cleaned by background job.';

-- DOWN
-- DROP TABLE IF EXISTS session_context;
