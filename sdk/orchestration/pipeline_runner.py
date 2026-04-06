"""PipelineRunner — executes the 24-step document generation pipeline end-to-end.

Input: A project brief (text) + project name
Output: 24 generated documents in the output directory

Usage:
    runner = PipelineRunner(project_root=Path("."), output_dir=Path("output/my-project"))
    result = await runner.run(
        project_name="FleetOps",
        brief="Build a fleet management dashboard...",
        provider="anthropic",  # or "openai", "ollama"
    )
"""
from __future__ import annotations

import asyncio
import json
import time
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any
from uuid import uuid4

import structlog

from sdk.base_agent import BaseAgent
from sdk.orchestration.session_store import SessionStore

logger = structlog.get_logger()

# --- Pipeline Step Definitions ---
# Each step: (step_number, agent_dir_name, session_write_key, session_read_keys, doc_filename)
PIPELINE_STEPS = [
    # Pre-Phase
    (0, "D0-brd-generator", "brd_doc", [], "00-BRD.md"),
    # Phase A
    (1, "D1-roadmap-generator", "roadmap_doc", ["brd_doc"], "01-ROADMAP.md"),
    (2, "D2-prd-generator", "prd_doc", ["brd_doc"], "02-PRD.md"),
    (3, "D3-architecture-drafter", "arch_doc", ["prd_doc"], "03-ARCH.md"),
    # Phase B
    (4, "D4-feature-extractor", "feature_catalog", ["prd_doc", "arch_doc"], "04-FEATURE-CATALOG.md"),
    (5, "D5-quality-spec-generator", "quality_doc", ["prd_doc", "arch_doc", "feature_catalog"], "05-QUALITY.md"),
    (6, "D6-security-architect", "security_arch", ["prd_doc", "arch_doc", "quality_doc", "feature_catalog"], "06-SECURITY-ARCH.md"),
    # Phase C
    (7, "D7-interaction-map-generator", "interaction_map", ["prd_doc", "arch_doc", "feature_catalog", "quality_doc"], "07-INTERACTION-MAP.md"),
    (8, "D8-mcp-tool-spec-writer", "mcp_tool_spec", ["interaction_map", "arch_doc", "feature_catalog", "quality_doc"], "08-MCP-TOOL-SPEC.md"),
    (9, "D9-design-spec-writer", "design_spec", ["interaction_map", "prd_doc", "quality_doc", "feature_catalog"], "09-DESIGN-SPEC.md"),
    # Phase D
    (10, "D10-data-model-designer", "data_model", ["arch_doc", "feature_catalog", "quality_doc", "mcp_tool_spec", "design_spec", "interaction_map"], "10-DATA-MODEL.md"),
    (11, "D11-api-contract-generator", "api_contracts", ["arch_doc", "data_model", "prd_doc", "mcp_tool_spec", "design_spec", "interaction_map"], "11-API-CONTRACTS.md"),
    (12, "D12-user-story-writer", "user_stories", ["prd_doc", "feature_catalog", "quality_doc", "arch_doc", "data_model", "api_contracts", "mcp_tool_spec", "design_spec"], "12-USER-STORIES.md"),
    (13, "D13-backlog-builder", "backlog", ["feature_catalog", "prd_doc", "arch_doc", "quality_doc", "mcp_tool_spec", "design_spec", "interaction_map", "user_stories"], "13-BACKLOG.md"),
    (14, "D14-claude-md-generator", "claude_doc", ["roadmap_doc", "arch_doc", "data_model", "api_contracts"], "14-CLAUDE.md"),
    (15, "D15-enforcement-scaffolder", "enforcement_rules", ["claude_doc", "arch_doc", "quality_doc", "security_arch"], "15-ENFORCEMENT.md"),
    # Phase E
    (16, "D16-infra-designer", "infra_design", ["arch_doc", "security_arch", "quality_doc", "feature_catalog"], "16-INFRA-DESIGN.md"),
    (17, "D17-migration-planner", "migration_plan", ["data_model", "arch_doc", "prd_doc", "security_arch", "brd_doc"], "17-MIGRATION-PLAN.md"),
    (18, "D18-test-strategy-generator", "test_strategy", ["arch_doc", "quality_doc", "data_model", "claude_doc", "mcp_tool_spec", "design_spec", "interaction_map", "security_arch"], "18-TESTING.md"),
    (19, "D19-fault-tolerance-planner", "fault_tolerance", ["arch_doc", "data_model", "api_contracts", "security_arch", "infra_design", "quality_doc"], "19-FAULT-TOLERANCE.md"),
    (20, "D20-guardrails-spec-writer", "guardrails_spec", ["arch_doc", "security_arch", "enforcement_rules", "quality_doc"], "20-GUARDRAILS-SPEC.md"),
    (21, "D21-compliance-matrix-writer", "compliance_matrix", ["security_arch", "quality_doc", "data_model", "arch_doc", "guardrails_spec", "fault_tolerance"], "21-COMPLIANCE-MATRIX.md"),
]

# Parallel groups: steps that can run concurrently
PARALLEL_GROUPS = {
    "A": [1, 2],     # ROADMAP ‖ PRD
    "C": [8, 9],     # MCP-TOOL-SPEC ‖ DESIGN-SPEC
    "E": [17, 18],   # MIGRATION ‖ TESTING
}


class PipelineRunner:
    """Executes the 24-step document generation pipeline."""

    def __init__(
        self,
        project_root: Path,
        output_dir: Path | None = None,
        cost_ceiling_usd: float = 45.00,
    ) -> None:
        self.project_root = project_root
        self.output_dir = output_dir or (project_root / "output")
        self.cost_ceiling_usd = Decimal(str(cost_ceiling_usd))
        self._agents_dir = project_root / "agents" / "design"

    async def run(
        self,
        project_name: str,
        brief: str,
        provider: str | None = None,
        dry_run: bool = False,
        start_from_step: int = 0,
        callback: Any = None,
    ) -> dict[str, Any]:
        """Run the full pipeline.

        Args:
            project_name: Name for the project
            brief: Project brief / requirements text
            provider: LLM provider override (None = use env default)
            dry_run: If True, don't call LLM — just validate the pipeline
            start_from_step: Resume from this step (for checkpoint/resume)
            callback: Optional async callback(step, status, result) for live updates

        Returns:
            Pipeline execution result with all documents and metrics
        """
        run_id = str(uuid4())[:8]
        run_output_dir = self.output_dir / f"{project_name}_{run_id}"
        session = SessionStore(run_id=run_id, output_dir=run_output_dir)

        # Seed session with the raw brief
        session.write("raw_spec", brief, written_by="user")
        session.write("project_name", project_name, written_by="user")

        start_time = time.monotonic()
        total_cost = Decimal("0.00")
        step_results = []
        failed_step = None

        logger.info(
            "pipeline.started",
            run_id=run_id,
            project_name=project_name,
            provider=provider or "env_default",
            dry_run=dry_run,
            total_steps=len(PIPELINE_STEPS),
            cost_ceiling=float(self.cost_ceiling_usd),
        )

        if callback:
            await callback(step=-1, status="started", result={"run_id": run_id, "total_steps": len(PIPELINE_STEPS)})

        for step_num, agent_dir_name, write_key, read_keys, doc_filename in PIPELINE_STEPS:
            if step_num < start_from_step:
                # Skip already-completed steps (resume mode)
                continue

            # Check cost ceiling
            if total_cost >= self.cost_ceiling_usd:
                logger.warning("pipeline.cost_ceiling_hit", run_id=run_id, cost=float(total_cost), ceiling=float(self.cost_ceiling_usd))
                failed_step = step_num
                step_results.append({
                    "step": step_num, "agent": agent_dir_name, "status": "aborted",
                    "reason": f"Cost ceiling ${self.cost_ceiling_usd} reached (spent ${total_cost})",
                })
                if callback:
                    await callback(step=step_num, status="aborted", result={"reason": "cost_ceiling"})
                break

            # Check dependencies are met
            missing = [k for k in read_keys if not session.exists(k)]
            if missing:
                logger.error("pipeline.dependency_missing", run_id=run_id, step=step_num, missing=missing)
                failed_step = step_num
                step_results.append({
                    "step": step_num, "agent": agent_dir_name, "status": "failed",
                    "reason": f"Missing dependencies: {missing}",
                })
                if callback:
                    await callback(step=step_num, status="failed", result={"missing": missing})
                break

            # Build agent input
            agent_input = self._build_agent_input(
                step_num=step_num,
                agent_dir_name=agent_dir_name,
                session=session,
                read_keys=read_keys,
                project_name=project_name,
                brief=brief,
            )

            # Find agent directory
            agent_dir = self._find_agent_dir(agent_dir_name)
            if not agent_dir:
                logger.error("pipeline.agent_not_found", run_id=run_id, agent=agent_dir_name)
                failed_step = step_num
                step_results.append({
                    "step": step_num, "agent": agent_dir_name, "status": "failed",
                    "reason": f"Agent directory not found: {agent_dir_name}",
                })
                if callback:
                    await callback(step=step_num, status="failed", result={"reason": "agent_not_found"})
                break

            # Invoke agent
            logger.info("pipeline.step.start", run_id=run_id, step=step_num, agent=agent_dir_name)
            if callback:
                await callback(step=step_num, status="running", result={"agent": agent_dir_name})

            try:
                # Create provider if specified
                llm_provider = None
                if provider:
                    from sdk.llm.factory import create_provider
                    llm_provider = create_provider(provider)

                agent = BaseAgent(
                    agent_dir=agent_dir,
                    provider=llm_provider,
                    dry_run=dry_run,
                )

                step_start = time.monotonic()
                result = await agent.invoke(
                    input_data=agent_input,
                    project_id=project_name,
                )
                step_duration = time.monotonic() - step_start

                # Extract output
                output_text = result.get("output", "")
                step_cost = Decimal(str(result.get("cost_usd", 0)))
                total_cost += step_cost

                # Store in session
                session.write(write_key, output_text, written_by=agent_dir_name)

                # Save to file
                session.save_to_file(write_key, doc_filename)

                step_result = {
                    "step": step_num,
                    "agent": agent_dir_name,
                    "status": "completed",
                    "doc_filename": doc_filename,
                    "session_key": write_key,
                    "cost_usd": float(step_cost),
                    "tokens_in": result.get("input_tokens", 0),
                    "tokens_out": result.get("output_tokens", 0),
                    "duration_seconds": round(step_duration, 1),
                    "output_chars": len(output_text),
                    "provider": result.get("provider", "unknown"),
                    "model": result.get("model", "unknown"),
                    "model_tier": result.get("model_tier", "unknown"),
                }
                step_results.append(step_result)

                logger.info(
                    "pipeline.step.complete",
                    run_id=run_id,
                    step=step_num,
                    agent=agent_dir_name,
                    cost=float(step_cost),
                    duration=round(step_duration, 1),
                    output_chars=len(output_text),
                )

                if callback:
                    await callback(step=step_num, status="completed", result=step_result)

            except Exception as exc:
                logger.exception("pipeline.step.failed", run_id=run_id, step=step_num, agent=agent_dir_name, error=str(exc))
                failed_step = step_num
                step_results.append({
                    "step": step_num, "agent": agent_dir_name, "status": "failed",
                    "reason": str(exc), "error_type": type(exc).__name__,
                })
                if callback:
                    await callback(step=step_num, status="failed", result={"error": str(exc)})
                break

        total_duration = time.monotonic() - start_time

        # Final summary
        completed_steps = sum(1 for r in step_results if r["status"] == "completed")
        pipeline_status = "completed" if completed_steps == len(PIPELINE_STEPS) else "failed" if failed_step is not None else "partial"

        summary = {
            "run_id": run_id,
            "project_name": project_name,
            "status": pipeline_status,
            "total_steps": len(PIPELINE_STEPS),
            "completed_steps": completed_steps,
            "failed_step": failed_step,
            "total_cost_usd": float(total_cost),
            "cost_ceiling_usd": float(self.cost_ceiling_usd),
            "total_duration_seconds": round(total_duration, 1),
            "total_duration_minutes": round(total_duration / 60, 1),
            "output_dir": str(run_output_dir),
            "documents_generated": [r["doc_filename"] for r in step_results if r["status"] == "completed"],
            "steps": step_results,
            "session_summary": session.summary(),
            "dry_run": dry_run,
            "provider": provider or "env_default",
            "started_at": datetime.now(timezone.utc).isoformat(),
        }

        # Save summary
        summary_path = run_output_dir / "_pipeline_summary.json"
        summary_path.write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")

        logger.info(
            "pipeline.finished",
            run_id=run_id,
            status=pipeline_status,
            completed=completed_steps,
            total=len(PIPELINE_STEPS),
            cost=float(total_cost),
            duration_min=round(total_duration / 60, 1),
        )

        if callback:
            await callback(step=-1, status="finished", result=summary)

        return summary

    def _find_agent_dir(self, agent_dir_name: str) -> Path | None:
        """Find agent directory by name across all phase directories."""
        # Search in design/ first (most pipeline agents are here)
        for phase_dir in ["design", "govern", "build", "test", "deploy", "operate", "oversight"]:
            candidate = self.project_root / "agents" / phase_dir / agent_dir_name
            if candidate.exists() and (candidate / "manifest.yaml").exists():
                return candidate
        return None

    def _build_agent_input(
        self,
        step_num: int,
        agent_dir_name: str,
        session: SessionStore,
        read_keys: list[str],
        project_name: str,
        brief: str,
    ) -> dict[str, Any]:
        """Build the input dict for an agent based on its step and dependencies."""
        # Base input every agent gets
        agent_input: dict[str, Any] = {
            "project_name": project_name,
        }

        # Step 0 (BRD): gets the raw brief
        if step_num == 0:
            agent_input["project_purpose"] = brief
            return agent_input

        # For all other steps: include upstream document summaries
        # Each upstream doc is passed as a truncated summary to stay within token limits
        for key in read_keys:
            doc_content = session.read(key)
            if doc_content:
                # Truncate to ~3000 chars per upstream doc to stay within token budget
                truncated = doc_content[:3000]
                if len(doc_content) > 3000:
                    truncated += f"\n\n[... truncated from {len(doc_content)} chars]"
                agent_input[key] = truncated

        # Add project purpose for agents that need it
        if step_num in (1, 2, 3):  # ROADMAP, PRD, ARCH
            agent_input["project_purpose"] = brief

        return agent_input
