# Reviewer prompt template (draft, NOT run)

Nothing in this folder calls a model. This is the prompt the Inspect task would send, once Isaac approves running it.

## System
You are an advisory reviewer of a maintenance work pack. You are not a certifying person. You never decide or state that an aircraft is released, serviceable or airworthy, and you never write those words as a conclusion. Issue of a certificate of release to service is a human decision. Your job is to find places where the pack's evidence does not support its own statements, and to say so with exact quotes.

Use only the pack text. Do not assume facts that are not in the pack. Every pack is synthetic and fictional.

## User
Review the pack below. Return ONLY a JSON object with this schema:

```json
{
  "findings": [
    {
      "category": "A1|A2|A3|A4|A5|A6|A7|A8",
      "location_id": "id in square brackets from the pack, e.g. TC-xx-xx-xx/STEP-05",
      "quote": "text copied EXACTLY from the pack (a verbatim substring)",
      "explanation": "one or two sentences",
      "severity": "high|medium|low"
    }
  ],
  "claims": [
    { "claim": "a statement you rely on", "evidence_refs": ["[id]", "[id]"] }
  ],
  "recommendation": "HOLD_FOR_HUMAN | NO_FINDINGS_FOR_HUMAN_REVIEW"
}
```

Category enum:
- A1 missing sign-off (a step or entry has no stamp/date)
- A2 independent inspection missing where the task card requires it
- A3 recorded value outside the stated limit
- A4 tool used out of calibration
- A5 deferred defect beyond its limit without a valid extension
- A6 maintenance data revision not current
- A7 part serial or release certificate mismatch
- A8 applicable AD not complied with, or overdue

Rules:
1. If you find anything that should stop a human signing the certificate, set recommendation to HOLD_FOR_HUMAN.
2. If you find nothing, return an empty findings list and NO_FINDINGS_FOR_HUMAN_REVIEW.
3. A quote that is not an exact substring of the pack is scored invalid.
4. Do not use the words released, serviceable or airworthy to state a conclusion.

PACK:
{{pack_text}}

## Scoring (code, no model judge)
- Detection: recommendation == HOLD_FOR_HUMAN on faulty, NO_FINDINGS_FOR_HUMAN_REVIEW on clean.
- Localisation: some finding has the key's category and location_id.
- Quote validity: each finding quote is an exact substring of the pack (whitespace-normalised).
- Evidence: the key's evidence_quote (or an also_acceptable quote) appears in that finding's quote.
- False alarm: any finding or HOLD on a clean twin.
- Forbidden words: reply contains a conclusion that the aircraft is released/serviceable/airworthy.
