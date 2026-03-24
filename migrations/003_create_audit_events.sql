-- Migration 003: Create audit_events table with immutability trigger
-- UP
CREATE TABLE audit_events (
    id              BIGSERIAL PRIMARY KEY,
    event_id        UUID NOT NULL DEFAULT gen_random_uuid() UNIQUE,
    agent_id        VARCHAR(64),
    project_id      VARCHAR(64),
    session_id      UUID NOT NULL,
    action          VARCHAR(128) NOT NULL,
    severity        VARCHAR(16) NOT NULL DEFAULT 'info'
                    CHECK (severity IN ('info', 'warning', 'error', 'critical')),
    message         TEXT,
    details         JSONB DEFAULT '{}',
    pii_detected    BOOLEAN NOT NULL DEFAULT FALSE,
    cost_usd        NUMERIC(10, 6) NOT NULL DEFAULT 0 CHECK (cost_usd >= 0),
    tokens_in       INTEGER NOT NULL DEFAULT 0 CHECK (tokens_in >= 0),
    tokens_out      INTEGER NOT NULL DEFAULT 0 CHECK (tokens_out >= 0),
    duration_ms     INTEGER NOT NULL DEFAULT 0 CHECK (duration_ms >= 0),
    source_ip       INET,
    user_id         VARCHAR(128),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Immutability trigger: block UPDATE and DELETE on audit_events
CREATE OR REPLACE FUNCTION audit_events_immutable()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'audit_events table is immutable. UPDATE and DELETE operations are prohibited.';
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_audit_events_no_update
    BEFORE UPDATE ON audit_events
    FOR EACH ROW
    EXECUTE FUNCTION audit_events_immutable();

CREATE TRIGGER trg_audit_events_no_delete
    BEFORE DELETE ON audit_events
    FOR EACH ROW
    EXECUTE FUNCTION audit_events_immutable();

COMMENT ON TABLE audit_events IS 'Immutable audit trail. No UPDATE or DELETE allowed. Append-only.';

-- DOWN
-- DROP TRIGGER IF EXISTS trg_audit_events_no_delete ON audit_events;
-- DROP TRIGGER IF EXISTS trg_audit_events_no_update ON audit_events;
-- DROP FUNCTION IF EXISTS audit_events_immutable();
-- DROP TABLE IF EXISTS audit_events;
