#!/usr/bin/env python3
import subprocess
import sys

def run(cmd: list[str]) -> int:
    print("+", " ".join(cmd))
    return subprocess.call(cmd)

def main() -> int:
    rc = run([sys.executable, "tools/dependency_gate.py"])
    if rc != 0:
        return rc
    rc = run([sys.executable, "-m", "unittest", "-q"])
    return rc

if __name__ == "__main__":
    raise SystemExit(main())
