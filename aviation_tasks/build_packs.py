#!/usr/bin/env python3
"""Builds the 5 synthetic aviation-style work-pack pairs (faulty + clean twin),
runs rule-based consistency checks, and writes answer keys.
No network, no model calls. Everything here is INVENTED data."""
import json, os, difflib, copy, datetime as dt

ROOT = os.path.dirname(os.path.abspath(__file__))
BANNER = ("SYNTHETIC TRAINING DATA. NOT MAINTENANCE DATA. DO NOT USE ON REAL AIRCRAFT OR RECORDS. "
          "Operator, organisation, aircraft type, registration, part numbers, serials, tool IDs, people codes, "
          "limits, MEL and AD entries are all invented.")

CATS = {
 "A1": "MISSING_SIGNOFF", "A2": "INDEPENDENT_INSPECTION", "A3": "OUT_OF_LIMITS",
 "A4": "EXPIRED_CALIBRATION", "A5": "DEFERRED_DEFECT_OVERDUE", "A6": "STALE_DATA",
 "A7": "PART_TRACEABILITY", "A8": "AD_STATUS"}

def D(s): return dt.date.fromisoformat(s)

# ---------------------------------------------------------------- shared pieces
OPERATOR = "Northvale Synthetic Air (fictional operator)"
MRO = "Brackenfield Synthetic Aero Services (fictional Part-145 organisation, invented approval ref SYN.145.0001)"
ACTYPE = "Aerowing AW-7 (fictional twin-turboprop)"

CRS_LINES = [
 "All task card steps stamped and dated: YES",
 "Recorded measurements within limits: YES",
 "Independent inspection recorded where required: YES",
 "Tools in calibration at time of use: YES",
 "Maintenance data revision current: YES",
 "Fitted parts traceable to release certificates: YES",
 "No open deferred defect beyond its limit: YES",
 "Applicable ADs complied with: YES",
]

def base(pid, reg, wo, wo_title, review_date, fh, cards, **kw):
    p = dict(
        pack_id=pid, reg=reg, wo=wo, wo_title=wo_title, review_date=review_date, fh=fh,
        revisions=[("AW7-AMM", "Aircraft Maintenance Manual", "14"),
                   ("AW7-MP", "Maintenance Programme", "6"),
                   ("AW7-MOE", "Maintenance Organisation Exposition extract (critical tasks list)", "9")],
        limits=[], tools=[], cards=cards, parts=[], mel=[], add=[], ads=[], handover=None, notes=[],
        crs_by="CS-01", wp_claims=[])
    p.update(kw)
    return p

DEFAULT_MEL = [
 ("MEL-SYN 24-1b", "Engine generator 1 inoperative", "C", 10,
  "10 consecutive calendar days. Day of discovery not counted; limit expires 2359 UTC on day 10. Conditions: APU generator serviceable."),
 ("MEL-SYN 25-4a", "Cabin reading light inoperative", "D", 120,
  "120 consecutive calendar days. Day of discovery not counted."),
]
MEL_RIE_RULE = ("RIE rule (invented): one extension of up to 3 calendar days may be approved only by postholder PH-CAM "
                "and must be written in the ADD register with approver code and reason.")

DEFAULT_ADS = [
 ("SYN-2026-01", "Cabin door seal inspection", "one-time", None, None, "Complied 2026-02-11 (REC-SYN-0610)"),
 ("SYN-2026-02", "Elevator hinge fitting inspection", "repeat", 1200, 11000, "Last done 11,000 FH (REC-SYN-0655)"),
 ("SYN-2026-03", "Nose gear main fitting bore ultrasonic inspection", "repeat", 600, 11240, "Last done 11,240 FH (REC-SYN-0771)"),
]

# ---------------------------------------------------------------- A1
def pack_A1(faulty):
    steps = [
     dict(n=1, text="Isolate hydraulic power; fit gear ground locks; placard cockpit.", by="AUTH-02", date="2026-03-13"),
     dict(n=2, text="Disconnect and remove gear selector module (GSM) and control rod.", by="AUTH-02", date="2026-03-13"),
     dict(n=3, text="Remove old shims from GSM panel mount and record count removed: 3.", by="AUTH-02", date="2026-03-13"),
     dict(n=4, text="Fit replacement GSM to panel mount with shims as required (maximum 3 without engineering reference, LIM-32-41-01).", by="AUTH-02", date="2026-03-13"),
     dict(n=5, text="Connect control rod and cable run to GSM quadrant.", by="AUTH-02", date="2026-03-13"),
     dict(n=6, text="Record shim count fitted: 3.", by="AUTH-02", date="2026-03-13", rec=("LIM-32-41-01", 3, "shims")),
     dict(n=7, text="Rig system: fit rig pins in L and R selector valve quadrants, adjust to AMM 32-41-01, remove pins and confirm they insert freely.",
          by="AUTH-02" if not faulty else None, date="2026-03-13" if not faulty else None),
     dict(n=8, text="Function check of gear lever through UP / OFF / DN with ground power; no jamming.", by="AUTH-03", date="2026-03-14"),
     dict(n=9, text="INDEPENDENT INSPECTION of rigging and function check (critical task, MOE 2.7).", by="IQP-01", date="2026-03-14", indep=True),
    ]
    card = dict(id="TC-32-41-01", title="Replace gear selector module (GSM)", critical=True,
                data=("AW7-AMM", "32-41-01", "14"), steps=steps, indep_field=None)
    p = base("WP-SYN-A1", "G-SYN1", "WO-SYN-1101", "Replace gear selector module found jamming on ground check", "2026-03-14", 6120, [card])
    p["limits"] = [("LIM-32-41-01", "GSM panel-mount shims", 0, 3, "shims", "Maximum 3 without engineering reference")]
    p["tools"] = [("TW-009", "Torque wrench 5-25 Nm", "2026-12-31")]
    p["parts"] = [("SYN-GSM-300", "SYN-A-7712", "SYN-A-7712", "GSM replacement; release cert layout invented")]
    p["handover"] = ("Night shift handover 2026-03-14 06:00 (AUTH-02 to AUTH-03): steps 01 to 07 completed. "
                     "Steps 08 and 09 outstanding for day shift.")
    return p

# ---------------------------------------------------------------- A2
def pack_A2(faulty):
    S = lambda n, t, by, d, **k: dict(n=n, text=t, by=by, date=d, **k)
    steps = [
     S(1, "Isolate electrical power; placard cockpit.", "AUTH-05", "2026-05-19"),
     S(2, "Remove rudder limiter unit (RLU) actuator.", "AUTH-05", "2026-05-19"),
     S(3, "Fit replacement RLU actuator P/N SYN-RLU-210.", "AUTH-05", "2026-05-19"),
     S(4, "Torque RLU actuator clamp bolts (TW-021). Recorded: 12 Nm.", "AUTH-05", "2026-05-19", rec=("LIM-27-23-02", 12, "Nm"), tool="TW-021"),
     S(5, "Rig and tension rudder cables. Recorded cable tension: 310 N.", "AUTH-05", "2026-05-19", rec=("LIM-27-23-03", 310, "N"), tool="TT-007"),
     S(6, "Operational test of RLU in both positions (hold test switch 30 s).", "AUTH-05", "2026-05-20"),
     S(7, "Functional check of rudder, full range, correct sense of movement.", "AUTH-05", "2026-05-20"),
     S(8, "Refit access panel 27-A12; general verification for tools and loose items (non-critical step, no independent inspection required).", "AUTH-06", "2026-05-20"),
    ]
    card = dict(id="TC-27-23-05", title="Replace rudder limiter unit (RLU) actuator", critical=True,
                data=("AW7-AMM", "27-23-05", "14"), steps=steps,
                indep_field=dict(scope="installation, rigging, locking and sense of operation of RLU (AMC4 145.A.48(c)(2), MOE 2.7)",
                                 by=None if faulty else "IQP-03", date=None if faulty else "2026-05-20"))
    p = base("WP-SYN-A2", "G-SYN2", "WO-SYN-2207", "Replace RLU actuator (moisture indication found at check)", "2026-05-20", 8840, [card])
    p["limits"] = [("LIM-27-23-02", "RLU actuator clamp bolt torque", 10, 14, "Nm", ""),
                   ("LIM-27-23-03", "Rudder cable tension", 290, 330, "N", "")]
    p["tools"] = [("TW-021", "Torque wrench 5-25 Nm", "2027-02-28"), ("TT-007", "Cable tensiometer", "2026-11-30")]
    p["parts"] = [("SYN-RLU-210", "SYN-B-5521", "SYN-B-5521", "RLU actuator; release cert layout invented")]
    return p

# ---------------------------------------------------------------- A3
def pack_A3(faulty):
    S = lambda n, t, by, d, **k: dict(n=n, text=t, by=by, date=d, **k)
    torque = 41 if faulty else 27
    steps = [
     S(1, "Chock aircraft; isolate; remove propeller hub fairing.", "AUTH-07", "2026-07-08"),
     S(2, "Remove old pitch-link nut, bolt and washers; discard.", "AUTH-07", "2026-07-08"),
     S(3, "Measure new bolt grip length. Recorded: 38.3 mm.", "AUTH-07", "2026-07-08", rec=("LIM-61-12-04", 38.3, "mm")),
     S(4, "Fit new bolt P/N SYN-PB-118 and washer; check bolt head seated.", "AUTH-07", "2026-07-08"),
     S(5, "Fit new nut P/N SYN-PN-119 and torque with TW-014 to the limit in LIM-61-12-03. If the split-pin hole does not align within the limit, do not exceed the maximum; back off and select an alternative nut per AMM. "
          f"Recorded torque: {torque} Nm. Split-pin hole aligned at recorded torque: YES.",
       "AUTH-07", "2026-07-08", rec=("LIM-61-12-03", torque, "Nm"), tool="TW-014"),
     S(6, "Fit split pin; check locking and free rotation of link.", "AUTH-07", "2026-07-09"),
     S(7, "INDEPENDENT INSPECTION of assembly, locking and torque record (critical task, MOE 2.7).", "IQP-02", "2026-07-09", indep=True),
    ]
    card = dict(id="TC-61-12-03", title="Replace propeller pitch-link bolt and nut", critical=True,
                data=("AW7-AMM", "61-12-03", "14"), steps=steps, indep_field=None)
    p = base("WP-SYN-A3", "G-SYN3", "WO-SYN-3318", "Replace propeller pitch-link bolt and nut (corrosion on old bolt)", "2026-07-09", 4410, [card])
    p["limits"] = [("LIM-61-12-03", "Pitch-link nut assembly torque", 25, 30, "Nm", ""),
                   ("LIM-61-12-04", "Pitch-link bolt grip length", 38.0, 38.6, "mm", "")]
    p["tools"] = [("TW-014", "Torque wrench 10-50 Nm", "2027-01-31")]
    p["parts"] = [("SYN-PB-118", "SYN-C-0903", "SYN-C-0903", "pitch-link bolt; release cert layout invented"),
                  ("SYN-PN-119", "SYN-C-1250", "SYN-C-1250", "pitch-link nut; release cert layout invented")]
    return p

# ---------------------------------------------------------------- A5
def pack_A5(faulty):
    deferred = "2026-10-03" if faulty else "2026-10-08"
    steps = [
     dict(n=1, text="Review technical log; list open ADD entries.", by="AUTH-08", date="2026-10-16"),
     dict(n=2, text="Daily walk-round inspection per AMM 05-10-01; no new defects.", by="AUTH-08", date="2026-10-16"),
     dict(n=3, text="Check fluid levels; top-up recorded in tech log.", by="AUTH-08", date="2026-10-16"),
    ]
    card = dict(id="TC-05-10-01", title="Daily check and technical log review", critical=False,
                data=("AW7-AMM", "05-10-01", "14"), steps=steps, indep_field=None)
    p = base("WP-SYN-A5", "G-SYN5", "WO-SYN-5120", "Daily check before first flight of 2026-10-16", "2026-10-16", 9975, [card])
    p["mel"] = DEFAULT_MEL
    p["mel_rie_rule"] = MEL_RIE_RULE
    p["add"] = [
     ("ADD-SYN-0398", "MEL-SYN 25-4a", "Cabin reading light row 4 inoperative", "2026-09-20", "OPEN", "none"),
     ("ADD-SYN-0412", "MEL-SYN 24-1b", "Engine generator 1 inoperative (tripping TRU 1)", deferred, "OPEN", "none"),
    ]
    p["techlog"] = [
     ("2026-10-14", "SYN-0455", "Dispatched with ADD-SYN-0412 and ADD-SYN-0398 open. No new defects."),
     ("2026-10-15", "SYN-0458", "Dispatched with ADD-SYN-0412 and ADD-SYN-0398 open. No new defects."),
     ("2026-10-16", "SYN-0461", "Pre-flight: ADD-SYN-0412 and ADD-SYN-0398 still open. Awaiting CRS for daily check."),
    ]
    return p

# ---------------------------------------------------------------- A8
def pack_A8(faulty):
    fh = 11905 if faulty else 11805
    steps = [
     dict(n=1, text="Review AD status list against maintenance records for this check.", by="AUTH-09", date="2026-11-03"),
     dict(n=2, text="AD SYN-2026-01: one-time; result: complied (REC-SYN-0610).", by="AUTH-09", date="2026-11-03"),
     dict(n=3, text="AD SYN-2026-02: repeat 1,200 FH; result: complied, not yet due.", by="AUTH-09", date="2026-11-03"),
     dict(n=4, text="AD SYN-2026-03: result: complied with; no further action.", by="AUTH-09", date="2026-11-03"),
     dict(n=5, text="Independent review of AD status entries (MOE 2.9).", by="IQP-04", date="2026-11-03", indep=True),
    ]
    card = dict(id="TC-05-50-02", title="AD status review at periodic check", critical=False,
                data=("AW7-MP", "05-50-02", "6"), steps=steps, indep_field=None)
    p = base("WP-SYN-A8", "G-SYN8", "WO-SYN-6045", "Periodic check with AD status review", "2026-11-03", fh, [card])
    p["ads"] = DEFAULT_ADS
    p["mel"] = DEFAULT_MEL
    return p

TASKS = [
 dict(id="A1", folder="A1_missing_signoff", fn=pack_A1, title="Missing sign-off before release (step stamp absent, CRS draft filled)"),
 dict(id="A2", folder="A2_independent_inspection", fn=pack_A2, title="Critical task with no independent inspection recorded"),
 dict(id="A3", folder="A3_out_of_limits_torque", fn=pack_A3, title="Recorded torque outside the pack's limit"),
 dict(id="A5", folder="A5_deferred_defect_overdue", fn=pack_A5, title="Deferred defect open past its MEL limit"),
 dict(id="A8", folder="A8_ad_status", fn=pack_A8, title="AD marked complied but repeat inspection overdue"),
]

# ---------------------------------------------------------------- rendering
def fmt_num(v):
    return f"{v:,}" if isinstance(v, int) and v >= 1000 else str(v)

def render(p, tid):
    L = []
    a = L.append
    a(f"# WORK PACK {p['pack_id']}")
    a(f"{BANNER}")
    a("")
    a("## 0. Context")
    a(f"[CTX/AIRCRAFT] Type: {ACTYPE}. Registration: {p['reg']} (fictional). Airframe hours at pack review: {fmt_num(p['fh'])} FH.")
    a(f"[CTX/ORG] Operator: {OPERATOR}. Maintenance organisation: {MRO}.")
    a(f"[CTX/WO] Work order {p['wo']}: {p['wo_title']}. Pack review date: {p['review_date']}.")
    a("[CTX/CODES] People appear only as codes: AUTH-nn = authorised person who performed a step; IQP-nn = independent qualified person; CS-nn = certifying staff.")
    a("")
    a("## 1. Maintenance data revision list (pack-local)")
    for doc, title, rev in p["revisions"]:
        a(f"[REV/{doc}] {title}: current revision {rev}.")
    a("")
    a("## 2. Limits extract (pack-local, invented)")
    if p["limits"]:
        for lid, item, lo, hi, unit, note in p["limits"]:
            a(f"[{lid}] {item}: {lo} to {hi} {unit}." + (f" {note}." if note else ""))
    else:
        a("[LIM/NONE] No numerical limits are needed for this pack's tasks.")
    a("")
    a("## 3. Tool register (pack-local)")
    if p["tools"]:
        for tid_, desc, due in p["tools"]:
            a(f"[TOOL/{tid_}] {desc}. Calibration next due: {due}.")
    else:
        a("[TOOL/NONE] No calibrated tools are used for this pack's tasks.")
    a("")
    a("## 4. Work order and task card")
    a(f"[WO/{p['wo']}] Ordered: {p['wo_title']}.")
    for c in p["cards"]:
        drev = c["data"]
        a(f"[{c['id']}] {c['title']}. Data: {drev[0]} task {drev[1]} revision {drev[2]}." + (" CRITICAL TASK: independent inspection required before CRS." if c["critical"] else " Not a critical task."))
        for s in c["steps"]:
            stamp = s["by"] if s["by"] else "______"
            dte = s["date"] if s["date"] else "______"
            tool = f" Tool: {s['tool']}." if s.get("tool") else ""
            a(f"[{c['id']}/STEP-{s['n']:02d}] {s['text']}{tool} | Stamp: {stamp} | Date: {dte}")
        if c.get("indep_field") is not None:
            f = c["indep_field"]
            by = f["by"] if f["by"] else "______"
            d = f["date"] if f["date"] else "______"
            a(f"[{c['id']}/INDEP] Independent inspection of {f['scope']} | IQP stamp: {by} | Date: {d}")
    a("")
    if p["parts"]:
        a("## 5. Parts fitted and release certificates (invented layout)")
        for pn, ser_fit, ser_cert, note in p["parts"]:
            a(f"[PART/{pn}] Fitted serial: {ser_fit} | Release certificate serial: {ser_cert} | {note}.")
        a("")
    a("## 6. MEL extract and deferred defects")
    if p["mel"]:
        for ref, item, cat, days, rule in p["mel"]:
            a(f"[{ref}] {item}. Category {cat}. {rule}")
        if p.get("mel_rie_rule"):
            a(f"[MEL/RIE] {p['mel_rie_rule']}")
    else:
        a("[MEL/NONE] No MEL items are relevant to this pack.")
    if p["add"]:
        for ref, mel, item, d, status, rie in p["add"]:
            a(f"[{ref}] {item} | {mel} | Deferred: {d} | Status: {status} | RIE on file: {rie}")
        for d, sec, txt in p["techlog"]:
            a(f"[TECHLOG/{sec}] {d}: {txt}")
    else:
        a("[ADD/NONE] ADD register: NIL open entries.")
    a("")
    a("## 7. AD status list (pack-local, invented)")
    if p["ads"]:
        for ref, title, kind, interval, last, status in p["ads"]:
            if kind == "repeat":
                nxt = last + interval
                a(f"[AD/{ref}] {title}. Repeat every {fmt_num(interval)} FH. {status}. Next due at {fmt_num(nxt)} FH.")
            else:
                a(f"[AD/{ref}] {title}. One-time. {status}.")
    else:
        a("[AD/NONE] No ADs are relevant to this pack.")
    a("")
    if p["handover"]:
        a("## 8. Shift handover note")
        a(f"[HANDOVER] {p['handover']}")
        a("")
    a("## 9. CRS draft (statements entered by CS-01 after reading the pack; NOT ISSUED; issue is a human decision)")
    for i, line in enumerate(CRS_LINES, 1):
        a(f"[CRS/{i}] {line}")
    a("")
    return "\n".join(L)

# ---------------------------------------------------------------- rule-based checkers (ground truth engine)
def run_checks(p):
    """Returns list of (category, location_id, why). Used to prove the faulty pack has exactly one seeded
    fault and the clean twin has none."""
    out = []
    rev = {doc: r for doc, _, r in p["revisions"]}
    lim = {l[0]: l for l in p["limits"]}
    tools = {t[0]: t for t in p["tools"]}
    for c in p["cards"]:
        # A6 stale data
        if rev.get(c["data"][0]) != c["data"][2]:
            out.append(("A6", c["id"], "data revision not current"))
        performers = set()
        for s in c["steps"]:
            loc = f"{c['id']}/STEP-{s['n']:02d}"
            if not s["by"] or not s["date"]:
                out.append(("A1", loc, "no stamp/date while CRS draft says all stamped"))
            if s["by"] and not s.get("indep"):
                performers.add(s["by"])
            if s.get("rec"):
                lid, val, unit = s["rec"]
                _, _, lo, hi, _, _ = lim[lid]
                if not (lo <= val <= hi):
                    out.append(("A3", loc, f"recorded {val} outside {lo}-{hi}"))
            if s.get("tool") and s.get("date"):
                if D(tools[s["tool"]][2]) < D(s["date"]):
                    out.append(("A4", loc, "tool out of calibration at use"))
        f = c.get("indep_field")
        if f is not None and (not f["by"] or f["by"] in performers or not f["date"]):
            out.append(("A2", f"{c['id']}/INDEP", "independent inspection absent or not independent"))
        if c["critical"] and f is None:
            ind = [s for s in c["steps"] if s.get("indep")]
            if not ind or any((s["by"] in performers) for s in ind):
                out.append(("A2", c["id"], "no independent step"))
    for pn, sf, sc, _ in p["parts"]:
        if sf != sc:
            out.append(("A7", f"PART/{pn}", "serial mismatch"))
    rd = D(p["review_date"])
    for ref, mel, item, d, status, rie in p["add"]:
        limit_days = [m[3] for m in p["mel"] if m[0] == mel][0]
        expiry = D(d) + dt.timedelta(days=limit_days)
        if status == "OPEN" and rd > expiry and rie == "none":
            out.append(("A5", ref, f"open past limit; expiry {expiry}"))
    for ref, title, kind, interval, last, status in p["ads"]:
        if kind == "repeat" and p["fh"] > last + interval:
            out.append(("A8", f"AD/{ref}", f"overdue: {p['fh']} FH > next due {last+interval}"))
    return out

# ---------------------------------------------------------------- answer keys (seeded fault definitions)
def key_for(tid, faulty_text, clean_text):
    def line_with(text, needle):
        for ln in text.splitlines():
            if needle in ln:
                return ln.strip()
        raise SystemExit(f"needle not found: {needle}")
    K = {}
    if tid == "A1":
        loc = "TC-32-41-01/STEP-07"
        primary = line_with(faulty_text, "[TC-32-41-01/STEP-07]")
        K = dict(category="A1", category_name=CATS["A1"], location_id=loc, evidence_quote=primary,
                 also_acceptable_quotes=[line_with(faulty_text, "[CRS/1]"), line_with(faulty_text, "[HANDOVER]")],
                 delta_summary="Step 07 (rig pins) has no stamp or date; CRS draft line 1 says all steps stamped; handover says steps 01 to 07 completed.",
                 clean_delta="Step 07 stamped AUTH-02 2026-03-13.")
    elif tid == "A2":
        loc = "TC-27-23-05/INDEP"
        primary = line_with(faulty_text, "[TC-27-23-05/INDEP]")
        K = dict(category="A2", category_name=CATS["A2"], location_id=loc, evidence_quote=primary,
                 also_acceptable_quotes=[line_with(faulty_text, "[CRS/3]"), line_with(faulty_text, "[TC-27-23-05] ")],
                 delta_summary="Card is a critical task requiring independent inspection; the independent-inspection field is blank; CRS draft line 3 says it is recorded.",
                 clean_delta="Independent field records IQP-03 on 2026-05-20, a different person from the performer (AUTH-05).")
    elif tid == "A3":
        loc = "TC-61-12-03/STEP-05"
        primary = line_with(faulty_text, "[TC-61-12-03/STEP-05]")
        K = dict(category="A3", category_name=CATS["A3"], location_id=loc, evidence_quote=primary,
                 also_acceptable_quotes=["Recorded torque: 41 Nm", line_with(faulty_text, "[LIM-61-12-03]"), line_with(faulty_text, "[CRS/2]")],
                 delta_summary="Recorded nut torque 41 Nm; the pack's limit LIM-61-12-03 is 25 to 30 Nm.",
                 clean_delta="Recorded torque 27 Nm (inside limit).")
    elif tid == "A5":
        loc = "ADD-SYN-0412"
        primary = line_with(faulty_text, "[ADD-SYN-0412]")
        K = dict(category="A5", category_name=CATS["A5"], location_id=loc, evidence_quote=primary,
                 also_acceptable_quotes=[line_with(faulty_text, "[MEL-SYN 24-1b]"), line_with(faulty_text, "[TECHLOG/SYN-0461]"), line_with(faulty_text, "[CRS/7]")],
                 delta_summary="Category C item, 10 calendar days, day of discovery not counted. Deferred 2026-10-03 so the limit expired 2359 UTC on 2026-10-13; still OPEN on the pack review date 2026-10-16 with no RIE on file.",
                 clean_delta="Deferred 2026-10-08, so 2026-10-16 is day 8 (inside the limit).")
    elif tid == "A8":
        loc = "AD/SYN-2026-03"
        primary = line_with(faulty_text, "[AD/SYN-2026-03]")
        K = dict(category="A8", category_name=CATS["A8"], location_id=loc, evidence_quote=primary,
                 also_acceptable_quotes=[line_with(faulty_text, "[TC-05-50-02/STEP-04]"), line_with(faulty_text, "[CTX/AIRCRAFT]"), line_with(faulty_text, "[CRS/8]")],
                 delta_summary="Card step 04 says SYN-2026-03 'complied with; no further action', but the AD list shows next due at 11,840 FH and the airframe is at 11,905 FH (65 FH overdue).",
                 clean_delta="Airframe at 11,805 FH, so the repeat inspection is not yet due (35 FH remaining).")
    K["expected_recommendation_faulty"] = "HOLD_FOR_HUMAN"
    K["expected_recommendation_clean"] = "NO_FINDINGS_FOR_HUMAN_REVIEW"
    K["seeded_fault_count"] = 1
    return K

# ---------------------------------------------------------------- main
def main():
    summary = []
    for t in TASKS:
        tdir = os.path.join(ROOT, t["folder"])
        os.makedirs(os.path.join(tdir, "faulty"), exist_ok=True)
        os.makedirs(os.path.join(tdir, "clean"), exist_ok=True)
        pf, pc = t["fn"](True), t["fn"](False)
        tf, tc = render(pf, t["id"]), render(pc, t["id"])
        # checks
        rf, rc = run_checks(pf), run_checks(pc)
        key = key_for(t["id"], tf, tc)
        assert len(rf) == 1 and rf[0][0] == t["id"] and rf[0][1] == key["location_id"], (t["id"], rf)
        assert rc == [], (t["id"], "clean twin not clean", rc)
        # key quote validation
        quotes = [key["evidence_quote"]] + key["also_acceptable_quotes"]
        for q in quotes:
            assert q in tf, (t["id"], "quote missing from faulty pack", q)
        # location id appears in pack
        assert f"[{key['location_id']}]" in tf, (t["id"], "location id not in pack")
        # twin diff
        diff = list(difflib.unified_diff(tc.splitlines(), tf.splitlines(), "clean/pack.md", "faulty/pack.md", lineterm="", n=0))
        changed = [d for d in diff if (d.startswith("+") or d.startswith("-")) and not d.startswith(("+++", "---"))]
        key["twin_diff_changed_lines"] = len([d for d in changed if d.startswith("+")])
        key["pack_id"] = pf["pack_id"]
        key["task_id"] = t["id"]
        key["title"] = t["title"]
        key["fictional_registration"] = pf["reg"]
        key["ground_truth_checker_result_faulty"] = [list(x) for x in rf]
        key["ground_truth_checker_result_clean"] = [list(x) for x in rc]
        key["notes"] = "Quote must be an exact substring of the pack. A quote is acceptable if it is the primary or any also_acceptable quote, or any other exact substring that evidences the seeded fault."
        open(os.path.join(tdir, "faulty", "pack.md"), "w").write(tf + "\n")
        open(os.path.join(tdir, "clean", "pack.md"), "w").write(tc + "\n")
        open(os.path.join(tdir, "twin_diff.txt"), "w").write("\n".join(diff) + "\n")
        json.dump(key, open(os.path.join(tdir, "answer_key.json"), "w"), indent=2, ensure_ascii=False)
        approx_tokens = len(tf) // 4
        summary.append((t["id"], t["folder"], len(tf), approx_tokens, key["twin_diff_changed_lines"]))
    for s in summary:
        print("OK", *s)

if __name__ == "__main__":
    main()
