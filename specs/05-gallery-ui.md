# 05-gallery-ui: Shared frontend and gallery upload experience

Status: **Not started — specification only.**

Source of truth: [PRD.md](../PRD.md). Repository rules: [AGENTS.md](../AGENTS.md). If this spec or its copied excerpts conflict with the current PRD, the PRD wins. No application implementation is authorized by the creation of this file.

Read [OPEN-QUESTIONS.md](OPEN-QUESTIONS.md) and [DESIGN-REFERENCE.md](DESIGN-REFERENCE.md) for affected decisions.
## Goal
Build mobile-first layout and Photos gallery with native upload and processing states. First part of build step 5; no separate upload/admin page.

## Requirements
- Next.js App Router, TypeScript, Tailwind; frontend paths/components/config from section 10.
- Inspect `home.jpeg`; obey written 3-column square grid, 2 px gaps, day headers, lazy loading, newest first and No date at end. Apply the resolved visual priority in DESIGN-REFERENCE: screenshots guide appearance, while explicit PRD structure, behaviour and colour/style requirements win.
- Desktop >480 px: centred 430 px app column, outer #F1F3F4. Fonts/icons/tokens per 5.1, no Google logo/wordmark or account photo.
- Top-bar Upload button opens `<input type="file" accept="image/*" multiple>`; empty normal gallery shows `No photos yet` and `Upload photos`.
- Upload→processing snackbars, immediate cards at photo date, per-photo bottom-right spinner, failed processing Retry, invalid-file message and dismissible no-date notice use exact section 5.2 copy.
- Poll `/api/status` every 5 seconds while processing and refresh cards/spinners; hide mutations whenever session query parameter is present.
- Copy screenshot bottom-nav labels/icons (Photos, Collections, Create, separate search entry); only Photos and search work. Preserve session on every internal link. Others are visible inert icons, no screens/errors.

## Relevant PRD constraints
Sections 3, 5.1–5.2 A, 9–10, 12.2 checks 1–2 and 14. Reference screenshots are .jpeg rather than .png; use existing files. Do not copy screenshot memories/video/backup features. Source appendix includes other screens for shared layout context, not additional phase ownership.

## Implementation requirements
Own layout/page, PhotoGrid, BottomNav, UploadButton and Snackbar; establish typed fetch wrappers and mirrored API types for later screens. `config.ts` contains NEXT_PUBLIC_API_URL only. Shared navigation/header code must preserve session for 08 and send X-Session-Id in test mode from the outset. GET gallery pages use next_cursor; handle loading/error/cold DB with progress and once-only timeout retry. Keep transient upload state and displayed cards consistent with server progress. Viewer links target phase 07 without inventing routes.

## API/data contracts
Use upload/photos/detail/status/retry APIs from 01–02 and section 9. Do not calculate media paths on the client. Upload failures and partial interruption count handling use the agreed per-file response contract. No browser original photo bytes stored in application state longer than needed for upload.

## Edge cases
Empty library, no date/stripped EXIF, HEIC errors, corrupted/oversized file among valid files, capacity limit, interrupted upload keeps completed files and reports successes, failed provider retry, all-provider rate limit processing, DB cold start and repeated navigation. Duplicate uploads are allowed. Retry hidden/blocked in test mode.

## Tests
Run locally and production build; inspect console/network. Compare at mobile target width and desktop wrapper; exercise native multi-picker from phone and laptop, immediate gallery appearance, spinner/status polling/snackbar lifecycle, no-date dismissal and retry. Verify known session param hides writes even before complete 08 integration. Real acceptance requires 30 uploads from phone and laptop; distinguish smaller development batches from that check.

## Acceptance criteria
Shared Home/navigation/grid behaviours match resolved reference guidance; phase's parts of manual checks 1–2 work. No invented pages, branding or active out-of-scope controls; uploads correctly reflect backend state. Date movement/name search finish in 07.

## Dependencies
00–04 complete backend-test gate; 01–02 APIs; recorded visual-priority guidance (resolved, not a blocker). 07 completes viewer links; 08 completes session creation/logging. Do not mark combined journeys complete before those dependencies.

## Definition of done
Build passes, UI actually runs without unexplained console/network failures, gallery/upload states exercised, responsive comparisons recorded; unfinished phone-specific criteria explicitly tracked; STATUS and README updated.

## Normative PRD excerpts

The following are copied unchanged from PRD v3.1 for implementation context. Re-read the linked source before implementation if it changes.

### 5.1 Visual style: match the Google Photos app
The user-facing screens (Home, Search, Viewer) must match the current Google Photos mobile app as closely as possible in layout, spacing, sizes, colours, icons, chip styles, grid and motion, so participants behave exactly as they do in the real app.

**Design reference (do this before building the frontend, 15 minutes):** take phone screenshots of the current Google Photos app and save them in `frontend/design-reference/`:
1. `home.png`: the Photos tab, scrolled to show date headers and the grid.
2. `search-empty.png`: the search screen before typing.
3. `search-results.png`: results for any query, showing the suggestion chips row if present.
4. `viewer.png`: one photo open, with the bottom actions visible.
5. `viewer-info.png`: the info panel swiped up.
The AI tool must match these screenshots pixel-for-pixel where possible (measure spacing from them) and use the tokens below only where the screenshots don't decide. New elements that don't exist in the real app (hint rows, "Not finding it?", drop row) must use the same chip and text styles as the real app's suggestion chips, so they look native.

**Only exceptions to an exact copy:** no Google or Google Photos logo and no "Google Photos" wordmark (use a neutral placeholder where the logo sits, for example a grey circle, or leave it out), and no account avatar photo (use a plain initial circle). This keeps the prototype from being mistaken for the real app if its link is shared, and changes nothing about how participants search.

**Default tokens (used where screenshots don't decide):**

| Token | Value |
|---|---|
| App name in UI | none |
| Font | `Google Sans Flex` if available on Google Fonts at build time (it is open-licensed); otherwise `Roboto`. Load via `next/font/google`, weights 400 and 500 |
| Icons | Material Symbols Outlined (Google Fonts, free), via `<link>` or `material-symbols` npm package |
| Background | `#FFFFFF` |
| Primary text | `#1F1F1F` |
| Secondary text | `#444746` |
| Primary / links / active nav | `#0B57D0` |
| Search bar surface | `#F0F4F9`, height 48 px, fully rounded |
| Chip | height 32 px, radius 8 px, border 1 px `#C4C7C5`, text 14 px 500; selected: bg `#D3E3FD`, no border, text `#041E49` |
| Grid gap | 2 px |
| Section date header | 14 px 500 `#1F1F1F`, padding 16 px left, 12 px top |
| Bottom nav | copy the items, icons and labels in `home.png`; only Photos and the search entry work, other items are visible but do nothing (no navigation, no error) |
| Viewer | full-screen black `#000000`, white icons |

**Layout width:** mobile-first. On screens wider than 480 px, render the app in a centred 430 px column with a light grey `#F1F3F4` page background, so desktop testing still looks like a phone.

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

