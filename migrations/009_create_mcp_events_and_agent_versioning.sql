-- Migration 009: Create mcp_call_events table and extend agent_registry for versioning
-- UP

-- 009a: MCP call event tracking (for MCP Monitoring Panel on Dashboard)
CREATE TABLE mcp_call_events (
    id              BIGSERIAL PRIMARY KEY,
    call_id         UUID NOT NULL DEFAULT gen_random_uuid() UNIQUE,
    server_name     VARCHAR(64) NOT NULL
                    CHECK (server_name IN ('agentic-sdlc-agents', 'agentic-sdlc-governance', 'agentic-sdlc-knowledge')),
    tool_name       VARCHAR(128) NOT NULL,
    caller          VARCHAR(256) NOT NULL,
    project_id      VARCHAR(64),
    duration_ms     INTEGER NOT NULL DEFAULT 0 CHECK (duration_ms >= 0),
    status          VARCHAR(16) NOT NULL DEFAULT 'success'
                    CHECK (status IN ('success', 'error', 'timeout')),
    error_message   TEXT,
    tokens_used     INTEGER NOT NULL DEFAULT 0 CHECK (tokens_used >= 0),
    cost_usd        NUMERIC(10, 6) NOT NULL DEFAULT 0 CHECK (cost_usd >= 0),
    called_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE mcp_call_events IS 'MCP tool invocation log for observability and the MCP Monitoring Panel';

-- 009b: Extend agent_registry with versioning and maturity columns
ALTER TABLE agent_registry
    ADD COLUMN IF NOT EXISTS canary_version VARCHAR(32),
    ADD COLUMN IF NOT EXISTS canary_traffic_pct SMALLINT NOT NULL DEFAULT 0
        CHECK (canary_traffic_pct >= 0 AND canary_traffic_pct <= 100),
    ADD COLUMN IF NOT EXISTS previous_version VARCHAR(32),
    ADD COLUMN IF NOT EXISTS maturity_level VARCHAR(32) NOT NULL DEFAULT 'supervised'
        CHECK (maturity_level IN ('supervised', 'assisted', 'autonomous', 'fully_autonomous')),
    ADD COLUMN IF NOT EXISTS promoted_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS rolled_back_at TIMESTAMPTZ;

-- DOWN
-- ALTER TABLE agent_registry
--     DROP COLUMN IF EXISTS canary_version,
--     DROP COLUMN IF EXISTS canary_traffic_pct,
--     DROP COLUMN IF EXISTS previous_version,
--     DROP COLUMN IF EXISTS maturity_level,
--     DROP COLUMN IF EXISTS promoted_at,
--     DROP COLUMN IF EXISTS rolled_back_at;
-- DROP TABLE IF EXISTS mcp_call_events;
