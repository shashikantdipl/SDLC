"""Filesystem scanner — discovers agents, docs, and pipeline state from project folder.

This is the data layer for the control panel. All data comes from the filesystem,
not a database. Works without PostgreSQL running.
"""
from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml


def scan_project(project_path: str) -> dict[str, Any]:
    """Scan a project folder and return complete project state."""
    root = Path(project_path)
    if not root.exists():
        return {"error": f"Path does not exist: {project_path}"}

    return {
        "project_path": str(root),
        "agents": scan_agents(root),
        "documents": scan_documents(root),
        "pipeline_config": scan_pipeline_config(root),
        "migrations": scan_migrations(root),
        "sdk": scan_sdk(root),
        "tests": scan_tests(root),
        "scanned_at": datetime.now().isoformat(),
    }


def scan_agents(root: Path) -> list[dict[str, Any]]:
    """Discover all agents from agents/ directory."""
    agents = []
    agents_dir = root / "agents"
    if not agents_dir.exists():
        return agents

    for phase_dir in sorted(agents_dir.iterdir()):
        if not phase_dir.is_dir() or phase_dir.name.startswith("."):
            continue
        phase = phase_dir.name

        for agent_dir in sorted(phase_dir.iterdir()):
            if not agent_dir.is_dir():
                continue

            manifest_path = agent_dir / "manifest.yaml"
            prompt_path = agent_dir / "prompt.md"

            agent_info = {
                "id": agent_dir.name,
                "phase": phase,
                "path": str(agent_dir),
                "has_manifest": manifest_path.exists(),
                "has_prompt": prompt_path.exists(),
                "has_agent_py": (agent_dir / "agent.py").exists(),
                "has_tests": (agent_dir / "tests").exists(),
                "manifest": {},
                "prompt_preview": "",
                "prompt_length": 0,
                "status": "unknown",
            }

            # Parse manifest
            if manifest_path.exists():
                try:
                    data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
                    if data:
                        identity = data.get("identity", {})
                        fm = data.get("foundation_model", {})
                        safety = data.get("safety", {})
                        agent_info["manifest"] = {
                            "name": identity.get("name", agent_dir.name),
                            "description": identity.get("description", ""),
                            "version": identity.get("version", "1.0.0"),
                            "extends": identity.get("extends", ""),
                            "tier": fm.get("tier", "unknown"),
                            "provider": fm.get("provider", "null"),
                            "temperature": fm.get("temperature", 0.2),
                            "max_tokens": fm.get("max_tokens", 4096),
                            "autonomy_tier": safety.get("autonomy_tier", "T2"),
                            "max_budget_usd": safety.get("max_budget_usd", 0.50),
                            "tags": identity.get("tags", []),
                        }
                        agent_info["status"] = "ready"
                except Exception:
                    agent_info["status"] = "manifest_error"

            # Read prompt preview
            if prompt_path.exists():
                try:
                    content = prompt_path.read_text(encoding="utf-8")
                    agent_info["prompt_length"] = len(content)
                    agent_info["prompt_preview"] = content[:200] + "..." if len(content) > 200 else content
                except Exception:
                    pass

            # Determine status
            if agent_info["has_manifest"] and agent_info["has_prompt"]:
                agent_info["status"] = "ready"
            elif agent_info["has_manifest"]:
                agent_info["status"] = "no_prompt"
            else:
                agent_info["status"] = "incomplete"

            agents.append(agent_info)

    return agents


def scan_documents(root: Path) -> list[dict[str, Any]]:
    """Scan Generated-Docs/ for all generated documents."""
    docs = []
    docs_dir = root / "Generated-Docs"
    if not docs_dir.exists():
        return docs

    for doc_file in sorted(docs_dir.glob("*.md")):
        content = doc_file.read_text(encoding="utf-8", errors="replace")
        lines = content.split("\n")

        # Extract doc number from filename
        parts = doc_file.stem.split("-", 1)
        doc_num = int(parts[0]) if parts[0].isdigit() else -1

        # Extract version from header
        version = "unknown"
        for line in lines[:10]:
            if "Version:" in line or "version:" in line:
                version = line.strip()
                break

        docs.append({
            "number": doc_num,
            "filename": doc_file.name,
            "title": lines[0].replace("#", "").strip() if lines else doc_file.stem,
            "lines": len(lines),
            "size_bytes": doc_file.stat().st_size,
            "version_header": version,
            "modified": datetime.fromtimestamp(doc_file.stat().st_mtime).isoformat(),
            "path": str(doc_file),
        })

    return docs


def scan_pipeline_config(root: Path) -> dict[str, Any]:
    """Read pipeline configuration from services/pipeline_service.py."""
    config = {
        "steps": [],
        "cost_ceiling_usd": 45.00,
        "parallel_groups": [],
    }

    service_path = root / "services" / "pipeline_service.py"
    if service_path.exists():
        content = service_path.read_text(encoding="utf-8")
        # Extract step names from DEFAULT_PIPELINE_CONFIG
        import re
        step_matches = re.findall(r'"(D\d+-\w+)"', content)
        if step_matches:
            config["steps"] = step_matches
        ceiling_match = re.search(r'cost_ceiling_usd=Decimal\("([\d.]+)"\)', content)
        if ceiling_match:
            config["cost_ceiling_usd"] = float(ceiling_match.group(1))

    return config


def scan_migrations(root: Path) -> list[dict[str, Any]]:
    """Scan migrations/ for SQL files."""
    migrations = []
    mig_dir = root / "migrations"
    if not mig_dir.exists():
        return migrations

    for sql_file in sorted(mig_dir.glob("*.sql")):
        content = sql_file.read_text(encoding="utf-8")
        migrations.append({
            "filename": sql_file.name,
            "has_up": "CREATE TABLE" in content or "ALTER TABLE" in content,
            "has_down": "-- DOWN" in content,
            "size_bytes": sql_file.stat().st_size,
        })

    return migrations


def scan_sdk(root: Path) -> dict[str, Any]:
    """Scan SDK layer."""
    sdk_dir = root / "sdk"
    llm_dir = sdk_dir / "llm"

    return {
        "base_agent": (sdk_dir / "base_agent.py").exists(),
        "base_hooks": (sdk_dir / "base_hooks.py").exists(),
        "manifest_loader": (sdk_dir / "manifest_loader.py").exists(),
        "llm_provider": (llm_dir / "provider.py").exists() if llm_dir.exists() else False,
        "anthropic_provider": (llm_dir / "anthropic_provider.py").exists() if llm_dir.exists() else False,
        "openai_provider": (llm_dir / "openai_provider.py").exists() if llm_dir.exists() else False,
        "ollama_provider": (llm_dir / "ollama_provider.py").exists() if llm_dir.exists() else False,
        "factory": (llm_dir / "factory.py").exists() if llm_dir.exists() else False,
    }


def scan_tests(root: Path) -> dict[str, Any]:
    """Scan test files."""
    tests_dir = root / "tests"
    if not tests_dir.exists():
        return {"total_files": 0, "directories": []}

    test_files = list(tests_dir.rglob("test_*.py")) + list(tests_dir.rglob("run_*.py"))
    directories = set()
    for f in test_files:
        rel = f.relative_to(tests_dir)
        if len(rel.parts) > 1:
            directories.add(rel.parts[0])

    return {
        "total_files": len(test_files),
        "directories": sorted(directories),
    }
