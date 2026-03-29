# INFRA-DESIGN — Agentic SDLC Platform
**Version:** v1.0 | Full-Stack-First | 2026-03-29
**Document:** 16 of 24 | Status: Draft

---

## Table of Contents

1. [Overview](#1-overview)
2. [Environment Strategy](#2-environment-strategy)
3. [Network Architecture](#3-network-architecture)
4. [Compute Sizing](#4-compute-sizing)
5. [CI/CD Pipeline](#5-cicd-pipeline)
6. [Database Operations](#6-database-operations)
7. [Infrastructure as Code](#7-infrastructure-as-code)
8. [Cost Estimates](#8-cost-estimates)
9. [Observability](#9-observability)
10. [Disaster Recovery](#10-disaster-recovery)
11. [Capacity Planning](#11-capacity-planning)
12. [Rollback Procedures](#12-rollback-procedures)

---

## 1. Overview

This document defines the infrastructure design for the Agentic SDLC Platform — a system comprising 3 MCP servers, 1 REST API, 1 Streamlit Dashboard, an agent runtime hosting 48 agents, a PostgreSQL database, and integrations with external LLM providers (Anthropic, OpenAI, Ollama). The infrastructure supports four environments (local, dev, staging, production) with progressive fidelity and automated promotion through a 9-stage CI/CD pipeline.

### Component Inventory

| Component | Technology | Port | Replicas (Prod) | Stateful |
|---|---|---|---|---|
| MCP Server: agents-server | Python (MCP SDK) | stdio / 8090 (HTTP) | 2 | No |
| MCP Server: governance-server | Python (MCP SDK) | stdio / 8091 (HTTP) | 2 | No |
| MCP Server: knowledge-server | Python (MCP SDK) | stdio / 8092 (HTTP) | 1 | No |
| REST API | Python (aiohttp) | 8080 | 2 | No |
| Streamlit Dashboard | Python (Streamlit) | 8501 | 1 | No (session in memory) |
| Agent Runtime | Python | N/A (internal) | 2 | No (session in DB) |
| PostgreSQL | PostgreSQL 15+ | 5432 | 1 primary + 1 replica | Yes |
| Prometheus | Prometheus | 9090 | 1 | Yes (TSDB) |
| Grafana | Grafana | 3000 | 1 | Yes (dashboards) |
| OpenTelemetry Collector | OTel Collector | 4317 (gRPC) / 4318 (HTTP) | 1 | No |

---

## 2. Environment Strategy

### 2.1 Environment Comparison

| Aspect | Local | Dev | Staging | Production |
|---|---|---|---|---|
| **Database** | SQLite (file-based) | PostgreSQL 15 (Docker) | PostgreSQL 15 (managed) | PostgreSQL 15 (managed, HA) |
| **Orchestration** | Docker Compose | Docker Compose | Kubernetes (single node) | Kubernetes (multi-node) |
| **LLM Providers** | Ollama (local only) | Ollama + Anthropic (dev key) | Anthropic + OpenAI (staging keys) | Anthropic + OpenAI + Ollama |
| **Data** | Synthetic fixtures | Synthetic fixtures | Anonymized copy of production | Real data |
| **Secrets** | `.env` file | `.env` file | HashiCorp Vault | HashiCorp Vault |
| **Observability** | Console logs only | Structured JSON logs | Full stack (OTel + Prometheus + Grafana) | Full stack (OTel + Prometheus + Grafana + alerting) |
| **Agent Count** | 7 (GOVERN phase only) | 14 (GOVERN + DESIGN) | 48 (all phases) | 48 (all phases) |
| **Budget Ceiling** | $1.00/run | $5.00/run | $25.00/run | $45.00/run |
| **Approval Gates** | Disabled (auto-approve all) | Enabled (T0 only) | Enabled (T0-T1) | Enabled (full policy) |
| **Backups** | None | None | Daily | Daily + continuous WAL archival |

### 2.2 Local Environment (`docker-compose.local.yaml`)

```yaml
# Simplified stack for developer workstation
services:
  mcp-agents:
    image: agentic-sdlc/mcp-agents:local
    volumes: ["./agents:/app/agents"]
    environment:
      DATABASE_URL: "sqlite:///data/local.db"
      LLM_PROVIDER: "ollama"
      OLLAMA_BASE_URL: "http://ollama:11434"

  mcp-governance:
    image: agentic-sdlc/mcp-governance:local
    environment:
      DATABASE_URL: "sqlite:///data/local.db"

  rest-api:
    image: agentic-sdlc/rest-api:local
    ports: ["8080:8080"]
    environment:
      DATABASE_URL: "sqlite:///data/local.db"

  dashboard:
    image: agentic-sdlc/dashboard:local
    ports: ["8501:8501"]
    environment:
      API_BASE_URL: "http://rest-api:8080"

  ollama:
    image: ollama/ollama:latest
    ports: ["11434:11434"]
    volumes: ["ollama-data:/root/.ollama"]

volumes:
  ollama-data:
```

### 2.3 Dev Environment (`docker-compose.dev.yaml`)

Extends local with PostgreSQL and structured logging:

```yaml
services:
  postgres:
    image: postgres:15-alpine
    ports: ["5432:5432"]
    environment:
      POSTGRES_DB: agentic_sdlc_dev
      POSTGRES_USER: app_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes: ["pgdata:/var/lib/postgresql/data"]

  mcp-agents:
    extends:
      file: docker-compose.local.yaml
      service: mcp-agents
    environment:
      DATABASE_URL: "postgresql://app_user:${DB_PASSWORD}@postgres:5432/agentic_sdlc_dev"
      LLM_PROVIDER: "ollama,anthropic"
      LOG_FORMAT: "json"

  # ... other services override DATABASE_URL similarly

volumes:
  pgdata:
```

### 2.4 Staging and Production (Kubernetes)

Staging and production use Kubernetes with Helm charts. Key differences:

| Aspect | Staging | Production |
|---|---|---|
| Namespace | `agentic-sdlc-staging` | `agentic-sdlc-prod` |
| Node count | 3 (1 control + 2 worker) | 5 (2 control + 3 worker) |
| Database | Managed PostgreSQL (single instance) | Managed PostgreSQL (HA with replica) |
| Ingress | Internal only (VPN required) | Public ingress with TLS termination |
| HPA | Disabled | Enabled (CPU > 70% triggers scale-up) |
| PDB | None | `minAvailable: 1` for all deployments |

---

## 3. Network Architecture

### 3.1 VPC Layout (Production)

```
+-----------------------------------------------------------------------+
|  VPC: agentic-sdlc-prod (10.0.0.0/16)                                |
|                                                                        |
|  +----------------------------+                                        |
|  | Public Subnet (10.0.1.0/24)|                                        |
|  |                            |                                        |
|  |  +---------------------+  |                                        |
|  |  | Load Balancer (ALB) |  |  <-- HTTPS (443) from internet         |
|  |  | - TLS termination   |  |                                        |
|  |  | - WAF rules         |  |                                        |
|  |  +----------+----------+  |                                        |
|  +-------------|-------------+                                        |
|                |                                                        |
|  +-------------|-----------------------------+                          |
|  | Private Subnet (10.0.2.0/24)              |                          |
|  |             |                             |                          |
|  |  +----------v----------+                  |                          |
|  |  | K8s Worker Nodes    |                  |                          |
|  |  |                     |                  |                          |
|  |  | +----------------+  |  +------------+  |                          |
|  |  | | REST API (8080)|  |  | Dashboard  |  |                          |
|  |  | +----------------+  |  | (8501)     |  |                          |
|  |  |                     |  +------------+  |                          |
|  |  | +----------------+  |                  |                          |
|  |  | | MCP Servers    |  |  +------------+  |                          |
|  |  | | (8090-8092)    |  |  | Agent      |  |                          |
|  |  | +----------------+  |  | Runtime    |  |                          |
|  |  |                     |  +------------+  |                          |
|  |  | +----------------+  |                  |                          |
|  |  | | OTel Collector |  |  +------------+  |                          |
|  |  | +----------------+  |  | Prometheus |  |                          |
|  |  |                     |  +------------+  |                          |
|  |  +---------------------+                  |                          |
|  +-------------------------------------------|                          |
|                                                                        |
|  +-------------------------------------------+                          |
|  | Isolated Subnet (10.0.3.0/24)             |                          |
|  |                                           |                          |
|  |  +---------------------+                  |                          |
|  |  | PostgreSQL (5432)   |                  |                          |
|  |  | - No internet access|                  |                          |
|  |  | - Private subnet    |                  |                          |
|  |  |   access only       |                  |                          |
|  |  +---------------------+                  |                          |
|  +-------------------------------------------+                          |
|                                                                        |
+-----------------------------------------------------------------------+

Outbound (from Private Subnet via NAT Gateway):
  - Anthropic API: api.anthropic.com (443)
  - OpenAI API: api.openai.com (443)
  - Slack Webhooks: hooks.slack.com (443)
  - PagerDuty API: events.pagerduty.com (443)
```

### 3.2 Network Security Rules

| Source | Destination | Port | Protocol | Purpose |
|---|---|---|---|---|
| Internet | Load Balancer | 443 | HTTPS | Dashboard and REST API access |
| Load Balancer | REST API pods | 8080 | HTTP | Proxy to REST API |
| Load Balancer | Dashboard pods | 8501 | HTTP | Proxy to Dashboard |
| Private subnet | MCP servers | 8090-8092 | HTTP | MCP streamable-http (internal only) |
| Private subnet | PostgreSQL | 5432 | TCP/TLS | Database connections |
| Private subnet | NAT Gateway | 443 | HTTPS | Outbound to LLM providers, Slack, PagerDuty |
| Prometheus | All pods | 9090 | HTTP | Metrics scraping |
| OTel Collector | Grafana Cloud / backend | 4317 | gRPC | Trace export |

---

## 4. Compute Sizing

### 4.1 Resource Requests and Limits per Component

| Component | CPU Request | CPU Limit | Memory Request | Memory Limit | Replicas | Notes |
|---|---|---|---|---|---|---|
| MCP agents-server | 0.25 | 0.5 | 256 MB | 512 MB | 2 | Thin handler; delegates to shared service |
| MCP governance-server | 0.25 | 0.5 | 256 MB | 512 MB | 2 | Cost tracking, audit queries |
| MCP knowledge-server | 0.25 | 0.5 | 256 MB | 512 MB | 1 | Lower traffic; knowledge queries |
| REST API | 0.5 | 1.0 | 512 MB | 1 GB | 2 | Handles dashboard + integration traffic |
| Streamlit Dashboard | 0.25 | 0.5 | 256 MB | 512 MB | 1 | Session state in memory; single instance sufficient |
| Agent Runtime | 1.0 | 2.0 | 1 GB | 2 GB | 2 | LLM context assembly requires memory; concurrent agent execution |
| PostgreSQL | 1.0 | 2.0 | 1 GB | 2 GB | 1+1 | Primary + read replica (production) |
| Prometheus | 0.5 | 1.0 | 512 MB | 1 GB | 1 | 15-day retention; 30s scrape interval |
| Grafana | 0.25 | 0.5 | 256 MB | 512 MB | 1 | Dashboard rendering; 5 concurrent users |
| OTel Collector | 0.25 | 0.5 | 256 MB | 512 MB | 1 | Trace batching and export |

### 4.2 Total Resource Requirements

| Environment | Total CPU | Total Memory | Storage |
|---|---|---|---|
| Local | 2 CPU | 2 GB | 10 GB (SQLite + Ollama models) |
| Dev | 4 CPU | 4 GB | 20 GB (PostgreSQL + Ollama) |
| Staging | 8 CPU | 12 GB | 50 GB (PostgreSQL + generated docs) |
| Production | 12 CPU | 16 GB | 100 GB (PostgreSQL + generated docs + backups) |

### 4.3 Horizontal Pod Autoscaler (Production)

| Component | Min Replicas | Max Replicas | Scale-Up Trigger | Scale-Down Trigger |
|---|---|---|---|---|
| REST API | 2 | 5 | CPU > 70% for 2 min | CPU < 30% for 5 min |
| Agent Runtime | 2 | 4 | CPU > 70% for 2 min | CPU < 30% for 5 min |
| MCP agents-server | 2 | 3 | CPU > 70% for 2 min | CPU < 30% for 5 min |
| MCP governance-server | 2 | 3 | CPU > 70% for 2 min | CPU < 30% for 5 min |

---

## 5. CI/CD Pipeline

### 5.1 Pipeline Stages

```
[1] Lint        [2] Unit Test    [3] Build         [4] Integration   [5] Security
    |                |               |                  |                 |
    v                v               v                  v                 v
 ruff + mypy    pytest (unit)   Docker build      pytest (integ)    Trivy scan
 schema valid   coverage >80%   Helm package      DB migrations     SBOM gen
                                Push to registry   MCP tool tests    Dep review
                                                   REST API tests
                                                   Dashboard render
                                                                        |
                                                                        v
[6] Deploy Staging  [7] Smoke Test    [8] Deploy Prod     [9] Post-Deploy
        |                 |                  |                    |
        v                 v                  v                    v
  Helm upgrade       Health checks      Canary (10%)       Health checks
  Run migrations     Pipeline trigger   Monitor 15 min     Smoke test
  Seed test data     Cost check         Promote to 100%    Notify Slack
                     Audit verify       (or rollback)      Update SBOM
```

### 5.2 Stage Detail

| Stage | Tools | Pass Criteria | Fail Action | Duration |
|---|---|---|---|---|
| 1. Lint | `ruff`, `mypy`, JSON Schema validator | Zero errors; zero type errors; all manifests valid | Block merge | ~1 min |
| 2. Unit Test | `pytest` with `pytest-cov` | All tests pass; coverage >= 80%; no flaky tests (0 retries needed) | Block merge | ~3 min |
| 3. Build | Docker, Helm, container registry | Images build successfully; Helm chart lints; pushed to registry | Block merge | ~5 min |
| 4. Integration Test | `pytest` with test database | All integration tests pass; MCP tools respond correctly; REST endpoints return expected shapes; Dashboard pages render | Block merge | ~8 min |
| 5. Security Scan | `trivy`, `syft`, GitHub Dependency Review | Zero critical/high CVEs in base image; SBOM generated; no new vulnerabilities introduced | Block merge (critical); warn (high) | ~3 min |
| 6. Deploy Staging | Helm, kubectl, Alembic | Deployment succeeds; migrations apply cleanly; all pods healthy | Alert on-call; manual investigation | ~5 min |
| 7. Smoke Test | pytest (smoke suite) | Health endpoints return 200; pipeline trigger returns run_id; cost check returns valid data; audit query returns results | Rollback staging | ~3 min |
| 8. Deploy Production | Helm (canary strategy) | Canary pods healthy; error rate < 1% for 15 min; latency within SLA | Automatic rollback | ~20 min |
| 9. Post-Deploy | Health checks, Slack notification | All health checks pass; smoke test passes; Slack notification sent | Alert on-call | ~2 min |

### 5.3 Branch Strategy

| Branch | Purpose | Deploys To | Auto-Deploy |
|---|---|---|---|
| `feature/*` | Feature development | None (CI only: stages 1-5) | No |
| `main` | Integration branch | Staging (stages 6-7) | Yes |
| `release/*` | Production release | Production (stages 8-9) | Yes (canary) |
| `hotfix/*` | Critical fixes | Production (expedited: stages 1-5, 8-9) | Manual approval |

---

## 6. Database Operations

### 6.1 Migration Strategy

| Aspect | Detail |
|---|---|
| Tool | Alembic (SQLAlchemy migration framework) |
| Migration directory | `alembic/versions/` |
| Naming convention | `{NNN}_{description}.py` (e.g., `001_create_agent_registry.py`) |
| Forward-only | All migrations are forward-only; rollback via separate down migration |
| Testing | Every migration tested in CI against empty DB and against previous version's DB |
| Production application | Applied during deploy stage, before new pods start |
| Timeout | 60 seconds per migration; abort deployment if exceeded |

### 6.2 Migration Inventory (Current)

| # | Migration | Tables Affected | Type |
|---|---|---|---|
| 001 | Create agent_registry | `agent_registry` | CREATE TABLE |
| 002 | Create cost_metrics | `cost_metrics` | CREATE TABLE |
| 003 | Create audit_events | `audit_events` | CREATE TABLE |
| 004 | Create pipeline_runs and pipeline_steps | `pipeline_runs`, `pipeline_steps` | CREATE TABLE |
| 005 | Create knowledge_exceptions | `knowledge_exceptions` | CREATE TABLE |
| 006 | Create session_context | `session_context` | CREATE TABLE |
| 007 | Create approval_requests | `approval_requests` | CREATE TABLE |
| 008 | Create pipeline_checkpoints | `pipeline_checkpoints` | CREATE TABLE |
| 009 | Create mcp_call_events; alter agent_registry | `mcp_call_events`, `agent_registry` | CREATE TABLE, ALTER TABLE |

### 6.3 Backup Strategy

| Aspect | Dev | Staging | Production |
|---|---|---|---|
| Backup method | None | pg_dump daily | pg_dump daily + continuous WAL archival |
| Backup schedule | N/A | 03:00 UTC daily | 03:00 UTC daily (full); continuous (WAL) |
| Retention | N/A | 7 days | 30 days (daily); 7 days (WAL) |
| Storage | N/A | Local volume | S3 bucket (cross-region) |
| Encryption | N/A | At rest (AES-256) | At rest (AES-256) + in transit (TLS) |
| Restore test | N/A | Monthly | Weekly automated restore to staging |
| Point-in-time recovery | N/A | No | Yes (via WAL replay, granularity: 1 minute) |

### 6.4 Database Connection Pool

| Parameter | Value | Rationale |
|---|---|---|
| `pool_size` | 10 | Sufficient for 2 REST API + 2 Agent Runtime + 3 MCP servers |
| `max_overflow` | 5 | Handle burst traffic without exhausting connections |
| `pool_timeout` | 30s | Fail fast if pool is exhausted |
| `pool_recycle` | 1800s (30 min) | Prevent stale connections |
| `pool_pre_ping` | true | Verify connection liveness before use |

---

## 7. Infrastructure as Code

### 7.1 Terraform Module Structure

```
terraform/
  modules/
    vpc/                    # VPC, subnets, NAT gateway, security groups
      main.tf
      variables.tf
      outputs.tf
    kubernetes/             # EKS/GKE cluster, node groups, RBAC
      main.tf
      variables.tf
      outputs.tf
    database/               # Managed PostgreSQL, parameter groups, backups
      main.tf
      variables.tf
      outputs.tf
    observability/          # Prometheus, Grafana, OTel Collector
      main.tf
      variables.tf
      outputs.tf
    secrets/                # Vault/Secrets Manager, secret rotation
      main.tf
      variables.tf
      outputs.tf
  environments/
    dev/
      main.tf               # Module instantiation with dev values
      terraform.tfvars
    staging/
      main.tf
      terraform.tfvars
    production/
      main.tf
      terraform.tfvars
  backend.tf                # Remote state (S3 + DynamoDB lock)
```

### 7.2 Terraform State Management

| Aspect | Configuration |
|---|---|
| Backend | S3 bucket with versioning enabled |
| State locking | DynamoDB table for concurrent access prevention |
| State encryption | AES-256 (S3 server-side encryption) |
| State separation | One state file per environment (dev, staging, production) |
| Access | CI/CD pipeline service account; human access via MFA-protected IAM role |

### 7.3 Helm Chart Structure

```
helm/
  agentic-sdlc/
    Chart.yaml
    values.yaml                 # Default values
    values-dev.yaml             # Dev overrides
    values-staging.yaml         # Staging overrides
    values-production.yaml      # Production overrides
    templates/
      deployment-rest-api.yaml
      deployment-mcp-agents.yaml
      deployment-mcp-governance.yaml
      deployment-mcp-knowledge.yaml
      deployment-dashboard.yaml
      deployment-agent-runtime.yaml
      service-rest-api.yaml
      service-dashboard.yaml
      ingress.yaml
      hpa.yaml
      pdb.yaml
      configmap.yaml
      secret.yaml
      serviceaccount.yaml
```

---

## 8. Cost Estimates

### 8.1 Infrastructure Cost per Environment (Monthly)

| Component | Local | Dev | Staging | Production |
|---|---|---|---|---|
| Compute (containers) | $0 (developer machine) | $0 (developer machine) | $150 (3-node K8s) | $350 (5-node K8s) |
| Database | $0 (SQLite) | $0 (Docker) | $50 (managed PostgreSQL, small) | $120 (managed PostgreSQL, HA) |
| Storage (block + object) | $0 | $0 | $20 | $50 |
| Load balancer | $0 | $0 | $0 (internal only) | $25 |
| NAT Gateway | $0 | $0 | $30 | $30 |
| Observability (Prometheus + Grafana) | $0 | $0 | $0 (self-hosted) | $0 (self-hosted) |
| Secrets management | $0 (.env) | $0 (.env) | $15 (Vault) | $15 (Vault) |
| **Subtotal (infra)** | **$0** | **$0** | **$265** | **$590** |

### 8.2 LLM API Cost Estimates (Monthly)

| Usage Scenario | Pipeline Runs/Month | Cost/Run | Monthly LLM Cost |
|---|---|---|---|
| Low (single team, 2 runs/week) | 8 | $25-$35 | $200-$280 |
| Medium (2 teams, 5 runs/week) | 20 | $25-$35 | $500-$700 |
| High (5 teams, daily runs) | 100 | $25-$35 | $2,500-$3,500 |

### 8.3 LLM Cost Breakdown per Pipeline Run

| Component | Tokens (est.) | Provider | Cost (est.) |
|---|---|---|---|
| G4-team-orchestrator (pipeline planning) | 50K input + 10K output | Anthropic Claude 3.5 Sonnet | $0.50 |
| Document generation agents (24 docs) | 800K input + 400K output | Anthropic Claude 3.5 Sonnet | $18.00 |
| G5-quality-gate-enforcer (24 evaluations) | 200K input + 50K output | Anthropic Claude 3.5 Haiku | $2.50 |
| G1-cost-tracker overhead | 10K input + 5K output | Anthropic Claude 3.5 Haiku | $0.15 |
| G2-audit-trail-validator overhead | 10K input + 5K output | Anthropic Claude 3.5 Haiku | $0.15 |
| Session context management | 30K input + 15K output | Anthropic Claude 3.5 Haiku | $0.45 |
| **Total per run** | **~1.1M input + ~485K output** | | **~$21.75** |
| **Budget ceiling** | | | **$45.00** |
| **Headroom** | | | **~52%** |

### 8.4 Total Monthly Cost Summary

| Category | Low Usage | Medium Usage | High Usage |
|---|---|---|---|
| Infrastructure (production) | $590 | $590 | $590 |
| LLM API costs | $240 | $600 | $3,000 |
| Slack (notifications) | $0 (free tier) | $0 | $0 |
| PagerDuty | $0 (free tier) | $20 | $20 |
| **Total** | **$830** | **$1,210** | **$3,610** |

---

## 9. Observability

### 9.1 Observability Stack

```
+-------------------+     +-------------------+     +-------------------+
| Application Pods  |     | OTel Collector    |     | Grafana           |
|                   |     |                   |     |                   |
| Structured JSON   +---->+ Log aggregation   +---->+ Log dashboards    |
| logs to stdout    |     |                   |     |                   |
|                   |     | Trace batching    |     | Trace viewer      |
| OTel SDK traces   +---->+ and export        +---->+ (Tempo/Jaeger)    |
|                   |     |                   |     |                   |
| /metrics endpoint |     +-------------------+     | Metric dashboards |
|         |         |                               |         ^         |
+---------+---------+                               +---------+---------+
          |                                                   |
          |         +-------------------+                     |
          +-------->+ Prometheus        +---------------------+
                    | (scrape /metrics) |
                    +-------------------+
```

### 9.2 Structured Logging

| Field | Type | Source | Example |
|---|---|---|---|
| `timestamp` | ISO 8601 | Auto | `2026-03-29T14:30:00.123Z` |
| `level` | string | Code | `info`, `warn`, `error` |
| `service` | string | Config | `rest-api`, `mcp-agents`, `agent-runtime` |
| `trace_id` | string | OTel SDK | `abc123def456` |
| `span_id` | string | OTel SDK | `789ghi` |
| `agent_id` | string | Context | `G1-cost-tracker` |
| `pipeline_run_id` | UUID | Context | `550e8400-e29b-41d4-a716-446655440000` |
| `message` | string | Code | `Pipeline step completed` |
| `duration_ms` | number | Instrumentation | `1234` |
| `error` | object | Exception handler | `{"type": "TimeoutError", "message": "LLM call timed out"}` |

### 9.3 Metrics (Prometheus)

| Metric | Type | Labels | Description |
|---|---|---|---|
| `mcp_tool_duration_seconds` | Histogram | `tool`, `server`, `status` | MCP tool call latency distribution |
| `rest_request_duration_seconds` | Histogram | `method`, `path`, `status_code` | REST API request latency |
| `dashboard_page_load_seconds` | Histogram | `page` | Streamlit page render time |
| `agent_invocation_duration_seconds` | Histogram | `agent_id`, `phase` | Agent execution time |
| `llm_request_duration_seconds` | Histogram | `provider`, `model`, `agent_id` | LLM API call latency |
| `llm_tokens_total` | Counter | `provider`, `model`, `direction` (input/output) | Token consumption |
| `cost_usd_total` | Counter | `agent_id`, `provider`, `project_id` | Accumulated LLM cost |
| `pipeline_runs_total` | Counter | `status` (running/completed/failed/cancelled) | Pipeline run count |
| `pipeline_step_quality_score` | Gauge | `agent_id`, `document_type` | Latest quality score per agent |
| `agent_health_status` | Gauge | `agent_id`, `phase` | 1=healthy, 0.5=degraded, 0=down |
| `circuit_breaker_state` | Gauge | `provider` | 0=closed, 0.5=half-open, 1=open |
| `approval_requests_pending` | Gauge | `reviewer` | Count of pending approvals |
| `db_connection_pool_active` | Gauge | `service` | Active database connections |
| `rate_limit_hits_total` | Counter | `client_id`, `interface` | Rate limit 429 response count |

### 9.4 Grafana Dashboards

| Dashboard | Panels | Refresh Rate | Primary Audience |
|---|---|---|---|
| **System Health** | Service uptime heatmap, HTTP error rate, DB connection pool utilization, pod CPU/memory, P95 latencies | 30s | David (DevOps) |
| **Agent Performance** | Agent invocation count, quality score trends, maturity tier distribution, per-agent latency, top error agents | 1 min | Priya (Platform), Anika (Eng Lead) |
| **Cost Burn-Down** | Fleet cost burn-down (real-time), per-agent cost bar chart, per-provider cost pie chart, budget utilization gauge, cost anomaly alerts | 30s | Marcus (Delivery), David (DevOps) |
| **Pipeline Execution** | Active pipeline count, step completion waterfall, document generation throughput, failure rate trend, checkpoint/resume count | 1 min | Marcus (Delivery), Priya (Platform) |
| **LLM Provider Health** | Per-provider latency P50/P95/P99, error rate, circuit breaker status, token throughput, cost per 1K tokens | 30s | Priya (Platform) |

### 9.5 AI-Specific Observability

| Metric Category | What We Track | Why It Matters |
|---|---|---|
| **Token usage per agent** | Input tokens, output tokens, total tokens per invocation, per run, per day | Cost attribution; detect agents with runaway token consumption |
| **Provider latency** | Per-provider P50/P95/P99 latency; latency by model | Provider selection optimization; detect provider degradation |
| **Quality scores** | Per-agent quality score distribution; quality trend over time | Agent maturity progression decisions; detect quality regression |
| **Confidence scores** | Per-agent confidence score distribution; correlation with human approval outcomes | Calibrate auto-approval thresholds; identify agents that over/under-estimate |
| **Override rate** | Percentage of agent outputs modified by human reviewers | Maturity progression gating; identify agents needing prompt improvement |
| **Context window utilization** | Percentage of context window used per agent invocation | Capacity planning; detect agents approaching context limits |
| **Hallucination rate (proxy)** | Quality score < 0.5 as proxy for hallucination | Agent reliability monitoring; trigger retraining or prompt revision |

### 9.6 Alerting Rules

| Alert | Condition | Severity | Channel | Response |
|---|---|---|---|---|
| Agent Down | `agent_health_status == 0` for > 2 min | Critical | PagerDuty + Slack | On-call investigates; check agent logs; restart if needed |
| Cost Budget Exceeded | `cost_usd_total{project_id=X}` > budget | Critical | Slack | G1-cost-tracker hard-stops agents; operator reviews |
| Pipeline Failure Rate Spike | `rate(pipeline_runs_total{status="failed"})` > 0.2 for 10 min | Warning | Slack | Investigate recent code changes; check LLM provider health |
| LLM Provider Circuit Open | `circuit_breaker_state{provider=X} == 1` | Warning | Slack | Check provider status page; failover to alternate provider if configured |
| Audit Trail Gap | Reconciliation job detects gap count > 0 | Critical | PagerDuty + Slack | Immediate investigation; compliance notification |
| Database Connection Pool Exhausted | `db_connection_pool_active > pool_size + max_overflow * 0.9` | Warning | Slack | Scale application pods; investigate connection leaks |
| P95 Latency SLA Breach | `mcp_tool_duration_seconds{quantile="0.95"} > 0.5` (reads) | Warning | Slack | Check query performance; review database indexes |
| High Error Rate | `rate(rest_request_duration_seconds_count{status_code=~"5.."}[5m]) / rate(rest_request_duration_seconds_count[5m]) > 0.05` | Critical | PagerDuty | Rollback if recent deployment; investigate error logs |

---

## 10. Disaster Recovery

### 10.1 Recovery Objectives

| Objective | Target | Justification |
|---|---|---|
| **RPO (Recovery Point Objective)** | 1 hour | Continuous WAL archival provides near-real-time backup; 1 hour accounts for worst-case WAL shipping lag |
| **RTO (Recovery Time Objective)** | 4 hours | Database restore (1h) + application deployment (30min) + validation (30min) + DNS propagation (2h worst case) |
| **MTTR (Mean Time to Recovery)** | 2 hours | Target for routine incidents (pod restart, connection pool exhaustion, provider failover) |

### 10.2 Disaster Scenarios and Response

| Scenario | Impact | Detection | Response | RTO |
|---|---|---|---|---|
| Single pod crash | Minimal (replica continues) | K8s liveness probe; auto-restart | Automatic (K8s restarts pod) | < 1 min |
| Node failure | Medium (multiple pods affected) | K8s node status; pod eviction | Automatic (K8s reschedules to healthy nodes) | < 5 min |
| Database primary failure | High (all writes blocked) | Connection errors; health check failure | Failover to read replica (manual promote) | < 30 min |
| Full cluster failure | Critical (platform unavailable) | Monitoring alerts; health endpoint failure | Provision new cluster from Terraform; restore DB from backup; deploy from container registry | 4 hours |
| LLM provider outage | Medium (pipeline runs fail) | Circuit breaker opens; error rate spike | Failover to alternate provider (if agent supports multiple); pause new pipeline runs | < 5 min (failover) |
| Data corruption | Critical (data integrity compromised) | Audit reconciliation failure; application errors | Point-in-time recovery from WAL backup to moment before corruption | 1-2 hours |
| Region outage | Critical (platform unavailable) | Cloud provider status page; all health checks fail | Restore from cross-region backup to standby region | 4-8 hours |

### 10.3 Backup and Recovery Architecture

```
Production Region (primary)                     Backup Region
+-----------------------------+                  +-----------------------------+
| PostgreSQL Primary          |                  | S3 Bucket (backup)          |
|   |                         |                  |                             |
|   +-- WAL archival -------->|--- S3 replication -->| Daily pg_dump snapshots  |
|   |                         |                  |   WAL archive files         |
|   +-- Daily pg_dump ------->|                  |   Container images (ECR)    |
|                             |                  |   Terraform state           |
| Container Registry (ECR)    |                  |                             |
|   |                         |                  +-----------------------------+
|   +-- Cross-region repl --->|
|                             |
+-----------------------------+
```

### 10.4 DR Testing Schedule

| Test Type | Frequency | Scope | Duration | Success Criteria |
|---|---|---|---|---|
| Backup restore verification | Weekly | Restore latest backup to staging; run smoke tests | 1 hour | All tables present; row counts within 1% of production; smoke tests pass |
| Pod failure simulation | Monthly | Kill random pods; verify auto-recovery | 30 min | All pods recover within 2 minutes; no data loss |
| Database failover test | Quarterly | Promote read replica to primary; verify application connectivity | 2 hours | Failover completes within 30 min; application reconnects; zero data loss |
| Full DR exercise | Quarterly | Restore entire platform from backup in secondary region | 4 hours | Platform operational within RTO (4h); data loss within RPO (1h) |

---

## 11. Capacity Planning

### 11.1 Current Baseline (Month 0)

| Metric | Value | Source |
|---|---|---|
| Pipeline runs/day | 2-3 | Estimated from 1 team, 2-3 client engagements/week |
| Agents active | 48 | Full fleet |
| Agent invocations/day | 100-200 | ~48 agents x 2-3 runs x 1-2 invocations each |
| Audit events/day | 200-400 | 1 audit event per agent invocation + system events |
| Cost metrics/day | 100-200 | 1 cost record per LLM API call |
| MCP tool calls/day | 200-500 | Developer + AI assistant usage |
| Database size | 500 MB | Initial schema + 30 days of data |
| Generated documents | 50-75 files/day | 24 docs x 2-3 runs |

### 11.2 Growth Projections

| Metric | Month 3 | Month 6 | Month 12 |
|---|---|---|---|
| Pipeline runs/day | 5-10 | 15-25 | 50-100 |
| Agent invocations/day | 300-600 | 900-1,500 | 3,000-6,000 |
| Audit events/day | 500-1,000 | 1,500-3,000 | 5,000-10,000 |
| Database size | 2 GB | 8 GB | 30 GB |
| Generated documents (cumulative) | 5,000 | 20,000 | 80,000 |
| Monthly LLM cost | $500-$700 | $1,500-$2,500 | $5,000-$10,000 |
| Concurrent users (Dashboard) | 3-5 | 5-10 | 10-20 |
| MCP tool calls/day | 500-1,000 | 1,500-3,000 | 5,000-10,000 |

### 11.3 Scaling Triggers

| Metric | Threshold | Action |
|---|---|---|
| Database size > 50 GB | 60% of allocated storage | Increase storage allocation; review retention policies |
| Pipeline runs/day > 50 | HPA max replicas for Agent Runtime | Increase HPA max; consider dedicated agent pools |
| Database connections > 80% of pool | `db_connection_pool_active / (pool_size + max_overflow)` | Increase pool_size; consider PgBouncer |
| Dashboard concurrent sessions > 10 | Streamlit memory pressure | Add Dashboard replica; consider session externalization |
| LLM token throughput > provider rate limit | Rate limit 429 responses increasing | Implement request queuing; negotiate higher rate limits; add Ollama capacity |

### 11.4 LLM Token Budget Forecasting

| Forecast Period | Pipeline Runs | Tokens (Input) | Tokens (Output) | Estimated Cost |
|---|---|---|---|---|
| Month 1 | 60 | 66M | 29M | $1,300 |
| Month 3 | 200 | 220M | 97M | $4,350 |
| Month 6 | 500 | 550M | 243M | $10,875 |
| Month 12 | 2,000 | 2.2B | 970M | $43,500 |

Budget alert thresholds:
- Monthly budget: set at 120% of forecast (buffer for cost variance)
- Weekly budget: monthly / 4 (even distribution)
- Daily budget: weekly / 5 (workday distribution)

---

## 12. Rollback Procedures

### 12.1 Rollback Decision Matrix

| Signal | Severity | Auto-Rollback | Manual Decision Window |
|---|---|---|---|
| Error rate > 5% for 5 min post-deploy | Critical | Yes (canary stage) | N/A |
| P95 latency > 2x baseline for 5 min | High | Yes (canary stage) | N/A |
| Health check failure on > 50% of new pods | Critical | Yes | N/A |
| Quality score regression (avg drops > 10%) | Medium | No | 30 min investigation window |
| Single non-critical endpoint degradation | Low | No | 1 hour investigation window |
| Migration failure | Critical | Yes (abort deployment) | N/A |

### 12.2 Application Rollback (Helm)

```bash
# Step 1: Identify current and previous release
helm history agentic-sdlc -n agentic-sdlc-prod

# Step 2: Rollback to previous release
helm rollback agentic-sdlc [REVISION] -n agentic-sdlc-prod

# Step 3: Verify rollback
kubectl get pods -n agentic-sdlc-prod
kubectl logs -l app=rest-api -n agentic-sdlc-prod --tail=50

# Step 4: Run smoke test
pytest tests/smoke/ --env=production

# Step 5: Notify team
# Automated Slack notification on rollback
```

### 12.3 Database Rollback

| Scenario | Procedure | Duration | Data Impact |
|---|---|---|---|
| **Failed migration (no data change)** | `alembic downgrade -1` to revert schema change | < 1 min | None |
| **Failed migration (with data change)** | Restore from pre-migration backup; re-apply safe migrations | 30-60 min | Data since backup may be lost (RPO applies) |
| **Data corruption (known time)** | Point-in-time recovery using WAL replay to moment before corruption | 1-2 hours | Data after recovery point lost |
| **Data corruption (unknown time)** | Restore from last known good backup; manual data reconciliation | 2-4 hours | Potentially significant data loss |

### 12.4 MCP Server Rollback

MCP servers are stateless; rollback involves redeploying the previous container image:

```bash
# Rollback specific MCP server
kubectl rollout undo deployment/mcp-agents -n agentic-sdlc-prod
kubectl rollout undo deployment/mcp-governance -n agentic-sdlc-prod
kubectl rollout undo deployment/mcp-knowledge -n agentic-sdlc-prod

# Verify MCP server health
kubectl exec -it deployment/mcp-agents -- python -c "from health import check; check()"
```

### 12.5 Agent Version Rollback

Agent versions are managed independently of application deployment:

```bash
# Via MCP tool
# Invoke rollback_canary MCP tool to revert agent to previous version

# Via REST API
curl -X POST http://localhost:8080/api/agents/{agent_id}/rollback \
  -H "Authorization: Bearer $JWT" \
  -d '{"reason": "Quality regression detected"}'
```

Agent rollback updates `agent_registry`:
- Sets `active_version = previous_version`
- Sets `canary_version = null`
- Records rollback in `audit_events` with action `agent.version.rollback`

### 12.6 LLM Provider Failover

Not a traditional rollback, but a critical recovery procedure:

```
Provider Failure Detected (circuit breaker opens)
       |
       v
[1] Check agent manifest for alternate providers
       |--- No alternate --> Pause agent; alert operator
       |--- Has alternate --> Continue
       |
       v
[2] Route subsequent LLM calls to alternate provider
       |
       v
[3] Verify data classification compatibility
       |--- C3 data + external alternate --> BLOCK; use Ollama only
       |--- C1/C2 data --> Proceed with alternate
       |
       v
[4] Monitor alternate provider health
       |
       v
[5] When primary recovers (circuit breaker closes), resume routing to primary
       |
       v
[6] Log entire failover event in audit_events
```
