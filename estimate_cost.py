#!/usr/bin/env python3
"""Offline cost estimate for ONE full real run (3 models x 16 samples x 2 epochs + cross-provider grader calls).
Counts input tokens with tiktoken o200k_base on the actual prompts (a proxy: Claude and Gemini tokenisers differ, so a
+25% margin is applied in the 'high' scenario). Output tokens are ASSUMED, not measured. No model is called."""
import json, os, tiktoken
import crs_pilot as C
import cost_guard as cg

enc = tiktoken.get_encoding("o200k_base")
samples = C.load_samples()
n_in = [len(enc.encode("\n".join(m.text for m in s.input))) for s in samples]
faulty = [s for s in samples if s.metadata["variant"] == "faulty"]
avg_in = sum(n_in) / len(n_in)
tot_in_one_pass = sum(n_in)                 # 16 samples
EPOCHS = 2
MODELS = {"claude-fable-5-1": "openai/gpt-6-astra", "gpt-6-astra": "google/gemini-4-argon", "gemini-4-argon": "anthropic/claude-fable-5-1"}
GRADER_IN = 700   # delta summary + findings JSON + instructions (assumed)
SCEN = {  # solver output tokens per call (incl. any hidden reasoning), grader output tokens, input margin
  "low":   dict(out=400,  gout=100, margin=1.00),
  "mid":   dict(out=1200, gout=150, margin=1.10),
  "high":  dict(out=2500, gout=250, margin=1.25),
  "worst": dict(out=C.MAX_OUT_TOKENS, gout=C.GRADER_MAX_OUT_TOKENS, margin=1.25),   # every call hits max_tokens
}
rows = []; detail = {}
for name, sc in SCEN.items():
    total = 0.0; per = {}
    for mid, gid in MODELS.items():
        pin, pout, _ = cg.PRICES[mid]
        in_tok = tot_in_one_pass * EPOCHS * sc["margin"]; out_tok = len(samples) * EPOCHS * sc["out"]
        solver_cost = (in_tok * pin + out_tok * pout) / 1e6
        gpin, gpout, _ = cg.PRICES[gid.split("/")[-1]]
        ncalls = len(faulty) * EPOCHS
        g_cost = (ncalls * GRADER_IN * sc["margin"] * gpin + ncalls * sc["gout"] * gpout) / 1e6
        per[mid] = dict(solver_usd=round(solver_cost, 3), grader_usd=round(g_cost, 3), grader_model=gid.split('/')[-1])
        total += solver_cost + g_cost
    detail[name] = dict(total_usd=round(total, 2), per_model=per, assumptions=sc)
out = dict(samples=len(samples), epochs=EPOCHS, solver_calls=len(samples) * EPOCHS * 3, grader_calls=len(faulty) * EPOCHS * 3,
           avg_prompt_tokens=round(avg_in), prompt_tokens_per_pass_16_samples=tot_in_one_pass,
           per_sample_tokens={s.id: n for s, n in zip(samples, n_in)}, scenarios=detail,
           prices_usd_per_M={k: v[:2] for k, v in cg.PRICES.items()}, argon_price_valid_until=cg.PRICES["gemini-4-argon"][2])
json.dump(out, open("cost_estimate.json", "w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if k != "per_sample_tokens"}, indent=1))
