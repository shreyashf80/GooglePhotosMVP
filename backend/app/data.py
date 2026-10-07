import json
from .config import DATA_PATH, DEMO_ASSET_BASE_URL
from .tags import build_tags

PHOTOS = json.loads(DATA_PATH.read_text())
for photo in PHOTOS:
    photo["tags"] = build_tags(photo["tags"] + photo["people_names"] + [photo["city"], photo["setting"], photo["event"]])
PHOTOS.sort(key=lambda p: p["id"])
PHOTOS.sort(key=lambda p: p["taken_at"] or "", reverse=True)
BY_ID = {p["id"]: p for p in PHOTOS}

def card(photo):
    return {"id": photo["id"], "thumb_url": DEMO_ASSET_BASE_URL + photo["image_path"], "taken_at": photo["taken_at"], "tag_status": "tagged"}

def detail(photo):
    return {**card(photo), "full_url": DEMO_ASSET_BASE_URL + photo["image_path"], "date_source": "manual", **{k:photo[k] for k in ("city", "setting", "caption", "people_names")}}
