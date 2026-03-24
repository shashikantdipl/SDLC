-- Migration 001: Create agent_registry table
-- UP
CREATE TABLE agent_registry (
    id              BIGSERIAL PRIMARY KEY,
    agent_id        VARCHAR(64) NOT NULL UNIQUE,
    name            VARCHAR(256) NOT NULL,
    phase           VARCHAR(32) NOT NULL
                    CHECK (phase IN ('govern', 'design', 'build', 'test', 'deploy', 'operate', 'oversight')),
    archetype       VARCHAR(64) NOT NULL
                    CHECK (archetype IN ('ci-gate', 'reviewer', 'ops-agent', 'discovery-agent', 'co-pilot', 'orchestrator', 'governance')),
    model           VARCHAR(64) NOT NULL DEFAULT 'claude-sonnet-4-6',
    status          VARCHAR(16) NOT NULL DEFAULT 'active'
                    CHECK (status IN ('active', 'degraded', 'offline', 'canary')),
    active_version  VARCHAR(32) DEFAULT '1.0.0',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE agent_registry IS 'Registry of all 48 SDLC agents with their configuration and status';

-- DOWN
-- DROP TABLE IF EXISTS agent_registry;
