# Edit made to a hash-listed file after the runs

The files `PREREG_HASHES.txt`, `PREREG_HASHES_post_run.txt`, `PREREG_HASHES_v2.txt` and `PREREG_HASHES_v2_post_run.txt` are unchanged from when they were written. One file named in them was edited afterwards, only to remove material that should not be published. No scoring logic, prompt, task pack, answer key or result was changed.

| File | Hash list naming it | What changed |
|---|---|---|
| `software_tasks/build_software_packs.py` | `PREREG_HASHES.txt` | (1) the local repository path default was replaced by the `TBC_REPO` environment variable; (2) the hard-coded organisation and person names used for redaction were moved to an untracked local file (`redact_terms.local.txt`, or the path in `REDACT_TERMS_FILE`) and are read into `PRIVATE_TERMS`; (3) docstring wording was neutralised. The packs the script writes are hashed separately and are unchanged. |

`software_tasks/README.md` (not in any hash list) also had a local repository path replaced by a neutral sentence.

The removed text is not shown here on purpose. It is held in a private mapping file that is not published.

## How the check works

`python3 verify_wording_edits.py --private PATH_TO_wording_edits_private.json` reverses the edit with the private mapping, hashes the rebuilt file with sha256 and compares it with the digest in `PREREG_HASHES.txt`. A PASS shows that the published file differs from the registered one only by the edit above. Without the private file the script prints `SKIPPED`. `python3 verify_prereg.py --private ...` shows the same result inside the normal hash check (the file prints as `EDITED`).

## Other files

All other hash-listed files are byte-identical to the versions used in the runs, including `crs_pilot.py`, `cost_guard.py`, `validate_mock.py`, `SCORING_RULES.md`, `aviation_tasks/prompt_template.md` and the answer keys and provenance files. Their hashes agree with the lists as described in the README ("Pre-registration integrity"); `aviation_tasks/prompt_template.md` has no digest in `PREREG_HASHES.txt` (the line is cut off in the original list).

The raw Inspect logs in `logs/` are unmodified.
