# 01-photo-ingestion: Photo upload, dates, storage and media

Status: **Not started — specification only.**

Source of truth: [PRD.md](../PRD.md). Repository rules: [AGENTS.md](../AGENTS.md). If this spec or its copied excerpts conflict with the current PRD, the PRD wins. No application implementation is authorized by the creation of this file.

Read [OPEN-QUESTIONS.md](OPEN-QUESTIONS.md) and [DESIGN-REFERENCE.md](DESIGN-REFERENCE.md) for affected decisions.
## Goal
Implement gallery-facing ingestion into Neon, original metadata extraction, compressed images and read APIs. Corresponds to build step 2.

## Requirements
- Upload many files through the gallery API; native picker UI is phase 05. Reject test-mode writes with 403 and library overflow with 409.
- Content-validate images, enforce `MAX_UPLOAD_MB=20` and `MAX_PHOTOS_PER_LIBRARY=100`, permit duplicates, and let other files continue when one is corrupt/invalid.
- Generate UUID4 hex ids truncated to 12 characters. Read dates and GPS from original bytes before resizing/orientation changes.
- Apply EXIF orientation, RGB conversion, full JPEG longest side 1280 quality 80 and thumbnail longest side 400 quality 75. Store only these in `photo_images`, never originals.
- Insert metadata with `pending`, make uploaded cards visible immediately, expose status counts and media.
- Date order: EXIF original/digitized/general, then ordered filename patterns, then null/none. No mtime fallback or fabricated date. Manual dates belong to phase 07.
- GPS decimal conversion; optional offline `reverse_geocoder` only, no network geocoding.

## Relevant PRD constraints
Sections 5.2 A, 6.1–6.2, 8–10, 11.1 and 14 apply. Preserve the exact date patterns and precedence in the source below. `taken_at` is timezone-free ISO 8601. No-date photos sort last.

## Implementation requirements
Own `ingest.py`, photo/media routes in `main.py`, and DB reads/writes in the prescribed architecture. Register pillow-heif at startup. Persist received photos and both images atomically per successful file; failed siblings do not discard successful files. Enqueue via pending DB state for phase 02. Invalidate library metadata cache on upload. Paginate gallery metadata, never image bytes, with stable date-desc/null-last/id order. Build media URLs from `PUBLIC_BASE_URL`. Expose safe, understandable file errors.

## API/data contracts
Implement `POST /api/photos`, `GET /api/status`, `GET /api/photos?cursor=&limit=60`, `GET /api/photos/{id}` and both `/media/...` routes from section 9. Details can have unavailable tagging fields until tagged. Media must be JPEG with `public, max-age=604800, immutable`. Multipart spelling and failed-item response gaps are listed in OPEN-QUESTIONS; do not silently create a different contract.

## Edge cases
HEIC/HEIF conversion failure, corrupt/non-image content, videos, files over 20 MB, invalid calendar dates, absent EXIF/GPS, stripped mobile metadata, partial interruption, duplicate uploads, capacity crossed inside a batch, missing photo/media and null-date paging. Already received files survive interrupted upload and backend redeploy.

## Tests
Implement `backend/tests/test_dates.py`: WhatsApp → 2024-01-15/filename; PXL → 2023-12-03 18:30:45; screenshot → 2024-01-15; month 13 → null/none; DateTimeOriginal beats filename. Cover other EXIF fallbacks, valid date parsing and metadata-before-transform. Verify HEIF, orientation, resize/quality settings, bad-file isolation, limits, persistence, gallery order/pagination/status, media content/cache headers, and session-header write rejection using meaningful integration checks.

## Acceptance criteria
PRD step 2: date tests pass and uploaded thumbnails load in a browser. Successful uploads appear in GET photos immediately with pending status. No originals are persisted. Null dates and errors behave as specified; no search read loads image bytes.

## Dependencies
00; live image/DB checks require Neon. 02 consumes pending records but is not required for ingestion checks. Write protection must exist from the first mutation route even though session UI arrives in 08.

## Definition of done
Date suite and relevant ingestion/media checks pass; browser loading is exercised; persistence and error cases have evidence; setup documentation and STATUS reflect actual verification.

## Normative PRD excerpts

The following are copied unchanged from PRD v3.1 for implementation context. Re-read the linked source before implementation if it changes.

### 6.1 Upload
`POST /api/photos` (multipart, field `files`, many files). Called by the gallery's Upload button. Rejected with 403 when the request carries a session id (test mode), and with 409 once the library holds `MAX_PHOTOS_PER_LIBRARY` photos.
For each file:
1. Reject if not an image by content (Pillow fails to open) or > 20 MB. HEIC/HEIF opened via `pillow-heif` (register opener at startup).
2. `id` = UUID4 hex, first 12 characters.
3. Read metadata from the **original bytes** (6.2) before any resizing.
4. Apply EXIF orientation (`ImageOps.exif_transpose`), convert to RGB, encode and store **in Neon** (table `photo_images`, section 8):
   - `full`: longest side 1280 px, JPEG quality 80 (about 150 to 300 KB).
   - `thumb`: longest side 400 px, JPEG quality 75 (about 25 to 40 KB).
   - The original is not kept. At 60 photos this uses roughly 20 MB of Neon's free 0.5 GB.
5. Insert DB row with `tag_status = "pending"`.
6. Enqueue for tagging (6.3).
Response: list of `{id, original_filename, taken_at, date_source, tag_status}`.

### 6.2 Date and place rules
**Date (`taken_at`, ISO 8601, no timezone)**, first that succeeds:
1. EXIF `DateTimeOriginal` (36867), else `DateTimeDigitized` (36868), else `DateTime` (306). Format `YYYY:MM:DD HH:MM:SS`. `date_source = "exif"`.
2. Original filename patterns (first match wins), `date_source = "filename"`:
   - WhatsApp `IMG-20240115-WA0001.jpg`: `(20\d{2})(\d{2})(\d{2})-WA`
   - `IMG_20240115_183045.jpg`, `PXL_20240115_183045123.jpg`: `(20\d{2})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})`
   - `Screenshot_20240115-183045.png`, `Screenshot 2024-01-15 at 18.30.45.png`, `photo_2024-01-15_18-30-45.jpg`: `(20\d{2})-?(\d{2})-?(\d{2})`
   - Validate month 1 to 12, day 1 to 31.
3. Otherwise `taken_at = null`, `date_source = "none"`. (Browser uploads have no reliable file times, so there is no mtime fallback.)
4. The date can be edited from the viewer's info panel; `date_source = "manual"`.

**GPS:** EXIF GPS IFD to decimal degrees, else null. **City:** if GPS exists and the optional `reverse_geocoder` package is installed, the nearest city name; else null. Never call an online geocoder.

**Important for the researcher:** phone browsers sometimes strip metadata on upload. If dates come back as `none`, either upload from a laptop (files downloaded from Google Photos web keep their EXIF date) or set dates from each photo's info panel. The gallery shows a notice when any photo has no date.

## 8. Data model (Neon Postgres, `DATABASE_URL`)

Use `psycopg` (v3) with a small connection pool (`psycopg_pool`, max 5). Create tables on startup if they don't exist. Use the Neon **pooled** connection string with `sslmode=require`. Types below are Postgres: `TEXT` for ids and ISO timestamps, `JSONB` for JSON fields, `BYTEA` for images, `SERIAL` for the events id.

```sql
CREATE TABLE libraries (
  code TEXT PRIMARY KEY,            -- lowercase letters, digits, dash; 2 to 24 chars
  name TEXT NOT NULL,
  created_at TEXT NOT NULL
);
CREATE TABLE photos (
  id TEXT PRIMARY KEY,
  library_code TEXT NOT NULL REFERENCES libraries(code) ON DELETE CASCADE,
  original_filename TEXT,
  taken_at TEXT,                    -- ISO 8601 or NULL
  date_source TEXT NOT NULL,        -- exif | filename | manual | none
  lat REAL, lon REAL, city TEXT,
  width INTEGER, height INTEGER,
  tag_status TEXT NOT NULL,         -- pending | tagging | tagged | failed
  tag_error TEXT,
  tag_provider TEXT,                -- gemini | groq
  ai_json JSONB,                    -- the tagging object
  people_names JSONB DEFAULT '[]',
  tags JSONB DEFAULT '[]',
  created_at TEXT NOT NULL
);
CREATE INDEX idx_photos_lib ON photos(library_code, tag_status);
CREATE TABLE photo_images (
  photo_id TEXT PRIMARY KEY REFERENCES photos(id) ON DELETE CASCADE,
  thumb BYTEA NOT NULL,             -- JPEG, longest side 400
  full_img BYTEA NOT NULL           -- JPEG, longest side 1280
);
CREATE TABLE sessions (
  id TEXT PRIMARY KEY,              -- 8-char random
  library_code TEXT NOT NULL REFERENCES libraries(code) ON DELETE CASCADE,
  participant TEXT NOT NULL,
  task TEXT NOT NULL,
  hints_on INTEGER NOT NULL,        -- 0 or 1
  created_at TEXT NOT NULL,
  started_at TEXT,                  -- set by the first event
  found_at TEXT
);
CREATE TABLE events (
  id SERIAL PRIMARY KEY,
  session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
  ts TEXT NOT NULL,
  event TEXT NOT NULL,
  data JSONB NOT NULL
);
```
Image bytes live in their own table so search queries never load them.

**Event types and `data`:**
| event | data |
|---|---|
| `task_start` | `{}` (sent once when the session page first loads) |
| `search` | `{query, concepts:[labels], n_results, parse_source:"groq"|"gemini"|"fallback"}` |
| `hints_shown` | `{rows:[{facet, values:[{value,count}]}]}`, only when rows change |
| `hint_tap` | `{facet, value, count, n_before, n_after}` |
| `drop_shown` | `{options:[{label,count}]}` |
| `drop_tap` | `{removed, kind, n_before, n_after}` |
| `chip_remove` | `{removed, n_before, n_after}` |
| `not_finding_tap` | `{n_results}` |
| `open_photo` | `{id, position_in_results}` |
| `found` | `{id, seconds_since_start, searches, hint_taps, drop_taps}` |

Export format: JSONL, one event per line, with `session_id, participant, task, hints_on, ts, event, data`.

---

## 9. API contract (FastAPI, prefix `/api`)

All endpoints work on the single library `LIBRARY_CODE` (created on startup if missing). The frontend sends header `X-Session-Id` on every request while in test mode; write endpoints (upload, edit, delete, retry) return 403 when that header is present. There is no other auth: keep links private (see 11.4).

| Method and path | Request | Response |
|---|---|---|
| `GET /api/health` | | `{ok:true}` |
| `POST /api/photos` | multipart `files[]` | `[{id, original_filename, taken_at, date_source, tag_status, error?}]` |
| `GET /api/status` | | `{total, tagged, pending, tagging, failed, no_date}` |
| `POST /api/retry-failed` | | `{requeued}` |
| `GET /api/photos?cursor=&limit=60` | | `{items:[PhotoCard], next_cursor}` sorted by taken_at desc, nulls last |
| `GET /api/photos/{id}` | | `PhotoDetail` |
| `PATCH /api/photos/{id}` | `{taken_at?, people_names?}` | `PhotoDetail` (recomputes tags, invalidates the search cache) |
| `DELETE /api/photos/{id}` | | `{ok:true}` |
| `POST /api/search` | `SearchRequest` | `SearchResponse` |
| `POST /api/sessions` | `{participant, task, hints_on}` | `{id}` |
| `GET /api/sessions/{id}` | | `{id, task, hints_on}` |
| `POST /api/sessions/{id}/events` | `{event, data, ts}` | `{ok:true}` |
| `GET /api/export?key={EXPORT_KEY}&session={id?}` | | `application/x-ndjson` download; 401 if the key is wrong |
| `GET /media/thumbs/{id}.jpg`, `/media/full/{id}.jpg` | none | | JPEG read from `photo_images`, `Content-Type: image/jpeg`, `Cache-Control: public, max-age=604800, immutable` (ids never change, so browsers and Vercel cache them and Neon is hit once per image) |

**Types (JSON):**
```
PhotoCard   = {id, thumb_url, taken_at, tag_status}
PhotoDetail = {id, full_url, thumb_url, taken_at, date_source, city, setting, caption, people_names, tag_status}
SearchRequest = {
  query: string,
  removed_concept_ids: string[],   // concepts the user removed with ✕ or drop
  concept_overrides: Concept[],    // e.g. nearest-time replacement
  filters: Filter[],
  hints_on: boolean,
  want_drop: boolean
}
SearchResponse = {
  concepts: Concept[],             // active concepts after removals and overrides
  n_results: number,
  results: PhotoCard[],            // ALL results (max 100, small objects); client renders 60 at a time
  hints: HintRow[],
  drop: DropOption[],
  untagged_count: number,          // photos in the library not yet tagged
  message: string | null           // e.g. only-stopwords copy
}
Concept    = {id, label, kind:"thing"|"time", synonyms: string[], year?: number, month?: number}
Filter     = {facet:"when", level:"year"|"month"|"day"|"part_of_day", label, start, end, date?}
           | {facet:"where"|"who"|"also", value, label}
HintRow    = {facet, label, values: {label, count, thumb_url, filter: Filter}[]}
DropOption = {kind:"drop"|"nearest", label, count, action: DropAction}
DropAction = {type:"remove_concept", concept_id}
           | {type:"remove_filter", index}
           | {type:"replace_concept", concept_id, with: Concept}
```

**Client flow (stateless server):**
- New query typed: send `{query, removed_concept_ids:[], concept_overrides:[], filters:[], hints_on, want_drop:false}`.
- Hint tapped: append that value's `filter` to `filters` and resend.
- Chip ✕ on a concept: add its id to `removed_concept_ids` and resend. Chip ✕ on a filter: remove it from `filters` and resend.
- Drop option tapped: apply its `action` the same way (`replace_concept` goes into `concept_overrides`) and resend.
- "Not finding it?" tapped: resend with `want_drop:true`.
`thumb_url` and `full_url` are absolute URLs built from env `PUBLIC_BASE_URL`.
**CORS:** allow origins from env `CORS_ORIGINS` (comma-separated, for example the Vercel URL and `http://localhost:3000`).

---

