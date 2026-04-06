"""SDLC Pipeline Runner — One command to generate all 24 documents.

Usage:
    # Full pipeline from a brief
    PYTHONPATH=. python sdlc_run.py --name "FleetOps" --brief "Build a fleet management dashboard..."

    # From a file
    PYTHONPATH=. python sdlc_run.py --name "FleetOps" --brief-file ./my_requirements.md

    # Dry run (no LLM calls, just validate pipeline)
    PYTHONPATH=. python sdlc_run.py --name "FleetOps" --brief "..." --dry-run

    # With specific provider
    PYTHONPATH=. python sdlc_run.py --name "FleetOps" --brief "..." --provider openai

    # Resume from step N
    PYTHONPATH=. python sdlc_run.py --name "FleetOps" --brief "..." --resume-from 5

    # Output to specific directory
    PYTHONPATH=. python sdlc_run.py --name "FleetOps" --brief "..." --output ./my-project-docs
"""
from __future__ import annotations

import argparse
import asyncio
import sys
import io
from pathlib import Path
from datetime import datetime

# Handle Windows encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from dotenv import load_dotenv
load_dotenv()

from sdk.orchestration.pipeline_runner import PipelineRunner


# --- Live callback for terminal output ---
async def print_callback(step: int, status: str, result: dict):
    """Print live pipeline progress to terminal."""
    timestamp = datetime.now().strftime("%H:%M:%S")

    if step == -1 and status == "started":
        print()
        print("=" * 70)
        print(f"  AGENTIC SDLC PIPELINE — {result.get('total_steps', 22)} steps")
        print("=" * 70)
        print(f"  Run ID: {result.get('run_id', '?')}")
        print(f"  Started: {timestamp}")
        print("=" * 70)
        print()
        return

    if step == -1 and status == "finished":
        r = result
        print()
        print("=" * 70)
        status_icon = "✅" if r["status"] == "completed" else "❌"
        print(f"  {status_icon} PIPELINE {r['status'].upper()}")
        print(f"  Steps: {r['completed_steps']}/{r['total_steps']}")
        print(f"  Cost:  ${r['total_cost_usd']:.2f} / ${r['cost_ceiling_usd']:.2f}")
        print(f"  Time:  {r['total_duration_minutes']:.1f} minutes")
        print(f"  Output: {r['output_dir']}")
        print("=" * 70)
        if r["documents_generated"]:
            print()
            print("  Generated Documents:")
            for doc in r["documents_generated"]:
                print(f"    📄 {doc}")
        print()
        return

    icon = {
        "running": "🔄",
        "completed": "✅",
        "failed": "❌",
        "aborted": "⛔",
    }.get(status, "⚪")

    agent = result.get("agent", "?")

    if status == "running":
        print(f"  [{timestamp}] {icon} Step {step:2d}: {agent} — running...")
    elif status == "completed":
        cost = result.get("cost_usd", 0)
        duration = result.get("duration_seconds", 0)
        chars = result.get("output_chars", 0)
        doc = result.get("doc_filename", "")
        print(f"  [{timestamp}] {icon} Step {step:2d}: {agent} — ${cost:.3f} | {duration:.0f}s | {chars} chars → {doc}")
    elif status == "failed":
        reason = result.get("reason", result.get("error", "unknown"))
        print(f"  [{timestamp}] {icon} Step {step:2d}: {agent} — FAILED: {reason[:80]}")
    elif status == "aborted":
        reason = result.get("reason", "unknown")
        print(f"  [{timestamp}] {icon} Step {step:2d}: {agent} — ABORTED: {reason[:80]}")


def main():
    parser = argparse.ArgumentParser(
        description="Agentic SDLC Pipeline — Generate 24 documents from a project brief",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python sdlc_run.py --name "FleetOps" --brief "Build a fleet management dashboard..."
  python sdlc_run.py --name "FleetOps" --brief-file ./requirements.md
  python sdlc_run.py --name "FleetOps" --brief "..." --provider openai --dry-run
        """,
    )
    parser.add_argument("--name", required=True, help="Project name")
    parser.add_argument("--brief", help="Project brief text")
    parser.add_argument("--brief-file", help="Path to file containing project brief")
    parser.add_argument("--provider", choices=["anthropic", "openai", "ollama"], help="LLM provider (default: env LLM_PROVIDER)")
    parser.add_argument("--output", help="Output directory (default: ./output/<name>_<run_id>)")
    parser.add_argument("--dry-run", action="store_true", help="Validate pipeline without calling LLM")
    parser.add_argument("--resume-from", type=int, default=0, help="Resume from step N")
    parser.add_argument("--cost-ceiling", type=float, default=45.0, help="Max cost in USD (default: 45)")

    args = parser.parse_args()

    # Get brief text
    if args.brief_file:
        brief_path = Path(args.brief_file)
        if not brief_path.exists():
            print(f"❌ Brief file not found: {args.brief_file}")
            sys.exit(1)
        brief = brief_path.read_text(encoding="utf-8")
    elif args.brief:
        brief = args.brief
    else:
        print("❌ Either --brief or --brief-file is required")
        sys.exit(1)

    if len(brief.strip()) < 20:
        print("❌ Brief too short (minimum 20 characters)")
        sys.exit(1)

    # Setup
    project_root = Path(".")
    output_dir = Path(args.output) if args.output else None

    runner = PipelineRunner(
        project_root=project_root,
        output_dir=output_dir,
        cost_ceiling_usd=args.cost_ceiling,
    )

    print(f"🤖 Agentic SDLC Pipeline")
    print(f"   Project:  {args.name}")
    print(f"   Provider: {args.provider or 'env default'}")
    print(f"   Dry run:  {args.dry_run}")
    print(f"   Ceiling:  ${args.cost_ceiling:.2f}")
    print(f"   Brief:    {brief[:100]}...")

    # Run
    result = asyncio.run(
        runner.run(
            project_name=args.name,
            brief=brief,
            provider=args.provider,
            dry_run=args.dry_run,
            start_from_step=args.resume_from,
            callback=print_callback,
        )
    )

    # Exit code
    if result["status"] == "completed":
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
