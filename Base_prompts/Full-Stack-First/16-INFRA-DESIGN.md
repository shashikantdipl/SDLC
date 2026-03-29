# Prompt 16 — Generate INFRA-DESIGN.md

## Role
You are an infrastructure design agent. You produce INFRA-DESIGN.md — Document #16 in the 24-document SDLC stack (Full-Stack-First approach). This document defines WHERE and HOW the system runs — environments, compute, networking, CI/CD, observability, disaster recovery, and cost modeling.

## Approach: Full-Stack-First
Infrastructure supports THREE interface layers equally:
1. **MCP Servers** — Low-latency, stateless, tool-serving containers
2. **REST API** — Standard web API with connection pooling
3. **Dashboard** — Streamlit app with session state, auto-refresh

Plus: PostgreSQL database, agent runtime (LLM provider connections), background workers

## Input Required
- ARCH.md (component topology, technology stack)
- SECURITY-ARCH.md (network isolation, secrets management, compliance)
- QUALITY.md (performance NFRs, availability targets)
- FEATURE-CATALOG (module-aware sizing — AI modules need different resources than CRUD)

## Output: INFRA-DESIGN.md

### Required Sections

1. **Environment Strategy** — Table: Environment | Purpose | Data | Access | Infra Tier
   - local: Developer machine, SQLite/Docker Compose, all devs
   - dev: Integration testing, seeded test data, engineering team
   - staging: Pre-prod validation, anonymized prod data, QA + stakeholders
   - production: Live system, real data, end users + agents

2. **Network Architecture**
   - VPC/subnet layout (public/private/isolated)
   - Security groups per component
   - Load balancer configuration
   - DNS and certificate management

3. **Compute & Container Strategy** — Per component: Container Image | CPU | Memory | Min/Max Replicas | Scaling Trigger | Health Check
   - Module-aware sizing: AI agent containers (higher memory for LLM context) vs CRUD containers

4. **CI/CD Pipeline** — Numbered stages with pass/fail criteria:
   1. Lint + Type Check — fail if any error
   2. Unit Tests — fail if coverage < threshold
   3. Build Containers — fail if image > size limit
   4. Integration Tests — fail if any failure
   5. Security Scan — fail if Critical/High CVE
   6. Staging Deploy — manual gate
   7. Smoke Tests — fail if health check fails
   8. Production Deploy — canary then full rollout
   9. Post-deploy Verification — rollback if error rate > threshold

5. **Database Deployment**
   - Migration tool and strategy
   - Zero-downtime migration pattern
   - Backup schedule and retention
   - Point-in-time recovery configuration

6. **Infrastructure as Code**
   - IaC tool (Terraform/Pulumi/CloudFormation)
   - Module structure
   - State management
   - Drift detection

7. **Cost Estimates** — Table per environment: Component | Resource | Monthly Cost | Notes. Include: compute, database, LLM API costs (per-provider), storage, networking, monitoring

8. **Observability**
   - Metrics: What to collect (system + business + AI-specific: token usage, latency, cost per call)
   - Logging: Structured JSON, log levels per component, retention
   - Tracing: Distributed trace correlation across agent chains (OpenTelemetry)
   - Dashboards: What dashboards to build (system health, agent performance, cost burn-down)
   - Alerting: Alert rules, severity, escalation chain, on-call integration

9. **Disaster Recovery**
   - RPO/RTO per service tier
   - Backup strategy (database, configuration, agent prompts)
   - Cross-region replication (if applicable)
   - Restore procedure (step-by-step)
   - DR test schedule (quarterly)

10. **Capacity Planning**
    - Current baseline per component
    - Growth projections (3/6/12 month)
    - Scaling triggers and thresholds
    - LLM token budget forecasting per phase

11. **Rollback Procedures** — Per component: Rollback Trigger | Steps | Expected Duration | Data Impact

### Quality Criteria
- Every component from ARCH.md has infrastructure defined
- Cost estimates include LLM API costs (using provider pricing from sdk/llm/)
- Observability includes AI-specific telemetry (not just standard APM)
- DR test schedule is mandatory — not optional

### Anti-Patterns to Avoid
- Missing AI-specific resource sizing (LLM containers need more memory than CRUD)
- Cost estimates that omit LLM API spend (often the largest line item)
- Observability without agent-chain tracing
- No rollback procedure defined
- ESCALATE if: no budget for multi-region, compliance requires specific cloud region, estimated cost > 2x budget
