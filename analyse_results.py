"""Reads Inspect logs of the real run and writes results/results.csv, results/RESULTS_data.json. Pure code, no model calls."""
import glob, json, math, csv, os, sys
VER = sys.argv[1] if len(sys.argv) > 1 else "v1"
OUT = "results" if VER == "v1" else "results/v2"
RUN = "logs/real_run_1" if VER == "v1" else "logs/real_run_2"
os.makedirs(OUT, exist_ok=True)
from inspect_ai.log import read_eval_log

def wilson(k, n, z=1.96):
    if n == 0: return (float("nan"), float("nan"))
    p = k / n; d = 1 + z*z/n
    c = (p + z*z/(2*n)) / d; h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / d
    return (max(0.0, c-h), min(1.0, c+h))

MODELS = {"anthropic": "claude-fable-5-1", "openai": "gpt-6-astra", "google": "gemini-4-argon"}
rows, detail, cases = [], {}, []
for prov, mid in MODELS.items():
    sub = "google_argon" if (VER == "v1" and prov == "google") else prov
    fs = sorted(glob.glob(f"{RUN}/{sub}/*.eval"))
    log = read_eval_log(fs[-1]) if fs else None
    ok = log is not None and log.status == "success" and log.samples
    detail[mid] = dict(status=(log.status if log else "no log"), n_samples=len(log.samples) if ok else 0)
    if not ok:
        continue
    for s in log.samples:
        v = s.scores["crs_scorer"].value
        md = s.metadata
        reply = s.output.completion if s.output else ""
        cases.append(dict(model=mid, task=md["task_id"], domain=md["domain"], variant=md["variant"], epoch=s.epoch, **v,
                          answer=s.scores["crs_scorer"].answer, reply=reply, grader=s.scores["crs_scorer"].explanation))
with open(f"{OUT}/cases.json", "w") as f:
    json.dump(cases, f, indent=1)

def agg(cs, model, domain=None):
    c = [x for x in cs if x["model"] == model and (domain is None or x["domain"] == domain)]
    fa = [x for x in c if x["variant"] == "faulty"]; cl = [x for x in c if x["variant"] == "clean"]
    r = dict(model=model, domain=domain or "all",
             faulty_n=len(fa), caught=sum(x["rec_ok"] for x in fa), missed=sum(1-x["rec_ok"] for x in fa),
             localised=sum(x["localised"] for x in fa), evidence=sum(x["evidence"] for x in fa), category=sum(x["category_ok"] for x in fa),
             clean_n=len(cl), false_alarms=sum(x["false_alarm"] for x in cl), clean_pass=sum(x["rec_ok"] for x in cl),
             findings=sum(x["n_findings"] for x in c), valid_quotes=sum(x["n_valid_quotes"] for x in c),
             invalid_quotes=sum(x["n_findings"]-x["n_valid_quotes"] for x in c),
             authority_violations=sum(x["forbidden"] for x in c), total_n=len(c), parsed=sum(x["parsed"] for x in c),
             claims=sum(x["claims_total"] for x in c), claims_valid=sum(x["claims_ref_valid"] for x in c),
             grader_ran=sum(x["grader_ran"] for x in fa), grader_yes=sum(x["grader_yes"] for x in fa))
    for name, k, n in [("caught", r["caught"], r["faulty_n"]), ("localised", r["localised"], r["faulty_n"]), ("evidence", r["evidence"], r["faulty_n"]),
                       ("false_alarms", r["false_alarms"], r["clean_n"]), ("invalid_quotes", r["invalid_quotes"], r["findings"]),
                       ("authority_violations", r["authority_violations"], r["total_n"])]:
        lo, hi = wilson(k, n); r[name + "_ci_lo"], r[name + "_ci_hi"] = round(lo, 3), round(hi, 3)
    return r

out = []
for mid in MODELS.values():
    if any(x["model"] == mid for x in cases):
        for dom in (None, "aviation", "software"):
            out.append(agg(cases, mid, dom))
if out:
    with open(f"{OUT}/results.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
json.dump(dict(rows=out, detail=detail), open(f"{OUT}/RESULTS_data.json", "w"), indent=1)
for r in out:
    print(r["model"], r["domain"], "caught", f'{r["caught"]}/{r["faulty_n"]}', "loc", r["localised"], "evid", r["evidence"], "FA", f'{r["false_alarms"]}/{r["clean_n"]}',
          "invalidQ", f'{r["invalid_quotes"]}/{r["findings"]}', "auth", r["authority_violations"], "parse", r["parsed"], "grader", f'{r["grader_yes"]}/{r["grader_ran"]}')
print(detail)
