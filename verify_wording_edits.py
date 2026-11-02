#!/usr/bin/env python3
"""Proves that the files listed in wording_edits.json differ from the self-registered versions only by the documented edits.

For each file, the edits are reversed using a private mapping (the removed original text, not published) and the sha256 of the
rebuilt original is compared with the digest in every PREREG_HASHES*.txt list that names the file.

Usage: python3 verify_wording_edits.py --private PATH_TO_wording_edits_private.json
       (or set WORDING_EDITS_PRIVATE). Without the private file the check is skipped and says so.
Exit code 0 = every rebuilt original matched; 1 = a mismatch; 2 = private file not supplied.
"""
import hashlib, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
LISTS = ["PREREG_HASHES.txt", "PREREG_HASHES_post_run.txt", "PREREG_HASHES_v2.txt", "PREREG_HASHES_v2_post_run.txt"]

def load_private(path=None):
    path = path or os.environ.get("WORDING_EDITS_PRIVATE")
    if not path:
        for a, b in zip(sys.argv, sys.argv[1:]):
            if a == "--private": path = b
    return json.load(open(path, encoding="utf-8")) if path and os.path.exists(path) else None

def digests(rel):
    out = {}
    for lst in LISTS:
        for line in open(os.path.join(HERE, lst), encoding="utf-8"):
            parts = line.split(None, 1)
            if len(parts) == 2 and parts[1].strip() == rel:
                out[lst] = parts[0]
    return out

def rebuild(entry, priv):
    text = open(os.path.join(HERE, entry["file"]), encoding="utf-8", newline="").read()
    for h in priv["hunks"][entry["file"]]:
        assert text.count(h["new"]) == 1, "hunk not found exactly once"
        text = text.replace(h["new"], h["old"], 1)
    return text

def check_all(priv, quiet=False):
    """Returns {file: {list: bool}}"""
    res = {}
    for e in json.load(open(os.path.join(HERE, "wording_edits.json")))["files"]:
        d = digests(e["file"])
        orig = hashlib.sha256(rebuild(e, priv).encode("utf-8")).hexdigest()
        res[e["file"]] = {l: (orig == dg) for l, dg in d.items()}
        if not quiet:
            if not d:
                print(f"  NOTE  {e['file']}: not in any hash list (rebuilt sha256 {orig[:16]}...)")
            for l, ok in res[e["file"]].items():
                print(f"  {'PASS' if ok else 'FAIL'}  {e['file']}  rebuilt original == digest in {l}")
    return res

if __name__ == "__main__":
    priv = load_private()
    if not priv:
        print("SKIPPED: private mapping not supplied (use --private PATH); nothing verified."); sys.exit(2)
    res = check_all(priv)
    bad = [f for f, r in res.items() if not all(r.values())]
    print("ALL PASS" if not bad else f"MISMATCH: {bad}")
    sys.exit(1 if bad else 0)
