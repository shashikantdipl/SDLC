"""Lifecycle — Complete app-building journey with HITL markers.

Shows exactly where the system works autonomously and where YOU need to act.
"""
import streamlit as st
from pathlib import Path
from datetime import datetime
import sys
import json

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

st.set_page_config(page_title="Lifecycle — End-to-End", layout="wide")
st.title("🎯 App Lifecycle — End-to-End Journey")

st.markdown("""
> This page shows the **complete journey** from brief to deployed app.
> 🤖 = Automated (no human needed) | 👤 = **HITL — You need to act** | ⏳ = Waiting
""")

# --- Lifecycle State ---
if "lifecycle" not in st.session_state:
    st.session_state.lifecycle = {
        "phase": "not_started",  # not_started, docs, code, test, deploy, live
        "docs_status": "pending",
        "code_status": "pending",
        "test_status": "pending",
        "deploy_status": "pending",
        "hitl_pending": [],
        "cost_total": 0,
        "started_at": None,
    }

lc = st.session_state.lifecycle

# --- Phase Indicator ---
st.markdown("---")
phases = [
    ("📝 Docs", "docs", "$3", "35 min"),
    ("💻 Code", "code", "$50-150", "4-8 hrs"),
    ("🧪 Test", "test", "$20-50", "2-4 hrs"),
    ("🚀 Deploy", "deploy", "$10-20", "1-2 hrs"),
]

cols = st.columns(len(phases))
for i, (name, key, cost, time) in enumerate(phases):
    with cols[i]:
        status = lc.get(f"{key}_status", "pending")
        icon = {"pending": "⚪", "running": "🔄", "hitl_needed": "👤", "completed": "✅", "failed": "❌"}.get(status, "⚪")
        st.markdown(f"### {icon} {name}")
        st.caption(f"{cost} | {time}")

# =====================================================================
# PHASE 1: DOCUMENT GENERATION
# =====================================================================
st.markdown("---")
st.header("📝 Phase 1: Document Generation")
st.markdown("**22 agents generate 24 specification documents from your brief.**")

with st.expander("📋 All 22 Pipeline Steps (click to expand)", expanded=False):
    steps_data = [
        (0, "D0-brd-generator", "BRD", "🤖", "Business requirements from your brief"),
        (1, "D1-roadmap-generator", "ROADMAP", "🤖", "Delivery timeline + milestones"),
        (2, "D2-prd-generator", "PRD", "🤖", "Personas, journeys, capabilities"),
        (3, "D3-architecture-drafter", "ARCH", "🤖", "System architecture + tech stack"),
        (4, "D4-feature-extractor", "FEATURES", "🤖", "18-field JSON feature catalog"),
        (5, "D5-quality-spec-generator", "QUALITY", "🤖", "NFRs + SLI/SLO targets"),
        (6, "D6-security-architect", "SECURITY", "🤖", "Auth, RBAC, threat model"),
        (7, "D7-interaction-map-gen", "INTERACTION-MAP", "🤖", "Shared data shapes (KEY doc)"),
        (8, "D8-mcp-tool-spec", "MCP-TOOL-SPEC", "🤖", "MCP tool definitions ‖ parallel"),
        (9, "D9-design-spec", "DESIGN-SPEC", "🤖", "Dashboard wireframes ‖ parallel"),
        (10, "D10-data-model", "DATA-MODEL", "🤖", "SQL DDL — copy-paste ready"),
        (11, "D11-api-contracts", "API-CONTRACTS", "🤖", "REST endpoints + schemas"),
        (12, "D12-user-stories", "USER-STORIES", "👤", "HITL: Review stories before backlog"),
        (13, "D13-backlog", "BACKLOG", "🤖", "Sprint-ready developer tasks"),
        (14, "D14-claude-md", "CLAUDE.md", "🤖", "Coding rules for the app"),
        (15, "D15-enforcement", "ENFORCEMENT", "🤖", ".claude/ rules + skills"),
        (16, "D16-infra-design", "INFRA", "🤖", "Environments + CI/CD + DR"),
        (17, "D17-migration", "MIGRATION", "🤖", "Data migration runbook ‖ parallel"),
        (18, "D18-testing", "TESTING", "🤖", "Test strategy + LLM eval ‖ parallel"),
        (19, "D19-fault-tolerance", "FAULT-TOLERANCE", "🤖", "5-layer failure scenarios"),
        (20, "D20-guardrails", "GUARDRAILS", "🤖", "AI safety guardrails"),
        (21, "D21-compliance", "COMPLIANCE", "🤖", "SOC2/GDPR/EU AI Act mapping"),
    ]

    for step, agent, doc, hitl, desc in steps_data:
        st.markdown(f"{hitl} **Step {step}** — `{doc}` — {desc}")

st.info("""
**👤 HITL Point (Step 12):** After USER-STORIES are generated, review them before BACKLOG is created.
This is your chance to adjust scope, priorities, or personas before sprint planning begins.

**All other steps are fully automated** — no human intervention needed.
""")

# Trigger button
col1, col2 = st.columns([2, 1])
with col1:
    brief_input = st.text_area("Enter your project brief:", height=150,
        placeholder="Build a fleet management dashboard for a logistics company with 200 trucks...")
with col2:
    project_name = st.text_input("Project name:", value="MyApp")
    provider = st.selectbox("LLM Provider:", ["anthropic", "openai", "ollama"])
    cost_est = {"anthropic": "$2.93", "openai": "$1.76", "ollama": "$0.00"}.get(provider, "?")
    st.metric("Est. Cost", cost_est)

if st.button("🚀 Generate All 24 Documents", type="primary", use_container_width=True):
    if len(brief_input.strip()) < 20:
        st.error("Brief must be at least 20 characters.")
    else:
        st.success(f"✅ Run this command in your terminal:")
        st.code(f'PYTHONPATH=. python sdlc_run.py --name "{project_name}" --brief "{brief_input[:200]}" --provider {provider}', language="bash")
        st.warning("👆 Copy and run this command. The pipeline will generate all 24 documents automatically.")

# =====================================================================
# PHASE 2: CODE GENERATION
# =====================================================================
st.markdown("---")
st.header("💻 Phase 2: Code Generation")
st.markdown("**Claude Code reads your 24 docs and writes the complete app.**")

st.warning("""
**👤 HITL Required:** You need to:
1. Open Claude Code (terminal or VS Code extension)
2. Give it the prompt below
3. Review the generated code
4. Approve or request changes
""")

with st.expander("📋 Claude Code Prompt (copy this)", expanded=True):
    claude_prompt = f"""Read ALL files in output/{project_name}_*/  — these are 24 specification documents for the app.

Key documents to read first:
1. 14-CLAUDE.md — This has ALL coding rules. Follow them exactly.
2. 03-ARCH.md — This has the system architecture.
3. 10-DATA-MODEL.md — This has the SQL DDL. Create migrations from this.
4. 11-API-CONTRACTS.md — This has every REST endpoint. Implement them all.
5. 13-BACKLOG.md — This has sprint-by-sprint tasks. Follow this order.

Build the app in this order:
Sprint 0: Create project scaffold (pyproject.toml, directory structure)
Sprint 0: Create database migrations from 10-DATA-MODEL.md
Sprint 1: Implement shared services from 03-ARCH.md service layer
Sprint 2: Implement REST API endpoints from 11-API-CONTRACTS.md
Sprint 3: Implement MCP tools from 08-MCP-TOOL-SPEC.md
Sprint 4: Implement dashboard from 09-DESIGN-SPEC.md
Sprint 5: Write tests following 18-TESTING.md strategy
Sprint 6: Set up CI/CD from 16-INFRA-DESIGN.md

Rules from 14-CLAUDE.md:
- ALL business logic in services/ (shared service layer)
- MCP handlers and REST handlers are THIN WRAPPERS calling services
- Dashboard consumes REST API only (never import services directly)
- Use sdk/llm/LLMProvider for any LLM calls (never import anthropic/openai directly)
- pytest for testing, testcontainers for DB tests
- structlog for logging (never print())

After each sprint, run: PYTHONPATH=. python tests/validate_all.py"""

    st.code(claude_prompt, language="text")

st.markdown("### 👤 HITL Points During Code Generation:")
hitl_code = [
    ("After Sprint 0", "Review project structure and migrations match DATA-MODEL"),
    ("After Sprint 1", "Review shared services match ARCH service layer"),
    ("After Sprint 2", "Review API endpoints match API-CONTRACTS — run pytest"),
    ("After Sprint 4", "Review dashboard matches DESIGN-SPEC wireframes"),
    ("After Sprint 5", "Review test coverage meets QUALITY thresholds"),
]
for when, what in hitl_code:
    st.markdown(f"👤 **{when}:** {what}")

# =====================================================================
# PHASE 3: TESTING
# =====================================================================
st.markdown("---")
st.header("🧪 Phase 3: Testing")
st.markdown("**Claude runs all tests. BUILD agents review code quality.**")

st.markdown("### Automated Test Stages:")
test_stages = [
    ("🤖 Stage 1", "Lint + Type Check", "ruff check . && mypy --strict .", "Auto"),
    ("🤖 Stage 2", "Unit Tests", "PYTHONPATH=. pytest tests/services/ -v", "Auto"),
    ("🤖 Stage 3", "API Tests", "PYTHONPATH=. pytest tests/api/ -v", "Auto"),
    ("🤖 Stage 4", "MCP Tests", "PYTHONPATH=. pytest tests/mcp/ -v", "Auto"),
    ("🤖 Stage 5", "Integration Tests", "PYTHONPATH=. pytest tests/integration/ -v", "Auto"),
    ("👤 Stage 6", "Review Test Results", "You review: all tests pass? Coverage met?", "HITL"),
]

for icon, name, cmd, mode in test_stages:
    col1, col2, col3 = st.columns([2, 4, 1])
    with col1:
        st.markdown(f"{icon} **{name}**")
    with col2:
        st.code(cmd, language="bash")
    with col3:
        st.markdown(f"`{mode}`")

st.markdown("### BUILD Agent Reviews (automated, Claude runs these):")
build_reviews = [
    ("B1", "Code Reviewer", "$0.07/file", "Quality, patterns, bugs"),
    ("B2", "Test Writer", "$0.13/file", "Generates missing tests"),
    ("B3", "Security Auditor", "$0.13/file", "OWASP, STRIDE, CWE scan"),
    ("B4", "Performance Analyzer", "$0.02/file", "N+1 queries, bottlenecks"),
    ("B7", "Dependency Auditor", "$0.02/run", "CVE scan, license check"),
    ("B8", "Build Validator", "$0.01/run", "8-gate CI validation"),
]

for agent, name, cost, desc in build_reviews:
    st.markdown(f"🤖 **{agent} {name}** ({cost}) — {desc}")

st.info("**👤 HITL:** After all tests pass and BUILD agents approve, you give final sign-off to proceed to deploy.")

# =====================================================================
# PHASE 4: DEPLOYMENT
# =====================================================================
st.markdown("---")
st.header("🚀 Phase 4: Deployment")
st.markdown("**This is where YOU are most needed.**")

st.error("""
**👤 HITL Required — All of these need your action:**
""")

deploy_steps = [
    ("👤", "Choose hosting", "AWS / Vercel / Railway / Fly.io / Self-hosted", "You decide based on budget + scale"),
    ("🤖", "Claude writes Terraform/Docker", "IaC from 16-INFRA-DESIGN.md", "Claude generates, you review"),
    ("👤", "Set up secrets", "API keys, DB credentials, env vars", "You provide production secrets"),
    ("👤", "Configure DNS", "Domain name → load balancer", "You own the domain"),
    ("🤖", "P1 Deploy Checklist", "10-category pre-deploy validation", "Agent validates readiness"),
    ("👤", "Click deploy", "Push to production", "You make the final call"),
    ("🤖", "P3 Release Notes", "Auto-generated from commits", "Agent generates"),
    ("👤", "Verify production", "Smoke test the live app", "You confirm it works"),
]

for icon, step, detail, note in deploy_steps:
    col1, col2, col3 = st.columns([3, 4, 3])
    with col1:
        st.markdown(f"{icon} **{step}**")
    with col2:
        st.markdown(detail)
    with col3:
        st.caption(note)

# =====================================================================
# PHASE 5: OPERATIONS (Post-Deploy)
# =====================================================================
st.markdown("---")
st.header("🔧 Phase 5: Operations (Post-Deploy)")

ops_items = [
    ("🤖", "O1 Incident Triage", "Auto-classifies SEV1-SEV4, suggests root cause"),
    ("🤖", "O4 SLA Monitor", "Tracks SLO compliance, predicts breaches"),
    ("🤖", "O5 Alert Manager", "Deduplicates, correlates, routes alerts"),
    ("👤", "On-call response", "YOU respond to P0/P1 incidents that agents escalate"),
    ("👤", "Capacity decisions", "YOU decide when to scale up/down based on O4 recommendations"),
    ("🤖", "OV-* Oversight", "10 agents continuously audit quality, security, compliance"),
]

for icon, item, desc in ops_items:
    st.markdown(f"{icon} **{item}** — {desc}")

# =====================================================================
# COMPLETE HITL SUMMARY
# =====================================================================
st.markdown("---")
st.header("📋 Complete HITL Summary — Where You Act")

st.markdown("### All 👤 Human-In-The-Loop Points:")

hitl_all = [
    ("Phase 1, Step 12", "Review USER-STORIES", "5 min", "Adjust scope before sprint planning", "Medium"),
    ("Phase 2, After each sprint", "Review generated code", "30 min/sprint", "Ensure code matches specs", "High"),
    ("Phase 3, After all tests", "Final sign-off on quality", "15 min", "All tests pass, coverage met", "High"),
    ("Phase 4, Hosting choice", "Choose infrastructure", "30 min", "Budget + scale + compliance", "Critical"),
    ("Phase 4, Secrets setup", "Provide API keys + credentials", "15 min", "Production secrets only you have", "Critical"),
    ("Phase 4, DNS setup", "Point domain to app", "15 min", "You own the domain", "Medium"),
    ("Phase 4, Deploy approval", "Click deploy button", "5 min", "Final go/no-go", "Critical"),
    ("Phase 4, Production verify", "Smoke test live app", "15 min", "Confirm it actually works", "Critical"),
    ("Phase 5, Incident response", "Respond to escalated incidents", "Varies", "P0/P1 need human judgment", "High"),
]

import pandas as pd
hitl_df = pd.DataFrame(hitl_all, columns=["When", "What", "Your Time", "Why", "Importance"])
st.dataframe(hitl_df, use_container_width=True, hide_index=True)

total_human_time = "~3-4 hours across the entire lifecycle"
st.metric("Total Human Time Required", total_human_time)

# =====================================================================
# COST SUMMARY
# =====================================================================
st.markdown("---")
st.header("💰 Total Cost Estimate")

cost_data = [
    ("Phase 1: Documents", "$3", "35 min", "100% automated"),
    ("Phase 2: Code Generation", "$50-150", "4-8 hrs", "Claude Code + your review"),
    ("Phase 3: Testing", "$20-50", "2-4 hrs", "Automated + your sign-off"),
    ("Phase 4: Deployment", "$10-20", "1-2 hrs", "Claude writes IaC, you deploy"),
    ("Phase 5: Operations (monthly)", "$5-10/mo", "Ongoing", "Monitoring agents"),
]

cost_df = pd.DataFrame(cost_data, columns=["Phase", "LLM Cost", "Time", "Your Involvement"])
st.dataframe(cost_df, use_container_width=True, hide_index=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total LLM Cost", "$80-220")
with col2:
    st.metric("Total Your Time", "3-4 hours")
with col3:
    st.metric("Total Calendar Time", "1-2 days")

st.success("""
**Bottom line:** For $80-220 in LLM costs and 3-4 hours of your time,
you get a complete app with 24 specification documents, working code,
tests, CI/CD, and deployment. The traditional way costs $50K-200K and 3-6 months.
""")
