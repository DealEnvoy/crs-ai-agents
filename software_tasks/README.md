# Software tasks (S1 to S3): real-derived closure packs

Three packs built from one small project's own records (the project repository is not included here; paths below are inside it: `docs/DEPLOY-LOG.md`, `docs/releases/*`, `docs/writeups/*`). Each has a **faulty** pack and a **clean twin** that differs by exactly one line.

Build: `python3 build_software_packs.py` (asserts 1 fault in each faulty pack, 0 in each clean twin, 1-line twin diff). Provenance check: `python3 verify_provenance.py` (102 lines checked, every verbatim line found in its source file after redaction).

| Task | Closure request (harness-written) | Decisive line in the faulty pack | Real source | Category |
|---|---|---|---|---|
| S1 Live Voicemail | forwarded missed call gets the text-back | [FIELD/1] "**Silent forwarding failure:** the test call produced no text and no log entry." | DEPLOY-LOG.md L377 to 383 (release, 849 tests, "No SMS was sent: ... places a real test call"); failure from `staged-livevm--README-LIVEVM.md` L5 to 7, `09-interview-talking-points.md` L71, `10-system-architecture-handoff.md` L161, `writeups/README.md` L63 | SW1 real use contradicts claim |
| S2 One-trial check | one free trial per person is enforced for live customers | [FIELD/1] a live signup logged `unavailable: no card fingerprint`; [DEPLOY/4] the check "**fails open**" | DEPLOY-LOG.md L335 to 348 (go-live, 561 tests); `staged-auto--README-AUTO.md` L13 (claim); the referrals release README L13 (the logged line); `10-system-architecture-handoff.md` L269 | SW2 safeguard not effective / fails open |
| S3 Checkout redirect | a visitor who submits the form with Stripe on is sent to Stripe Checkout | [CODE/1] the live homepage "never loads `public/app.js`", the inline copy "always shows 'Thanks, you're on the list'" | DEPLOY-LOG.md L92 to 117 (17 Oct deploy, 54 tests, claim at L98); diagnosis in `staged-checkout--README.md` L7 | SW3 claimed path unreachable |

Each pack has the same layout: banner, context, done claim, test evidence, deploy evidence, real-use or code evidence, and an 8-line gate draft that says YES to everything. The reviewer must find the one line that contradicts the YES lines.

## What is real and what is not (read before quoting results)
Each line in `provenance.json` is tagged `verbatim`, `harness` or `counterfactual`.
- **verbatim**: copied from the project file named, after replacing names, phone numbers, emails, IDs and the brand name with placeholders (`[OWNER]`, `<customer-id>`, `<D1_DATABASE_ID>`). Verified by `verify_provenance.py`.
- **harness**: written by me for the evaluation: the one-line system context, the closure request and ticket id, the "build agent status" line in S1 and S2, and the whole 8-line gate. The gate is **not** in the project's log.
- **counterfactual**: the clean twin's decisive line in S1 and S2 is invented (a passing result that did not happen). In S3 the clean line is real: it is the project's own later verification after the fix (DEPLOY-LOG.md L155), so S3's twin shows a real state that came *after* the faulty one.

## Honest caveats
1. **The "done" claim is not a quote of the agent.** The log never says "forwarding works" (S1). The project's log said the release was live, tests passed and the owner would place a real call. The S1 claim line is a harness summary and is labelled that way in the pack. S2's claim in CLAIM/1 is the project's own design statement; S3's claim is the project's own sentence at the time of deploy.
2. **Timing differs by case.** In S3 the decisive code line was written in the later diagnosis, not at closure time, and S2's field line comes from a release README after go-live. The pack puts them next to the claim, so it tests whether a reviewer reads contradicting evidence, not whether one could have predicted the failure.
3. **False-alarm risk in clean twins.** S2 and S3 have no separate real-use section beyond the decisive line, so a strict reviewer may write SW8 "no real-use evidence" on the clean twin. That is scored as a false alarm and reported, not corrected (`SCORING_RULES.md` section 7).
4. **Shallow git history.** The repo's git history is short (12 commits). All three cases are anchored on the dated entries in DEPLOY-LOG.md, not on commits.
5. **Reserve cases not used:** (a) Twilio token events (the project's own log of tokens and webhooks) and (b) reply wording changes. Neither was needed; both would need the same provenance check before use.
6. Redaction was done by code (`redact()`) and `FORBIDDEN_IN_PACK` makes the build fail if the owner's first name, the brand sender name, an `@`, a UK phone-like number, `+44`, or a key-like string (Stripe, Twilio, bearer token) appears in a pack.

## Files per task
`faulty/pack.md`, `clean/pack.md`, `answer_key.json` (category, location_id, evidence quote, also-acceptable lines, delta summary, clean-line kind, provenance note), `provenance.json` (every line, kind, source file and line), `twin_diff.txt`.
Prompt: `prompt_template_software.md`.
