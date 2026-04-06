"""Live test of D21-compliance-matrix-writer — Compliance Matrix."""

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
    agent = BaseAgent(agent_dir=Path("agents/design/D21-compliance-matrix-writer"))
    print(f"Agent: {agent.agent_id}")
    print(f"Provider: {agent.provider_name} | Tier: {agent._model_tier.value} | Model: {agent.model}")
    print()

    result = await agent.invoke(
        input_data={
            "project_name": "FleetOps",
            "regulatory_frameworks": [
                "SOC2",
                "GDPR",
                "EU_AI_ACT",
                "NIST_AI_RMF",
            ],
            "security_controls": [
                {"control_id": "SC-001", "description": "Role-based access control for all agent endpoints", "category": "Access Control"},
                {"control_id": "SC-002", "description": "TLS 1.3 encryption for data in transit", "category": "Encryption"},
                {"control_id": "SC-003", "description": "AES-256 encryption for data at rest", "category": "Encryption"},
                {"control_id": "SC-004", "description": "PII detection and redaction pipeline", "category": "Data Protection"},
                {"control_id": "SC-005", "description": "Audit trail with immutable append-only logging", "category": "Audit"},
                {"control_id": "SC-006", "description": "Network segmentation between agent tiers", "category": "Network Security"},
            ],
            "quality_nfrs": [
                "Q-001",
                "Q-002",
                "Q-003",
                "Q-004",
                "Q-005",
            ],
            "data_entities": [
                {"name": "UserProfile", "classification": "Confidential"},
                {"name": "AgentConfig", "classification": "Internal"},
                {"name": "AuditLog", "classification": "Restricted"},
                {"name": "GeneratedDocument", "classification": "Internal"},
                {"name": "LLMCallRecord", "classification": "Confidential"},
            ],
            "guardrails": [
                {"id": "IG-001", "layer": "Input", "description": "Prompt injection detection"},
                {"id": "IG-002", "layer": "Input", "description": "PII/sensitive data filtering"},
                {"id": "PG-001", "layer": "Processing", "description": "Token budget enforcement"},
                {"id": "OG-001", "layer": "Output", "description": "Hallucination detection"},
                {"id": "GG-001", "layer": "Governance", "description": "Kill switch"},
                {"id": "GG-002", "layer": "Governance", "description": "Human-in-the-loop gates"},
            ],
            "fault_tolerance_scenarios": [
                "P0: Total LLM provider outage — all providers unreachable",
                "P0: Data corruption in audit trail — immutable log tampered",
                "P1: Single agent timeout cascade — downstream agents stalled",
                "P1: Rate limit exceeded on primary provider — failover triggered",
                "P1: Kill switch false positive — pipeline halted unnecessarily",
            ],
            "features": [
                "F-001",
                "F-002",
                "F-003",
                "F-004",
                "F-005",
                "F-006",
                "F-007",
                "F-008",
            ],
        },
        project_id="fleetops-021",
    )

    print(f"Cost:     ${result['cost_usd']:.4f}")
    print(f"Tokens:   {result['input_tokens']} in / {result['output_tokens']} out")
    print(f"Duration: {result['duration_ms']}ms ({result['duration_ms']/1000:.1f}s)")
    print(f"Provider: {result['provider']} | Tier: {result['model_tier']}")
    print()

    output = result["output"]

    # == 10 Sections present ===================================================
    sections = [
        "Applicable Frameworks",
        "SOC 2 Trust Service Criteria",
        "GDPR Article Mapping",
        "EU AI Act",
        "NIST AI Risk Management",
        "Control-to-Feature Cross-Reference",
        "Evidence Collection",
        "Audit Readiness Checklist",
        "Exception Log",
        "Compliance Review Schedule",
    ]
    found_sections = []
    missing_sections = []
    for section in sections:
        if section.lower() in output.lower():
            found_sections.append(section)
        else:
            missing_sections.append(section)
    print(f"Sections: {len(found_sections)}/{len(sections)}")
    if missing_sections:
        print(f"  MISSING: {missing_sections}")
    else:
        print(f"  PASS: All 10 sections present")

    # == SOC 2 Trust Service Criteria ==========================================
    has_cc6 = bool(re.search(r"CC6", output))
    has_a1 = bool(re.search(r"A1", output))
    has_pi1 = bool(re.search(r"PI1", output))
    has_c1 = bool(re.search(r"C1", output))
    has_p1 = bool(re.search(r"P1", output))
    soc2_categories = {"CC6": has_cc6, "A1": has_a1, "PI1": has_pi1, "C1": has_c1, "P1": has_p1}
    soc2_found = [k for k, v in soc2_categories.items() if v]
    soc2_missing = [k for k, v in soc2_categories.items() if not v]
    print(f"SOC 2 TSC categories:")
    print(f"  Found: {len(soc2_found)}/5 — {soc2_found}")
    if soc2_missing:
        print(f"  MISSING: {soc2_missing}")
    else:
        print(f"  PASS: All 5 SOC 2 categories present")

    # Count SOC 2 control rows (lines with TSC IDs in tables)
    soc2_rows = len(re.findall(r"\|\s*(?:CC|A1|PI|C1|P1)\S*\s*\|", output))
    print(f"  SOC 2 control rows: {soc2_rows}")
    print(f"  Minimum 20 controls: {'PASS' if soc2_rows >= 20 else 'FAIL — got ' + str(soc2_rows)}")

    # == GDPR Articles =========================================================
    has_art5 = bool(re.search(r"Article\s*5|Art\.?\s*5", output))
    has_art17 = bool(re.search(r"Article\s*17|Art\.?\s*17", output))
    has_art25 = bool(re.search(r"Article\s*25|Art\.?\s*25", output))
    has_art32 = bool(re.search(r"Article\s*32|Art\.?\s*32", output))
    gdpr_articles = {"Art 5": has_art5, "Art 17": has_art17, "Art 25": has_art25, "Art 32": has_art32}
    gdpr_found = [k for k, v in gdpr_articles.items() if v]
    gdpr_missing = [k for k, v in gdpr_articles.items() if not v]
    print(f"GDPR key articles:")
    print(f"  Found: {len(gdpr_found)}/4 — {gdpr_found}")
    if gdpr_missing:
        print(f"  MISSING: {gdpr_missing}")
    else:
        print(f"  PASS: All key GDPR articles present")

    # Count total GDPR article rows
    gdpr_rows = len(re.findall(r"\|\s*(?:Article\s*\d+|Art\.?\s*\d+)", output))
    print(f"  GDPR article rows: {gdpr_rows}")
    print(f"  Minimum 10 articles: {'PASS' if gdpr_rows >= 10 else 'FAIL — got ' + str(gdpr_rows)}")

    # == EU AI Act with guardrail references ===================================
    has_eu_ai_act = "eu ai act" in output.lower()
    has_risk_classification = "risk classification" in output.lower() or "risk level" in output.lower()
    has_transparency = "transparency" in output.lower()
    has_human_oversight = "human oversight" in output.lower()
    has_technical_doc = "technical documentation" in output.lower()
    has_quality_mgmt = "quality management" in output.lower()
    has_post_market = "post-market" in output.lower() or "post market" in output.lower()

    eu_ai_reqs = {
        "Risk Classification": has_risk_classification,
        "Transparency": has_transparency,
        "Human Oversight": has_human_oversight,
        "Technical Documentation": has_technical_doc,
        "Quality Management": has_quality_mgmt,
        "Post-Market Monitoring": has_post_market,
    }
    eu_ai_found = [k for k, v in eu_ai_reqs.items() if v]
    eu_ai_missing = [k for k, v in eu_ai_reqs.items() if not v]
    print(f"EU AI Act requirements:")
    print(f"  Section present: {'PASS' if has_eu_ai_act else 'FAIL'}")
    print(f"  Found: {len(eu_ai_found)}/6 — {eu_ai_found}")
    if eu_ai_missing:
        print(f"  MISSING: {eu_ai_missing}")
    else:
        print(f"  PASS: All 6 EU AI Act requirements present")

    # Check guardrail references in EU AI Act section
    ig_refs = sorted(set(re.findall(r"IG-\d{3}", output)))
    pg_refs = sorted(set(re.findall(r"PG-\d{3}", output)))
    og_refs = sorted(set(re.findall(r"OG-\d{3}", output)))
    gg_refs = sorted(set(re.findall(r"GG-\d{3}", output)))
    all_guardrail_refs = ig_refs + pg_refs + og_refs + gg_refs
    print(f"  Guardrail IDs referenced: {len(all_guardrail_refs)} — {all_guardrail_refs}")
    print(f"  IG-001 referenced: {'PASS' if 'IG-001' in ig_refs else 'FAIL'}")
    print(f"  GG-001 referenced: {'PASS' if 'GG-001' in gg_refs else 'FAIL'}")
    print(f"  GG-002 referenced: {'PASS' if 'GG-002' in gg_refs else 'FAIL'}")

    # == NIST AI RMF 4 functions ===============================================
    has_govern = bool(re.search(r"\bgovern\b", output, re.IGNORECASE))
    has_map = bool(re.search(r"\bmap\b", output, re.IGNORECASE))
    has_measure = bool(re.search(r"\bmeasure\b", output, re.IGNORECASE))
    has_manage = bool(re.search(r"\bmanage\b", output, re.IGNORECASE))
    nist_functions = {"Govern": has_govern, "Map": has_map, "Measure": has_measure, "Manage": has_manage}
    nist_found = [k for k, v in nist_functions.items() if v]
    nist_missing = [k for k, v in nist_functions.items() if not v]
    print(f"NIST AI RMF functions:")
    print(f"  Found: {len(nist_found)}/4 — {nist_found}")
    if nist_missing:
        print(f"  MISSING: {nist_missing}")
    else:
        print(f"  PASS: All 4 NIST functions present")

    # == Control-to-Feature cross-reference (F-NNN) ============================
    feature_refs = sorted(set(re.findall(r"F-\d{3}", output)))
    print(f"Control-to-Feature cross-reference:")
    print(f"  Feature IDs found: {len(feature_refs)} — {feature_refs}")
    print(f"  F-001 present: {'PASS' if 'F-001' in feature_refs else 'FAIL'}")
    print(f"  F-008 present: {'PASS' if 'F-008' in feature_refs else 'FAIL'}")
    print(f"  Minimum 5 features: {'PASS' if len(feature_refs) >= 5 else 'FAIL — got ' + str(len(feature_refs))}")

    # == Evidence collection procedures ========================================
    has_evidence = "evidence collection" in output.lower() or "evidence" in output.lower()
    has_automated = "automated" in output.lower()
    has_manual = "manual" in output.lower()
    has_retention = "retention" in output.lower()
    print(f"Evidence collection:")
    print(f"  Section present: {'PASS' if has_evidence else 'FAIL'}")
    print(f"  Automated collection: {'PASS' if has_automated else 'FAIL'}")
    print(f"  Manual collection: {'PASS' if has_manual else 'FAIL'}")
    print(f"  Retention mentioned: {'PASS' if has_retention else 'FAIL'}")

    # == Audit readiness checklist =============================================
    has_audit_checklist = "audit readiness" in output.lower() or "audit checklist" in output.lower()
    has_pen_test = "penetration test" in output.lower() or "pen test" in output.lower()
    has_ai_safety_assessment = "ai safety assessment" in output.lower() or "ai safety" in output.lower()
    print(f"Audit readiness checklist:")
    print(f"  Section present: {'PASS' if has_audit_checklist else 'FAIL'}")
    print(f"  Pen test item: {'PASS' if has_pen_test else 'FAIL'}")
    print(f"  AI safety assessment: {'PASS' if has_ai_safety_assessment else 'FAIL'}")

    # == Exception log with expiry =============================================
    has_exception_log = "exception log" in output.lower() or "exception" in output.lower()
    ex_ids = sorted(set(re.findall(r"EX-\d{3}", output)))
    has_expiry = "expiry" in output.lower() or "expiration" in output.lower()
    has_remediation = "remediation" in output.lower()
    print(f"Exception log:")
    print(f"  Section present: {'PASS' if has_exception_log else 'FAIL'}")
    print(f"  Exception IDs (EX-NNN): {len(ex_ids)} — {ex_ids}")
    print(f"  Expiry dates present: {'PASS' if has_expiry else 'FAIL'}")
    print(f"  Remediation plans: {'PASS' if has_remediation else 'FAIL'}")
    print(f"  No permanent exceptions: {'PASS' if 'permanent' not in output.lower() or 'no permanent' in output.lower() else 'CHECK — word permanent found'}")

    # == Compliance review schedule ============================================
    has_review_schedule = "review schedule" in output.lower() or "compliance review" in output.lower()
    has_quarterly = "quarterly" in output.lower()
    has_annual = "annual" in output.lower()
    has_monthly = "monthly" in output.lower()
    print(f"Compliance review schedule:")
    print(f"  Section present: {'PASS' if has_review_schedule else 'FAIL'}")
    print(f"  Quarterly reviews: {'PASS' if has_quarterly else 'FAIL'}")
    print(f"  Annual reviews: {'PASS' if has_annual else 'FAIL'}")
    print(f"  Monthly reviews: {'PASS' if has_monthly else 'FAIL'}")

    # == Status values =========================================================
    has_implemented = "implemented" in output.lower()
    has_partially = "partially implemented" in output.lower()
    has_planned = "planned" in output.lower()
    has_na = "not applicable" in output.lower() or "N/A" in output
    status_values = {
        "Implemented": has_implemented,
        "Partially Implemented": has_partially,
        "Planned": has_planned,
        "Not Applicable / N-A": has_na,
    }
    status_found = [k for k, v in status_values.items() if v]
    print(f"Status values used:")
    print(f"  Found: {len(status_found)}/4 — {status_found}")
    print(f"  At least 3 status types: {'PASS' if len(status_found) >= 3 else 'FAIL — got ' + str(len(status_found))}")

    # == Security control IDs referenced =======================================
    sc_ids = sorted(set(re.findall(r"SC-\d{3}", output)))
    print(f"Security control IDs (SC-NNN):")
    print(f"  Found: {len(sc_ids)} — {sc_ids}")
    print(f"  Minimum 4 referenced: {'PASS' if len(sc_ids) >= 4 else 'FAIL — got ' + str(len(sc_ids))}")

    # == Quality NFR IDs referenced ============================================
    q_ids = sorted(set(re.findall(r"Q-\d{3}", output)))
    print(f"Quality NFR IDs (Q-NNN):")
    print(f"  Found: {len(q_ids)} — {q_ids}")

    # == Markdown tables present ===============================================
    table_rows = len(re.findall(r"^\|.*\|$", output, re.MULTILINE))
    print(f"Markdown table rows: {table_rows}")
    print(f"  Tables present (30+ rows): {'PASS' if table_rows >= 30 else 'FAIL — got ' + str(table_rows)}")

    # == Frameworks referenced =================================================
    frameworks_found = []
    for fw in ["SOC 2", "SOC2", "GDPR", "EU AI Act", "NIST AI RMF", "NIST"]:
        if fw.lower() in output.lower():
            frameworks_found.append(fw)
    print(f"Frameworks referenced: {frameworks_found}")
    print(f"  All 4 frameworks: {'PASS' if len(frameworks_found) >= 4 else 'FAIL'}")

    # == Data entities referenced ==============================================
    entities_found = []
    for entity in ["UserProfile", "AgentConfig", "AuditLog", "GeneratedDocument", "LLMCallRecord"]:
        if entity.lower() in output.lower():
            entities_found.append(entity)
    print(f"Data entities referenced: {len(entities_found)}/5 — {entities_found}")

    # == Fault tolerance scenarios =============================================
    has_fault = "fault" in output.lower() or "outage" in output.lower() or "failover" in output.lower() or "disaster" in output.lower()
    print(f"Fault tolerance context: {'PASS' if has_fault else 'FAIL'}")

    print()
    print("=== FIRST 3000 CHARS ===")
    print(output[:3000])


if __name__ == "__main__":
    asyncio.run(main())
