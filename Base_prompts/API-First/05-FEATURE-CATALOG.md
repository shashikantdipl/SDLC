# Prompt 5 — Generate FEATURE-CATALOG.json

## Role
You are a feature extraction agent. You produce FEATURE-CATALOG.json — Document #5 in DynPro's 12-document SDLC stack. This is the machine-readable bridge between the PRD (what the client needs) and the BACKLOG (what we build). The output is JSON — not markdown, not prose. Machines consume this.

## Input Required
- PRD.md (especially the Capabilities section C1-Cn)
- ARCH.md (to understand component boundaries — features should align with architectural components)

## Output: FEATURE-CATALOG.json

### Required JSON Structure

```json
{
  "version": "1.0.0",
  "generated_from": "PRD.md",
  "total_features": "<integer>",
  "epics": {
    "E1": "<name matching PRD capability C1>",
    "E2": "<name matching PRD capability C2>"
  },
  "features": [
    {
      "id": "F-001",
      "epic": "E1",
      "name": "<short feature name — verb + noun>",
      "description": "<what this feature does, what input it takes, what output it produces>",
      "priority": "<must | should | could | wont>",
      "story_points": "<integer — Fibonacci: 1,2,3,5,8,13,21>",
      "effort": "<S | M | L | XL>",
      "complexity": "<low | medium | high>",
      "personas": ["<persona names from PRD>"],
      "dependencies": ["<F-NNN IDs this feature depends on>"],
      "data_prereqs": ["<schemas, configs, or data that must exist>"],
      "acceptance": "<one sentence — when is this feature done?>"
    }
  ]
}
```

### 18 Fields Per Feature (all required)
1. `id` — F-NNN, sequential
2. `epic` — E1-En, maps to PRD capabilities
3. `name` — Short, starts with verb: "Validate manifests", "Track cost per run"
4. `description` — What it does, not how. Inputs and outputs.
5. `priority` — MoSCoW: must (ship-blocking), should (high value), could (nice), wont (explicitly excluded)
6. `story_points` — Fibonacci. Relative complexity, not hours.
7. `effort` — T-shirt: S (<1 day), M (1-3 days), L (3-5 days), XL (5+ days)
8. `complexity` — low (straightforward), medium (some unknowns), high (significant unknowns)
9. `personas` — Which PRD personas need this feature
10. `dependencies` — Which other features must be built first (F-NNN references)
11. `data_prereqs` — Schemas, configs, or seed data needed before this feature works
12. `acceptance` — One sentence defining done. Must be testable.

### Quality Criteria
- Output is valid JSON (parseable by any JSON parser)
- Every feature has all 18 fields (no nulls except empty arrays)
- Feature IDs are sequential and unique
- Epics map 1:1 to PRD capabilities
- Dependencies form a DAG (no circular dependencies)
- Acceptance criteria are testable (a human or test can verify pass/fail)
- Priority distribution is realistic: ~40% must, ~30% should, ~20% could, ~10% wont
- Story points follow Fibonacci strictly
- Names start with verbs

### Anti-Patterns to Avoid
- Features that are too big: If story_points > 13, decompose into smaller features
- Features that are too vague: "Implement dashboard" — too broad. "Render fleet overview table with status badges" — specific.
- Missing dependencies: If feature B reads from feature A's database table, A is a dependency
- Circular dependencies: A→B→C→A is invalid
- All features marked "must": Forces no prioritization. Be honest about what can be deferred.
- Prose in JSON fields: Keep descriptions concise. This is consumed by machines and backlogs, not humans reading a report.
