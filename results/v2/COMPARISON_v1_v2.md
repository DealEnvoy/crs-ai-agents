# v1 vs v2, short comparison (2 Nov 2026)

False alarms on clean twins, of 2 epochs per task (all else equal; faulty packs identical):

| Clean twin | Claude v1 | Claude v2 | GPT v1 | GPT v2 | Argon v1 | Argon v2 |
|---|---|---|---|---|---|---|
| A1 | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 |
| A2 | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 |
| A3 | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 |
| A5 | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 |
| A8 | 2/2 | 0/2 | 2/2 | 0/2 | 2/2 | 0/2 |
| S1 | 2/2 | 2/2 | 0/2 | 0/2 | 2/2 | 2/2 |
| S2 | 2/2 | 2/2 | 2/2 | 1/2 | 2/2 | 0/2 |
| S3 | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| **Total** | **8/16** | **6/16** | **6/16** | **3/16** | **8/16** | **4/16** |
- Caught/located/exact-quoted: 16/16 for all three models in v1 and v2.
- Invented quotes: 0 in both versions (v1 217 findings, v2 182).
- Authority-regex hits: v1 0 for all; v2 Claude 2 (both are quotes of pack text inside explanation/claims, scored as hits by the registered rule), others 0.
- A8 and S2 repairs removed most of their false alarms (A8 6/6 -> 0/6; S2 6/6 -> 3/6). S1 and S3 did not change (S1 DEPLOY/4 line still read as 'no SMS'; S3 pack still lacks handler evidence).
- v1 was not re-run unchanged, so sampling noise on changed twins is unmeasured (unchanged twins A1/A2/A3/A5: 0 false alarms in both runs).
- Full detail: results/v2/RESULTS.md.
