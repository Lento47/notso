#!/usr/bin/env python3
from __future__ import annotations

import ast
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN_FILES = {
    "requirements.txt",
    "Pipfile",
    "Pipfile.lock",
    "poetry.lock",
    "package.json",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
}

# Adjust if you want to allow more/less.
ALLOWED_IMPORT_PREFIXES = (
    "notso",  # your local package
)

# Python stdlib “rough allowlist”: we’ll permit any import that resolves to stdlib-ish
# by allowing common modules; and also permit relative imports and local package.
# If you want ultra-strict, replace this with an explicit allowlist.
COMMON_STDLIB = {
    "argparse","collections","dataclasses","datetime","functools","hashlib","html",
    "http","io","json","logging","math","os","pathlib","re","shlex","socket",
    "sqlite3","statistics","struct","sys","time","typing","unittest","urllib","uuid"
}

def is_stdlib(mod: str) -> bool:
    top = mod.split(".", 1)[0]
    return top in COMMON_STDLIB

def scan_forbidden_files() -> list[str]:
    found = []
    for p in REPO_ROOT.rglob("*"):
        if p.is_file() and p.name in FORBIDDEN_FILES:
            found.append(str(p.relative_to(REPO_ROOT)))
    return found

def scan_imports() -> list[str]:
    problems = []
    for py in REPO_ROOT.rglob("*.py"):
        if any(part in (".venv", "venv", "__pycache__", "dist", "build") for part in py.parts):
            continue
        try:
            tree = ast.parse(py.read_text(encoding="utf-8"), filename=str(py))
        except SyntaxError as e:
            problems.append(f"{py.relative_to(REPO_ROOT)}: syntax error: {e}")
            continue

        for node in ast.walk(tree):
            mod = None
            if isinstance(node, ast.Import):
                for alias in node.names:
                    mod = alias.name
                    if not (is_stdlib(mod) or mod.startswith(ALLOWED_IMPORT_PREFIXES)):
                        problems.append(f"{py.relative_to(REPO_ROOT)}: disallowed import '{mod}'")
            elif isinstance(node, ast.ImportFrom):
                if node.level and node.level > 0:
                    continue  # relative import OK
                mod = node.module or ""
                if mod and not (is_stdlib(mod) or mod.startswith(ALLOWED_IMPORT_PREFIXES)):
                    problems.append(f"{py.relative_to(REPO_ROOT)}: disallowed import-from '{mod}'")
    return problems

def main() -> int:
    bad_files = scan_forbidden_files()
    bad_imports = scan_imports()

    if bad_files:
        print("Dependency gate failed: forbidden dependency files found:")
        for f in bad_files:
            print(f"  - {f}")

    if bad_imports:
        print("Dependency gate failed: disallowed imports found:")
        for p in bad_imports:
            print(f"  - {p}")

    if bad_files or bad_imports:
        return 1

    print("Dependency gate passed.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
