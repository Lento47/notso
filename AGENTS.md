# Notso Search Engine — Codex Contract (AGENTS.md)

## Non-negotiables: “Built by us”
- Standard library only. No pip/npm/cargo/maven/go modules.
- Do not add dependency files (requirements.txt, pyproject deps, package.json, etc).
- All functional code must live in this repo and be authored here.
- No copying code from the internet.

## Must-haves
- CLI + minimal HTTP API + tiny web UI (vanilla HTML/CSS/JS).
- On-disk storage format documented and versioned.
- Tests for every major module; deterministic.
- Demo docs + demo command.

## Anti-loop: STOP rules
If you detect repetition or no net progress:
1) Stop immediately.
2) Output a Loop Break Report:
   - Symptom
   - Root cause guess
   - Smallest next action (one file change or one command)
   - Acceptance criteria
   - Exactly 2 fallback options

## Response format (every time)
- Work Completed
- Next Actions (max 7)
- Artifacts Updated/Added (paths)

## Where to find the full specs
- Master prompt: docs/MASTER_PROMPT.md
- Workflow: docs/WORKFLOW.md
- Repo blueprint: docs/REPO_BLUEPRINT.md
- Agent prompts: docs/AGENTS/
- Enforcement: tools/dependency_gate.py + tools/run_checks.py
