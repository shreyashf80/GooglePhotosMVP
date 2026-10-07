from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from . import config
from .data import PHOTOS, BY_ID, card, detail
from .models import PhotoCard, PhotoDetail, SearchRequest, SearchResponse
from .search import active_concepts, match, drop_options
from .hints import hints

app=FastAPI(title="Search Hints Demo",version="0.1.0")
app.add_middleware(CORSMiddleware,allow_origins=config.CORS_ORIGINS,allow_methods=["GET","POST"],allow_headers=["Content-Type"])

@app.get("/api/health")
def health(): return {"ok":True}

@app.get("/api/photos")
def gallery(cursor:str|None=None,limit:int=Query(60,ge=1,le=100)):
    start=0
    if cursor:
        ids=[p["id"] for p in PHOTOS]
        if cursor not in ids: raise HTTPException(400,"Invalid gallery cursor")
        start=ids.index(cursor)+1
    page=PHOTOS[start:start+limit]
    return {"items":[card(p) for p in page],"next_cursor":page[-1]["id"] if page and start+limit<len(PHOTOS) else None}

@app.get("/api/photos/{photo_id}",response_model=PhotoDetail)
def photo(photo_id:str):
    if photo_id not in BY_ID: raise HTTPException(404,"Photo not found")
    return detail(BY_ID[photo_id])

@app.post("/api/search",response_model=SearchResponse)
def search(request:SearchRequest):
    concepts=active_concepts(request)
    if not request.query.strip() or (not concepts and not request.removed_concept_ids and not request.filters):
        return {"concepts":[],"n_results":0,"results":[],"hints":[],"drop":[],"untagged_count":0,"message":"Type something you remember about the photo."}
    filters=[f.model_dump() for f in request.filters]
    results=match(PHOTOS,concepts,filters)
    drop=drop_options(PHOTOS,concepts,filters,len(results)) if request.hints_on and (len(results)<=config.DROP_ROW_MAX_RESULTS or request.want_drop) else []
    return {"concepts":concepts,"n_results":len(results),"results":[card(p) for p in results],"hints":hints(results,concepts,filters) if request.hints_on else [],"drop":drop,"untagged_count":0,"message":None}
