# 08-test-mode-logging: Session links, conditions, events and export

Status: **Not started — specification only.**

Source of truth: [PRD.md](../PRD.md). Repository rules: [AGENTS.md](../AGENTS.md). If this spec or its copied excerpts conflict with the current PRD, the PRD wins. No application implementation is authorized by the creation of this file.

Read [OPEN-QUESTIONS.md](OPEN-QUESTIONS.md) and [DESIGN-REFERENCE.md](DESIGN-REFERENCE.md) for affected decisions.
## Goal
Implement build step 6: participant mode with hints on/off, complete ordered instrumentation and downloadable research logs.

## Requirements
- `/start?p={participantId}&hints={on|off}&task={optional text}` POSTs session then redirects immediately to `/search?session={id}`, or gallery with home=1. Spinner only; no form/admin page.
- Session id 8-char random; single LIBRARY_CODE; persist task/participant/condition/times in Neon. Reopening resulting session link resumes same session.
- Read session parameter, fetch condition, preserve it on every nav/back/grid link; send X-Session-Id on every API request while in test mode.
- Hide upload/retry/date/name/delete in test mode; reject all write endpoints with session header regardless of UI. This header lock is the specified prototype boundary, no extra authentication.
- Hints-off suppresses hints and drop; both conditions use same matching engine. Normal mode hints-on, no logging and no This is it.
- Emit all exact section 8 events/data. Search means typed submitted search, not every refinement. Hints_shown only when rows change. Record before/after counts and source provenance accurately.
- Set started_at from first event, task_start only when empty; found sets found_at, ignores second tap, logs elapsed seconds/searches/hint_taps/drop_taps; snackbar mm:ss.
- Export all or one session as ordered JSONL; exact fields/content type, protected by EXPORT_KEY with wrong-key 401. No log-download page.

## Relevant PRD constraints
Sections 5.2 modes/start/D, 5.3, 8–9, 11.4, 12.2 checks 5–6, 14–15. Shared curated demo, 6–8 participants, two photos each, 5-minute research task cap; do not add app timer enforcement or analytics dashboard. Metrics/success bar remain study procedures, not new UI.

## Implementation requirements
Own backend sessions.py and session/event/export routes; frontend start/page and lib/session.ts plus integration into 05–07. Atomic DB checks enforce once-only task_start/found despite reloads/retries. Keep elapsed timer/counters coherent across gallery/search/viewer navigation; use persisted/session context rather than resetting per component. Export in event insertion order. Log source gap and HintRow event `value` mapping require agreed contract. Do not expose EXPORT_KEY in frontend code or logs.

## API/data contracts
Exact section 8 schema/event payloads/export fields and section 9 sessions/events/export endpoint shapes appended. ts is supplied by client for event POST; schema fields remain as written. No new endpoint. Session GET returns id/task/hints_on (not arbitrary extra fields). Optional task default is an implementation choice, not a new required field in start URL.

## Edge cases
Same resulting link twice, task_start race, double found/reload/navigation, invalid/missing session id, event-request failures, export all/one/empty, wrong key, off-condition requests, absent participant task and session data surviving redeploy. Reliable event failures must not silently count as successful logging.

## Tests
Backend API checks for session creation/read, conditions, all write locks, once-only start/found and JSONL field/order/content-type/key protection. Browser both conditions: all nav preserves context, all actions produce exact events/counts, rows-change rule, normal mode no logs, off no hints/drop, found once with correct elapsed/counters. Export and compare against the actual journey, including parse_source fallback. No weakening matching in hints-off.

## Acceptance criteria
Manual checks 5–6 pass: P1/off hides hints/drop/mutations; This is it logs found once; export includes actions in order. On/off results remain identical for same query/filter state. Restart keeps sessions/events. No implementation claim based on fake UI success while event API failed.

## Dependencies
00 schema; 03 provenance and search state; 05–07 action hooks. Resolve source transport and event-shape gaps. No deployment credentials needed for local checks; DB needed for persistence/export.

## Definition of done
Session/lock/event/export checks pass and complete actual browser journeys are checked against JSONL; counters/time survive navigation; README shows test links/export without secrets; STATUS records evidence.

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

## 15. Test plan with participants

**Library setup:**
- **Now (this MVP): shared demo library** built from the recipe in 6.0. Before each task, show the participant the target photo for 5 seconds, then hide it and wait 2 minutes (talk about something else), so they search from a fading memory, not a fresh one. Then: "Find the photo you saw." This tests the interaction honestly at small scale.
- **Later: own library.** Each participant uploads their own photos into their own library, with consent. Stronger evidence for real memory; needs more photos and time.

**Task:** "Find the photo you saw. Tell me what you remember as you search." Two target photos per participant (each from a crowded pattern in 6.0), 5 minute cap each.
**Conditions (counterbalanced):** A = session with hints off; B = session with hints on. Each photo gets its own session link.
**Participants:** 6 to 8 frequent Google Photos users.

| Metric | Definition | Primary? |
|---|---|---|
| Found rate | Tasks ending with `found` within 5 minutes | Primary |
| Time to find | `seconds_since_start` at `found` | Primary |
| Searches typed | Count of `search` events | Secondary |
| Recovery after a miss | Of tasks where the first search did not end in `found`, share later found | Secondary |
| Hint use | `hint_tap` and `drop_tap` counts; share of finds where the last action before opening the photo was a hint or drop tap | Secondary |
| Recognition moments | Think-aloud quotes like "oh, that's the one at the old flat" | Qualitative |

**Success bar (fixed before testing):** hints on beats hints off on found rate **and** median time to find, for at least 5 of 8 participants, with no participant calling the hints confusing. If not met, the hypothesis in 2.4 is weakened.

---

