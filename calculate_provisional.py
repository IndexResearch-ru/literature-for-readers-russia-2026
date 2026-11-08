#!/usr/bin/env python3
"""Reproduce provisional score intervals. Never assign final ranks."""
import csv
from pathlib import Path
P = Path(__file__).resolve().parent

def read(name):
    with (P / name).open(encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file, delimiter=";"))

weights = {r["criterion_id"]: float(r["weight_percent"]) for r in read("SCORING_MODEL.csv")}
assert len(weights) == 6 and abs(sum(weights.values()) - 100) < 1e-9
rows = read("PROVISIONAL_SCORE_MATRIX.csv")
assert len(rows) == 15
for r in rows:
    lower = upper = 0.0
    for criterion, weight in weights.items():
        value = r[criterion + "_level"]
        if value != "":
            level = int(value)
            assert 0 <= level <= 4
            lower += weight * level / 4
            upper += weight * level / 4
        else:
            assert r[criterion + "_evidence_status"] == "U"
            upper += weight
    assert abs(lower - float(r["lower_bound_proxy"])) < 0.001
    assert abs(upper - float(r["upper_bound_proxy"])) < 0.001
    print(f'{r["candidate_id"]}: {lower:.2f}–{upper:.2f} / 100 (provisional; rank not assigned)')
assert all(r["final_scoring_eligible"] != "YES" for r in rows)
print("PRELIMINARY_UNRANKED_PUBLISHED; FINAL_TOP10_HOLD")
