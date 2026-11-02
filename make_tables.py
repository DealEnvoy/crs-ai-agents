import json, sys
def tables(VER):
    OUT = "results" if VER == "v1" else "results/v2"
    D = json.load(open(f"{OUT}/RESULTS_data.json")); cases = json.load(open(f"{OUT}/cases.json"))
    R = {(r["model"], r["domain"]): r for r in D["rows"]}
    ms = ["claude-fable-5-1", "gpt-6-astra", "gemini-4-argon"]
    def ci(r, k, n): return f'{r[k+"_ci_lo"]:.2f} to {r[k+"_ci_hi"]:.2f}'
    L = []
    L.append("| Measure | Claude Fable 5.1 | GPT-6 Astra | Gemini 4 Argon |"); L.append("|---|---|---|---|")
    def row(label, f): L.append("| " + label + " | " + " | ".join(f(R[(m, "all")]) for m in ms) + " |")
    row("Seeded faults caught (HOLD_FOR_HUMAN), of 16 faulty", lambda r: f'**{r["caught"]} / 16** (CI {ci(r,"caught",16)})')
    row("Seeded faults missed", lambda r: str(r["missed"]))
    row("...with the right location_id", lambda r: f'{r["localised"]} / 16')
    row("...with an exact-quote evidence match", lambda r: f'{r["evidence"]} / 16')
    row("...with the right category code (secondary)", lambda r: f'{r["category"]} / 16')
    row("False alarms on the 16 clean twins", lambda r: f'**{r["false_alarms"]} / 16** (CI {ci(r,"false_alarms",16)})')
    row("Invented or non-exact quotes", lambda r: f'**{r["invalid_quotes"]} / {r["findings"]}** findings (CI {ci(r,"invalid_quotes",0)})')
    row("Authority-regex hits, of 32 replies", lambda r: f'**{r["authority_violations"]} / 32** (CI {ci(r,"authority_violations",32)})')
    row("Replies that parsed as the required JSON", lambda r: f'{r["parsed"]} / 32')
    row("Claims whose evidence_refs all exist in the pack", lambda r: f'{r["claims_valid"]} / {r["claims"]}')
    row("Findings in total (clean + faulty replies)", lambda r: str(r["findings"]))
    L.append("")
    L.append("| Model | Aviation (5 tasks, n=10 per arm) | Software (3 tasks, n=6 per arm) |"); L.append("|---|---|---|")
    for m in ms:
        a, s = R[(m, "aviation")], R[(m, "software")]
        L.append(f'| {m} | caught {a["caught"]}/10, false alarms {a["false_alarms"]}/10 | caught {s["caught"]}/6, false alarms {s["false_alarms"]}/6 |')
    return "\n".join(L), cases
def fa_by_task(cases, m, t): return sum(x["false_alarm"] for x in cases if x["model"] == m and x["task"] == t and x["variant"] == "clean")
if __name__ == "__main__":
    t1, c1 = tables("v1"); t2, c2 = tables("v2")
    ms = ["claude-fable-5-1", "gpt-6-astra", "gemini-4-argon"]; tasks = ["A1", "A2", "A3", "A5", "A8", "S1", "S2", "S3"]
    open("results/tables_v1.md", "w").write(t1); open("results/tables_v2.md", "w").write(t2)
    L = ["| Clean twin | Claude v1 | Claude v2 | GPT v1 | GPT v2 | Argon v1 | Argon v2 |", "|---|---|---|---|---|---|---|"]
    for t in tasks:
        L.append("| " + t + " | " + " | ".join(f"{fa_by_task(c1 if v==1 else c2, m, t)}/2" for m in ms for v in (1, 2)) + " |")
    L.append("| **Total** | " + " | ".join(f"**{sum(fa_by_task(c1 if v==1 else c2, m, t) for t in tasks)}/16**" for m in ms for v in (1, 2)) + " |")
    open("results/tables_false_alarms.md", "w").write("\n".join(L))
    print(t2); print(); print("\n".join(L))
