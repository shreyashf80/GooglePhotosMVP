import calendar
import math
from datetime import datetime, timedelta
from . import config
from .data import card
from .tags import normalize

LABELS={"when":"WHEN","who":"WHO'S IN IT","also":"ALSO IN THESE PHOTOS"}

def time_bucket(taken_at,level):
    dt=datetime.fromisoformat(taken_at)
    if level=="year":
        start=datetime(dt.year,1,1); end=datetime(dt.year+1,1,1); label=str(dt.year)
    elif level=="month":
        start=datetime(dt.year,dt.month,1)
        end=datetime(dt.year+1,1,1) if dt.month==12 else datetime(dt.year,dt.month+1,1)
        label=f"{calendar.month_name[dt.month]} {dt.year}"
    else:
        start=datetime(dt.year,dt.month,dt.day); end=start+timedelta(days=1); label=f"{dt.day} {calendar.month_abbr[dt.month]} {dt.year}"
    return label,{"facet":"when","level":level,"label":label,"start":start.isoformat(),"end":end.isoformat()}

def hints(results,concepts,filters):
    n=len(results)
    if n<config.HINT_MIN_RESULTS: return []
    rows=[]
    banned={normalize(s) for c in concepts for s in c["synonyms"]}
    active={normalize(f.get("value",f["label"])) for f in filters}
    when={}
    for level in ("year","month","day"):
        buckets={}
        for p in results:
            if not p["taken_at"]: continue
            value,f=time_bucket(p["taken_at"],level)
            buckets.setdefault(value,{"photos":[],"filter":f})["photos"].append(p)
        if sum(len(v["photos"])>=config.MIN_VALUE_COUNT for v in buckets.values())>=2:
            when=buckets; break
    who={}; also={}
    for p in results:
        for name in p["people_names"]:
            label=name.title()
            who.setdefault(label,{"photos":[],"filter":{"facet":"who","value":name,"label":label}})["photos"].append(p)
        excluded=banned|active|{normalize(p["setting"]),normalize(p["city"]),"everyday","other"}|{normalize(v) for v in p["people_names"]}
        for tag in set(p["tags"])-excluded:
            label=tag.title()
            also.setdefault(label,{"photos":[],"filter":{"facet":"also","value":tag,"label":label}})["photos"].append(p)
    for facet,buckets in (("when",when),("who",who),("also",also)):
        eligible=[(label,v) for label,v in buckets.items() if config.MIN_VALUE_COUNT<=len(v["photos"])<=config.MAX_ELIGIBLE_SHARE*n and normalize(label) not in active]
        if len(eligible)<2: continue
        if facet=="when":
            total=sum(len(v["photos"]) for _,v in eligible)
            probabilities=[len(v["photos"])/total for _,v in eligible]
            score=(total/n)*(-sum(p*math.log(p) for p in probabilities)/math.log(len(eligible)))
        else:
            chosen=sorted(eligible,key=lambda item:(abs(len(item[1]["photos"])-n/2),item[0]))[:config.MAX_VALUES_PER_ROW]
            score=sum(1-abs(len(v["photos"])-n/2)/(n/2) for _,v in chosen)/len(chosen)
        if score<config.MIN_FACET_SCORE: continue
        display_values=eligible
        if facet=="also":
            # Demo presentation: do not repeat a phrase's component words when
            # they identify precisely the same photo set. Scoring stays unchanged.
            display_values=[(label,v) for label,v in eligible if not any(
                label.lower() in other_label.lower().split() and len(other_label.split())>1
                and {p["id"] for p in v["photos"]}=={p["id"] for p in other["photos"]}
                for other_label,other in eligible)]
        selected=sorted(display_values,key=lambda item:(-len(item[1]["photos"]),item[0]))[:config.MAX_VALUES_PER_ROW]
        if len(selected)<2: continue
        if facet=="when": selected.sort(key=lambda item:item[1]["filter"]["start"])
        values=[]
        for label,v in selected:
            ordered=sorted(v["photos"],key=lambda p:(p["taken_at"] is None,p["taken_at"] or "",p["id"]))
            thumb=ordered[(len(ordered)-1)//2]
            values.append({"label":label,"count":len(ordered),"thumb_url":card(thumb)["thumb_url"],"filter":v["filter"]})
        rows.append((score,facet,{"facet":facet,"label":LABELS[facet],"values":values}))
    priority={"when":0,"who":1,"also":2}
    rows.sort(key=lambda row:(-row[0],priority[row[1]]))
    return [row[2] for row in rows[:config.MAX_HINT_ROWS]]
