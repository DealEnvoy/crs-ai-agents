#!/usr/bin/env python3
"""Checks the AAIB source list (aaib_sources.json).

  python3 verify_sources.py            offline: every entry has a gov.uk report page and a PDF link, and every quote is short (<= 40 words)
  python3 verify_sources.py --fetch    also downloads each official PDF, extracts its text with `pdftotext -raw` (poppler-utils)
                                       and checks that every quote appears verbatim (whitespace, hyphen and quote-mark variants normalised)

The full report texts are not kept in this repository; only links and the short quotes are.
"""
import json, os, re, subprocess, sys, tempfile, urllib.request
ROOT = os.path.dirname(os.path.abspath(__file__))
MAX_WORDS = 40
def norm(s):
    s = s.replace("\u2011", "-").replace("\u2010", "-").replace("\u2013", "-").replace("\u2019", "'").replace("\u2018", "'")
    s = s.replace("\u201c", '"').replace("\u201d", '"').replace("\u00ad", "")
    s = re.sub(r"-\s*\n\s*", "-", s)
    return re.sub(r"\s+", " ", s).strip()
fetch = "--fetch" in sys.argv
data = json.load(open(os.path.join(ROOT, "aaib_sources.json"), encoding="utf-8"))
bad = 0
for k, v in data.items():
    if k.startswith("_note"):
        continue
    ok_links = v["page_url"].startswith("https://www.gov.uk/aaib-reports/") and v["pdf_url"].startswith("https://") and v["pdf_url"].endswith(".pdf")
    print(("OK  " if ok_links else "FAIL"), k, "links present:", v["page_url"]); bad += (not ok_links)
    txt = None
    if fetch:
        req = urllib.request.Request(v["pdf_url"], headers={"User-Agent": "Mozilla/5.0 (verify_sources.py)"})
        with tempfile.TemporaryDirectory() as td:
            pdf = os.path.join(td, "r.pdf")
            open(pdf, "wb").write(urllib.request.urlopen(req, timeout=120).read())
            txt = norm(subprocess.run(["pdftotext", "-raw", pdf, "-"], capture_output=True, text=True, check=True).stdout)
    for q in v["quotes"]:
        ok = len(q.split()) <= MAX_WORDS and (txt is None or norm(q) in txt)
        print("   ", "OK  " if ok else "FAIL", ("verbatim in PDF; " if fetch else "") + f"{len(q.split())} words:", q[:70])
        bad += (not ok)
sys.exit(1 if bad else 0)
