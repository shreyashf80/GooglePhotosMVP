# 00-foundation: Backend foundation and shared contracts

Status: **Not started — specification only.**

Source of truth: [PRD.md](../PRD.md). Repository rules: [AGENTS.md](../AGENTS.md). If this spec or its copied excerpts conflict with the current PRD, the PRD wins except for the explicitly authorized AI-provider clarification recorded below. No application implementation is authorized by the creation of this file.

Read [OPEN-QUESTIONS.md](OPEN-QUESTIONS.md) and [DESIGN-REFERENCE.md](DESIGN-REFERENCE.md) for affected decisions.
## Goal
Establish the PRD's runnable FastAPI foundation, Neon schema and single default library without implementing later features. Corresponds to build step 1.

## Requirements
- Python 3.11+, FastAPI, stateless backend; Neon Postgres owns metadata, image bytes, sessions and events.
- Create the exact section 8 tables and index on startup if absent; create `LIBRARY_CODE` when missing. Keep `library_code` in storage without a library selector or multiple-library UI.
- `GET /api/health` returns `{ok:true}` locally.
- Configuration belongs in `backend/app/config.py`; use section 11.1 variables/defaults except replace singular GROQ_API_KEY with comma-separated GROQ_API_KEYS under the authorized clarification. Both Gemini and Groq credential lists belong exclusively to the backend. Frontend public configuration belongs in `frontend/lib/config.ts` when phase 05 begins.
- Preserve section 10 module boundaries and dependencies. No auth, admin, vector database, external worker service or filesystem image persistence.

## Relevant PRD constraints
Sections 0, 3, 8–11 and 13 step 1 apply. The appended schema, API and configuration are normative source excerpts. No speculative endpoints. Section 18's historical volume requirement does not supersede current Neon storage.

## Implementation requirements
- Initialize `main.py`, `config.py`, `db.py`, `models.py`, requirements and placeholder-only `.env.example` in their specified paths. Do not claim future routes are implemented merely because models exist.
- Use psycopg v3 and `psycopg_pool` with max 5 connections; pooled Neon URL with `sslmode=require`.
- Define section 9 request/response models for dependent phases; keep image queries separate from metadata reads.
- Configure CORS from the comma-separated `CORS_ORIGINS`; derive absolute media URLs from `PUBLIC_BASE_URL`.
- Establish cache invalidation integration points; actual mutation owners implement invalidation in phases 01, 02 and 07.
- Keep `.env` and frontend secret values out of version control, logs, responses and documentation. Use no real credentials in fixtures.
- Startup/shutdown must support the later HEIF opener and one in-process tagging worker, without starting an unimplemented worker.

## API/data contracts
The exact section 8 schema and section 9 shapes follow. This phase implements health and schema, not all listed endpoints. Default library naming is unspecified; choose a neutral value without introducing UI.

## Edge cases
Repeated startup must preserve data; unavailable/cold Neon must not expose credentials. Search metadata access must not join/load BYTEA. Do not silently substitute SQLite or local image files for Neon.

## Tests
Verify health response, idempotent schema/library initialization, configured pool limit, CORS and model serialization. Use a separate Neon branch for DB integration checks; unit checks must not mutate the demo database. Record unavailable DB verification honestly.

## Acceptance criteria
Health works locally with configured Neon; tables/index and library match the PRD; repeated startup does not destroy data; configuration matches section 11.1 with the authorized plural Groq credential-list override; no secrets are committed.

## Dependencies
No prior implementation phase. Live verification needs a pooled Neon connection string and separate local-test branch. Resolving the shared contract gaps in `OPEN-QUESTIONS.md` is required only before implementing those affected contracts.

## Definition of done
Build-step-1 checks pass with recorded evidence; shared models/configuration are reviewable; local foundation setup is documented in README; update STATUS only after verification.

## Authorized AI-provider clarification

The user's 6 October 2026 clarification in [AI-PROVIDER-POOLS.md](AI-PROVIDER-POOLS.md) governs provider/key selection where it explicitly differs from PRD v3.1. Both Gemini and Groq use comma-separated backend-only key pools; no OpenAI integration is allowed. PRD remains authoritative for everything else. Copied PRD excerpts below remain verbatim historical source snapshots: their singular GROQ_API_KEY and generic all-fail rule are superseded as described in the clarification.

Foundation owns `backend/app/providers.py` configuration and shared pool interfaces, as required by the explicit centralization clarification. Later tagging/search integrate with this module. `.env.example` must use empty GEMINI_API_KEYS= and GROQ_API_KEYS= with comma-separated/backend-only comments, never actual values; no singular Groq requirement. Include pool configuration/round-robin/per-key allowance/cooldown tests from AI-PROVIDER-POOLS in foundation verification. This shared module is the sole necessary repository-structure addition.

## Normative PRD excerpts

The following are copied unchanged from PRD v3.1 for implementation context. Re-read the linked source before implementation if it changes.

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

## 10. Repo structure

```
search-hints/
  README.md
  backend/
    app/
      main.py            FastAPI app, routers, startup (DB init, worker start, HEIF opener)
      config.py          env vars with defaults (section 11)
      db.py              Neon Postgres pool (psycopg), schema creation
      models.py          Pydantic request/response models
      ingest.py          upload handling, resizing, metadata (6.1, 6.2)
      tagging.py         worker, providers, prompt, rate limits, validation (6.3, 6.4)
      tags.py            normalisation and tag building (6.5)
      search.py          query parsing, matching, drop and nearest time (7.1, 7.2, 7.5)
      hints.py           facets, buckets, scoring (7.3, 7.4)
      sessions.py        sessions, events, export
    tests/
      test_dates.py  test_tags.py  test_search.py  test_hints.py
      fixtures/mini_library.json   (20 to 40 hand-written tagged photos, no images)
    requirements.txt     fastapi, uvicorn[standard], python-multipart, pillow, pillow-heif,
                         psycopg[binary], psycopg_pool, google-genai, groq, python-dotenv,
                         pytest, httpx
                         (optional, commented: reverse_geocoder)
    Procfile             web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    .env.example
  frontend/
    design-reference/    Google Photos screenshots (5.1), used only while building
    app/
      layout.tsx         font, mobile column wrapper, Material Symbols link
      page.tsx           Photos gallery (with Upload button)
      search/page.tsx    Search screen
      photo/[id]/page.tsx  Viewer
      start/page.tsx     creates a test session and redirects (no UI)
    components/
      SearchBar.tsx  ActiveChips.tsx  HintRow.tsx  HintChip.tsx  DropRow.tsx
      PhotoGrid.tsx  BottomNav.tsx  Snackbar.tsx  InfoSheet.tsx  UploadButton.tsx
      PeopleEditor.tsx  DateEditor.tsx  ConfirmDialog.tsx
    lib/
      api.ts             typed fetch wrappers for every endpoint
      config.ts          NEXT_PUBLIC_API_URL
      session.ts         reads ?session=, adds X-Session-Id header, sends events, counters, timer
      types.ts           mirrors section 9 types
    tailwind.config.ts   colour tokens from 5.1
    .env.example         NEXT_PUBLIC_API_URL=
```

---

### 11.1 Backend env vars (`backend/.env.example`)
```
LIBRARY_CODE=demo
EXPORT_KEY=change-me                 # only protects the log download
DATABASE_URL=postgresql://user:pass@ep-xxx-pooler.region.aws.neon.tech/dbname?sslmode=require
PUBLIC_BASE_URL=http://localhost:8000
CORS_ORIGINS=http://localhost:3000
GEMINI_API_KEYS=key1,key2
GEMINI_VISION_MODEL=gemini-2.5-flash-lite
GEMINI_TEXT_MODEL=gemini-2.5-flash-lite
GEMINI_RPM=8
GROQ_API_KEY=
GROQ_VISION_MODEL=meta-llama/llama-4-scout-17b-16e-instruct
GROQ_TEXT_MODEL=llama-3.1-8b-instant
GROQ_RPM=20
TAG_PROVIDERS=gemini,groq
QUERY_PROVIDERS=groq,gemini
TAG_BATCH_SIZE=4
GROQ_BATCH_SIZE=1
QUERY_TIMEOUT_S=4
HINT_MIN_RESULTS=5
MIN_VALUE_COUNT=1
MIN_FACET_SCORE=0.25
MAX_HINT_ROWS=3
MAX_VALUES_PER_ROW=4
MAX_ELIGIBLE_SHARE=0.85
DROP_ROW_MAX_RESULTS=1
MAX_PHOTOS_PER_LIBRARY=100
MAX_UPLOAD_MB=20
```

