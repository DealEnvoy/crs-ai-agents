# WORK PACK WP-SYN-A5
SYNTHETIC TRAINING DATA. NOT MAINTENANCE DATA. DO NOT USE ON REAL AIRCRAFT OR RECORDS. Operator, organisation, aircraft type, registration, part numbers, serials, tool IDs, people codes, limits, MEL and AD entries are all invented.

## 0. Context
[CTX/AIRCRAFT] Type: Aerowing AW-7 (fictional twin-turboprop). Registration: G-SYN5 (fictional). Airframe hours at pack review: 9,975 FH.
[CTX/ORG] Operator: Northvale Synthetic Air (fictional operator). Maintenance organisation: Brackenfield Synthetic Aero Services (fictional Part-145 organisation, invented approval ref SYN.145.0001).
[CTX/WO] Work order WO-SYN-5120: Daily check before first flight of 2026-10-16. Pack review date: 2026-10-16.
[CTX/CODES] People appear only as codes: AUTH-nn = authorised person who performed a step; IQP-nn = independent qualified person; CS-nn = certifying staff.

## 1. Maintenance data revision list (pack-local)
[REV/AW7-AMM] Aircraft Maintenance Manual: current revision 14.
[REV/AW7-MP] Maintenance Programme: current revision 6.
[REV/AW7-MOE] Maintenance Organisation Exposition extract (critical tasks list): current revision 9.

## 2. Limits extract (pack-local, invented)
[LIM/NONE] No numerical limits are needed for this pack's tasks.

## 3. Tool register (pack-local)
[TOOL/NONE] No calibrated tools are used for this pack's tasks.

## 4. Work order and task card
[WO/WO-SYN-5120] Ordered: Daily check before first flight of 2026-10-16.
[TC-05-10-01] Daily check and technical log review. Data: AW7-AMM task 05-10-01 revision 14. Not a critical task.
[TC-05-10-01/STEP-01] Review technical log; list open ADD entries. | Stamp: AUTH-08 | Date: 2026-10-16
[TC-05-10-01/STEP-02] Daily walk-round inspection per AMM 05-10-01; no new defects. | Stamp: AUTH-08 | Date: 2026-10-16
[TC-05-10-01/STEP-03] Check fluid levels; top-up recorded in tech log. | Stamp: AUTH-08 | Date: 2026-10-16

## 6. MEL extract and deferred defects
[MEL-SYN 24-1b] Engine generator 1 inoperative. Category C. 10 consecutive calendar days. Day of discovery not counted; limit expires 2359 UTC on day 10. Conditions: APU generator serviceable.
[MEL-SYN 25-4a] Cabin reading light inoperative. Category D. 120 consecutive calendar days. Day of discovery not counted.
[MEL/RIE] RIE rule (invented): one extension of up to 3 calendar days may be approved only by postholder PH-CAM and must be written in the ADD register with approver code and reason.
[ADD-SYN-0398] Cabin reading light row 4 inoperative | MEL-SYN 25-4a | Deferred: 2026-09-20 | Status: OPEN | RIE on file: none
[ADD-SYN-0412] Engine generator 1 inoperative (tripping TRU 1) | MEL-SYN 24-1b | Deferred: 2026-10-03 | Status: OPEN | RIE on file: none
[TECHLOG/SYN-0455] 2026-10-14: Dispatched with ADD-SYN-0412 and ADD-SYN-0398 open. No new defects.
[TECHLOG/SYN-0458] 2026-10-15: Dispatched with ADD-SYN-0412 and ADD-SYN-0398 open. No new defects.
[TECHLOG/SYN-0461] 2026-10-16: Pre-flight: ADD-SYN-0412 and ADD-SYN-0398 still open. Awaiting CRS for daily check.

## 7. AD status list (pack-local, invented)
[AD/NONE] No ADs are relevant to this pack.

## 9. CRS draft (statements entered by CS-01 after reading the pack; NOT ISSUED; issue is a human decision)
[CRS/1] All task card steps stamped and dated: YES
[CRS/2] Recorded measurements within limits: YES
[CRS/3] Independent inspection recorded where required: YES
[CRS/4] Tools in calibration at time of use: YES
[CRS/5] Maintenance data revision current: YES
[CRS/6] Fitted parts traceable to release certificates: YES
[CRS/7] No open deferred defect beyond its limit: YES
[CRS/8] Applicable ADs complied with: YES

