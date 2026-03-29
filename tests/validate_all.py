"""MANDATORY VALIDATION GATE — Run after EVERY change.

This script checks EVERYTHING:
1. All pytest tests (tests/ AND agents/**/tests/)
2. All imports work (no broken module references)
3. All agent manifests load without error
4. All agent prompts exist and are substantial
5. All service files import cleanly
6. All route files import cleanly
7. All MCP server files import cleanly
8. No stale references (old doc numbers, old method names)
9. SDK base_agent works in dry-run mode

Exit code 0 = ALL CLEAR. Any other = BROKEN.

Usage:
    PYTHONPATH=. python tests/validate_all.py
"""

import sys
import os
import importlib
import subprocess
from pathlib import Path

# Ensure project root on path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

ERRORS = []
WARNINGS = []
PASSES = []


def check(name, condition, error_msg=""):
    if condition:
        PASSES.append(name)
    else:
        ERRORS.append(f"FAIL: {name} — {error_msg}")


def warn(name, msg):
    WARNINGS.append(f"WARN: {name} — {msg}")


print("=" * 70)
print("MANDATORY VALIDATION GATE")
print("=" * 70)
print()

# ─────────────────────────────────────────────────────────────────────
# 1. PYTEST — Run ALL tests in BOTH directories
# ─────────────────────────────────────────────────────────────────────
print("[1/9] Running pytest on tests/ AND agents/**/tests/ ...")

# Collect all test directories
test_dirs = ["tests/"]
for agent_test in ROOT.glob("agents/**/tests"):
    if agent_test.is_dir():
        test_dirs.append(str(agent_test.relative_to(ROOT)))

# Build ignore list for live API test scripts
ignores = []
for f in ROOT.glob("tests/run_*.py"):
    ignores.extend(["--ignore", str(f.relative_to(ROOT))])

cmd = [
    sys.executable, "-m", "pytest",
    *test_dirs,
    *ignores,
    "--tb=line", "-q",
    "--no-header",
]

result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT),
                        env={**os.environ, "PYTHONPATH": str(ROOT)})

# Parse results
output = result.stdout + result.stderr
lines = output.strip().split("\n")
summary_line = [l for l in lines if "passed" in l or "failed" in l or "error" in l]

if result.returncode == 0:
    PASSES.append(f"pytest: {summary_line[-1].strip() if summary_line else 'passed'}")
else:
    # Extract failures
    failed_lines = [l for l in lines if "FAILED" in l or "ERROR" in l]
    for fl in failed_lines[:10]:  # Cap at 10
        ERRORS.append(f"pytest: {fl.strip()}")
    if not failed_lines:
        ERRORS.append(f"pytest: exit code {result.returncode} — {summary_line[-1].strip() if summary_line else 'unknown error'}")

print(f"  {'PASS' if result.returncode == 0 else 'FAIL'}")

# ─────────────────────────────────────────────────────────────────────
# 2. IMPORTS — All source files import without error
# ─────────────────────────────────────────────────────────────────────
print("[2/9] Checking all source imports ...")

import_modules = [
    "sdk.base_agent",
    "sdk.base_hooks",
    "sdk.llm.provider",
    "sdk.llm.factory",
    "sdk.llm.anthropic_provider",
    "sdk.manifest_loader",
    "schemas.data_shapes",
    "services.pipeline_service",
    "services.agent_service",
    "services.cost_service",
    "services.audit_service",
    "services.approval_service",
    "services.knowledge_service",
    "services.health_service",
    "services.session_service",
    "api.app",
    "api.routes.pipelines",
    "api.routes.agents",
    "api.routes.cost",
    "api.routes.audit",
    "api.routes.approvals",
    "api.routes.knowledge",
    "api.routes.health",
    "api.middleware.error_handler",
    "api.middleware.auth",
]

import_failures = 0
for mod in import_modules:
    try:
        importlib.import_module(mod)
    except Exception as e:
        ERRORS.append(f"import {mod}: {type(e).__name__}: {e}")
        import_failures += 1

if import_failures == 0:
    PASSES.append(f"imports: {len(import_modules)} modules imported cleanly")
print(f"  {'PASS' if import_failures == 0 else f'FAIL ({import_failures} broken)'}")

# ─────────────────────────────────────────────────────────────────────
# 3. AGENT MANIFESTS — All load and have required fields
# ─────────────────────────────────────────────────────────────────────
print("[3/9] Checking all agent manifests ...")

import yaml

agent_dirs = list(ROOT.glob("agents/*/*"))
manifest_count = 0
manifest_issues = 0

required_sections = ["identity", "foundation_model", "perception", "safety", "output"]

for agent_dir in agent_dirs:
    manifest = agent_dir / "manifest.yaml"
    if not manifest.exists():
        continue
    manifest_count += 1
    try:
        data = yaml.safe_load(manifest.read_text(encoding="utf-8"))
        if not data:
            ERRORS.append(f"manifest {agent_dir.name}: empty YAML")
            manifest_issues += 1
            continue
        missing = [s for s in required_sections if s not in data]
        if missing:
            ERRORS.append(f"manifest {agent_dir.name}: missing sections {missing}")
            manifest_issues += 1
        # Check LLM-agnostic (tier instead of hardcoded model)
        fm = data.get("foundation_model", {})
        if "tier" not in fm:
            warn(f"manifest {agent_dir.name}", "no 'tier' field — may not be LLM-agnostic")
    except Exception as e:
        ERRORS.append(f"manifest {agent_dir.name}: {e}")
        manifest_issues += 1

if manifest_issues == 0 and manifest_count > 0:
    PASSES.append(f"manifests: {manifest_count} agents validated")
print(f"  {'PASS' if manifest_issues == 0 else f'FAIL ({manifest_issues} issues)'} — {manifest_count} manifests")

# ─────────────────────────────────────────────────────────────────────
# 4. AGENT PROMPTS — All exist and are substantial
# ─────────────────────────────────────────────────────────────────────
print("[4/9] Checking all agent prompts ...")

prompt_issues = 0
prompt_count = 0

for agent_dir in agent_dirs:
    manifest = agent_dir / "manifest.yaml"
    if not manifest.exists():
        continue
    prompt = agent_dir / "prompt.md"
    if not prompt.exists():
        ERRORS.append(f"prompt {agent_dir.name}: prompt.md MISSING")
        prompt_issues += 1
        continue
    prompt_count += 1
    content = prompt.read_text(encoding="utf-8")
    if len(content) < 200:
        ERRORS.append(f"prompt {agent_dir.name}: only {len(content)} chars (stub?)")
        prompt_issues += 1

if prompt_issues == 0 and prompt_count > 0:
    PASSES.append(f"prompts: {prompt_count} agent prompts validated (all >200 chars)")
print(f"  {'PASS' if prompt_issues == 0 else f'FAIL ({prompt_issues} issues)'} — {prompt_count} prompts")

# ─────────────────────────────────────────────────────────────────────
# 5. BASE_AGENT DRY-RUN — Can load and invoke without API key
# ─────────────────────────────────────────────────────────────────────
print("[5/9] Testing BaseAgent dry-run (no API key needed) ...")

try:
    import asyncio
    from sdk.base_agent import BaseAgent

    async def _test_dry_run():
        # Pick any agent that exists
        test_agent_dir = None
        for d in ROOT.glob("agents/govern/G1-cost-tracker"):
            if (d / "manifest.yaml").exists():
                test_agent_dir = d
                break
        if not test_agent_dir:
            return "no agent found"

        agent = BaseAgent(agent_dir=test_agent_dir, dry_run=True)
        result = await agent.invoke({"test": "data"}, project_id="validation")
        if result["dry_run"] is not True:
            return "dry_run not True"
        if not result["agent_id"]:
            return "no agent_id"
        # Test .model and .info work without API key
        _ = agent.model
        _ = agent.info
        return None

    err = asyncio.run(_test_dry_run())
    if err:
        ERRORS.append(f"dry-run: {err}")
    else:
        PASSES.append("dry-run: BaseAgent loads, invokes, .model/.info work without API key")
    print(f"  {'PASS' if not err else f'FAIL: {err}'}")
except Exception as e:
    ERRORS.append(f"dry-run: {type(e).__name__}: {e}")
    print(f"  FAIL: {e}")

# ─────────────────────────────────────────────────────────────────────
# 6. STALE REFERENCES — No old doc numbers or method names
# ─────────────────────────────────────────────────────────────────────
print("[6/9] Scanning for stale references ...")

import re

stale_patterns = [
    (r"total_steps\s*[=:]\s*14\b", "total_steps=14 (should be 22)"),
    (r"14-document", "14-document (should be 24)"),
    (r"14\+2", "14+2 (should be 24)"),
    (r"svc\.promote_agent\(", "svc.promote_agent() — renamed to promote_version()"),
    (r"svc\.rollback_agent\(", "svc.rollback_agent() — renamed to rollback_version()"),
    (r"svc\.set_canary\(", "svc.set_canary() — renamed to set_canary_traffic()"),
    (r"svc\.get_agent_health\(", "svc.get_agent_health() — renamed to check_health()"),
    (r"svc\.get_agent_maturity\(", "svc.get_agent_maturity() — renamed to get_maturity()"),
    (r"from agents\.govern\.G1_cost_tracker", "broken import from hyphenated dir"),
]

stale_count = 0
py_files = list(ROOT.glob("**/*.py"))
# Exclude venv, __pycache__, .git
py_files = [f for f in py_files if ".venv" not in str(f) and "__pycache__" not in str(f) and ".git" not in str(f) and "validate_all.py" not in str(f)]

for f in py_files:
    try:
        content = f.read_text(encoding="utf-8", errors="replace")
        for pattern, desc in stale_patterns:
            matches = re.findall(pattern, content)
            if matches:
                rel = f.relative_to(ROOT)
                ERRORS.append(f"stale ref in {rel}: {desc} ({len(matches)} occurrences)")
                stale_count += 1
    except Exception:
        pass

if stale_count == 0:
    PASSES.append(f"stale refs: scanned {len(py_files)} .py files, 0 stale references")
print(f"  {'PASS' if stale_count == 0 else f'FAIL ({stale_count} stale refs)'}")

# ─────────────────────────────────────────────────────────────────────
# 7. ROUTE ↔ SERVICE PARITY — Method names match
# ─────────────────────────────────────────────────────────────────────
print("[7/9] Checking route-service method parity ...")

parity_issues = 0
try:
    route_file = ROOT / "api" / "routes" / "agents.py"
    service_file = ROOT / "services" / "agent_service.py"

    if route_file.exists() and service_file.exists():
        route_content = route_file.read_text(encoding="utf-8")
        service_content = service_file.read_text(encoding="utf-8")

        # Extract svc.method_name calls from routes
        route_calls = set(re.findall(r"svc\.(\w+)\(", route_content))
        # Extract async def method names from service (handles multi-line signatures)
        service_methods = set(re.findall(r"async def (\w+)\(", service_content))

        for call in route_calls:
            if call not in service_methods:
                ERRORS.append(f"parity: route calls svc.{call}() but AgentService has no such method")
                parity_issues += 1

    if parity_issues == 0:
        PASSES.append(f"parity: all route calls match service methods")
except Exception as e:
    ERRORS.append(f"parity check: {e}")

print(f"  {'PASS' if parity_issues == 0 else f'FAIL ({parity_issues} mismatches)'}")

# ─────────────────────────────────────────────────────────────────────
# 8. MANIFEST LOADER — Can find agents in ALL directories
# ─────────────────────────────────────────────────────────────────────
print("[8/9] Checking ManifestLoader search paths ...")

try:
    from sdk.manifest_loader import ManifestLoader
    loader = ManifestLoader(base_dir=ROOT)

    # Check that all agents with manifests can be found
    loader_issues = 0
    for agent_dir in agent_dirs:
        manifest = agent_dir / "manifest.yaml"
        if not manifest.exists():
            continue
        data = yaml.safe_load(manifest.read_text(encoding="utf-8"))
        agent_id = data.get("identity", {}).get("id", agent_dir.name)
        loaded = loader._load_agent_manifest(agent_id)
        if not loaded:
            ERRORS.append(f"loader: cannot find {agent_id} in {agent_dir.parent.name}/")
            loader_issues += 1

    if loader_issues == 0:
        PASSES.append(f"loader: all {manifest_count} agents discoverable by ManifestLoader")
    print(f"  {'PASS' if loader_issues == 0 else f'FAIL ({loader_issues} agents not found)'}")
except Exception as e:
    ERRORS.append(f"loader: {e}")
    print(f"  FAIL: {e}")

# ─────────────────────────────────────────────────────────────────────
# 9. GENERATED DOCS — All 24 exist with correct numbering
# ─────────────────────────────────────────────────────────────────────
print("[9/9] Checking Generated-Docs completeness ...")

docs_dir = ROOT / "Generated-Docs"
doc_issues = 0

if docs_dir.exists():
    doc_files = sorted([f.name for f in docs_dir.glob("*.md")])
    # Check we have 00 through 23
    for i in range(24):
        prefix = f"{i:02d}-"
        matching = [f for f in doc_files if f.startswith(prefix)]
        if not matching:
            ERRORS.append(f"docs: missing Doc {i:02d} in Generated-Docs/")
            doc_issues += 1

    if doc_issues == 0:
        PASSES.append(f"docs: all 24 documents present (00-23)")
else:
    ERRORS.append("docs: Generated-Docs/ directory missing")
    doc_issues += 1

print(f"  {'PASS' if doc_issues == 0 else f'FAIL ({doc_issues} missing)'}")

# ─────────────────────────────────────────────────────────────────────
# FINAL REPORT
# ─────────────────────────────────────────────────────────────────────
print()
print("=" * 70)
print("VALIDATION REPORT")
print("=" * 70)
print()

for p in PASSES:
    print(f"  PASS: {p}")

if WARNINGS:
    print()
    for w in WARNINGS:
        print(f"  {w}")

if ERRORS:
    print()
    for e in ERRORS:
        print(f"  {e}")

print()
total = len(PASSES) + len(ERRORS)
print(f"Result: {len(PASSES)}/{total} checks passed, {len(ERRORS)} failures, {len(WARNINGS)} warnings")
print()

if ERRORS:
    print("STATUS: BLOCKED — Fix all failures before proceeding.")
    sys.exit(1)
else:
    print("STATUS: ALL CLEAR — Safe to proceed.")
    sys.exit(0)
