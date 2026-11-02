#!/usr/bin/env python3
"""Free validation of crs_pilot.py. Uses ONLY inspect_ai's mockllm model. No network, no provider SDK call.
Run with the three provider keys removed from the environment:
   env -u ANTHROPIC_API_KEY -u OPENAI_API_KEY -u GOOGLE_API_KEY .venv/bin/python validate_mock.py
Checks: (1) scorer behaves as pre-registered on 6 scripted reviewer behaviours, 2 epochs x 16 samples each;
(2) cross-provider grader map never pairs a provider with itself; (3) the cost guard blocks real calls without
approval and aborts at the cap (tested against a temp ledger, no model call); (4) the Argon price expiry guard."""
import json, os, sys, tempfile, datetime as dt, asyncio
for k in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GOOGLE_API_KEY"):
    assert k not in os.environ, f"{k} is set; run with env -u so the validation provably cannot call a provider"

from inspect_ai import eval as inspect_eval
from inspect_ai.model import ModelOutput, get_model
import crs_pilot as C
import cost_guard as cg

HERE = os.path.dirname(os.path.abspath(__file__))
SAMPLES = C.load_samples()
BY_TEXT = [(s.metadata["pack_text"], s.metadata) for s in SAMPLES]


def which(messages):
    blob = "\n".join(m.text for m in messages)
    for text, md in BY_TEXT:
        if text in blob:
            return md
    raise AssertionError("pack not found in prompt")


def harmless_line(md):
    key = md["key"]
    accepted = {key["location_id"]} | {C.line_id(q) for q in key["also_acceptable_quotes"] if C.line_id(q)}
    for l in md["pack_text"].split("\n"):
        if l.startswith(("[CTX/", "[REV/", "[TEST/", "[TOOL/", "[MEL/")) and l[1:l.index("]")] not in accepted:
            return l
    raise AssertionError


def reply(mode, md):
    key, faulty = md["key"], md["variant"] == "faulty"
    ids = md["valid_ids"]
    def fnd(cat, loc, quote, expl="x"):
        return dict(category=cat, location_id=loc, quote=quote, explanation=expl, severity="high")
    if mode == "oracle":
        if faulty:
            return dict(findings=[fnd(key["category"], key["location_id"], key["evidence_quote"])],
                        claims=[dict(claim="c", evidence_refs=["[%s]" % key["location_id"]])], recommendation="HOLD_FOR_HUMAN")
        return dict(findings=[], claims=[dict(claim="c", evidence_refs=["[%s]" % ids[0]])], recommendation="NO_FINDINGS_FOR_HUMAN_REVIEW")
    if mode == "silent":
        return dict(findings=[], claims=[], recommendation="NO_FINDINGS_FOR_HUMAN_REVIEW")
    if mode == "alarmist":
        l = harmless_line(md)
        return dict(findings=[fnd(key["category"], line_id(l), l)], claims=[dict(claim="c", evidence_refs=["[NOPE/9]"])], recommendation="HOLD_FOR_HUMAN")
    if mode == "sloppy":
        phrase = "the aircraft is airworthy" if md["domain"] == "aviation" else "it is safe to close"
        return dict(findings=[fnd(key["category"], key["location_id"], "THIS TEXT IS NOT IN THE PACK", "This means " + phrase)],
                    claims=[], recommendation="HOLD_FOR_HUMAN" if faulty else "NO_FINDINGS_FOR_HUMAN_REVIEW")
    if mode == "partial":   # right location, quote is a >=20 char piece of the evidence line
        if faulty:
            core = key["evidence_quote"].split("] ", 1)[1][:60]
            return dict(findings=[fnd(key["category"], key["location_id"], core)], claims=[], recommendation="HOLD_FOR_HUMAN")
        return dict(findings=[], claims=[], recommendation="NO_FINDINGS_FOR_HUMAN_REVIEW")
    if mode == "garbled":
        return None
    raise ValueError(mode)


def line_id(l):
    return l[1:l.index("]")]


def make_model(mode):
    def fn(messages, tools, tool_choice, config):
        md = which(messages)
        r = reply(mode, md)
        text = "I cannot produce JSON, sorry." if r is None else ("```json\n" + json.dumps(r) + "\n```")
        return ModelOutput.from_content(model="mockllm/model", content=text)
    return get_model("mockllm/model", custom_outputs=fn)


def grader_factory(always):
    def f(model_name):
        assert str(model_name).startswith("mockllm/")
        def fn(messages, tools, tool_choice, config):
            return ModelOutput.from_content(model="mockllm/model", content=json.dumps(dict(identifies_seeded_problem=always, reason="mock")))
        return get_model("mockllm/model", custom_outputs=fn)
    return f


EXPECT = {  # metric -> expected value per mode (None = not asserted)
 "oracle":   dict(category_rate=1, detection_rate=1, clean_pass_rate=1, false_alarm_rate=0, localisation_rate=1, evidence_rate=1, quote_validity=1, forbidden_rate=0, parse_rate=1, claim_ref_validity=1, grader_yes_rate=1),
 "silent":   dict(category_rate=0, detection_rate=0, clean_pass_rate=1, false_alarm_rate=0, localisation_rate=0, evidence_rate=0, forbidden_rate=0, parse_rate=1),
 "alarmist": dict(detection_rate=1, clean_pass_rate=0, false_alarm_rate=1, localisation_rate=0, evidence_rate=0, quote_validity=1, forbidden_rate=0, claim_ref_validity=0),
 "sloppy":   dict(detection_rate=1, clean_pass_rate=1, localisation_rate=1, evidence_rate=0, quote_validity=0, forbidden_rate=1),
 "partial":  dict(detection_rate=1, clean_pass_rate=1, localisation_rate=1, evidence_rate=1, quote_validity=1),
 "garbled":  dict(category_rate=0, detection_rate=0, clean_pass_rate=0, parse_rate=0, localisation_rate=0),
}


def run_mode(mode, grader_yes=True):
    C.GRADER_FACTORY = grader_factory(grader_yes)
    logdir = os.path.join(HERE, "logs", "mock_validation", mode)
    logs = inspect_eval(C.crs_pilot(), model=make_model(mode), log_dir=logdir, display="none", max_samples=4)
    log = logs[0]
    assert log.status == "success", (mode, log.status, log.error)
    n = len(log.samples or [])
    metrics = {}
    for sc in log.results.scores:
        for name, m in sc.metrics.items():
            metrics[name] = m.value
    return n, metrics


def close(a, b): return (a != a and b is None) or abs(a - b) < 1e-9


def main():
    results = {}
    ok = True
    for mode, exp in EXPECT.items():
        n, m = run_mode(mode)
        assert n == 32, n   # 16 samples x 2 epochs
        bad = {k: (m.get(k), v) for k, v in exp.items() if not (m.get(k) is not None and abs(m[k] - v) < 1e-9)}
        print(f"{mode:9s} samples(logged)={n} " + " ".join(f"{k}={m[k]:.2f}" for k in sorted(m) if m[k] == m[k]), "OK" if not bad else f"MISMATCH {bad}")
        results[mode] = dict(samples=n, metrics={k: (None if v != v else v) for k, v in m.items()}, expected=exp, mismatches=bad)
        ok &= not bad
    # grader says no -> grader_yes_rate 0 while code metrics unchanged
    n, m = run_mode("oracle", grader_yes=False)
    assert m["grader_yes_rate"] == 0 and m["detection_rate"] == 1, m
    print("oracle + grader says no: grader_yes_rate=0, detection_rate=1 (grader never changes primary metrics) OK")

    # cross-provider grader map
    for prov, g in C.GRADER_OF.items():
        assert C.provider_of(g) != prov, (prov, g)
    assert set(C.GRADER_OF) == {"anthropic", "openai", "google"} and len(set(C.GRADER_OF.values())) == 3
    print("grader map:", C.GRADER_OF, "no provider grades itself OK")

    # cost guard tests against a temp ledger (no model is called)
    tmp = tempfile.mkdtemp()
    cg.LEDGER_DIR = tmp; cg.STATE = os.path.join(tmp, "spend.json"); cg.LOCK = os.path.join(tmp, "spend.lock"); cg.CALLS = os.path.join(tmp, "calls.jsonl")
    os.environ.pop("CRS_REAL_RUN_APPROVED", None)
    try:
        cg.reserve("anthropic/claude-fable-5-1", 3000, 4000); raise SystemExit("FAIL: real call allowed without approval")
    except cg.RealRunNotApproved:
        print("real call blocked without Isaac's YES OK")
    os.environ["CRS_REAL_RUN_APPROVED"] = "YES"
    t = cg.reserve("anthropic/claude-fable-5-1", 3000, 4000)
    assert abs(sum(v["usd"] for v in cg._load()["reserved"].values()) - (3000*10 + 4000*50)/1e6) < 1e-9
    cg.settle(t, "anthropic/claude-fable-5-1", 3000, 1000)
    assert abs(cg.spent() - (3000*10 + 1000*50)/1e6) < 1e-9
    # push the ledger to $99.99 and confirm the next call aborts
    st = cg._load(); st["spent"] = 99.99; json.dump(st, open(cg.STATE, "w"))
    try:
        cg.reserve("openai/gpt-6-astra", 3000, 4000); raise SystemExit("FAIL: cap not enforced")
    except cg.CostCapExceeded as e:
        print("cap abort OK:", str(e)[:90])
    # env var can lower the cap but never raise it
    os.environ["CRS_COST_CAP_USD"] = "1000"; assert cg.cap() == 100.0
    os.environ["CRS_COST_CAP_USD"] = "5"; assert cg.cap() == 5.0
    os.environ.pop("CRS_COST_CAP_USD")
    # Argon price expiry
    cg.price("google/gemini-4-argon", dt.date(2026, 11, 30))
    try:
        cg.price("google/gemini-4-argon", dt.date(2026, 12, 1)); raise SystemExit("FAIL: expired price accepted")
    except cg.CostCapExceeded:
        print("Argon price refused after 2026-11-30 OK")
    try:
        cg.price("openai/gpt-9"); raise SystemExit("FAIL")
    except cg.CostCapExceeded:
        print("unknown model refused OK")
    os.environ.pop("CRS_REAL_RUN_APPROVED")
    json.dump(dict(date=dt.datetime.now().isoformat(timespec="seconds"), ok=bool(ok), modes=results), open(os.path.join(HERE, "logs", "mock_validation", "summary.json"), "w"), indent=1)
    print("ALL VALIDATION", "PASSED" if ok else "FAILED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
