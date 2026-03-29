"""Live test of D6-security-architect."""

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
    agent = BaseAgent(agent_dir=Path("agents/design/D6-security-architect"))
    print(f"Agent: {agent.agent_id}")
    print(f"Provider: {agent.provider_name} | Tier: {agent._model_tier.value} | Model: {agent.model}")
    print()

    result = await agent.invoke(
        input_data={
            "project_name": "FleetOps Dashboard",
            "personas": [
                {"name": "Maria Santos", "role": "Lead Dispatcher", "primary_interface": "dashboard"},
                {"name": "James Park", "role": "Operations Manager", "primary_interface": "dashboard"},
                {"name": "Sarah Chen", "role": "IT Director", "primary_interface": "mcp"},
                {"name": "Alex Rivera", "role": "DevOps Engineer", "primary_interface": "mcp"},
                {"name": "David Kim", "role": "VP Operations", "primary_interface": "dashboard"},
            ],
            "components": [
                {"name": "MCP Fleet Server", "technology": "Python MCP SDK", "port": 3100},
                {"name": "REST API", "technology": "aiohttp", "port": 8080},
                {"name": "Dashboard", "technology": "Streamlit", "port": 8501},
                {"name": "PostgreSQL", "technology": "PostgreSQL 15", "port": 5432},
                {"name": "Agent Runtime", "technology": "Python + LLMProvider", "port": None},
                {"name": "Samsara Integration", "technology": "REST client", "port": None},
            ],
            "data_entities": [
                {"name": "Vehicle", "source": "AS/400 migration", "sensitivity": "internal"},
                {"name": "Driver", "source": "AS/400 migration", "sensitivity": "confidential"},
                {"name": "Route", "source": "Application", "sensitivity": "internal"},
                {"name": "GPSPosition", "source": "Samsara API", "sensitivity": "internal"},
                {"name": "Delivery", "source": "Application", "sensitivity": "internal"},
                {"name": "HOSRecord", "source": "AS/400 migration", "sensitivity": "confidential"},
                {"name": "FuelTransaction", "source": "Fuel card CSV", "sensitivity": "confidential"},
                {"name": "CostRecord", "source": "Computed", "sensitivity": "confidential"},
                {"name": "AuditEvent", "source": "System", "sensitivity": "confidential"},
                {"name": "APIKey", "source": "Configuration", "sensitivity": "restricted"},
                {"name": "JWTSigningKey", "source": "Configuration", "sensitivity": "restricted"},
            ],
            "security_nfrs": [
                {"id": "Q-017", "rule": "MCP API key required on every tool call"},
                {"id": "Q-018", "rule": "REST JWT validation on every request"},
                {"id": "Q-019", "rule": "MCP tool input validated against JSON Schema"},
                {"id": "Q-020", "rule": "Dashboard CSRF protection on all forms"},
                {"id": "Q-021", "rule": "PII detection on all agent outputs"},
                {"id": "Q-022", "rule": "No secrets in logs or outputs"},
            ],
            "interfaces": ["mcp", "rest", "dashboard"],
            "regulatory": ["SOC2", "GDPR", "DOT_HOS", "EU_AI_ACT"],
            "agent_count": 48,
        },
        project_id="fleetops-001",
    )

    print(f"Cost:     ${result['cost_usd']:.4f}")
    print(f"Tokens:   {result['input_tokens']} in / {result['output_tokens']} out")
    print(f"Duration: {result['duration_ms']}ms ({result['duration_ms']/1000:.1f}s)")
    print(f"Provider: {result['provider']} | Tier: {result['model_tier']}")
    print()

    output = result["output"]

    # Section checks
    sections = ["Data Classification", "Authentication", "Authorization", "Agent Permission",
                "Secrets", "Threat Model", "Attack Surface", "OWASP",
                "Data Governance", "Supply Chain", "Compliance"]
    found = [s for s in sections if s.lower() in output.lower()]
    missing = [s for s in sections if s.lower() not in output.lower()]
    print(f"Sections: {len(found)}/{len(sections)}")
    if missing:
        print(f"  Missing: {missing}")

    # STRIDE check
    stride_refs = len(re.findall(r"Spoofing|Tampering|Repudiation|Information|Denial|Elevation", output))
    print(f"STRIDE references: {stride_refs}")

    # OWASP check
    owasp_refs = set(re.findall(r"A0[1-9]|A10", output))
    print(f"OWASP categories: {len(owasp_refs)}/10 (A01-A10)")

    # Classification check
    classifications = set(re.findall(r"Public|Internal|Confidential|Restricted", output))
    print(f"Data classifications used: {classifications}")

    # Auth types
    has_mcp_auth = "API key" in output or "api key" in output.lower()
    has_jwt = "JWT" in output
    has_session = "session" in output.lower()
    print(f"MCP auth (API key): {has_mcp_auth}")
    print(f"REST auth (JWT): {has_jwt}")
    print(f"Dashboard auth (session): {has_session}")

    # Agent permissions
    has_autonomy_tiers = "T0" in output or "T1" in output or "T2" in output or "T3" in output
    has_least_privilege = "least" in output.lower() and "privilege" in output.lower()
    print(f"Autonomy tiers: {has_autonomy_tiers}")
    print(f"Least privilege: {has_least_privilege}")

    # AI-specific security
    has_ollama_rule = "Ollama" in output or "local" in output.lower() and "confidential" in output.lower()
    print(f"Confidential data -> local LLM rule: {has_ollama_rule}")

    print()
    print("=== FIRST 2000 CHARS ===")
    print(output[:2000])


if __name__ == "__main__":
    asyncio.run(main())
