# 07-photo-viewer: Viewer, info sheet, date and People edits

Status: **Not started — specification only.**

Source of truth: [PRD.md](../PRD.md). Repository rules: [AGENTS.md](../AGENTS.md). If this spec or its copied excerpts conflict with the current PRD, the PRD wins. No application implementation is authorized by the creation of this file.

Read [OPEN-QUESTIONS.md](OPEN-QUESTIONS.md) and [DESIGN-REFERENCE.md](DESIGN-REFERENCE.md) for affected decisions.
## Goal
Complete build step 5 with viewer and researcher-only metadata edits/delete.

## Requirements
- Inspect viewer.jpeg and viewer-info.jpeg. Apply the resolved visual priority: screenshots guide viewer appearance, typography, spacing, surfaces, icons and proportions; explicit PRD functionality, behaviour and colour/style requirements win. Full-screen contained photo on black, white icons, back arrow, screenshot top/bottom action styling. No working share/edit-image/album/favourite feature.
- Swipe next/previous in the incoming gallery or search result list, preserve order/context and session when returning.
- Info sheet via swipe up or info tap: date/time, city else setting, AI caption as description. Do not add screenshot albums/backup/camera-info features absent from PRD.
- Normal-mode pencil opens native date-time input; save taken_at and manual date_source, re-sort gallery. People Add name/Enter/remove chips persist people_names and make names searchable.
- Delete only in normal mode: `Delete this photo?`, `Cancel`, `Delete`, then previous screen. No trash bin/undo invention.
- Test mode hides every edit/delete control and exposes `This is it` above action bar: blue #0B57D0/white; log found, exact elapsed snackbar, disable button. Phase 08 owns log/timer/idempotency integration.

## Relevant PRD constraints
Sections 3, 5.2 C, 6.6, 7 cache rules, 9, 12.2 checks 2,6,9, 13 cut list and 14. People/WHO/swipe/Delete remain included: optional/cuttable is not approval to cut. Metadata edits do not change image bytes/ids.

## Implementation requirements
Own photo/[id]/page, InfoSheet, PeopleEditor, DateEditor, ConfirmDialog. Backend implements PATCH/DELETE with same session-header write guard as upload. Recompute tags on edits, preserve provider-generated fields and invalidate cached library metadata on both edit/delete. Cascade image deletion per schema. Handle untagged/failed detail fields gracefully. Viewer/list context is client-owned, no server session search state.

## API/data contracts
Use GET PhotoDetail and PATCH `{taken_at?, people_names?}` → PhotoDetail; DELETE→`{ok:true}`. taken_at timezone-free ISO, manual date_source. Full image URL is absolute. Any request with X-Session-Id to edit/delete returns 403. Found event payload belongs to 08, no extra endpoint.

## Edge cases
Missing date input, null caption/place before tagging, edited item changes gallery position, names repeated/removed/normalized, deleted current item, first/last swipe, direct viewer link with no incoming list, back across query context and repeated found taps. Native date input must not silently shift timezone-free values.

## Tests
Verify backend edit fields/tag recomputation/cache refresh and session locks; deletion cascades. Browser: open from gallery/search, contain image, info gestures, date moves photo, People name search, remove name, confirm/cancel delete and return state, swipes/endpoints and test-mode hidden mutations. Build/console/network checks. 08 completes found/timer duplicate tests.

## Acceptance criteria
Manual check 2's date/name flow and checks 1–4's viewer journey work. Viewer/photo/list order preserved; mutations refresh results; no unintended screenshot features. Test mode is locked on both UI/backend.

## Dependencies
01–02 detail/storage/tags, 05 gallery, 06 search-origin context, recorded visual-priority guidance (resolved, not a blocker); 08 supplies persisted found action. Backend guards do not wait for 08.

## Definition of done
Build and route checks pass, actual edit/name/delete/navigation flows are exercised, mutation cache behaviour is demonstrated, no new scope; record deferred phone/found verification explicitly.

## Normative PRD excerpts

The following are copied unchanged from PRD v3.1 for implementation context. Re-read the linked source before implementation if it changes.

### 5.2 Screens

**Two modes, decided by the URL:**
- **Normal mode** (no `session` parameter): everything works, including Upload, edit and delete. Nothing is logged. This is how the researcher sets up the library and demos the feature.
- **Test mode** (`?session={id}` present): Upload, edit and delete are hidden; "This is it" appears in the viewer; every action is logged. All internal links (bottom nav, search pill, grid taps, back arrow) must keep the `session` parameter.

**Starting test mode:** the researcher opens `/start?p={participantId}&hints={on|off}&task={optional text}`. This page calls `POST /api/sessions`, then immediately redirects to `/search?session={id}` (or `/` if `home=1` is also given). The researcher hands the phone over, or sends the resulting link. No page or form is shown on `/start` other than a brief spinner.

**A. Photos (gallery, home), route `/`**
- Top bar as in `home.png`. On the right, an **Upload** icon button (Material Symbol `upload` or `add_photo_alternate`, matching the real app's icon size and colour). Hidden in test mode.
- Tapping Upload opens the device's native picker: `<input type="file" accept="image/*" multiple>` (on phones this offers the gallery and camera). No custom upload screen.
- After picking: a snackbar at the bottom, styled like Google Photos, `Uploading {n} photos…`, then `Processing {n} photos…` while tagging runs, then it disappears. Uploaded photos appear in the grid immediately (at their photo date), each with a small circular spinner in the bottom-right corner until tagged.
- If some fail: snackbar `{k} photos couldn't be processed` with a `Retry` action. A file that is not an image or is over 20 MB: snackbar `{filename} couldn't be uploaded`.
- If any photos have no date: a one-line notice under the top bar, `{k} photos have no date. Open one and tap ⓘ to add it.`, dismissible.
- Grid: all photos, newest first, grouped by day with headers like `Sat, Feb 11, 2024` (photos with no date go under `No date` at the end). 3 columns, square thumbnails, 2 px gap, lazy-loaded images.
- Bottom nav with Photos active. Tap a photo: opens the Viewer.
- Empty library (normal mode): centred text `No photos yet` and a filled button `Upload photos` that opens the picker.
- While tagging is pending, the gallery polls `GET /api/status` every 5 s and refreshes spinners.

**B. Search, route `/search`**
```
┌─────────────────────────────────────┐
│ ←  [ cat on couch            ✕ ]    │  search bar (autofocus when empty)
│ [cat ✕] [couch ✕] [2023 ✕]          │  active chips row (horizontal scroll)
│ 48 photos            Not finding it? │
├─────────────────────────────────────┤
│ WHEN                                 │
│ (◉ 2022 · 20) (◉ 2023 · 18) (◉ …)   │  hint chips, horizontal scroll
│ WHERE                                │
│ (◉ Living room · 30) (◉ Balcony · 12)│
│ ALSO IN THESE PHOTOS                 │
│ (◉ Blanket · 14) (◉ Kitten · 9)      │
├─────────────────────────────────────┤
│ ▢ ▢ ▢   results grid, 3 columns      │
│ ▢ ▢ ▢                                 │
└─────────────────────────────────────┘
```
- Empty state before searching: the search bar and the text `Search the way you remember it` with example chips `my cat on couch`, `beach sunset`, `birthday cake` that fill the search box when tapped (they are examples only; they do not count as hints).
- Hint chip: 24 px circular thumbnail on the left, then label `{value} · {count}`. Rows scroll horizontally; the row label sits above the chips, 12 px 500, uppercase, letter-spacing 0.5 px, `#444746`.
- Submit on Enter or the keyboard's search key. Show a thin indeterminate progress bar under the search bar while waiting.
- Results grid: same as home, no date headers, newest first, show 60 then load 60 more on scroll.

**C. Viewer, route `/photo/{id}`**
- Layout as in `viewer.png`: full-screen photo (contain) on black, back arrow top-left, top-right icons as in the real app. Swipe left or right moves to the next or previous photo in the list the user came from (gallery order or search results).
- Bottom action bar as in `viewer.png`. Only **Delete** works (normal mode only): confirm dialog `Delete this photo?` with `Cancel` and `Delete`; then return to the previous screen. Other icons are visual only.
- **Info panel** (swipe up or tap ⓘ, as in `viewer-info.png`): date and time, place (city if known, else setting), and the AI caption shown as the description. In normal mode:
  - A pencil next to the date opens a native date-time input; saving sets `date_source = "manual"` and re-sorts the photo.
  - A `People` row with `Add name` chips: type a name, press Enter to add, ✕ to remove. Saves to `people_names`. This stands in for Google Photos' face tagging.
- **Test mode only:** a bottom button `This is it` (filled, `#0B57D0`, white text) above the action bar. Tapping it logs `found`, shows a snackbar `Thanks! You found it in mm:ss`, and disables the button.

**D. Log download (no page):** the researcher opens `{API}/api/export?key={EXPORT_KEY}` in a browser to download all sessions' events as one JSONL file. Optional `&session={id}` downloads one session.

### 6.6 People names (optional)
AI cannot know names. In the viewer's info panel, the `People` row lets the researcher add names (for example `Kabir`, `Pooja`). Saved to `people_names` and added to `tags`. If no photo has names, the `who` facet falls back to people counts. This takes a few minutes for a demo library and stands in for Google Photos' face groups.

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

