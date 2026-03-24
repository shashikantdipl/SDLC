-- Migration 005: Create knowledge_exceptions table
-- UP
CREATE TABLE knowledge_exceptions (
    exception_id    VARCHAR(64) PRIMARY KEY,
    title           VARCHAR(256) NOT NULL,
    rule            TEXT NOT NULL,
    description     TEXT,
    severity        VARCHAR(16) NOT NULL DEFAULT 'warning'
                    CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    tier            VARCHAR(16) NOT NULL
                    CHECK (tier IN ('universal', 'stack', 'client')),
    stack_name      VARCHAR(128),
    client_id       VARCHAR(128),
    active          BOOLEAN NOT NULL DEFAULT TRUE,
    applies_to_phases TEXT[],
    applies_to_agents TEXT[],
    fire_count      INTEGER NOT NULL DEFAULT 0 CHECK (fire_count >= 0),
    last_fired_at   TIMESTAMPTZ,
    tags            TEXT[] DEFAULT '{}',
    promoted_by     VARCHAR(128),
    promoted_at     TIMESTAMPTZ,
    created_by      VARCHAR(128) NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE knowledge_exceptions
    ADD CONSTRAINT chk_tier_client CHECK (tier != 'client' OR client_id IS NOT NULL);

ALTER TABLE knowledge_exceptions
    ADD CONSTRAINT chk_tier_stack CHECK (tier != 'stack' OR stack_name IS NOT NULL);

COMMENT ON TABLE knowledge_exceptions IS 'Three-tier knowledge exception catalog (universal > stack > client)';

-- DOWN
-- DROP TABLE IF EXISTS knowledge_exceptions;
