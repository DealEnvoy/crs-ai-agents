#!/usr/bin/env python3
"""Check the files in this repo against the sha256 lists recorded in PREREG_HASHES*.txt.

Usage: python3 verify_prereg.py [PREREG_HASHES_v2.txt ...]    (default: all four lists)

Notes on what a mismatch means (see SCORING_RULES.md, changelog):
  * PREREG_HASHES.txt is the registration before any real call. crs_pilot.py, cost_guard.py and SCORING_RULES.md
    were edited after registration and the edits are recorded in the changelog, so those three differ from that list.
  * software_tasks/build_software_packs.py differs from PREREG_HASHES.txt because the hard-coded private redaction
    terms and local path were moved out of it after the runs (builder script only; the packs it writes are hashed
    separately and match).
  * PREREG_HASHES_v2.txt was written before any v2 call. Every file in it should match.
  * Files named in wording_edits.json (only software_tasks/build_software_packs.py) show as EDITED, and
    are proven to differ only by the documented edit when the private mapping is supplied:
        python3 verify_prereg.py --private PATH_TO_wording_edits_private.json     (or env WORDING_EDITS_PRIVATE)
    The hash lists themselves are never modified.
"""
import hashlib, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import verify_wording_edits as VW
_args = sys.argv[1:]
if "--private" in _args:
    i = _args.index("--private"); del _args[i:i + 2]
PRIV = VW.load_private()
EDITED = {e["file"] for e in json.load(open(os.path.join(HERE, "wording_edits.json")))["files"]}
_REV = VW.check_all(PRIV, quiet=True) if PRIV else None
lists = _args or ["PREREG_HASHES.txt", "PREREG_HASHES_post_run.txt", "PREREG_HASHES_v2.txt", "PREREG_HASHES_v2_post_run.txt"]
for lst in lists:
    ok = bad = missing = 0
    print("==", lst)
    for line in open(os.path.join(HERE, lst), encoding="utf-8"):
        if line.startswith("#") or not line.strip():
            continue
        parts = line.split(None, 1)
        if len(parts) != 2:
            print("  (skipped line without a digest:", line.strip(), ")"); continue
        digest, path = parts
        path = path.strip()
        p = os.path.join(HERE, path)
        if not os.path.exists(p):
            print("  MISSING ", path); missing += 1; continue
        h = hashlib.sha256(open(p, "rb").read()).hexdigest()
        if h == digest:
            ok += 1
        elif path in EDITED:
            if _REV is None:
                print("  EDITED  ", path, "(documented; pass --private to prove it)"); bad += 1
            elif _REV[path].get(lst):
                print("  EDITED  ", path, "(rebuilt original matches this digest)"); ok += 1
            else:
                print("  DIFFERS ", path, "(rebuilt original does NOT match)"); bad += 1
        else:
            print("  DIFFERS ", path); bad += 1
    print(f"  {ok} match, {bad} differ, {missing} missing")
