# Certificate of Release to Service (CRS) for AI agents, Pilot 0: 5 aviation-style tasks

> Status note: this file was written before the runs (see the repository `README.md` for what was run and found). Statements below such as "draft", "No model has seen these packs" and "Local files only" describe that earlier stage.

Local files only. No model was called, nothing was published or sent. Built 1 Nov 2026 (Europe/London).

## Read this first
**Every work pack here is invented.** The operator, organisation, aircraft type ("Aerowing AW-7"), registrations (G-SYN1, G-SYN2, G-SYN3, G-SYN5, G-SYN8), part numbers, serials, tool IDs, people codes (AUTH-nn, IQP-nn, CS-nn), limits, MEL entries, AD numbers and dates are fictional. No real airline, employer, person or record is used. Each pack carries a banner saying it is synthetic and must not be used on real aircraft. The packs are only *inspired by* the kind of failure described in the public AAIB reports below. They do not reproduce those reports' facts, figures or documents.

Each task has a faulty pack with exactly one seeded fault and a clean twin that differs by exactly one line (the fix). The pack is a short work pack: context, revision list, limits, tool register, task card, parts, MEL/ADD, AD list, handover, and a *prefilled CRS draft* (clearly marked "NOT ISSUED; issue is a human decision"). The reviewer model is advisory only (see `prompt_template.md`).

## The 5 tasks

| ID | Fault type | Inspiring AAIB report (verified) | What the faulty pack seeds | Clean twin difference |
|---|---|---|---|---|
| A1 `A1_missing_signoff` | A1 missing sign-off | AAIB Bulletin 10/2016, Boeing 747-436 G-CIVX. https://www.gov.uk/aaib-reports/aaib-investigation-to-boeing-747-436-g-civx | Gear selector module replacement (G-SYN1, WO-SYN-1101). Step 07 (rig pins) has blank stamp and date. Handover says steps 01-07 complete; CRS draft says all steps stamped. | Step 07 stamped AUTH-02, 2026-03-13. |
| A2 `A2_independent_inspection` | A2 independent inspection missing | AAIB Bulletin 7/2012, ATR72-202 EI-SLG. https://www.gov.uk/aaib-reports/atr72-202-ei-slg-15-march-2011 | RLU actuator replacement, a critical task (G-SYN2, WO-SYN-2207, TC-27-23-05). The card requires an independent inspection (AMC4 145.A.48(c)(2) style); the INDEP line has blank IQP stamp and date; CRS draft says it is recorded. | INDEP line stamped IQP-03, 2026-05-20. |
| A3 `A3_out_of_limits_torque` | A3 value outside limit | AAIB Bulletin 2/2001, Agusta A109E Power G-TVAA. https://www.gov.uk/aaib-reports/agusta-a109e-power-g-tvaa-17-june-2000 | Nut torque task (G-SYN3, WO-SYN-3318, TC-61-12-03). Step 05 records 41 Nm against an invented limit of 25-30 Nm; the independent inspector has stamped; CRS draft says measurements within limits. | Recorded torque 27 Nm. |
| A5 `A5_deferred_defect_overdue` | A5 deferred defect beyond limit | AAIB Bulletin 10/2019, Boeing 737-4Q8 G-JMCR. https://www.gov.uk/aaib-reports/aaib-investigation-to-boeing-737-4q8-g-jmcr | Daily check (G-SYN5, WO-SYN-5120). ADD-SYN-0412 (generator inoperative, invented MEL Category C, 10 days) was deferred 2026-10-03; at 2026-10-16 it is past its limit with no RIE on file; aircraft dispatched twice since. CRS draft says no open defect beyond limit. | Deferral date in ADD-SYN-0412 is 2026-10-08 (still in limit). |
| A8 `A8_ad_status` | A8 AD overdue | AAIB Bulletin 2/2010, Avro 146-RJ100 G-BXAR. https://www.gov.uk/aaib-reports/avro-146-rj100-g-bxar-13-february-2009 | Periodic check (G-SYN8, WO-SYN-6045). Invented repeat AD SYN-2026-03 (600 FH) was last done at 11,240 FH, next due 11,840 FH; airframe is at 11,905 FH, so overdue; task card step says "complied with; no further action". | Airframe hours 11,805 FH (not yet due). |

Per-task folder: `faulty/pack.md`, `clean/pack.md`, `twin_diff.txt` (unified diff, one changed line), `answer_key.json` (category, location id, exact evidence quote, also-acceptable quotes, expected recommendation). `build_packs.py` regenerates everything and asserts that a rule-based checker finds exactly one fault of the right category in the faulty pack and none in the clean twin, that every key quote is an exact substring of the faulty pack, and that the location id appears as `[id]`.

## Verified AAIB facts (opened and read 1 Nov 2026)
Quotes are in `aaib_sources.json`; `python3 verify_sources.py` checks each against the official PDF (`--fetch`; the report texts themselves are not included here). All quotes passed. Maintenance error was a cause or factor in each:

- **G-CIVX** (747-436, 30 Jan 2016): "The night shift staff removed and re-rigged the LGCM, but did not have time to compete [sic] the function checks, and the task cards were left uncertified." Also: "An inadequate handover between the night shift and the day shift."
- **EI-SLG** (ATR72-202, 15 Mar 2011; Irish-registered, investigated by AAIB UK): "The required independent inspection of the work and the operational test of the TLU system were not carried out." Also "...an independent (duplicate) inspection must be performed."
- **G-TVAA** (A109E, 17 Jun 2000): "...some of this had been expended in tightening the nut against the thread run-out, leaving the component stack-up essentially loose."
- **G-JMCR** (737-4Q8, 12 Oct 2018): "The RIE for the defect on Gen 1 should only have been granted in exceptional circumstances."
- **G-BXAR** (RJ100, 13 Feb 2009): "...had not been properly embodied at previous overhaul by Messier Services Inc, despite their overhaul records showing its incorporation."

PDF links are in `aaib_sources.json`. Reserve (not used): N9085H Cessna 172M, https://www.gov.uk/aaib-reports/aaib-investigation-to-cessna-172m-skyhawk-ii-n9085h ("...a duplicate inspection of the elevator trim system was not carried out").

## Public rules used (UK Regulation (EU) No 1321/2014, CAA consolidation, October 2026 page footer)
https://regulatorylibrary.caa.co.uk/1321-2014-PDF/PDF.pdf . Verbatim extracts in `source_notes/regulation_excerpts.txt` (third-party material under the CAA's terms) with printed page numbers: 145.A.45(e) p478; 145.A.48 p487; AMC2 p488; AMC3/AMC4 145.A.48(c)(2) pp489-491 (independent inspection, "authorised person" and "independent qualified person"); 145.A.50 p492 (certificate of release to service); 145.A.55 p504; M.A.303 p79 (ADs carried out within AD requirements); M.A.403 p111 (aircraft defects). The packs use these terms; the numerical limits, MEL durations and organisation procedures are invented.

## Not covered
No UK AAIB report was found and verified for A4 (calibration), A6 (stale data revision) or A7 (serial/certificate mismatch), so those categories are not in this set of 5. They stay in the prompt enum so a reviewer can still report them. Candidates could be sought later, including in non-UK investigation reports.

## Unverified / caveats
- **Registrations (changed 2 Nov 2026):** the first draft used G-XSYA to G-XSYE. G-INFO could not be queried reliably from the box (the public search page is a JavaScript form, and its backing API returned 404 for every mark tried, so it cannot confirm anything), so those could not be shown to be unallocated. They were replaced by G-SYN1, G-SYN2, G-SYN3, G-SYN5 and G-SYN8. UK marks are four letters after G-, so a mark with a digit should not be a real UK registration. [UNVERIFIED against G-INFO directly; this is a format argument]
- **Invented MEL category durations** (B/C/D) and the RIE rule are illustrative. Real durations come from the operator's MEL and MMEL. [UNVERIFIED against any real MEL]
- **EASA equivalence:** the rule text is the UK consolidation. EASA wording is not checked. [UNVERIFIED]
- **A3 is loosely matched.** G-TVAA concerned torque stack-up against thread run-out, not a recorded out-of-limit number. The 41 Nm value and the 25-30 Nm limit are invented, and so is the independent-inspector stamp.
- **A5 and A8 are simplified.** G-JMCR had an approved RIE (the AAIB criticised its approval); the pack instead has none on file. G-BXAR's issue was an overhaul shop's declared service bulletin embodiment; the pack instead has a simple overdue repeat AD. Neither pack claims to reproduce the real cause.
- **A3 double failure:** the faulty pack has an independent inspection stamp over the bad torque record. The checker counts one seeded fault (the value); the stamp is context.
- **Twin diff in A5 and A8:** the twin changes a date (A5, on the `[ADD-SYN-0412]` line) or the airframe hours (A8, on the `[CTX/AIRCRAFT]` line). In A8 the evidence line `[AD/SYN-2026-03]` is therefore identical in both packs, and the fault is only visible by comparing it with the airframe hours. The code checker tells the packs apart.
- **False-alarm risk:** every pack's CRS draft ends with the same 8 "YES" statements. A cautious reviewer might flag boilerplate on clean twins. Clean twins test exactly that.
- **Pack length:** about 900-1,000 tokens each, well under the 10-15k target. Realistic filler could be added later; that would change the difficulty.
- The G-CIVX report contains the AAIB typo "compete"; it is kept as published.
- G-BXKD was considered as an A6-style reserve at summary level only. [UNVERIFIED; not used]
- The Inspect scoring and prompt are drafted, not tested. No model has seen these packs.

## Files
`build_packs.py` (generator and checker), `verify_sources.py`, `aaib_sources.json`, `prompt_template.md`, `source_notes/regulation_excerpts.txt`, and five task folders.
