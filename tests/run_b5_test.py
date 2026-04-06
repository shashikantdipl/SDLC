"""Live test of B5-refactor-assistant."""

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

# Deliberately messy code with multiple refactoring opportunities:
# - 70-line function
# - nested if/else 4 levels deep
# - duplicated 5-line block
# - single-letter variable names
# - class doing 3 unrelated things
MESSY_CODE = '''
"""Order processing module — needs serious refactoring."""
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class OrderManager:
    """Handles orders, sends emails, and generates reports — violates SRP."""

    def __init__(self, db, mailer, config):
        self.db = db
        self.mailer = mailer
        self.config = config
        self.r = []  # unclear name: holds recent reports

    def process_order(self, o):
        """Massive function that does too many things."""
        # Validate
        x = o.get("items", [])
        t = 0
        d = None
        v = True
        if x:
            for i in x:
                if i.get("price") is not None:
                    if i["price"] > 0:
                        if i.get("quantity") is not None:
                            if i["quantity"] > 0:
                                t = t + i["price"] * i["quantity"]
                            else:
                                v = False
                                logger.error("Bad quantity")
                        else:
                            v = False
                            logger.error("No quantity")
                    else:
                        v = False
                        logger.error("Bad price")
                else:
                    v = False
                    logger.error("No price")
        else:
            v = False
            logger.error("No items")

        if not v:
            return {"status": "error", "message": "Validation failed"}

        # Apply discount — duplicated logic block 1
        if o.get("customer_type") == "premium":
            d = t * 0.15
            t = t - d
            logger.info(f"Discount applied: {d}")
            self.db.execute("INSERT INTO discounts (order_id, amount, type) VALUES (?, ?, ?)",
                            (o["order_id"], d, "premium"))
            self.db.commit()

        # Apply discount — duplicated logic block 2 (same pattern, different type)
        if o.get("coupon_code") == "SAVE10":
            d = t * 0.10
            t = t - d
            logger.info(f"Discount applied: {d}")
            self.db.execute("INSERT INTO discounts (order_id, amount, type) VALUES (?, ?, ?)",
                            (o["order_id"], d, "coupon"))
            self.db.commit()

        # Save order
        self.db.execute(
            "INSERT INTO orders (id, customer_id, total, status, created_at) VALUES (?, ?, ?, ?, ?)",
            (o["order_id"], o["customer_id"], t, "confirmed", datetime.now().isoformat())
        )
        self.db.commit()

        # Send confirmation email — not order processing concern
        s = f"Order {o['order_id']} Confirmed"
        b = f"Dear Customer,\\nYour order total is ${t:.2f}.\\nThank you!"
        self.mailer.send(to=o["email"], subject=s, body=b)

        # Generate mini report — not order processing concern
        rpt = {
            "order_id": o["order_id"],
            "items_count": len(x),
            "total": t,
            "discount": d,
            "timestamp": datetime.now().isoformat()
        }
        self.r.append(rpt)

        # Log to file — yet another concern
        with open("orders.log", "a") as f:
            f.write(json.dumps(rpt) + "\\n")

        return {"status": "confirmed", "total": t, "discount": d}

    def get_reports(self):
        return self.r

    def clear_reports(self):
        self.r = []
'''


async def main():
    agent = BaseAgent(agent_dir=Path("agents/build/B5-refactor-assistant"))
    print(f"Agent: {agent.agent_id}")
    print(f"Provider: {agent.provider_name} | Tier: {agent._model_tier.value} | Model: {agent.model}")
    print()

    result = await agent.invoke(
        input_data={
            "file_path": "services/order_manager.py",
            "code_content": MESSY_CODE,
            "language": "python",
            "refactor_goals": ["all"],
            "max_function_lines": 50,
            "max_cyclomatic_complexity": 10,
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

            # --- Check analysis section ---
            analysis = data.get("analysis", {})
            print("=== ANALYSIS ===")
            print(f"  Complexity before: {analysis.get('complexity_before', '?')}")
            print(f"  Complexity after:  {analysis.get('complexity_after', '?')}")
            print(f"  Functions before:  {analysis.get('function_count_before', '?')}")
            print(f"  Functions after:   {analysis.get('function_count_after', '?')}")
            longest = analysis.get("longest_function", {})
            print(f"  Longest function:  {longest.get('name', '?')} ({longest.get('lines', '?')} lines)")
            print(f"  Duplication count: {analysis.get('duplication_count', '?')}")

            has_complexity = (
                analysis.get("complexity_before") is not None
                and analysis.get("complexity_after") is not None
            )
            print(f"\n  [{'PASS' if has_complexity else 'FAIL'}] Analysis has complexity metrics")

            # --- Check refactoring plan ---
            plan = data.get("refactoring_plan", [])
            print(f"\n=== REFACTORING PLAN ({len(plan)} steps) ===")
            ref_ids = []
            types_found = set()
            for step in plan:
                sid = step.get("id", "?")
                ref_ids.append(sid)
                stype = step.get("type", "?")
                types_found.add(stype)
                risk = step.get("risk", "?")
                print(f"  {sid}: {stype} | risk={risk} | {step.get('target', '?')}")

            has_ref_ids = all(re.match(r"REF-\d{3}", rid) for rid in ref_ids) and len(ref_ids) > 0
            print(f"\n  [{'PASS' if has_ref_ids else 'FAIL'}] All steps have REF-NNN IDs")

            has_extract = any("extract" in t for t in types_found)
            has_simplify = any("simplify" in t for t in types_found)
            has_dedup = any("dedup" in t for t in types_found)
            has_rename = any("rename" in t for t in types_found)
            has_split = any("split" in t for t in types_found)

            print(f"  [{'PASS' if has_extract else 'FAIL'}] extract_method detected")
            print(f"  [{'PASS' if has_simplify else 'FAIL'}] simplify_conditionals detected")
            print(f"  [{'PASS' if has_dedup else 'FAIL'}] deduplicate detected")
            print(f"  [{'PASS' if has_rename else 'FAIL'}] rename detected")
            print(f"  [{'PASS' if has_split else 'FAIL'}] split_class detected")

            # --- Check refactored code ---
            refactored = data.get("refactored_code", "")
            has_refactored = len(refactored) > 100
            print(f"\n=== REFACTORED CODE ===")
            print(f"  Length: {len(refactored)} chars")
            print(f"  [{'PASS' if has_refactored else 'FAIL'}] Refactored code is present")

            # Check code is shorter or better structured (more functions)
            original_lines = len(MESSY_CODE.strip().splitlines())
            refactored_lines = len(refactored.strip().splitlines())
            print(f"  Original lines:   {original_lines}")
            print(f"  Refactored lines: {refactored_lines}")

            # --- Check behavioral changes ---
            behavioral = data.get("behavioral_changes", [])
            is_pure = len(behavioral) == 0
            print(f"\n=== BEHAVIORAL CHANGES ===")
            print(f"  Count: {len(behavioral)}")
            if behavioral:
                for bc in behavioral:
                    print(f"    - {bc}")
            print(f"  [{'PASS' if is_pure else 'WARN'}] {'Pure refactoring (no behavior changes)' if is_pure else 'Some behavioral changes noted'}")

            # --- Check test impact ---
            test_impact = data.get("test_impact", [])
            print(f"\n=== TEST IMPACT ===")
            print(f"  Entries: {len(test_impact)}")
            for ti in test_impact:
                print(f"    - {ti}")

            # --- Summary ---
            print("\n=== SUMMARY ===")
            checks = [has_complexity, has_ref_ids, has_refactored, has_extract, has_simplify]
            passed = sum(checks)
            print(f"  Core checks passed: {passed}/{len(checks)}")
            print(f"  Bonus detections: dedup={has_dedup}, rename={has_rename}, split={has_split}")

        else:
            print("WARNING: Could not extract JSON from output")
    except json.JSONDecodeError as e:
        print(f"WARNING: JSON parse error: {e}")

    print()
    print("=== FIRST 3000 CHARS OF RAW OUTPUT ===")
    print(output[:3000])


if __name__ == "__main__":
    asyncio.run(main())
