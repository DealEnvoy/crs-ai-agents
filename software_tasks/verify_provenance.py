#!/usr/bin/env python3
"""Independent check: every 'verbatim' pack line is a substring of the REDACTED source line it claims,
and the pack file contains that exact line. Also re-scans packs for redaction leaks.
Exit code 1 on any failure."""
import json, os, sys, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_software_packs import redact, REPO, FORBIDDEN_IN_PACK, T
ROOT = os.path.dirname(os.path.abspath(__file__))
bad = 0; n = 0
for t in T:
    prov = json.load(open(os.path.join(ROOT, t["folder"], "provenance.json")))
    for variant in ("faulty", "clean"):
        pack = open(os.path.join(ROOT, t["folder"], variant, "pack.md")).read()
        for e in prov[variant]:
            n += 1
            full = "[%s] %s" % (e["line_id"], e["text"])
            if full not in pack:
                print("PACK MISSING LINE", t["task_id"], variant, e["line_id"]); bad += 1
            if e["kind"] == "verbatim":
                srcf = os.path.join(REPO, e["src"])
                line = open(srcf, encoding="utf-8").read().split("\n")[e["src_line"] - 1]
                if e["text"] not in redact(line):
                    print("NOT VERBATIM", t["task_id"], variant, e["line_id"], e["src"], e["src_line"]); bad += 1
        for pat in FORBIDDEN_IN_PACK:
            if re.search(pat, pack):
                print("LEAK", t["task_id"], variant, pat); bad += 1
kinds = {}
for t in T:
    prov = json.load(open(os.path.join(ROOT, t["folder"], "provenance.json")))
    for variant in ("faulty", "clean"):
        for e in prov[variant]:
            kinds[(t["task_id"], variant, e["kind"])] = kinds.get((t["task_id"], variant, e["kind"]), 0) + 1
for k in sorted(kinds): print(k, kinds[k])
print("checked", n, "lines;", "FAIL" if bad else "ALL OK")
sys.exit(1 if bad else 0)
