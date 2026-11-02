#!/usr/bin/env python3
"""Free end-to-end test that the $ cap aborts a running eval. Uses a local fake provider ('fakecost/fake-model',
no network) that reports token usage, priced at the Fable list price, against a TEMP ledger with the cap
lowered to $0.50 via CRS_COST_CAP_USD. Expect: the eval fails with CostCapExceeded before 16 x 2 samples finish,
and the ledger total never exceeds the cap."""
import os, sys, tempfile, json
for k in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GOOGLE_API_KEY"):
    assert k not in os.environ, "run with env -u for the three keys"
from inspect_ai import eval as inspect_eval
from inspect_ai.model import ModelAPI, ModelOutput, ModelUsage, modelapi, get_model
import cost_guard as cg
import crs_pilot as C

tmp = tempfile.mkdtemp()
cg.LEDGER_DIR = tmp; cg.STATE = os.path.join(tmp, "spend.json"); cg.LOCK = os.path.join(tmp, "spend.lock"); cg.CALLS = os.path.join(tmp, "calls.jsonl")
cg.PRICES["fake-model"] = (10.0, 50.0, None)
os.environ["CRS_REAL_RUN_APPROVED"] = "YES"      # allowed here only because the provider below is local and fake
os.environ["CRS_COST_CAP_USD"] = "0.50"
C.GRADER_FACTORY = lambda name: get_model("mockllm/model")

@modelapi(name="fakecost")
class FakeCost(ModelAPI):
    def __init__(self, model_name, base_url=None, api_key=None, config=None, **kw):
        super().__init__(model_name, base_url, api_key, [], config) if config else super().__init__(model_name, base_url, api_key)
    async def generate(self, input, tools, tool_choice, config):
        out = ModelOutput.from_content(model="fake-model", content='{"findings": [], "claims": [], "recommendation": "NO_FINDINGS_FOR_HUMAN_REVIEW"}')
        out.usage = ModelUsage(input_tokens=3000, output_tokens=1500, total_tokens=4500)   # $0.105 per call
        return out

logs = inspect_eval(C.crs_pilot(), model="fakecost/fake-model", log_dir=os.path.join(tmp, "logs"), display="none", max_samples=2)
log = logs[0]
spent = json.load(open(cg.STATE))["spent"]
calls = sum(1 for _ in open(cg.CALLS))
print("eval status:", log.status, "| error:", (log.error.message[:120] if log.error else None))
print(f"real-priced fake calls made: {calls}, ledger spent ${spent:.3f}, cap $0.50")
assert log.status == "error" and "cost cap" in (log.error.message if log.error else "").lower()
assert spent <= 0.50 + 1e-9
assert calls < 32
print("COST ABORT TEST PASSED (eval aborted by the cap; spend stayed at or under the cap)")
