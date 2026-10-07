# 03-search-engine: Query parsing, matching, drop and nearest time

Status: **Not started — specification only.**

Source of truth: [PRD.md](../PRD.md). Repository rules: [AGENTS.md](../AGENTS.md). If this spec or its copied excerpts conflict with the current PRD, the PRD wins except for the explicitly authorized AI-provider clarification recorded below. No application implementation is authorized by the creation of this file.

Read [OPEN-QUESTIONS.md](OPEN-QUESTIONS.md) and [DESIGN-REFERENCE.md](DESIGN-REFERENCE.md) for affected decisions.
## Goal
Implement deterministic stateless search and one-step recovery. Together with 04 this is build step 4.

## Requirements
- Search only tagged metadata cached per library, never image bytes; invalidate on uploads, tagging, dates, names and deletion. Target computation under 300 ms excluding parsing.
- Parse time locally before removing the exact stopwords; year, adjacent month/year and month-only concepts. Time matching excludes null dates.
- Parse remaining things Groq pool→Gemini pool→existing local deterministic parser, with exact prompt, JSON output, 4-second timeout and lowercase-query memory cache. Select healthy keys through the shared backend layer, skip cooling keys, and fall back locally without waiting through tagging cooldowns. Local fallback retains one concept per remaining word plus the exact small bidirectional synonym map.
- Stable short concept ids, user's labels and normalized synonyms. Whole tag equality or whole-word caption matching; intersect every concept and every active filter. Sort date descending/null last/id ties.
- Removed ids and replacement overrides are reapplied on each request; no per-tab server search state.
- Drop computation removes each active concept/filter separately, retains everything else, includes only counts > current N, sorts count descending and limits to 4.
- When a time concept yields zero results, compute alternatives without it at the user's granularity; nearest bucket first, ties earlier, replacement action. Preserve other concepts and filters.
- Hints-off condition suppresses both hints and drop; normal mode is hints-on. Phase 08 integrates persisted session condition.

## Relevant PRD constraints
Sections 7.1–7.3, 7.5, 9, 12.1 and 14. Preserve prompts, stopwords, synonyms and DROP_ROW_MAX_RESULTS=1 exactly. No AI recommendations, embedding search or conversational follow-up.

## Implementation requirements
Implement task parsing/matching in `search.py`; consume the centralized provider layer from 00 and do not duplicate pool, cooldown, rate-limit or retry/fallback state; expose search route with typed section 9 models. Build the 20–40 hand-tagged no-image fixture at `backend/tests/fixtures/mini_library.json`, including the required 12 cat/couch photos across 2022/2023/2024, two rooms and four blanket photos. Give fixture enough other variation for the section 12 also row without altering scoring. 04 plugs hint computation into the same endpoint; this phase can be tested without hint rows before integration.

## API/data contracts
Implement `POST /api/search` and full stateless request/response from the appendix. Return ALL matching PhotoCards (max 100); frontend paging is presentation-only. Active concepts reflect removals/overrides. `untagged_count` covers library photos not tagged; `message` carries exact stopword copy. Preserve Filter range semantics and DropAction types. Parse-source logging transport, override identity and part-of-day shape need the clarifications recorded in OPEN-QUESTIONS.

## Edge cases
Parser timeout/invalid response/provider failure, only stopwords, time-only search, no dates, month without year, multiword labels, substring false positives, partial tagging, zero results, identical filters, repeated requests from independent tabs, nearest-time ties, no recovery candidates and removing a replaced concept. With nothing useful, exact no-match copy applies through UI.

## Tests
`test_search.py` runs parser in local fallback mode: cat/couch matches kitten/sofa; kabir 2025 separates thing/time; nearest 2024 from 2024/2023; Feb 2025 nearest Nov 2024 over Mar 2023; every drop count > N; removed concept restores prior count exactly. Also verify whole-word matching, date/active-filter intersections, overrides, each remove_filter action, sorting/nulls, hints-off recovery suppression and parser cache/fallback. Time-only and month-only nearest behaviour require an explicit documented interpretation of the gap.

## Acceptance criteria
All specified search unit cases pass; results/recovery follow the stateless API; cache refresh reflects mutations; metadata computation meets the target when measured. 04 integration is required before the complete backend gate is passed.

## Dependencies
00–02 contracts/normalization. Pure algorithm tests use the metadata fixture without live AI or image storage. 04 depends on this result/filter pipeline; 06 consumes the final endpoint. Resolve affected contract/nearest-time gaps before their implementation.

## Definition of done
Search tests pass without weakened expectations; endpoint behaviour is exercised; parser source is available to the later logging owner through an agreed contract; evidence and README are updated. Complete backend acceptance remains pending until 04.

## Authorized AI-provider clarification

The user's 6 October 2026 clarification in [AI-PROVIDER-POOLS.md](AI-PROVIDER-POOLS.md) governs provider/key selection where it explicitly differs from PRD v3.1. Both Gemini and Groq use comma-separated backend-only key pools; no OpenAI integration is allowed. PRD remains authoritative for everything else. Copied PRD excerpts below remain verbatim historical source snapshots: their singular GROQ_API_KEY and generic all-fail rule are superseded as described in the clarification.

Tests/acceptance additionally include every relevant shared-pool case in AI-PROVIDER-POOLS: four-key rotation, partial/empty lists, peer retry after 429, Retry-After and cooldown expiry, full pool exhaustion, concurrency across both tasks and credential-safe errors. Tagging verifies Groq vision gating/pending recovery; parsing verifies timeout-bounded provider/local fallback. Normalized tags, prompts, API shapes and matching/hint algorithms remain unchanged.

## Normative PRD excerpts

The following are copied unchanged from PRD v3.1 for implementation context. Re-read the linked source before implementation if it changes.

### 7.1 Query parsing
Input: query string. Output: list of **concepts** `{id, label, synonyms[], kind}` where `kind` is `"thing"` or `"time"`; `id` is a short stable slug of the label.

1. **Time concepts (local regex, no AI):**
   - Month name or 3-letter abbreviation with an optional adjacent year → `{kind:"time", label:"Feb 2024", month:2, year:2024}` or `{label:"February", month:2, year:null}`.
   - Standalone year `\b(19|20)\d{2}\b` → `{kind:"time", label:"2024", year:2024}`.
   - Remove matched text from the query.
2. **Stopwords removed** (`STOPWORDS`): `my, me, our, the, a, an, on, at, in, with, of, and, photo, photos, picture, pictures, pic, pics, image, images, that, this, from, when, was, were, i, we, us, some, find, show`.
3. **Thing concepts:** call the query parser (provider order `QUERY_PROVIDERS = "groq,gemini"`, Groq model `GROQ_TEXT_MODEL` default `llama-3.1-8b-instant`, Gemini model `GEMINI_TEXT_MODEL` default `gemini-2.5-flash-lite`), timeout `QUERY_TIMEOUT_S` = 4 s, JSON output. Cache results by lowercase query in memory. On any failure, fall back to: one concept per remaining word, synonyms = the word plus entries from `SYNONYMS`.

**Exact query prompt:**
```
Turn this photo search into concepts. Return JSON only:
{"concepts":[{"label":"...","synonyms":["...","..."]}]}
Rules: one concept per distinct thing the user mentioned (object, animal, person name, place, event, colour, activity).
"label" is the user's word. "synonyms" has 2 to 6 everyday words a photo label might use for the same thing, singular, lowercase, including the label itself.
Do not add concepts the user did not mention. Ignore filler words.
Search: "{query}"
```
Example: `"my cat on couch"` → `cat: [cat, kitten, kitty]`, `couch: [couch, sofa, settee]`.

**`SYNONYMS` (fallback, keep small):** `couch↔sofa, cat↔kitten, dog↔puppy, kid↔child, baby↔infant, beach↔sea, food↔meal, cake↔dessert, car↔vehicle, mountain↔hill, wedding↔marriage, party↔celebration, mom↔mother, dad↔father`.

### 7.2 Matching
- A photo matches a **thing** concept if any normalised synonym equals any tag, or appears as a whole word in the normalised caption.
- A photo matches a **time** concept if `taken_at` has that year (and month, if given; a month with no year matches that month in any year). Photos with `taken_at = null` never match time concepts.
- **Results** = photos matching **all** concepts **and** all active filters.
- Sort: `taken_at` descending, nulls last, ties by id.

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

