"""Live test of B3-security-auditor — deep security analysis."""

import asyncio
import json
import re
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from dotenv import load_dotenv
load_dotenv()

from sdk.base_agent import BaseAgent
from pathlib import Path

# Code with multiple security issues for the auditor to find
VULNERABLE_CODE = '''
"""User management API handler."""
import os
import hashlib
from aiohttp import web
import aiohttp

SECRET_KEY = "my-app-secret-key-2024"  # Hardcoded secret
DB_URL = "postgresql://admin:password123@prod-db:5432/fleet"  # Hardcoded credentials

async def login(request):
    body = await request.json()
    username = body["username"]
    password = body["password"]

    # SQL injection vulnerability
    row = await request.app["db"].fetchrow(
        f"SELECT * FROM users WHERE username = '{username}' AND password_hash = '{hashlib.md5(password.encode()).hexdigest()}'"
    )

    if row:
        import jwt
        token = jwt.encode({"user_id": row["id"], "role": row["role"]}, SECRET_KEY, algorithm="HS256")
        return web.json_response({"token": token, "password": password})  # PII leak: returning password

    return web.json_response({"error": "Invalid credentials"}, status=401)

async def get_user_profile(request):
    user_id = request.match_info["user_id"]
    # No auth check — anyone can access any profile (IDOR)
    row = await request.app["db"].fetchrow(
        f"SELECT * FROM users WHERE id = {user_id}"  # SQL injection
    )
    if not row:
        return web.json_response({"error": f"User {user_id} not found", "query": f"SELECT * FROM users WHERE id = {user_id}"}, status=404)  # Query in error response

    return web.json_response(dict(row))  # Returns ALL fields including password_hash, ssn

async def fetch_avatar(request):
    url = request.query["url"]  # SSRF: unvalidated URL
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:  # Fetches any URL including internal
            data = await resp.read()
    return web.Response(body=data)

async def admin_delete(request):
    # No role check — any user can delete
    user_id = request.match_info["user_id"]
    await request.app["db"].execute(f"DELETE FROM users WHERE id = {user_id}")
    return web.json_response({"deleted": user_id})
'''


async def main():
    agent = BaseAgent(agent_dir=Path("agents/build/B3-security-auditor"))
    print(f"Agent: {agent.agent_id}")
    print(f"Provider: {agent.provider_name} | Tier: {agent._model_tier.value} | Model: {agent.model}")
    print()

    result = await agent.invoke(
        input_data={
            "file_path": "api/routes/users.py",
            "code_content": VULNERABLE_CODE,
            "language": "python",
            "audit_scope": ["all"],
            "security_policy": {
                "data_classification": [
                    {"entity": "password", "level": "restricted"},
                    {"entity": "ssn", "level": "restricted"},
                    {"entity": "email", "level": "confidential"},
                    {"entity": "username", "level": "internal"},
                ],
                "auth_requirements": [
                    "All endpoints require JWT or API key",
                    "Admin endpoints require role=admin",
                ],
                "rbac_roles": ["admin", "operator", "viewer"],
            },
            "dependencies": [
                {"name": "aiohttp", "version": "3.9.0"},
                {"name": "pyjwt", "version": "2.8.0"},
            ],
        },
        project_id="test-001",
    )

    print(f"Cost:     ${result['cost_usd']:.4f}")
    print(f"Tokens:   {result['input_tokens']} in / {result['output_tokens']} out")
    print(f"Duration: {result['duration_ms']}ms ({result['duration_ms']/1000:.1f}s)")
    print(f"Provider: {result['provider']} | Tier: {result['model_tier']}")
    print()

    output = result["output"]

    try:
        if "```json" in output:
            json_str = output.split("```json")[1].split("```")[0].strip()
        elif output.strip().startswith("{"):
            json_str = output.strip()
        else:
            json_str = None

        if json_str:
            audit = json.loads(json_str)

            summary = audit.get("audit_summary", {})
            print(f"Risk Rating: {summary.get('risk_rating', 'unknown')}")
            print(f"OWASP triggered: {summary.get('owasp_categories_triggered', [])}")
            print(f"CWEs found: {summary.get('cwe_ids_found', [])}")
            print(f"STRIDE threats: {summary.get('stride_threats', [])}")

            findings = audit.get("findings", [])
            print(f"\nFindings: {len(findings)} total")
            by_sev = {}
            for f in findings:
                s = f.get("severity", "?")
                by_sev[s] = by_sev.get(s, 0) + 1
            for s in ["critical", "high", "medium", "low"]:
                if s in by_sev:
                    print(f"  {s}: {by_sev[s]}")

            # Check key vulnerabilities found
            all_text = " ".join(
                f.get("title", "") + " " + f.get("description", "") + " " + f.get("owasp", "") + " " + f.get("cwe", "")
                for f in findings
            ).lower()

            checks = {
                "SQL Injection (A03/CWE-89)": "sql injection" in all_text or "cwe-89" in all_text,
                "Hardcoded secrets (A02/CWE-798)": "hardcoded" in all_text or "cwe-798" in all_text,
                "Broken access control (A01)": "access control" in all_text or "idor" in all_text or "a01" in all_text,
                "PII in response": "pii" in all_text or "password" in all_text and "response" in all_text,
                "SSRF (A10)": "ssrf" in all_text or "a10" in all_text,
                "Weak crypto (MD5)": "md5" in all_text or "weak" in all_text,
                "Missing auth check": "auth" in all_text and ("missing" in all_text or "no" in all_text),
            }

            print("\nKey vulnerabilities detected:")
            for check, found in checks.items():
                print(f"  {'FOUND' if found else 'MISSED'}: {check}")

            # OWASP coverage
            owasp = audit.get("owasp_coverage", {})
            if owasp:
                print(f"\nOWASP categories assessed: {len(owasp)}/10")

            # Data flow
            dfa = audit.get("data_flow_analysis", {})
            if dfa:
                print(f"Data flow inputs: {len(dfa.get('inputs', []))}")
                print(f"PII exposure risk: {dfa.get('pii_exposure_risk', 'unknown')}")

            # Exploit scenarios
            exploits = sum(1 for f in findings if f.get("exploit_scenario"))
            print(f"Findings with exploit scenarios: {exploits}/{len(findings)}")

        else:
            print("WARNING: Could not extract JSON")
    except json.JSONDecodeError as e:
        print(f"WARNING: JSON parse error: {e}")

    print()
    print("=== FIRST 2500 CHARS ===")
    print(output[:2500])


if __name__ == "__main__":
    asyncio.run(main())
