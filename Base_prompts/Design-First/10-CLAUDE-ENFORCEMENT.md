# Prompt 10 — Generate .claude/ Enforcement Layer

## Role
You are an enforcement scaffolder agent. You produce the .claude/ directory — Document #10 in DynPro's 12-document SDLC stack. This directory contains the rules that Claude Code follows when writing code in this repo. It's the automated enforcement of CLAUDE.md's rules.

## Input Required
- CLAUDE.md (rules to enforce — Python rules, TypeScript rules, forbidden patterns)
- ARCH.md (which languages and frameworks are used)
- Repo structure (which directories contain which types of files)

## Output: .claude/ directory structure

```
.claude/
├── settings.json       # Hooks configuration (pre-commit, pre-push)
├── rules/
│   ├── python.md       # Activates on **/*.py
│   ├── typescript.md   # Activates on **/*.ts, **/*.tsx
│   ├── agents.md       # Activates on agents/**/*
│   └── schemas.md      # Activates on packages/schemas/**/*
└── skills/
    ├── new-agent.md    # /new-agent slash command
    └── new-test.md     # /new-test slash command
```

### settings.json
```json
{
  "hooks": {
    "pre-commit": ["<validation commands>"],
    "pre-push": ["<test commands>"]
  },
  "rules_dir": ".claude/rules",
  "skills_dir": ".claude/skills"
}
```

### Rule Files
Each rule file:
- Title with activation glob pattern (e.g., "Activates on **/*.py")
- Bulleted list of imperative rules
- Rules must be from CLAUDE.md — this file ENFORCES, doesn't add new rules
- Keep rules concise — one line each
- Rules must be machine-checkable (Claude Code evaluates each rule against generated code)

### Skill Files
Each skill file:
- Usage line (slash command + arguments)
- Numbered steps the skill executes
- File creation patterns with templates
- Validation step at the end

### Quality Criteria
- Every rule in CLAUDE.md's language sections has a corresponding line in the appropriate rule file
- Glob patterns are correct (test with actual file paths)
- Skills produce valid file structures when executed
- settings.json hooks reference commands that exist in the repo
- No rules contradict each other across files
- Rules are concise enough that Claude Code can evaluate them quickly
