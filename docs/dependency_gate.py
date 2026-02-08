Option A: Dependency Gate

“Fail the build if any import is not from stdlib or local package.”

Option B: Vendor Scanner

“Search repo for pip install, npm install, requirements.txt, package.json, and block if found.”

Option C: Explicit allowlist

In Python: allow imports only from sys, os, re, math, json, html, urllib, http, pathlib, argparse, hashlib, struct, sqlite3 (optional), unittest, dataclasses, typing, time, logging.
