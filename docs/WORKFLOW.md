Workflow:
- Milestone-driven.
- Each milestone produces a runnable state.
- No milestone is complete without: tests passing + demo command works.

Hard Stop / Loop Break:
Trigger a Loop Break Report if:
- The same next-steps list appears twice with no new artifacts.
- Two consecutive turns without file additions/changes.
- Conflicting requirements are discovered and not resolved in the same turn.

Loop Break Report format:
- Symptom:
- Root cause guess:
- Smallest next action (single command or single file change):
- Acceptance criteria:
- If still blocked, list exactly 2 fallback options.
