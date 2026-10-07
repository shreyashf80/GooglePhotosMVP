# 04-hint-engine: Result-derived facets and adaptive time hints

Status: **Not started — specification only.**

Source of truth: [PRD.md](../PRD.md). Repository rules: [AGENTS.md](../AGENTS.md). If this spec or its copied excerpts conflict with the current PRD, the PRD wins. No application implementation is authorized by the creation of this file.

Read [OPEN-QUESTIONS.md](OPEN-QUESTIONS.md) and [DESIGN-REFERENCE.md](DESIGN-REFERENCE.md) for affected decisions.
## Goal
Offer deterministic recognizable details that split current results, completing build step 4 and the backend gate before frontend work.

## Requirements
- Compute on the CURRENT matching results only; require hints on and N ≥5.
- Facets: when adaptive time; where city if ≥2 distinct cities else setting; who names if any result has names else specified people-count buckets; also tags with all specified exclusions.
- Adaptive coarsest level with ≥2 buckets each reaching MIN_VALUE_COUNT: year→month→day→part-of-day. Exclude null dates. Preserve a selected filter's original range/level after recomputation.
- Eligibility c≥1 and c≤0.85N; environment-controlled count threshold 2 must work. Exclude every active value and query synonym where specified.
- Single-valued score is coverage × normalized entropy of eligible values; 0 for k<2. Multi-valued selection/score follows section 7.4 exactly, including up to four counts closest to N/2 and fewer-than-two zero score.
- Rows score ≥0.25, highest first, max 3, ties when/where/who/also. Values max 4; when highest-count eligible buckets then chronological display, others highest-count first.
- Representative thumbnail at median taken_at with nulls last, fallback lowest id. No image-byte reads.

## Relevant PRD constraints
Exact formulas, facets and time windows in section 7.4 are appended. Config: HINT_MIN_RESULTS=5, MIN_VALUE_COUNT=1, MIN_FACET_SCORE=0.25, MAX_HINT_ROWS=3, MAX_VALUES_PER_ROW=4, MAX_ELIGIBLE_SHARE=0.85. Do not lower thresholds or replace the deterministic algorithm to get attractive demos.

## Implementation requirements
Own `hints.py`; integrate with 03 POST search. Use normalized metadata from 02. Store chosen time ranges in returned Filter objects so changes in hint granularity do not reinterpret old chips. Honour all exclusions for also and active values. Use configured limits and keep lower-ranked facets out. Resolve Night/time-filter serialization and unprovided tie conventions as recorded in OPEN-QUESTIONS; choose deterministic incidental ties without changing specified priorities.

## API/data contracts
Return section 9 `HintRow` values with label/count/absolute thumb_url/filter and exact uppercase row labels. Frontend uses the supplied filter, not a guessed value. Multi-valued WHO uses names; count fallback uses the exact bucket labels. No additional API route or generated recommendation text.

## Edge cases
N=4 vs N=5, identical facet values, only undated results, mixed named/unnamed photos, two cities with missing city values, value at exactly 85%, sparse singleton tags, overlapping multi-valued tags, finer buckets after filtering, nighttime across midnight and even-size median ties.

## Tests
Implement every section 12.1 `test_hints.py` case in the appended source: months within one year; part-of-day within one day; never show ubiquitous tag; count threshold 1 vs 2; N boundary; demo fixture produces when/where/also; at most 3×4; active values excluded; year filter persists under month rows. Also verify exact score calculation, row tie-break, chronological when order, city/setting choice, name/count WHO and thumbnail choice. Fixtures for a row must contain ≥2 eligible values as the score formula demands.

## Acceptance criteria
Every backend unit suite (dates/tags/search/hints) passes BEFORE phase 05. Broad fixture searches have useful result-derived rows; taps' filters actually narrow; same-value hints never reappear; no-date and hints-off rules hold. No tests/thresholds weakened.

## Dependencies
00–03; requires agreed part-of-day contract. Algorithm tests need no provider credentials. Frontend implementation waits for complete backend suite per section 12.1.

## Definition of done
Run entire backend suite, record results and search/hint integration behaviour, inspect algorithms against PRD and update STATUS. Performance measurement and eventual demo-library checks stay explicitly pending if not yet exercised.

## Normative PRD excerpts

The following are copied unchanged from PRD v3.1 for implementation context. Re-read the linked source before implementation if it changes.

### 7.3 Active filters
Added by tapping hints; sent by the client on every search request (the server is stateless).
- `when` filters: `{facet:"when", level:"year"|"month"|"day"|"part_of_day", label, start, end}` with ISO `start` inclusive and `end` exclusive; part-of-day filters also carry `date` and the hour range. A photo passes if `taken_at` falls in the range. The filter keeps its own level even if later rows use a finer level.
- Other filters: `{facet, value}`. Single-valued facets: equal value. Multi-valued facets (`also`, `who` with names): value is in the photo's list.

Query concepts and filters are shown together as removable chips, in the order added.

### 7.4 Hint facets
Computed on the current results (size N), only when hints are on and N ≥ `HINT_MIN_RESULTS` (5).

| Facet | Row label | Value per photo (`None` = excluded from counts) |
|---|---|---|
| `when` | WHEN | Adaptive time bucket (below) |
| `where` | WHERE | `city` if at least 2 different cities appear among results; otherwise `setting` |
| `who` | WHO'S IN IT | If any result has `people_names`: each name (multi-valued). Otherwise `people_count` bucket: `0 → "No people"`, `1 → "1 person"`, `2-4 → "2 to 4 people"`, `5+ → "5 or more people"` |
| `also` | ALSO IN THESE PHOTOS | Each tag (multi-valued), excluding synonyms of query concepts, values already used as filters, the photo's `setting`, `city`, names, and event values `everyday` and `other` |

**Adaptive time bucket:** the coarsest level that gives at least 2 buckets each with ≥ `MIN_VALUE_COUNT` photos: **year** (`2023`) → **month** (`Feb 2024`) → **day** (`11 Feb 2024`) → **part of day** (`Morning` 05:00-11:59, `Afternoon` 12:00-16:59, `Evening` 17:00-20:59, `Night` 21:00-04:59). Chosen fresh for each request.

**Eligible values:** count `c ≥ MIN_VALUE_COUNT` (default 1 for the small demo library; set 2 for larger libraries) and `c ≤ MAX_ELIGIBLE_SHARE × N` (0.85). A value present in every result is never eligible.

**Facet score:**
- Single-valued facets (`when`, `where`, `who` without names): `coverage = sum(c)/N`; `balance = entropy(c/sum(c)) / ln(k)` with k eligible values (0 if k < 2); `score = coverage × balance`.
- Multi-valued facets: choose up to 4 eligible values with counts closest to N/2; `score = mean(1 − |c − N/2| / (N/2))`; 0 if fewer than 2 chosen.

**Rows shown:** facets with `score ≥ MIN_FACET_SCORE` (0.25), highest first, max `MAX_HINT_ROWS` (3). Tie-break: when, where, who, also.
**Values per row:** max `MAX_VALUES_PER_ROW` (4). `when`: the 4 eligible buckets with the highest counts, displayed chronologically. Others: highest count first.
**Thumbnail per value:** among photos with that value, the one at the median `taken_at` (nulls last), fallback lowest id.

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

### 12.1 Backend unit tests (must pass before building the frontend)
**Dates (`test_dates.py`)**
- `IMG-20240115-WA0001.jpg` → 2024-01-15, source `filename`.
- `PXL_20231203_183045123.jpg` → 2023-12-03 18:30:45.
- `Screenshot 2024-01-15 at 18.30.45.png` → 2024-01-15.
- `IMG_20241345_000000.jpg` (month 13) → no match, `none`.
- An image with EXIF `DateTimeOriginal` uses it over the filename.

**Tags (`test_tags.py`)**
- `"Christmas Trees"` → contains `christmas tree`, `christmas`, `tree`.
- `"glass"` stays `glass`; `"cats"` → `cat`.

**Search (`test_search.py`, fixture, query parser in fallback mode)**
- `"my cat on couch"` → concepts `cat`, `couch`; a photo tagged `kitten` and `sofa` matches.
- `"kabir 2025"` → one thing concept, one time concept (year 2025).
- `"kabir 2025"` with 0 results while Kabir photos exist in 2024 and 2023 → nearest-time option `2024`.
- `"kabir feb 2025"` with 0 results while Kabir photos exist in Nov 2024 and Mar 2023 → nearest-time option `Nov 2024`.
- Drop options never show a count ≤ current N.
- Removing a concept via `removed_concept_ids` restores the earlier count exactly.

**Hints (`test_hints.py`)**
- 40 results all in 2023 across 4 months → `when` uses month buckets.
- 30 results on one day → `when` uses part-of-day buckets.
- A tag on 100% of results never appears in `also`.
- With `MIN_VALUE_COUNT = 2`, a value with count 1 never appears; with the default 1, it can.
- N = 4 → no hint rows; N = 5 with two distinct years → a `when` row appears.
- Demo fixture: 12 "cat on couch" photos across 2022, 2023 and 2024, in two rooms, 4 with a blanket → the query `my cat on couch` returns `when`, `where` and `also` rows.
- At most 3 rows, at most 4 values each.
- A value used as an active filter never appears again.
- A `when` filter at year level still applies after rows switch to month level.

