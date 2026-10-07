# 06-search-ui: Search, active chips, hints and recovery UI

Status: **Not started — specification only.**

Source of truth: [PRD.md](../PRD.md). Repository rules: [AGENTS.md](../AGENTS.md). If this spec or its copied excerpts conflict with the current PRD, the PRD wins. No application implementation is authorized by the creation of this file.

Read [OPEN-QUESTIONS.md](OPEN-QUESTIONS.md) and [DESIGN-REFERENCE.md](DESIGN-REFERENCE.md) for affected decisions.
## Goal
Build the recognition/refinement loop and recovery interactions on `/search`, second part of build step 5.

## Requirements
- Inspect search-empty.jpeg and search-results.jpeg, but do not copy conversational search, AI answers, backup controls or feedback buttons: PRD excludes them. Visual priority is resolved: use compatible screenshot typography, spacing, surfaces, icons and proportions for PRD-defined elements; explicit PRD colour/style requirements and search interactions take priority.
- Search pill/back/clear, autofocus when empty, Enter/search-key submit, thin indeterminate progress bar. Exact empty copy and example chips: my cat on couch, beach sunset, birthday cake; tapping fills input (not a hint event).
- Active concepts and filters in addition order, removable and horizontally scrollable. Clear removes query/chips/results. A new query resets removed ids/overrides/filters/want_drop.
- Count and Not finding it? placement; hints only at N≥5/on; N=2–4 results only; N=0–1 automatic drop; requested drop at any N. Hints-off has no hint/drop rows.
- Native-styled hint chips: 24 px circular thumbnail; label · count; uppercase 12 px/500 row label with 0.5 px spacing and #444746. Row horizontal scroll.
- Send supplied filter when tapped; apply exact remove/replace actions. Chips removal restores earlier counts. Nearest-time copy/action is exact; do not guess new query text.
- Render results in 3 columns without date headers, first 60 then next 60 on scroll. Persist result/search context for viewer back/swipe; keep session params on links.
- Show `{k} photos are still being processed` when untagged_count>0. Preserve exact stopword/no-match/error copy.

## Relevant PRD constraints
Sections 5.2 B, 5.3–5.4, 7, 9, 12.2 checks 1,3,4,7 and 14. Screenshot behavioural mismatches do not authorize changing search scope. Normal mode hints always on/no logging; 08 owns session condition and event persistence.

## Implementation requirements
Own search/page, SearchBar, ActiveChips, HintRow, HintChip and DropRow; use api/types/config shared in 05. Maintain client-owned stateless SearchRequest context and list order. Preserve gallery/search origin when opening viewer; handle stale requests so displayed counts/chips/rows belong to latest request. Avoid re-parsing on hint taps through backend query cache, not client-produced concepts. Use progress and one retry on cold-start timeout. No additional search mode, conversation UI or filters screen.

## API/data contracts
POST search full contract and client flow appended verbatim. Read response results directly with absolute URLs. No server search session. 08 instruments actions using before/after counts once the request resolves. Use agreed parse-source transport without changing API silently.

## Edge cases
Only stopwords, empty/zero/one result, no useful drop candidates, all identical facets, async failure/race, rapid removals, wrong time, override then remove, active year filter with month hints, partial tagging and navigating back from viewer. Backend fallback is invisible except log provenance; do not invent AI-error screens.

## Tests
Run production build and browser console/network checks. Exercise examples, submit/clear, hints eligibility at N=4/5, tap→narrow→chip→remove→restore, on-demand/automatic drop, nearest replacement, active-filter exclusion and client load-more. Verify requested count restoration against fixture API. Check hints-off suppression and session preservation with 08. Measure hint-tap latency under 1 second on mobile data after first parse (later deployment verification).

## Acceptance criteria
Manual checks 3–4 pass locally; specified search copy, result counts, chip state and algorithms render correctly. Phone look check and under-1-second criterion remain unverified until actually measured. Condition-off retains matching results while suppressing hints/drop.

## Dependencies
03–04 final endpoint, 05 shared frontend, recorded visual-priority guidance (resolved, not a blocker). 07 for viewer return journey; 08 for real hints-off session/logs; 09 for deployment/mobile-data measurement.

## Definition of done
Browser search/refinement/recovery paths exercised, build passes, no unexplained network/console errors, state restoration verified and evidence recorded. Complete session/manual-performance criteria are owned jointly with 08–09.

## Normative PRD excerpts

The following are copied unchanged from PRD v3.1 for implementation context. Re-read the linked source before implementation if it changes.

### 5.3 Behaviour rules on the Search screen
| Situation | What the user sees |
|---|---|
| Results N ≥ 5 (`HINT_MIN_RESULTS`) and hints on | Up to 3 hint rows, then results. |
| Results 2 to 4 | Results only; "Not finding it?" link visible. |
| Results 0 to 1 | "Not finding it?" row shown automatically above results. |
| Tap "Not finding it?" | The drop row appears regardless of N. |
| Tap a hint chip | It becomes an active chip; results and hints recompute; that value never appears again as a hint. |
| Tap ✕ on an active chip | That concept or filter is removed; everything recomputes. |
| Tap ✕ in the search bar | Clears the query, chips and results. |
| Test mode with hints off | No hint rows and no drop row; search and results work the same. |
| Normal mode (no session) | Hints are on; nothing is logged; no "This is it" button. |

### 5.4 Exact UI copy
- Search placeholder: `Search your photos`
- Empty search screen: `Search the way you remember it`
- Results count: `{N} photos` / `1 photo`
- Row labels: `WHEN`, `WHERE`, `WHO'S IN IT`, `ALSO IN THESE PHOTOS`
- Hint chip: `{value} · {count}`
- Link: `Not finding it?`
- Drop row label: `NOT FINDING IT? TRY`
- Drop chip: `Drop {concept label} · {count}`
- Nearest time chip: `Nothing in {requested}. Closest: {bucket label} · {count}`
- No results and no drop options: `No photos match. Try fewer words, or something you can see in the photo.`
- Only stopwords typed: `Type something you remember about the photo.`
- Search error: `Something went wrong. Try again.`
- Found: `Thanks! You found it in {mm:ss}`

---

### 7.3 Active filters
Added by tapping hints; sent by the client on every search request (the server is stateless).
- `when` filters: `{facet:"when", level:"year"|"month"|"day"|"part_of_day", label, start, end}` with ISO `start` inclusive and `end` exclusive; part-of-day filters also carry `date` and the hour range. A photo passes if `taken_at` falls in the range. The filter keeps its own level even if later rows use a finer level.
- Other filters: `{facet, value}`. Single-valued facets: equal value. Multi-valued facets (`also`, `who` with names): value is in the photo's list.

Query concepts and filters are shown together as removable chips, in the order added.

### 7.5 Not finding it? (drop a detail and nearest time)
Returned when N ≤ `DROP_ROW_MAX_RESULTS` (1) or when the client sends `want_drop: true`.
1. For each query concept and each active filter, the result count with that item removed (others kept). Include only if count > N. Order by count descending, max 4.
2. **Nearest time:** if a time concept exists and results with it are 0, take results without it, group them at the granularity the user typed (year; month+year; or month in any year), and offer the bucket nearest in time to the request (ties: earlier). It goes first. Tapping it replaces the time concept with that bucket.
3. If nothing has count > 0, the client shows the "No photos match" copy.

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

