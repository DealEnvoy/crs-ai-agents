"""Hard total cost cap for CRS Pilot 0. Local file ledger, shared by every run and process.
Every real model call (solver and grader) must reserve its WORST-CASE cost first; if
spent + reserved + this call's worst case would pass HARD_CAP_USD the call raises CostCapExceeded
and the run aborts. mockllm calls cost 0 and never touch the real-run gate.
List prices are the ones Isaac gave (per million tokens): Fable and Astra $10 in / $50 out,
Argon $2 in / $10 out until 2026-11-30. After that date Argon calls are refused until PRICES is updated."""
import datetime as dt, fcntl, json, os, time, uuid

HERE = os.path.dirname(os.path.abspath(__file__))
LEDGER_DIR = os.path.join(HERE, "ledger")
STATE = os.path.join(LEDGER_DIR, "spend.json")
LOCK = os.path.join(LEDGER_DIR, "spend.lock")
CALLS = os.path.join(LEDGER_DIR, "calls.jsonl")
HARD_CAP_USD = 100.0

# model id -> (usd per M input tokens, usd per M output tokens, price valid until or None)
PRICES = {
    "claude-fable-5-1": (10.0, 50.0, None),
    "gpt-6-astra": (10.0, 50.0, None),
    "gemini-4-argon": (2.0, 10.0, "2026-11-30"),
}
RESERVATION_TTL_S = 900


class CostCapExceeded(RuntimeError):
    pass


class RealRunNotApproved(RuntimeError):
    pass


def cap() -> float:
    c = float(os.environ.get("CRS_COST_CAP_USD", HARD_CAP_USD))
    return min(c, HARD_CAP_USD)  # an env var can lower the cap, never raise it


def is_mock(model_name: str) -> bool:
    return str(model_name).startswith("mockllm/")


def model_id(model_name: str) -> str:
    return str(model_name).split("/")[-1]


def price(model_name: str, today: dt.date | None = None):
    mid = model_id(model_name)
    if mid not in PRICES:
        raise CostCapExceeded(f"no list price recorded for {mid}; refusing to call it")
    pin, pout, until = PRICES[mid]
    today = today or dt.date.today()
    if until and today > dt.date.fromisoformat(until):
        raise CostCapExceeded(f"{mid} price {pin}/{pout} was only valid until {until}; update PRICES before running")
    return pin, pout


def call_cost(model_name: str, in_tok: int, out_tok: int) -> float:
    pin, pout = price(model_name)
    return (in_tok * pin + out_tok * pout) / 1e6


def _load():
    os.makedirs(LEDGER_DIR, exist_ok=True)
    if not os.path.exists(STATE):
        return {"spent": 0.0, "reserved": {}}
    return json.load(open(STATE))


def _locked(fn):
    os.makedirs(LEDGER_DIR, exist_ok=True)
    with open(LOCK, "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        try:
            return fn()
        finally:
            fcntl.flock(lk, fcntl.LOCK_UN)


def require_real_run_approval(model_name: str):
    if is_mock(model_name):
        return
    if os.environ.get("CRS_REAL_RUN_APPROVED") != "YES":
        raise RealRunNotApproved("real model call blocked: Isaac's YES is required (set CRS_REAL_RUN_APPROVED=YES only after he says yes)")


def reserve(model_name: str, est_in_tokens: int, max_out_tokens: int) -> str | None:
    """Reserve worst-case cost. Returns a token (None for mock models)."""
    if is_mock(model_name):
        return None
    require_real_run_approval(model_name)
    worst = call_cost(model_name, est_in_tokens, max_out_tokens)
    token = uuid.uuid4().hex

    def _do():
        st = _load()
        now = time.time()
        st["reserved"] = {k: v for k, v in st["reserved"].items() if now - v["t"] < RESERVATION_TTL_S}
        outstanding = sum(v["usd"] for v in st["reserved"].values())
        if st["spent"] + outstanding + worst > cap():
            raise CostCapExceeded(
                f"cost cap ${cap():.2f} would be passed: spent ${st['spent']:.4f} + reserved ${outstanding:.4f} + this call worst case ${worst:.4f}")
        st["reserved"][token] = {"t": now, "usd": worst}
        json.dump(st, open(STATE, "w"))
    _locked(_do)
    return token


def settle(token: str | None, model_name: str, in_tok: int, out_tok: int, tag: str = ""):
    if token is None:
        return 0.0
    cost = call_cost(model_name, in_tok, out_tok)

    def _do():
        st = _load()
        st["reserved"].pop(token, None)
        st["spent"] = round(st["spent"] + cost, 6)
        json.dump(st, open(STATE, "w"))
        with open(CALLS, "a") as fh:
            fh.write(json.dumps(dict(ts=dt.datetime.now().isoformat(timespec="seconds"), model=model_id(model_name),
                                     in_tok=in_tok, out_tok=out_tok, usd=round(cost, 6), total_usd=st["spent"], tag=tag)) + "\n")
        if st["spent"] > cap():
            raise CostCapExceeded(f"cost cap ${cap():.2f} passed: spent ${st['spent']:.4f}")
    _locked(_do)
    return cost


def effective_input_tokens(usage) -> int:
    """Billable input tokens from an Inspect ModelUsage. Providers (Anthropic) report cache writes/reads separately from
    input_tokens, so they must be added or the ledger undercounts. Conservative: cache write at 1.25x, cache read at 1.0x."""
    g = lambda n: getattr(usage, n, 0) or 0
    return int(g("input_tokens") + 1.25 * g("input_tokens_cache_write") + g("input_tokens_cache_read"))


def adjust(usd: float, tag: str):
    """Add a manual correction to the ledger (used once for the smoke test, before effective_input_tokens existed)."""
    def _do():
        st = _load()
        st["spent"] = round(st["spent"] + usd, 6)
        json.dump(st, open(STATE, "w"))
        with open(CALLS, "a") as fh:
            fh.write(json.dumps(dict(ts=dt.datetime.now().isoformat(timespec="seconds"), model="adjustment", in_tok=0, out_tok=0,
                                     usd=round(usd, 6), total_usd=st["spent"], tag=tag)) + "\n")
    _locked(_do)


def release(token: str | None):
    """Drop a reservation when the call failed before any tokens were billed."""
    if token is None:
        return

    def _do():
        st = _load()
        st["reserved"].pop(token, None)
        json.dump(st, open(STATE, "w"))
    _locked(_do)


def spent() -> float:
    return _locked(lambda: _load()["spent"])
