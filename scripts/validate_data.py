#!/usr/bin/env python3
"""Check the internal consistency of the knowledge base. Exit status 1 on any problem.

- 31 ECD entries with unique codes; status agrees with grade (A/B supported, C/D to_be_verified);
  every source in source_refs is in references.json;
- 410 toneless and 1,295 toned syllables; every code in the mapping table exists in the ECD and carries
  the ECD grade; has_grade_d is correct;
- the summary figures of the mapping table: 1,288 toned syllables (interjections excluded) map to
  3.53 entries on average (max 8); 775 (60.2%) involve only A/B entries; 223 (17.3%) include a D entry.
"""
import json
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data"
problems = []


def check(cond, msg):
    if not cond:
        problems.append(msg)


ecd = json.loads((DATA / "ecd.json").read_text(encoding="utf-8"))
refs = {r["short"] for r in json.loads((DATA / "references.json").read_text(encoding="utf-8"))["references"]}
ids = {json.loads((DATA / f).read_text(encoding="utf-8")).get("dataset_id")
       for f in ("ecd.json", "emt_toned.json", "emt_base.json", "neutral_tone_layer.json", "references.json")}
check(len(ids) == 1 and None not in ids, f"dataset_id differs between files: {ids}")
entries = ecd["entries"]
grade = {e["error_id"]: e["evidence_strength"] for e in entries}
check(len(entries) == 31 and len(grade) == 31, "ECD should have 31 unique entries")
for e in entries:
    want = "supported" if e["evidence_strength"] in "AB" else "to_be_verified"
    check(e["status"] == want, f"{e['error_id']}: status {e['status']} vs grade {e['evidence_strength']}")
    for r in e["source_refs"]:
        check(r in refs, f"{e['error_id']}: unknown source {r}")
check(sorted(grade.values()).count("A") == 16, "expected 16 grade-A entries")

for name, n in (("emt_base.json", 410), ("emt_toned.json", 1295)):
    syl = json.loads((DATA / name).read_text(encoding="utf-8"))["syllables"]
    check(len(syl) == n, f"{name}: {len(syl)} syllables, expected {n}")
    for k, row in syl.items():
        for i in row["entries"]:
            check(i["code"] in grade, f"{name} {k}: unknown code {i['code']}")
            check(i["grade"] == grade.get(i["code"]), f"{name} {k}: grade of {i['code']} differs from ECD")
        if not row["interjection"]:
            check(row["has_grade_d"] == any(i["grade"] == "D" for i in row["entries"]), f"{name} {k}: has_grade_d")

toned = json.loads((DATA / "emt_toned.json").read_text(encoding="utf-8"))["syllables"]
real = [r for r in toned.values() if not r["interjection"]]
codes = [{i["code"] for i in r["entries"]} for r in real]
n = len(real)
ab = sum(1 for c in codes if c and all(grade[x] in "AB" for x in c))
dd = sum(1 for c in codes if any(grade[x] == "D" for x in c))
stats = (n, round(sum(map(len, codes)) / n, 2), max(map(len, codes)), ab, round(100 * ab / n, 1), dd,
         round(100 * dd / n, 1))
check(stats == (1288, 3.53, 8, 775, 60.2, 223, 17.3), f"mapping summary changed: {stats}")

if problems:
    print("\n".join(problems))
    sys.exit(1)
print(f"OK: ECD {ecd['version']} with {len(entries)} entries; mapping summary {stats}")
