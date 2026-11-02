"""Builds results/chart.png from results/RESULTS_data.json and results/cases.json (no model calls)."""
import json, collections, sys
VER = sys.argv[1] if len(sys.argv) > 1 else "v1"
OUT = "results" if VER == "v1" else "results/v2"
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
D = json.load(open(f"{OUT}/RESULTS_data.json")); cases = json.load(open(f"{OUT}/cases.json"))
allrows = {r["model"]: r for r in D["rows"] if r["domain"] == "all"}
names = ["claude-fable-5-1", "gpt-6-astra", "gemini-4-argon"]
fig, ax = plt.subplots(1, 2, figsize=(12, 4.8), gridspec_kw=dict(width_ratios=[1.1, 1.4]))
w = 0.26; cols = {"caught": "#2e7d32", "missed": "#c62828", "false": "#ef6c00"}
for i, n in enumerate(names):
    r = allrows.get(n)
    if not r:
        ax[0].text(i, 8, "NOT RUN\nGoogle key has no\nquota for this model\n(free-tier limit 0)", ha="center", va="center", fontsize=8, color="#555")
        continue
    vals = [("caught", r["caught"]), ("missed", r["missed"]), ("false", r["false_alarms"])]
    for j, (k, v) in enumerate(vals):
        ax[0].bar(i + (j - 1) * w, v, w, color=cols[k], label={"caught": "faults caught (of 16 faulty)", "missed": "faults missed (of 16 faulty)", "false": "false alarms (of 16 clean twins)"}[k] if i == 0 else None)
        ax[0].text(i + (j - 1) * w, v + 0.25, str(v), ha="center", fontsize=9)
ax[0].set_xticks(range(3)); ax[0].set_xticklabels(["Claude Fable 5.1", "GPT-6 Astra", "Gemini 4 Argon"], fontsize=9)
ax[0].set_ylim(0, 24); ax[0].set_ylabel("task-epochs (8 tasks x 2 epochs)"); ax[0].legend(fontsize=8, loc="upper right")
ax[0].set_title("Caught / missed / false alarms per model", fontsize=10)
tasks = ["A1", "A2", "A3", "A5", "A8", "S1", "S2", "S3"]; x = range(len(tasks)); w2 = 0.27
for i, (n, c) in enumerate([("claude-fable-5-1", "#1565c0"), ("gpt-6-astra", "#6a1b9a"), ("gemini-4-argon", "#00897b")]):
    fa = [sum(x_["false_alarm"] for x_ in cases if x_["model"] == n and x_["task"] == t and x_["variant"] == "clean") for t in tasks]
    ax[1].bar([k + (i - 1) * w2 for k in x], fa, w2, color=c, label=n)
ax[1].set_xticks(list(x)); ax[1].set_xticklabels(tasks); ax[1].set_yticks([0, 1, 2]); ax[1].set_ylim(0, 2.4)
ax[1].set_ylabel("false alarms on the clean twin (of 2 epochs)"); ax[1].legend(fontsize=8)
ax[1].set_title("Where the false alarms were" + (" (A8, S1-S3 twins have known design flaws, see RESULTS.md)" if VER == "v1" else " (v2 repaired twins)"), fontsize=9)
fig.suptitle("CRS Pilot 0, %s, 2 Nov 2026 (descriptive counts, n is tiny)" % ("v1 (original twins), three models" if VER == "v1" else "v2 (repaired clean twins), three models"), fontsize=11)
fig.tight_layout(); fig.savefig(f"{OUT}/chart.png", dpi=150)
print("ok")
