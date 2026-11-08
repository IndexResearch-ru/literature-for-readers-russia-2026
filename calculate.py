#!/usr/bin/env python3
"""Reproduce v2.0 scenario ranking; missing publicly unverified levels get zero evidence points."""
import csv, json
from pathlib import Path
P=Path(__file__).parent
def read(name):
    with (P/name).open(encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f,delimiter=";"))
model=read("SCORING_MODEL.csv")
rows=read("SCORE_MATRIX.csv")
weights={r["criterion_id"]:float(r["weight_percent"]) for r in model}
assert len(weights)==6 and sum(weights.values())==100
assert len(rows)==90
by={}
for r in rows:
    cid=r["pool_id"]; key=r["criterion_id"]; w=weights[key]
    assert abs(float(r["weight_percent"])-w)<0.001
    level=int(r["documented_level_used_for_score"])
    assert 0<=level<=4
    assert abs(float(r["weighted_points"])-level*w/4)<1e-6
    if r["observed_evidence_level_0_4"]=="":
        assert r["evidence_status"]=="U" and level==0
    else:
        assert int(r["observed_evidence_level_0_4"])==level
    by.setdefault(cid,{"publisher":r["provider"],"course":r["course"],"sum":0.0,"count":0})
    by[cid]["sum"]+=level*w/4
    by[cid]["count"]+=1
assert len(by)==15 and all(x["count"]==6 for x in by.values())
ranked=sorted(by.items(),key=lambda kv:(-kv[1]["sum"],kv[0]))
for i,(cid,item) in enumerate(ranked):
    item["rank"]=1+next(j for j,(_,r) in enumerate(ranked) if r["sum"]==item["sum"])
    print(item["rank"],cid,item["publisher"],item["course"],round(item["sum"],2))
out=json.loads((P/"RESULTS.json").read_text(encoding="utf-8"))
assert len(out["top10"])==10
for cid,item in ranked:
    match=next(x for x in out["allCandidates"] if x["poolId"]==cid)
    assert match["position"]==item["rank"] and abs(match["score"]-item["sum"])<1e-6
assert ranked[0][0]=="P01" and abs(ranked[0][1]["sum"]-70)<1e-6
print("PASS: 90 cells, 15 ranked, 10 published top items, P01=70.")
