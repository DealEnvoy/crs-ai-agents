"""Per-provider spend from ledger/calls.jsonl (list-price estimate; upper bound). Phases by timestamp (Europe/London = GMT on 2 Nov 2026)."""
import json, collections
P = {"claude-fable-5-1": "anthropic", "gpt-6-astra": "openai", "gemini-4-argon": "google", "adjustment": "anthropic"}
rows = [json.loads(l) for l in open("ledger/calls.jsonl")]
def phase(r):
    t = r["ts"][11:]
    if t < "01:30:00": return "v1_main_run_(anthropic+openai, incl. smoke)"
    if t < "01:41:27": return "v1_argon_(smoke+full+regrade_of_GPT)"
    return "v2_all_three"
out = collections.OrderedDict()
for r in rows:
    ph = phase(r); pr = P[r["model"]]
    d = out.setdefault(ph, {}).setdefault(pr, dict(usd=0.0, calls=0, in_tok=0, out_tok=0))
    d["usd"] += r["usd"]; d["calls"] += 1; d["in_tok"] += r["in_tok"]; d["out_tok"] += r["out_tok"]
    if r["model"] == "gemini-4-argon" and r["tag"] == "grader" and ph.startswith("v1"):
        out[ph].setdefault("google_of_which_regrade_of_GPT", dict(usd=0.0, calls=0))
        out[ph]["google_of_which_regrade_of_GPT"]["usd"] += r["usd"]; out[ph]["google_of_which_regrade_of_GPT"]["calls"] += 1
tot = collections.defaultdict(float); 
for ph, d in out.items():
    for pr, v in d.items():
        if pr in ("anthropic", "openai", "google"): tot[pr] += v["usd"]
        v["usd"] = round(v["usd"], 4)
res = dict(by_phase=out, total_by_provider={k: round(v, 4) for k, v in tot.items()}, total_usd=round(sum(tot.values()), 4), cap_usd=100.0,
           note="List-price estimate from reported token usage (Anthropic cache writes x1.25, reads x1.0); an upper bound on invoices. Includes grader calls. Anthropic includes the $0.0328 logged adjustment.")
json.dump(res, open("results/spend_all.json", "w"), indent=1)
print(json.dumps(res, indent=1))
