"""Live test of B6-doc-generator."""

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

# Service file with NO docstrings — 1 class, 4 methods, zero documentation.
UNDOCUMENTED_CODE = '''
import logging
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)


class CostService:

    def __init__(self, db_conn, budget_limit: float = 1000.0):
        self.db = db_conn
        self.budget_limit = budget_limit
        self.cache = {}

    def get_report(self, project_id: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> dict:
        if not project_id:
            raise ValueError("project_id is required")
        rows = self.db.execute(
            "SELECT agent_id, SUM(cost_usd) as total FROM costs WHERE project_id = ? AND date BETWEEN ? AND ? GROUP BY agent_id",
            (project_id, start_date or "2024-01-01", end_date or datetime.now().strftime("%Y-%m-%d")),
        )
        total = sum(r["total"] for r in rows)
        return {
            "project_id": project_id,
            "total_cost_usd": total,
            "by_agent": {r["agent_id"]: r["total"] for r in rows},
            "period": {"start": start_date, "end": end_date},
        }

    def check_budget(self, project_id: str) -> dict:
        report = self.get_report(project_id)
        spent = report["total_cost_usd"]
        remaining = self.budget_limit - spent
        is_over = remaining < 0
        if is_over:
            logger.warning(f"Project {project_id} is over budget by ${abs(remaining):.2f}")
        return {
            "project_id": project_id,
            "budget_limit": self.budget_limit,
            "spent": spent,
            "remaining": remaining,
            "is_over_budget": is_over,
        }

    def record_spend(self, project_id: str, agent_id: str, cost_usd: float, description: str = "") -> dict:
        if cost_usd < 0:
            raise ValueError("cost_usd must be non-negative")
        if not agent_id:
            raise ValueError("agent_id is required")
        self.db.execute(
            "INSERT INTO costs (project_id, agent_id, cost_usd, description, date) VALUES (?, ?, ?, ?, ?)",
            (project_id, agent_id, cost_usd, description, datetime.now().strftime("%Y-%m-%d")),
        )
        self.db.commit()
        self.cache.pop(project_id, None)
        return {"status": "recorded", "project_id": project_id, "agent_id": agent_id, "cost_usd": cost_usd}

    def get_anomalies(self, project_id: str, threshold_multiplier: float = 2.0) -> list:
        report = self.get_report(project_id)
        by_agent = report["by_agent"]
        if not by_agent:
            return []
        avg_cost = sum(by_agent.values()) / len(by_agent)
        anomalies = []
        for agent_id, cost in by_agent.items():
            if cost > avg_cost * threshold_multiplier:
                anomalies.append({
                    "agent_id": agent_id,
                    "cost_usd": cost,
                    "average_usd": round(avg_cost, 4),
                    "ratio": round(cost / avg_cost, 2),
                })
        return anomalies
'''


async def main():
    agent = BaseAgent(agent_dir=Path("agents/build/B6-doc-generator"))
    print(f"Agent: {agent.agent_id}")
    print(f"Provider: {agent.provider_name} | Tier: {agent._model_tier.value} | Model: {agent.model}")
    print()

    result = await agent.invoke(
        input_data={
            "file_path": "services/cost_service.py",
            "code_content": UNDOCUMENTED_CODE,
            "language": "python",
            "doc_format": "google",
            "output_type": "all",
            "project_context": "Agentic SDLC Platform — AI agent control plane tracking costs across 48 agents",
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
            data = json.loads(json_str)
            doc = data.get("documentation", {})
            cov = data.get("coverage", {})

            # --- Check module docstring ---
            module_doc = doc.get("module_docstring", "")
            has_module_doc = len(module_doc) > 20
            print("=== MODULE DOCSTRING ===")
            print(f"  Length: {len(module_doc)} chars")
            print(f"  Preview: {module_doc[:120]}...")
            print(f"  [{'PASS' if has_module_doc else 'FAIL'}] Module docstring present and substantive")

            # --- Check class and method docstrings ---
            classes = doc.get("classes", [])
            print(f"\n=== CLASSES ({len(classes)}) ===")
            has_cost_service = False
            method_names_found = []
            methods_with_args = 0
            methods_with_returns = 0
            methods_with_raises = 0

            for cls in classes:
                cls_name = cls.get("name", "")
                if cls_name == "CostService":
                    has_cost_service = True
                cls_doc = cls.get("docstring", "")
                print(f"  Class: {cls_name} | docstring length: {len(cls_doc)}")
                for method in cls.get("methods", []):
                    m_name = method.get("name", "")
                    m_doc = method.get("docstring", "")
                    method_names_found.append(m_name)
                    if "Args:" in m_doc or "Args\n" in m_doc:
                        methods_with_args += 1
                    if "Returns:" in m_doc or "Returns\n" in m_doc:
                        methods_with_returns += 1
                    if "Raises:" in m_doc or "Raises\n" in m_doc:
                        methods_with_raises += 1
                    print(f"    Method: {m_name} | docstring length: {len(m_doc)} | Args={'Y' if 'Args' in m_doc else 'N'} Returns={'Y' if 'Returns' in m_doc else 'N'} Raises={'Y' if 'Raises' in m_doc else 'N'}")

            expected_methods = {"__init__", "get_report", "check_budget", "record_spend", "get_anomalies"}
            found_set = set(method_names_found)
            # __init__ is optional per prompt rules but the 4 public methods are required
            required_methods = {"get_report", "check_budget", "record_spend", "get_anomalies"}
            has_all_methods = required_methods.issubset(found_set)
            method_count = len(found_set & required_methods)

            print(f"\n  [{'PASS' if has_cost_service else 'FAIL'}] CostService class documented")
            print(f"  [{'PASS' if has_all_methods else 'FAIL'}] All 4 required methods documented ({method_count}/4 found: {found_set & required_methods})")
            print(f"  [{'PASS' if methods_with_args >= 4 else 'FAIL'}] Methods have Args section ({methods_with_args}/4+)")
            print(f"  [{'PASS' if methods_with_returns >= 4 else 'FAIL'}] Methods have Returns section ({methods_with_returns}/4+)")
            print(f"  [{'PASS' if methods_with_raises >= 2 else 'FAIL'}] Methods with Raises section ({methods_with_raises}/2+ expected — get_report and record_spend raise)")

            # --- Check documented_code ---
            documented_code = doc.get("documented_code", "")
            print(f"\n=== DOCUMENTED CODE ===")
            print(f"  Length: {len(documented_code)} chars")
            has_documented_code = len(documented_code) > len(UNDOCUMENTED_CODE)
            has_class_def = "class CostService" in documented_code
            has_def_get_report = "def get_report" in documented_code
            has_triple_quotes = documented_code.count('"""') >= 6  # at least module + class + 4 methods = 12 quotes / 2 = 6 pairs minimum
            print(f"  [{'PASS' if has_documented_code else 'FAIL'}] Documented code is longer than original ({len(documented_code)} > {len(UNDOCUMENTED_CODE)})")
            print(f"  [{'PASS' if has_class_def else 'FAIL'}] Contains class CostService definition")
            print(f"  [{'PASS' if has_def_get_report else 'FAIL'}] Contains def get_report")
            print(f"  [{'PASS' if has_triple_quotes else 'FAIL'}] Contains multiple docstrings (triple-quote count: {documented_code.count('\"\"\"')})")

            # --- Check readme_section ---
            readme = doc.get("readme_section", "")
            print(f"\n=== README SECTION ===")
            print(f"  Length: {len(readme)} chars")
            is_markdown = "#" in readme or "```" in readme
            has_readme = len(readme) > 50 and is_markdown
            print(f"  [{'PASS' if has_readme else 'FAIL'}] README section is markdown with content")

            # --- Check usage_examples ---
            examples = doc.get("usage_examples", [])
            print(f"\n=== USAGE EXAMPLES ===")
            print(f"  Count: {len(examples)}")
            has_examples = len(examples) >= 1
            for i, ex in enumerate(examples):
                print(f"  Example {i+1} preview: {ex[:100]}...")
            print(f"  [{'PASS' if has_examples else 'FAIL'}] At least one usage example present")

            # --- Check coverage ---
            print(f"\n=== COVERAGE ===")
            total_doc = cov.get("total_documentable", 0)
            documented = cov.get("documented", 0)
            coverage_pct = cov.get("coverage_pct", 0)
            missing = cov.get("missing", [])
            print(f"  Total documentable: {total_doc}")
            print(f"  Documented:         {documented}")
            print(f"  Coverage:           {coverage_pct}%")
            print(f"  Missing:            {missing}")
            has_full_coverage = coverage_pct == 100 or (total_doc > 0 and documented == total_doc)
            print(f"  [{'PASS' if has_full_coverage else 'FAIL'}] 100% documentation coverage")

            # --- Summary ---
            print("\n" + "=" * 50)
            print("=== SUMMARY ===")
            checks = {
                "Module docstring present": has_module_doc,
                "CostService class documented": has_cost_service,
                "All 4 methods documented": has_all_methods,
                "Methods have Args sections": methods_with_args >= 4,
                "Methods have Returns sections": methods_with_returns >= 4,
                "Methods have Raises sections": methods_with_raises >= 2,
                "Documented code is complete": has_documented_code and has_class_def and has_def_get_report,
                "Documented code has docstrings": has_triple_quotes,
                "README section is markdown": has_readme,
                "Usage examples present": has_examples,
                "Coverage is 100%": has_full_coverage,
            }
            passed = sum(checks.values())
            total = len(checks)
            for name, ok in checks.items():
                print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
            print(f"\n  Result: {passed}/{total} checks passed")
            if passed == total:
                print("  ALL CHECKS PASSED")
            else:
                print(f"  {total - passed} check(s) failed")

        else:
            print("WARNING: Could not extract JSON from output")
    except json.JSONDecodeError as e:
        print(f"WARNING: JSON parse error: {e}")

    print()
    print("=== FIRST 3000 CHARS OF RAW OUTPUT ===")
    print(output[:3000])


if __name__ == "__main__":
    asyncio.run(main())
