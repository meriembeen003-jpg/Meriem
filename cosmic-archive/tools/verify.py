#!/usr/bin/env python3
"""Re-hash every archived file and compare with MANIFEST.csv."""
import csv, hashlib, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bad, n = [], 0
for row in csv.DictReader(open(os.path.join(ROOT, "MANIFEST.csv"), encoding="utf-8")):
    p = os.path.join(ROOT, row["file"]); n += 1
    if not os.path.exists(p):
        bad.append((row["file"], "missing")); continue
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    if h.hexdigest() != row["sha256"]:
        bad.append((row["file"], "sha256 mismatch"))
    elif os.path.getsize(p) != int(row["bytes"]):
        bad.append((row["file"], "size mismatch"))
print(f"checked {n} files; problems: {len(bad)}")
for f, why in bad: print(" ", why, f)
sys.exit(1 if bad else 0)
