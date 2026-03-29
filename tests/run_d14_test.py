"""Live test of D14-claude-md-generator — CLAUDE.md Project Configuration."""

import asyncio
import re
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from dotenv import load_dotenv
load_dotenv()

from sdk.base_agent import BaseAgent
from pathlib import Path


async def main():
    agent = BaseAgent(agent_dir=Path("agents/design/D14-claude-md-generator"))
    print(f"Agent: {agent.agent_id}")
    print(f"Provider: {agent.provider_name} | Tier: {agent._model_tier.value} | Model: {agent.model}")
    print()

    result = await agent.invoke(
        input_data={
            "project_name": "FleetOps",
            "project_purpose": "AI-powered fleet management platform for logistics companies — real-time tracking, route optimization, compliance monitoring, and predictive maintenance",
            "architecture_summary": {
                "languages": ["Python 3.12", "TypeScript 5.x"],
                "frameworks": ["aiohttp", "Streamlit", "FastMCP"],
                "databases": ["PostgreSQL 16"],
                "services": [
                    "fleet_service",
                    "route_service",
                    "compliance_service",
                    "delivery_service",
                    "driver_service",
                    "maintenance_service",
                    "analytics_service",
                    "notification_service",
                ],
                "interfaces": ["MCP", "REST", "Dashboard"],
            },
            "repo_structure": {
                "mcp-servers/": "MCP server implementations (fleet, route, compliance)",
                "api/": "REST API routes and middleware",
                "api/routes/": "Route handlers per resource",
                "api/middleware/": "Auth, logging, error handling middleware",
                "dashboard/": "Streamlit dashboard pages",
                "dashboard/pages/": "Individual dashboard views",
                "dashboard/components/": "Reusable UI components",
                "services/": "Shared service layer — ALL business logic lives here",
                "sdk/": "SDK and LLM provider abstractions",
                "sdk/llm/": "LLM provider layer (Anthropic, OpenAI, Ollama)",
                "sdk/llm/providers/": "Individual provider implementations",
                "agents/": "Agent manifests and prompts",
                "agents/govern/": "GOVERN phase agents (G1-G5)",
                "agents/design/": "DESIGN phase agents (D0-D21)",
                "schemas/": "JSON schemas and contracts",
                "schemas/contracts/": "API and MCP contract schemas",
                "migrations/": "PostgreSQL migration files (UP + DOWN)",
                "tests/": "Test suites",
                "tests/unit/": "Unit tests per service",
                "tests/integration/": "Integration tests",
                "tests/golden/": "Golden file tests for agents",
            },
            "entity_conventions": {
                "table_naming": "snake_case plural",
                "pk_type": "UUID v7",
                "column_naming": "snake_case",
                "timestamps": "created_at, updated_at on every table",
                "sample_tables": [
                    "vehicles",
                    "drivers",
                    "routes",
                    "deliveries",
                    "hos_records",
                    "maintenance_logs",
                    "fleet_events",
                    "driver_scores",
                ],
            },
            "api_patterns": {
                "base_url": "/api/v1",
                "envelope": {
                    "data": "...",
                    "meta": {"page": 1, "per_page": 25, "total": 100},
                    "errors": [],
                },
                "auth": "Bearer JWT",
                "sample_endpoints": [
                    "GET /api/v1/vehicles",
                    "GET /api/v1/vehicles/:id",
                    "POST /api/v1/vehicles",
                    "GET /api/v1/routes",
                    "POST /api/v1/routes",
                    "PATCH /api/v1/routes/:id",
                    "GET /api/v1/drivers",
                    "GET /api/v1/hos-violations",
                    "GET /api/v1/deliveries",
                    "POST /api/v1/deliveries",
                    "GET /api/v1/maintenance/predictions",
                ],
            },
            "roadmap_context": {
                "current_milestone": "M1 — Core Fleet Tracking",
                "timeline": "M1 (Weeks 1-4), M2 (Weeks 5-8), M3 (Weeks 9-12)",
            },
        },
        project_id="fleetops-014",
    )

    print(f"Cost:     ${result['cost_usd']:.4f}")
    print(f"Tokens:   {result['input_tokens']} in / {result['output_tokens']} out")
    print(f"Duration: {result['duration_ms']}ms ({result['duration_ms']/1000:.1f}s)")
    print(f"Provider: {result['provider']} | Tier: {result['model_tier']}")
    print()

    output = result["output"]

    # == Line count check =====================================================
    line_count = len(output.strip().split("\n"))
    print(f"Total lines: {line_count}")
    if line_count <= 500:
        print(f"  PASS: Under 500-line limit")
    else:
        print(f"  FAIL: Exceeds 500-line limit ({line_count} lines)")

    # == All 10 sections present ==============================================
    sections = [
        "Project",
        "Architecture",
        "Repo Structure",
        "Language Rules",
        "Implementation Patterns",
        "Key Reference Tables",
        "Key Commands",
        "Pipelines",
        "Cost",
        "Forbidden Patterns",
    ]
    found_sections = []
    missing_sections = []
    for s in sections:
        if s.lower() in output.lower():
            found_sections.append(s)
        else:
            missing_sections.append(s)
    print(f"Sections: {len(found_sections)}/{len(sections)}")
    if missing_sections:
        print(f"  MISSING: {missing_sections}")
    else:
        print(f"  PASS: All 10 sections present")

    # == Repo structure tree found ============================================
    tree_markers = ["mcp-servers/", "api/", "dashboard/", "services/", "sdk/",
                    "agents/", "schemas/", "migrations/", "tests/"]
    tree_found = [t for t in tree_markers if t in output]
    tree_missing = [t for t in tree_markers if t not in output]
    print(f"Repo structure directories: {len(tree_found)}/{len(tree_markers)}")
    if tree_missing:
        print(f"  MISSING: {tree_missing}")
    else:
        print(f"  PASS: All repo structure directories present")

    # == Language rules present ================================================
    lang_tools = ["mypy", "ruff", "pytest"]
    lang_found = [t for t in lang_tools if t.lower() in output.lower()]
    lang_missing = [t for t in lang_tools if t.lower() not in output.lower()]
    print(f"Language tools referenced: {len(lang_found)}/{len(lang_tools)}  {lang_found}")
    if lang_missing:
        print(f"  MISSING: {lang_missing}")
    else:
        print(f"  PASS: All language tools (mypy, ruff, pytest) present")

    # == All 7 implementation patterns mentioned ==============================
    patterns = [
        "Shared Service",
        "MCP Tool",
        "API Route",
        "Dashboard View",
        "Agent",
        "Migration",
        "LLM Provider",
    ]
    pat_found = [p for p in patterns if p.lower() in output.lower()]
    pat_missing = [p for p in patterns if p.lower() not in output.lower()]
    print(f"Implementation patterns: {len(pat_found)}/{len(patterns)}")
    if pat_missing:
        print(f"  MISSING: {pat_missing}")
    else:
        print(f"  PASS: All 7 implementation patterns mentioned")

    # == Shared Service pattern is FIRST pattern ==============================
    # Find positions of each pattern heading in the output
    shared_pos = output.lower().find("shared service")
    mcp_tool_pos = output.lower().find("mcp tool")
    api_route_pos = output.lower().find("api route")
    dashboard_pos = output.lower().find("dashboard view")
    if shared_pos != -1 and mcp_tool_pos != -1 and api_route_pos != -1:
        if shared_pos < mcp_tool_pos and shared_pos < api_route_pos and shared_pos < dashboard_pos:
            print(f"  PASS: Shared Service pattern appears FIRST (pos {shared_pos})")
        else:
            print(f"  FAIL: Shared Service pattern is NOT first "
                  f"(shared={shared_pos}, mcp={mcp_tool_pos}, api={api_route_pos})")
    else:
        print(f"  WARNING: Could not locate pattern positions for ordering check")

    # == Forbidden patterns found =============================================
    forbidden_keywords = [
        "business logic",
        "hardcoded secret",
        "print()",
        "blocking",
        "structlog",
    ]
    fb_found = [k for k in forbidden_keywords if k.lower() in output.lower()]
    fb_missing = [k for k in forbidden_keywords if k.lower() not in output.lower()]
    print(f"Forbidden pattern keywords: {len(fb_found)}/{len(forbidden_keywords)}")
    if fb_missing:
        print(f"  MISSING: {fb_missing}")
    else:
        print(f"  PASS: All forbidden pattern keywords present")

    # == Key commands found ====================================================
    command_keywords = ["pip install", "pytest", "streamlit", "python"]
    cmd_found = [c for c in command_keywords if c.lower() in output.lower()]
    cmd_missing = [c for c in command_keywords if c.lower() not in output.lower()]
    print(f"Key command keywords: {len(cmd_found)}/{len(command_keywords)}")
    if cmd_missing:
        print(f"  MISSING: {cmd_missing}")
    else:
        print(f"  PASS: All key command keywords found")

    # == Entity conventions referenced =========================================
    entity_tables = ["vehicles", "drivers", "routes", "deliveries", "hos_records"]
    ent_found = [e for e in entity_tables if e in output]
    ent_missing = [e for e in entity_tables if e not in output]
    print(f"Entity tables referenced: {len(ent_found)}/{len(entity_tables)}")
    if ent_missing:
        print(f"  MISSING: {ent_missing}")
    else:
        print(f"  PASS: All entity tables referenced")

    # == API patterns referenced ===============================================
    api_refs = ["/api/v1/vehicles", "/api/v1/routes"]
    api_found = [a for a in api_refs if a in output]
    api_missing = [a for a in api_refs if a not in output]
    print(f"API patterns referenced: {len(api_found)}/{len(api_refs)}")
    if api_missing:
        print(f"  MISSING: {api_missing}")
    else:
        print(f"  PASS: All API patterns referenced")

    # == Pipeline / workflow paths =============================================
    has_mcp_path = "mcp" in output.lower() and "service" in output.lower() and "database" in output.lower()
    has_dash_path = "dashboard" in output.lower() and "rest" in output.lower()
    print(f"MCP pipeline path: {'PASS' if has_mcp_path else 'FAIL'}")
    print(f"Dashboard pipeline path: {'PASS' if has_dash_path else 'FAIL'}")

    # == services/ directory as business logic home ============================
    services_mentions = len(re.findall(r"services/", output))
    print(f"services/ directory mentions: {services_mentions}")
    if services_mentions >= 3:
        print(f"  PASS: services/ referenced adequately")
    else:
        print(f"  WARNING: services/ referenced only {services_mentions} times")

    # == LLMProvider / sdk.llm reference ======================================
    llm_ref = "llmprovider" in output.lower() or "sdk.llm" in output.lower() or "sdk/llm" in output.lower()
    print(f"LLM Provider abstraction referenced: {'PASS' if llm_ref else 'FAIL'}")

    # == UUID reference (from entity conventions) ==============================
    uuid_ref = "uuid" in output.lower()
    print(f"UUID PK type referenced: {'PASS' if uuid_ref else 'FAIL'}")

    # == snake_case convention referenced =====================================
    snake_ref = "snake_case" in output.lower()
    print(f"snake_case convention referenced: {'PASS' if snake_ref else 'FAIL'}")

    print()
    print("=== FIRST 3000 CHARS ===")
    print(output[:3000])


if __name__ == "__main__":
    asyncio.run(main())
