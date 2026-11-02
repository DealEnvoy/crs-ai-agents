"""Secondary metric only: re-grade GPT-6 Astra's v1 findings with the registered grader (Gemini 4 Argon). Writes results/gpt_regrade_argon.json."""
import asyncio, json, sys
import crs_pilot as c
ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
src = "results/cases.json" if ver == "v1" else "results/v2/cases.json"
cases = json.load(open(src))
samples = {s.id: s.metadata for s in c.load_samples()} if ver == "v1" else {s.id: s.metadata for s in c.load_samples()}
async def main():
    out = []
    for x in cases:
        if x["model"] != "gpt-6-astra" or x["variant"] != "faulty" or not x["parsed"] or x["n_findings"] == 0:
            continue
        md = samples[f'{x["task"]}-faulty']
        d = c.parse_reply(x["reply"])
        g, ans = await c.run_grader("openai/gpt-6-astra", md, d)
        out.append(dict(task=x["task"], epoch=x["epoch"], grader=g, argon_yes=ans, claude_graded_yes=x["grader_yes"]))
    return out
res = asyncio.run(main())
json.dump(res, open(f"results/gpt_regrade_argon_{ver}.json", "w"), indent=1)
print(len(res), "argon yes:", sum(1 for r in res if r["argon_yes"]), "claude yes:", sum(r["claude_graded_yes"] for r in res), [r["grader"] for r in res][:1])
