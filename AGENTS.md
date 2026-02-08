# Notso Search Engine — Agent Instructions (AGENTS.md)

## Non-negotiables
- Standard library only. No pip/npm/cargo/maven/go modules.
- Everything functional must be implemented in this repo by us.
- No copying code from the internet. Re-implement from first principles.
- Every major module must include at least one deterministic unit test.
- Every response must update or add files (unless producing a Loop Break Report).

## Loop avoidance
If you detect repetition or no net progress:
1) Stop immediately.
2) Output a “Loop Break Report”:
   - Symptom
   - Root cause guess
   - Smallest next action (one file change or one command)
   - Acceptance criteria
   - Exactly 2 fallback options

## Repo commands
- Run tests: `python -m unittest -q`
- Build index demo: `python tools/build_index.py`
- Run server: `python -m notso.serve.httpd`
- CLI search: `python -m notso.cli search "query"`

## Architecture rules
- Keep modules small and focused.
- Public interfaces must be documented (function signatures + docstrings).
- Storage formats must be versioned and documented under `src/notso/storage/formats.md`.
