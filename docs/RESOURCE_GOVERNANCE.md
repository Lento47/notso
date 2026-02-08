# Resource Governance Plan (Best Practices)

This document defines how the Notso search engine protects itself from resource
exhaustion while keeping searches fast and deterministic. It is intentionally
standard-library only and designed to be enforced by the CLI and HTTP API.

## Workflow A: Memory Guardrails (avoid OOMs / leaks)

**Goal:** Detect rising memory use early and stop work before the process
crashes.

**Mechanism:** `ResourceGuard` in `src/notso/resource_plan.py` tracks peak memory
via `tracemalloc` and compares it against `max_memory_bytes`.

**Steps:**
1. The caller sets `--max-memory-kb` (CLI) or the HTTP query parameter.
2. `ResourceGuard.start()` enables `tracemalloc`.
3. Each block of work calls `checkpoint(...)`.
4. If memory exceeds the limit, the search stops early and returns results so far.

**Done Definition:** When the memory limit is set to a small value, the search
terminates with a `StopReason` of `max_memory_bytes` and continues serving new
requests.

## Workflow B: CPU Budgeting with Work Blocks

**Goal:** Use CPU efficiently and avoid long, blocking loops.

**Mechanism:** Term blocks (see `plan_term_blocks`) and time budgets
(`max_seconds`) allow the search to yield between blocks.

**Steps:**
1. The query terms are ordered by IDF (rarest first).
2. The terms are chunked into blocks (`term_block_size`).
3. After each block, `ResourceGuard.checkpoint(...)` enforces `max_seconds`.
4. If the time budget is exceeded, the search stops early with a stop reason.

**Done Definition:** When `max_seconds` is set to a short duration, the engine
returns partial results and reports `max_seconds` as the stop reason.

## Workflow C: Token Distribution for Faster Searches

**Goal:** Prioritize the most informative tokens and reduce wasted scoring.

**Mechanism:** `plan_query_terms` orders unique terms by IDF so the highest-value
tokens are scored first.

**Steps:**
1. Tokenize the query.
2. Order unique terms by IDF (descending).
3. Apply `max_query_terms` to keep only the highest-impact tokens.
4. Score documents using only the selected tokens.

**Done Definition:** Limiting `max_query_terms` reduces work while maintaining
relevance for the top results.

## Workflow D: Safe Degradation Under Heavy Load

**Goal:** Prevent the entire app from crashing when resources are constrained.

**Mechanism:** `StopReason` returns a deterministic reason to the caller so the
system can fall back safely.

**Steps:**
1. The search starts with explicit limits.
2. Any limit breach triggers a `StopReason`.
3. The engine returns the best results computed so far.
4. The CLI/API surfaces the stop reason to the user or logs it.

**Done Definition:** Under artificial stress (tiny limits), the engine exits
gracefully and remains responsive to subsequent searches.
