import calendar
import re
from datetime import datetime
from .tags import normalize

STOPWORDS = set("my me our the a an on at in with of and photo photos picture pictures pic pics image images that this from when was were i we us some find show".split())
SYNONYM_GROUPS = ["couch sofa", "cat kitten", "dog puppy", "kid child", "baby infant", "beach sea", "food meal", "cake dessert", "car vehicle", "mountain hill", "wedding marriage", "party celebration", "mom mother", "dad father", "medicine medication"]
SYNONYMS = {word: group.split() for group in SYNONYM_GROUPS for word in group.split()}
SYNONYMS["cafe"] = ["cafe", "coffee shop"]
MONTHS = {name.lower(): i for i in range(1,13) for name in (calendar.month_name[i],calendar.month_abbr[i])}
MONTH_PATTERN = "|".join(sorted(MONTHS,key=len,reverse=True))

def slug(label):
    return re.sub(r"[^a-z0-9]+", "-", normalize(label)).strip("-")

def parse(query):
    concepts, consumed = [], []
    text = query.lower()
    # Time is extracted first; matched years must not become a second time concept.
    for match in re.finditer(rf"\b({MONTH_PATTERN})\b(?:\s+((?:19|20)\d{{2}}))?",text):
        month, year = MONTHS[match[1]], int(match[2]) if match[2] else None
        label = f"{calendar.month_abbr[month]} {year}" if year else calendar.month_name[month]
        concepts.append({"id":slug(label),"label":label,"kind":"time","synonyms":[],"year":year,"month":month})
        consumed.append(match.span())
    for start,end in reversed(consumed):
        text = text[:start]+" "*(end-start)+text[end:]
    for match in re.finditer(r"\b(?:19|20)\d{2}\b",text):
        year = int(match[0])
        concepts.append({"id":str(year),"label":str(year),"kind":"time","synonyms":[],"year":year})
    text = re.sub(r"\b(?:19|20)\d{2}\b"," ",text)
    text = normalize(text)
    # Only documented phrases are combined; unknown details remain constraints.
    words = re.findall(r"[a-z0-9]+", text)
    things = []
    i = 0
    while i < len(words):
        if words[i] == "coffee" and i+1 < len(words) and words[i+1] == "shop":
            label="cafe"; i+=2
        else:
            label=words[i]; i+=1
        if label not in STOPWORDS:
            things.append({"id":slug(label),"label":label.title() if label == "goa" else label,"kind":"thing","synonyms":SYNONYMS.get(label,[label])})
    unique = {}
    for concept in things+concepts:
        unique.setdefault(concept["id"],concept)
    return list(unique.values())

def matches_concept(photo, concept):
    if concept["kind"] == "time":
        if not photo["taken_at"]: return False
        date=datetime.fromisoformat(photo["taken_at"])
        return (not concept.get("year") or date.year==concept["year"]) and (not concept.get("month") or date.month==concept["month"])
    caption=normalize(photo["caption"])
    return any(normalize(s) in photo["tags"] or re.search(r"(?<!\w)"+re.escape(normalize(s))+r"(?!\w)",caption) for s in concept["synonyms"])

def matches_filter(photo, filter):
    if filter["facet"] == "when":
        return bool(photo["taken_at"] and filter["start"] <= photo["taken_at"] < filter["end"])
    values=photo["people_names"] if filter["facet"]=="who" else photo["tags"]
    return normalize(filter["value"]) in [normalize(v) for v in values]

def match(photos,concepts,filters):
    return [p for p in photos if all(matches_concept(p,c) for c in concepts) and all(matches_filter(p,f) for f in filters)]

def active_concepts(request):
    overrides={c.id:c.model_dump(exclude_none=True) for c in request.concept_overrides}
    return [overrides.get(c["id"],c) for c in parse(request.query) if c["id"] not in request.removed_concept_ids]

def drop_options(photos, concepts, filters, n):
    options=[]
    for i,c in enumerate(concepts):
        count=len(match(photos,concepts[:i]+concepts[i+1:],filters))
        if count>n:
            options.append({"kind":"drop","label":f"Drop {c['label']} · {count}","count":count,"action":{"type":"remove_concept","concept_id":c["id"]}})
    for i,f in enumerate(filters):
        count=len(match(photos,concepts,filters[:i]+filters[i+1:]))
        if count>n:
            options.append({"kind":"drop","label":f"Drop {f['label']} · {count}","count":count,"action":{"type":"remove_filter","index":i}})
    options.sort(key=lambda o:(-o["count"],o["label"]))
    # Nearest alternatives keep every other concept/filter, rather than searching the library indiscriminately.
    nearest=[]
    if n == 0:
        for i,c in enumerate(concepts):
            if c["kind"]!="time" or not c.get("year"): continue
            buckets={}
            for p in match(photos,concepts[:i]+concepts[i+1:],filters):
                if not p["taken_at"]: continue
                dt=datetime.fromisoformat(p["taken_at"])
                key=(dt.year,dt.month) if c.get("month") else (dt.year,)
                buckets.setdefault(key,[]).append(p)
            if not buckets: continue
            wanted=c["year"]*12+c["month"] if c.get("month") else c["year"]
            key=min(buckets,key=lambda k:(abs((k[0]*12+k[1] if len(k)==2 else k[0])-wanted),k))
            label=f"{calendar.month_abbr[key[1]]} {key[0]}" if len(key)==2 else str(key[0])
            replacement={"id":c["id"],"kind":"time","label":label,"synonyms":[],"year":key[0]}
            if len(key)==2: replacement["month"]=key[1]
            count=len(buckets[key])
            nearest.append({"kind":"nearest","label":f"Nothing in {c['label']}. Closest: {label} · {count}","count":count,"action":{"type":"replace_concept","concept_id":c["id"],"with":replacement}})
    return (nearest+options)[:4]
