#!/usr/bin/env python3
"""Publish the archive to Google Drive.

For every catalog entry the script:
  * de-duplicates: an observation is kept once, at its highest-resolution encoding;
  * uploads the image (original bytes, untouched) into its thematic folder;
  * uploads the calibrated FITS product next to the render it produced;
  * attaches a scientific caption comment (explanation, measured properties,
    wavelength, source, attribution/licence).
Progress is journaled to ``state.json`` so the run can be resumed safely.
"""
import json
import os
import sys
import time
import urllib.request
import urllib.error
import subprocess
import hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import catalog  # noqa: E402

STATE = os.path.join(HERE, "state.json")
API = "https://api-docs.arena.ai/v1/files/"
MODEL = "claude-sonnet-4-5"


def load_state():
    if os.path.exists(STATE):
        return json.load(open(STATE))
    return {"uploads": {}, "comments": {}, "skipped": []}


def dump_state(st):
    json.dump(st, open(STATE, "w"), indent=1, ensure_ascii=False)


def api_key():
    for p in ("/home/user/.config/arena/api_key", "/etc/arena/api_key"):
        if os.path.exists(p):
            return open(p).read().strip()
    return os.environ.get("ARENA_API_KEY", "")


def post_file(path, name):
    """Upload a local file to the connector file store; returns a file id."""
    boundary = "----archive" + hashlib.sha1(name.encode()).hexdigest()[:12]
    data = open(path, "rb").read()
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{name}"\r\n'
        f"Content-Type: application/octet-stream\r\n\r\n"
    ).encode() + data + f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(API, data=body, method="POST",
                                 headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    with urllib.request.urlopen(req, timeout=600) as r:
        j = json.load(r)
    return j.get("id") or j.get("file", {}).get("id"), j


def caption(e):
    """Scientific caption in Arabic, ready to be posted as a Drive comment."""
    props = e.get("props") or ""
    txt = (
        f"**{e['name']}**\n\n"
        f"التفسير العلمي: {e.get('science', '').strip()}\n\n"
        f"الخصائص المرصودة: {props}\n\n"
        f"الطول الموجي / النطاق: {e['wl']}\n\n"
        f"المصدر: {e['src']} — {e['telescope']} ({e['instrument']}) — تاريخ الرصد: {e['date']}\n\n"
        f"حقوق النسب: {e['credit']} — الرخصة: {e['license']}\n\n"
        f"ملف: {os.path.basename(e['file'])} — SHA1: {e['sha1'][:16]}…"
    )
    return txt[:4000]


def main():
    st = load_state()
    ents = catalog.build()
    print(f"{len(ents)} catalog entries")
    for e in ents:
        print(f"{e['bytes']/1e6:7.1f}MB  {e['name'][:60]}")


if __name__ == "__main__":
    main()
