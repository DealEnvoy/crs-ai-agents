#!/usr/bin/env python3
"""Builds the v2 task set in ./v2 : v1 faulty packs are copied BYTE-IDENTICAL; only the CLEAN twins of A8, S1, S2, S3 change
(twin-design flaws found after the v1 run; see SCORING_RULES.md changelog v2). Runs a v2 checker, verifies provenance for software
lines, writes keys and twin diffs. No network, no model calls. v1 files are not touched."""
import os, sys, json, shutil, glob, difflib, re, copy
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "aviation_tasks")); sys.path.insert(0, os.path.join(HERE, "software_tasks"))
import build_packs as bp
import build_software_packs as bs

V2 = os.path.join(HERE, "v2")
if os.path.exists(V2): shutil.rmtree(V2)
for dom, pat in (("aviation_tasks", "A*_*"), ("software_tasks", "S*_*")):
    for d in sorted(glob.glob(os.path.join(HERE, dom, pat))):
        if os.path.isdir(d):
            shutil.copytree(d, os.path.join(V2, dom, os.path.basename(d)))

def ndiff(clean, faulty):
    diff = [l for l in difflib.unified_diff(clean.splitlines(), faulty.splitlines(), "clean/pack.md", "faulty/pack.md", lineterm="", n=0)]
    ch = [l for l in diff if l[:1] in "+-" and l[:3] not in ("+++", "---")]
    return diff, sum(1 for l in ch if l.startswith("+"))

# ------------------------------------------------------------------ A8
def a8():
    t = [x for x in bp.TASKS if x["id"] == "A8"][0]
    pf, pc = t["fn"](True), t["fn"](False)
    for c in pc["cards"]:
        for s in c["steps"]:
            if s["n"] == 4:
                s["text"] = "AD SYN-2026-03: repeat 600 FH; result: complied, not yet due."
    tf, tc = bp.render(pf, "A8"), bp.render(pc, "A8")
    assert open(os.path.join(HERE, "aviation_tasks", t["folder"], "faulty", "pack.md")).read() == tf + "\n", "faulty A8 must be unchanged"
    assert bp.run_checks(pc) == [], "A8 clean twin not clean"
    assert "no further action" not in tc.lower()
    d = os.path.join(V2, "aviation_tasks", t["folder"])
    diff, nplus = ndiff(tc, tf)
    open(os.path.join(d, "clean", "pack.md"), "w").write(tc + "\n")
    open(os.path.join(d, "twin_diff.txt"), "w").write("\n".join(diff) + "\n")
    k = json.load(open(os.path.join(d, "answer_key.json")))
    k["clean_delta"] = ("Airframe at 11,805 FH, so the repeat inspection is not yet due (35 FH remaining). v2: step 04 in the clean twin now reads "
                        "'repeat 600 FH; result: complied, not yet due.' (v1 said 'complied with; no further action', which models objected to for a repeating AD). The faulty pack is unchanged from v1.")
    k["twin_diff_changed_lines"] = nplus
    k["v2_clean_changes"] = ["TC-05-50-02/STEP-04 wording (clean twin only)"]
    json.dump(k, open(os.path.join(d, "answer_key.json"), "w"), indent=2, ensure_ascii=False)
    return "A8", nplus

# ------------------------------------------------------------------ software
ISSUE = ("ISSUE/1", bs.H("Issue log (harness-written): no open issue is logged against this change."))

def sw_clean_sections(t):
    secs = [[title, list(lines)] for title, lines in bs.sections_for(t, False)]
    def find(title_prefix):
        return [s for s in secs if s[0].startswith(title_prefix)][0]
    def replace(sec, lid, spec):
        sec[1] = [(i, spec if i == lid else s) for i, s in sec[1]]
    tid = t["task_id"]
    if tid == "S1":
        replace(find("4."), "FIELD/1", bs.CF("**Forwarding test:** after this release, [OWNER]'s real test call produced a text (with the WhatsApp link) and a `customer_calls` log entry.",
                 "Counterfactual (v2 wording). The real history had no such result at release time: the real test failed and passed only after Live Voicemail was switched off (docs/writeups/README.md L63). v2 ties the field line to the real test call named in DEPLOY/4, because v1's wording read as contradicting 'No SMS was sent'."))
    if tid == "S2":
        replace(find("3."), "DEPLOY/4", bs.CF("Abandoned checkouts don't count. If the Stripe lookup fails, the check **fails closed** (the customer is not provisioned) and the alert says the card check was unavailable.",
                 "Counterfactual (v2). The first sentence is real (staged-auto README); the real design is fail-open ('the customer is provisioned'). v2 removes the fail-open sentence from the clean twin because it contradicted gate line 5."))
        replace(find("4."), "FIELD/1", bs.CF("**One-trial check** (live signup <customer-id> logged `ok: mobile, email and card fingerprint checked, no earlier match`)",
                 "Counterfactual. The real first live signup logged 'unavailable: no card fingerprint' (docs/writeups/10-system-architecture-handoff.md L269). v2 also names mobile and email so the line covers the whole claim."))
        sec = find("3."); sec[1].append(("DEPLOY/5", bs.V("LOG", "**Live version: `ad20ff2c-caca-49df-b729-29cc62043d97`** (version 31).", find="**Live version: `ad20ff2c")))
    if tid == "S3":
        sec = find("0.")
        replace(sec, "CTX/REQ", bs.H("Closure request (harness-written): close ticket CHECKOUT-1, 'the live homepage signup form uses the shared app.js handler, which redirects to Stripe Checkout when the server returns a checkout_url. Stripe stays off at this deploy, so no live checkout is expected yet'."))
        sec = find("3."); sec[1].append(("DEPLOY/4", bs.V("LOG", "**Live version: `b4958e57-3f13-4373-a5d1-d2eda3a4a1b7`**", find="**Live version: `b4958e57")))
    # issue log section before the gate (all three software clean twins)
    i = [n for n, s in enumerate(secs) if s[0].startswith("5.")][0]
    secs.insert(i, ["4b. Issue log", [ISSUE]])
    return [(a, b) for a, b in secs]

def render_secs(t, secs):
    out = ["# CLOSURE PACK %s" % t["pack_id"], bs.BANNER, ""]; prov = []
    for title, lines in secs:
        out.append("## " + title)
        for lid, spec in lines:
            out.append("[%s] %s" % (lid, spec["text"]))
            prov.append(dict(line_id=lid, **{k: v for k, v in spec.items() if k != "text"}, text=spec["text"]))
        out.append("")
    return "\n".join(out), prov

def check_v2(t, text, faulty):
    """v1 checker plus the clean-twin audit rules that were missing in v1 (mismatch/contradiction inside a pack)."""
    f = list(bs.check_pack(t, text)); d = bs.parse(text)
    gy = {k: v.endswith(": YES") for k, v in d.items() if k.startswith("GATE/")}
    tid = t["task_id"]
    if tid == "S1" and "No SMS was sent" in d.get("DEPLOY/4", "") and "produced a text" in d["FIELD/1"] and "real test call" not in d["FIELD/1"]:
        f.append(("SW8", "FIELD/1", "field line not tied to the real test call; reads as contradicting 'No SMS was sent'"))
    if tid == "S2" and "fails open" in d.get("DEPLOY/4", "") and gy["GATE/5"]:
        f.append(("SW2", "DEPLOY/4", "fail-open recorded while gate says nothing fails open"))
    if tid == "S3" and "with Stripe on" in d["CTX/REQ"] and "Stripe is switched off" in d["CTX/SYSTEM"] and "no live checkout is expected" not in d["CTX/REQ"]:
        f.append(("SW8", "CTX/REQ", "closure request is about Stripe on, but the deploy has Stripe off and the evidence covers page wiring only"))
    return f

def sw(t):
    secs = sw_clean_sections(t)
    ctext, cprov = render_secs(t, secs)
    ftext_v1 = open(os.path.join(HERE, "software_tasks", t["folder"], "faulty", "pack.md")).read()
    ftext, fprov = bs.render(t, True)
    assert ftext == ftext_v1, "faulty software pack must be unchanged"
    bs.scan_forbidden(ctext, t["pack_id"] + " clean v2")
    ff, cf = check_v2(t, ftext, True), check_v2(t, ctext, False)
    assert any(x[1] == t["decisive_id"] for x in ff), (t["task_id"], ff)
    assert cf == [], (t["task_id"], "v2 clean twin not clean", cf)
    d = os.path.join(V2, "software_tasks", t["folder"])
    open(os.path.join(d, "clean", "pack.md"), "w").write(ctext)
    diff, nplus = ndiff(ctext, ftext)
    open(os.path.join(d, "twin_diff.txt"), "w").write("\n".join(diff) + "\n")
    # v1 clean check on the v2 clean pack must also be empty
    assert bs.check_pack(t, ctext) == []
    prov = json.load(open(os.path.join(d, "provenance.json"))); prov["clean"] = cprov; prov["v2_note"] = "faulty unchanged from v1; clean rebuilt (see answer_key v2_clean_changes)"
    json.dump(prov, open(os.path.join(d, "provenance.json"), "w"), indent=2, ensure_ascii=False)
    k = json.load(open(os.path.join(d, "answer_key.json")))
    changes = {"S1": ["FIELD/1 wording tied to the owner's real test call (v1 read as contradicting DEPLOY/4 'No SMS was sent')", "added [ISSUE/1] issue-log section"],
               "S2": ["DEPLOY/4 fail-open sentence replaced by a fail-closed counterfactual (v1 contradicted GATE/5)", "FIELD/1 now covers mobile, email and card fingerprint", "added DEPLOY/5 real live-version line (verbatim)", "added [ISSUE/1] issue-log section"],
               "S3": ["CTX/REQ narrowed to what is evidenced (page wiring; Stripe stays off) in the clean twin only (v1 asked about Stripe-on while Stripe was off)", "added DEPLOY/4 real live-version line (verbatim)", "added [ISSUE/1] issue-log section"]}[t["task_id"]]
    k["v2_clean_changes"] = changes; k["twin_diff_changed_lines"] = nplus
    k["clean_delta"] = t["clean_delta"] + " v2 clean twin changes: " + "; ".join(changes) + ". The faulty pack is byte-identical to v1."
    k["ground_truth_checker_result_clean"] = []
    if k["clean_decisive_line_kind"] != "verbatim": k["clean_decisive_line_kind"] = "counterfactual"
    json.dump(k, open(os.path.join(d, "answer_key.json"), "w"), indent=2, ensure_ascii=False)
    # provenance verification of every verbatim line in the v2 clean pack
    n = 0
    for e in cprov:
        if e["kind"] == "verbatim":
            line = open(os.path.join(bs.REPO, e["src"]), encoding="utf-8").read().split("\n")[e["src_line"] - 1]
            assert e["text"] in bs.redact(line), (t["task_id"], e["line_id"]); n += 1
    return t["task_id"], nplus, n

res = [a8()] + [sw(t) for t in bs.T]
for r in res: print("OK v2", *r)
