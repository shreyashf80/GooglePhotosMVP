# 09-deployment: Integration, deployment and final acceptance

Status: **Not started — specification only.**

Source of truth: [PRD.md](../PRD.md). Repository rules: [AGENTS.md](../AGENTS.md). If this spec or its copied excerpts conflict with the current PRD, the PRD wins except for the explicitly authorized AI-provider clarification recorded below. No application implementation is authorized by the creation of this file.

Read [OPEN-QUESTIONS.md](OPEN-QUESTIONS.md) and [DESIGN-REFERENCE.md](DESIGN-REFERENCE.md) for affected decisions.
## Goal
Finish build step 7: verified deployment preparation, deployed smoke test and criterion-by-criterion acceptance review, without expanding scope.

## Requirements
- Run full backend tests before frontend gate and again at final review; production frontend build, console/network/runtime review and secret inspection.
- Complete end-to-end upload→gallery pending→tagged→search→hints→narrow/chip→remove/restore→wrong-time recovery→viewer. Test normal date/name/delete and on/off sessions/export.
- Neon pooled SSL URL, separate local-test branch; Railway backend folder/Procfile, ONE instance, NO volume; Vercel frontend root/NEXT_PUBLIC_API_URL. All DB/image/session/event persistence is Neon.
- Set PUBLIC_BASE_URL to backend URL, CORS_ORIGINS to actual frontend origin; preserve local configuration and complete placeholder .env examples. No secrets committed or public.
- Curate 30–60 demo photos according to section 6.0 counts/time/room/event patterns, fix dates/names, pre-test every demo query. Do not fake tagging quality or lower eligibility thresholds.
- Deploy only after local verification and necessary user authorization. Smoke: health ok, phone upload five photos, processing clears, search finds them, TEST/on session, JSONL export.
- Measure hint tap <1 second on mobile data after initial parse; computation <300 ms excluding parser. Redeploy persistence check covers photos AND sessions. Compare Home/Search/Viewer on same phone against real app using screenshot visual guidance while explicit PRD structure, functionality, behaviour and colour/style requirements take priority.
- README documents purpose/architecture/prerequisites/env/local setup/tests/demo upload/normal mode/test sessions/export/deployment/limitations using practical tested commands.

## Relevant PRD constraints
Sections 6.0, 11–16, 12.2 all ten checks, 13 build order/cut list and 17 non-MVP future work. Source excerpts follow so study/deployment/edge-case requirements remain available. Historical review-log claims do not override current single-library/Neon design.

## Implementation requirements
Add specified backend Procfile and deployment configuration only as required; do not introduce infrastructure or alternate hosting. Maintain acceptance evidence and STATUS. Warm app before demo for Neon cold start. No silent cuts; prescribed cut order is city lookup→who/People→part-of-day→swipe→Delete, and any cut must be explicitly authorized/reported. Essential upload/date/hints/drop/nearest/test/logging cannot be cut independently.

## API/data contracts
No new API. Verify public absolute media URLs, health, image cache/CORS and export after deployment. Schema/byte storage survives release, in-memory caches rebuild. Configuration retains section 11.1 defaults except the authorized GROQ_API_KEYS replacement and shared per-key pool behaviour; changes to current model env values require provider availability verification and notice if material.

## Edge cases
Re-run relevant section 14 cases across the complete system: rate limits/failure, stripped metadata, invalid/HEIC files, interruption, cap/duplicates, no dates, partial tags, empty search, parser timeout, identical facets, cold Neon, repeated session/found and redeploy. Participant own-photo consent/privacy is an operational procedure; do not invent consent UI or own-library management. Keep main link private; share test links only.

## Tests
Run `pytest` in backend and `npm run build` in frontend once implementation exists. Record environment, result and failures/fixes. All ten section 12.2 manual checks require individual outcomes (pass/fail/not verified) and evidence; step smoke alone is insufficient. Real phone/laptop uploads, mobile-data latency, same-phone visual comparison under the recorded visual-priority decision, live provider restart and redeploy persistence need actual external/device testing.

## Acceptance criteria
Every section 12 backend case and manual check reviewed individually; app runnable from README; no known critical issue hidden; unresolved credential/device checks explicitly identified. Deployment success alone is not completion. Research participant results are not preconditions for declaring code built; preserve section 15 protocol/metrics without claiming unrun study outcomes.

## Dependencies
00–08 verified locally; Neon credentials, Gemini/Groq comma-separated backend key lists, Railway/Vercel accounts/authorization, demo photos, phone/laptop access and deployment approval at the point needed. Resolve product contradictions before affected implementation; document unavoidable unverified criteria.

## Definition of done
Final acceptance report includes Implemented, Tests, Verified manually, Not verified, Deviations, Remaining issues and exact Run instructions. Only mark deployed/smoke/performance/device checks passed when exercised; remaining human-access work is concrete. Re-read PRD acceptance criteria and AGENTS final-review requirements before reporting completion.

## Authorized AI-provider clarification

The user's 6 October 2026 clarification in [AI-PROVIDER-POOLS.md](AI-PROVIDER-POOLS.md) governs provider/key selection where it explicitly differs from PRD v3.1. Both Gemini and Groq use comma-separated backend-only key pools; no OpenAI integration is allowed. PRD remains authoritative for everything else. Copied PRD excerpts below remain verbatim historical source snapshots: their singular GROQ_API_KEY and generic all-fail rule are superseded as described in the clarification.

Deployment/configuration verification must confirm plural backend-only GEMINI_API_KEYS/GROQ_API_KEYS lists, all configured independently quota-bearing keys usable, no singular Groq dependency, no keys in frontend/API/logs/errors, and no OpenAI provider/dependency/configuration/fallback. `.env.example` requirements and live provider prerequisites follow AI-PROVIDER-POOLS; model defaults are unchanged and selected vision capability must be verified before use.

## Normative PRD excerpts

The following are copied unchanged from PRD v3.1 for implementation context. Re-read the linked source before implementation if it changes.

### 6.0 Demo library recipe (small, curated, shows every behaviour)
With few photos, hints only appear if the library is built so searches return several look-alikes. Upload **30 to 60 photos** chosen to create these patterns, then fix any wrong dates from each photo's info panel so the time spread is real:

| Pattern | Photos | Shows |
|---|---|---|
| One pet (or object) in the same spot across 3 different years or homes, for example the cat on a couch | 10 to 14 | **When** hints (years), **Where** hints (two rooms or homes), **Also in** hints (blanket, kitten, toy) |
| One person across 3 or 4 events in different months | 8 to 12 | **When** at month level, **Who** hint (set names in the People field), event-based **Also in** hints |
| Two trips or outings with similar scenery (beach, hills) | 8 to 10 | **Where** hints (two cities if GPS exists, else settings), drop a detail |
| Several photos from one single day (a party or wedding) | 5 to 8 | **When** at part-of-day level (afternoon vs evening) |
| A few distinctive photos (a receipt, a landmark, a sign with text) | 3 to 5 | Contrast: these are found in one search, no hints needed |

Then pre-test these demo queries and keep the ones that show the behaviour cleanly:
`my cat on couch` (several hint rows), `{person name}` (Who and When), `beach` (Where), `{person name} 2025` where no 2025 photos exist (nearest time), `cat on bed with red blanket` (drop a detail).

## 11. Configuration and deployment

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

### 11.2 Local run
```
cd backend && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && cp .env.example .env   (fill keys and the Neon DATABASE_URL)
uvicorn app.main:app --reload --port 8000
cd ../frontend && npm install && cp .env.example .env.local   (NEXT_PUBLIC_API_URL=http://localhost:8000)
npm run dev
```

### 11.3 Deploy
- **Neon:** create a project (free tier), copy the **pooled** connection string into `DATABASE_URL`. Use a separate Neon branch for local testing so test data never mixes with the demo library.
- **Railway (backend):** new service from the `backend/` folder, start command from `Procfile`. No volume is needed, because all data lives in Neon. Run **one instance only** (the tagging worker runs in-process). Set all env vars; `PUBLIC_BASE_URL` = the Railway public URL; `CORS_ORIGINS` = the Vercel URL.
- **Vercel (frontend):** import the repo with root directory `frontend/`; set `NEXT_PUBLIC_API_URL` to the Railway URL.
- **Smoke test after deploy:** `/api/health` returns ok; on a phone, tap Upload on the gallery and add 5 photos; spinners clear; a search returns them; `/start?p=TEST&hints=on` opens test mode; `/api/export?key=...` downloads its events.

### 11.4 Privacy
- Photos are stored in Neon and sent as small thumbnails to Gemini or Groq for tagging. Free tiers may use data to improve the providers' products.
- If participants upload their own photos, read them: "Small copies of your photos will be sent to Google Gemini or Groq to generate short descriptions, and stored on a private test server. They are deleted after the study." Do not upload without a yes. Delete their photos after the session.
- There is no login: anyone with the app link can upload, edit or delete in normal mode. Do not share the link publicly; share only `/start` test links, which lock those actions. The 100-photo cap limits abuse.

---

## 12. Acceptance criteria and tests

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

### 12.2 Manual acceptance checks
1. On a phone browser (Chrome Android or Safari iOS), Home and Search look like the Google Photos app: search pill, 3-column grid with 2 px gaps, date headers, bottom nav, chip styling per 5.1.
2. Tapping Upload on the gallery opens the phone's photo picker; 30 photos upload from a phone and from a laptop; spinners clear as tagging finishes; editing a date in the info panel moves the photo in the grid; adding a name in People makes it searchable.
3. A broad search shows at least one hint row with thumbnails; tapping a hint shrinks results and adds a chip; ✕ restores the previous count.
4. A query with a wrong year shows the nearest-time chip.
5. `/start?p=P1&hints=off` opens test mode: no hint rows, no drop row, and no Upload, edit or delete anywhere.
6. In test mode, "This is it" logs `found`; `/api/export?key=...` downloads JSONL containing every action in order.
7. After the first query-parsing call, each hint tap updates in under 1 s on mobile data.
8. Redeploying the backend keeps photos and sessions (all data is in Neon).
9. Side by side with the real Google Photos app on the same phone, Home, Search and Viewer are hard to tell apart, except for the missing logo.
10. Every demo query from 6.0 shows the behaviour it is meant to show.

---

## 13. Build order (5 to 6 hours)

| Step | Time | Output | Done when |
|---|---|---|---|
| 1 | 30 min | Backend skeleton: config, DB schema, health, default library created on startup | `/api/health` ok locally |
| 2 | 45 min | Upload, resizing, dates, media routes | `test_dates.py` passes; uploaded thumbs load in the browser |
| 3 | 45 min | Tagging worker with Gemini, Groq fallback, retries | 20 photos reach `tagged`; killing the server mid-run and restarting resumes |
| 4 | 60 min | `search.py`, `hints.py`, search endpoint, fixture tests | All unit tests pass |
| 5 | 75 min | Frontend: layout, gallery grid with Upload button and snackbars, Search screen with chips, hint rows, drop row, Viewer with info panel | Manual checks 1 to 4 pass locally on a phone-sized window |
| 6 | 30 min | `/start` test mode, write-locking, event logging, export URL | Manual checks 5 and 6 pass |
| 7 | 30 min | Deploy Railway and Vercel (Neon already set up), upload the demo library (6.0), smoke test | Manual checks 7 to 10 pass |

**Cut list if time runs short (in this order):** city lookup, `who` facet and the People editor, part-of-day buckets, swipe between photos in the viewer, Delete in the viewer. Never cut: Upload button, date editing, hints, drop a detail, nearest time, test mode and logging.

---

## 14. Edge cases

| Case | Required behaviour |
|---|---|
| Photo has no date | Excluded from `when` counts and time matching; shown in results last and under "No date" on Home. |
| Mobile upload strips EXIF | Dates show `none`; the gallery shows the no-date notice (5.2 A); fix from the info panel. |
| HEIC file | Converted via pillow-heif; if conversion fails, that file gets the "couldn't be uploaded" snackbar. |
| Corrupt or non-image file | Rejected with the "couldn't be uploaded" snackbar; others continue. |
| Upload interrupted (screen locked, network drop) | Files already received are kept; the snackbar shows how many succeeded; the user can upload the rest again. |
| Tagging provider returns invalid JSON | Retry once, then the next provider, then `failed`. |
| All providers rate-limited | Photos stay `pending` with spinners; worker keeps retrying with backoff; snackbar stays on `Processing…`. |
| Someone opens the app link (not a test link) and deletes photos | Accepted risk for a prototype; keep the main link private; re-upload from the laptop folder if needed. |
| Search while some photos untagged | Only tagged photos are searched; Search screen shows a small grey note `{k} photos are still being processed` if k > 0. |
| Query parser fails or times out | Use local fallback; log `parse_source: "fallback"`. |
| Only stopwords typed | Show the copy from 5.4; no request results. |
| All results identical on every facet | No hint rows; "Not finding it?" link still shown. |
| Library over 100 photos | Upload rejected beyond the limit with a clear message. |
| Neon cold start (free tier sleeps when idle) | First request may take 1 to 3 s; frontend shows the progress bar and retries once on timeout. Open the app once before a demo to wake it. |
| Session link opened twice | Same session; `task_start` only logged if `started_at` is empty. |
| "This is it" tapped twice | Second tap ignored. |
| Railway redeploy | Nothing lost: data and images live in Neon; in-memory caches rebuild on first request. |
| Duplicate uploads | Allowed; no de-duplication. |

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

## 16. Risks and mitigations

| Risk | Mitigation |
|---|---|
| AI tags miss what users remember | `notable` field in the prompt; drop a detail; log searches with 0 results to see what was missed. |
| Dates lost on mobile upload | Laptop upload recommended; manual date edit; warning banner. |
| Free-tier limits or model names change | All in env vars; two providers with fallback; resumable worker. |
| Small library makes hints look trivial | Curated demo recipe (6.0) built so each hint type has a real choice to make; demo queries pre-tested. |
| Neon free-tier storage or compute limits | Images compressed (about 20 MB for 60 photos); 100-photo cap; images cached a week by browsers. |
| Prototype search weaker than Google Photos | Main comparison is hints on vs off within the same prototype. |
| Participants confused by a look-alike app | It mirrors Google Photos layout so behaviour transfers; brief participants that it is a prototype. |
| Privacy of participant photos | Consent script, private links, delete library after study. |
| Overlap with existing Photos suggestions and Ask Photos | Note in findings; the test isolates result-derived, splitting hints. |

---

## 17. Later (not in MVP)
- Face clustering so `who` works without manual names.
- Learning the user's own words (for example "Didi" means Pooja).
- Hints inside one crowded moment by sub-scene.
- Real integration through Google's picker or on-device inside the app.

---

## 18. PRD review log

| # | Gap found | Fix |
|---|---|---|
| 1 | v1 required exporting and indexing a local folder | Browser upload with server-side processing (6.1) |
| 2 | v1 ran in Streamlit on a laptop, not testable on a phone | Next.js mobile-first web on Vercel, FastAPI on Railway (5, 11.3) |
| 3 | "Looks like Google Photos" could lead to copying brand assets | Material 3 look with Roboto and Material Symbols; explicit no-logo, no-name rule (5.1) |
| 4 | Railway's filesystem resets on redeploy | Volume at `/data` required; persistence is an acceptance check (11.3, 12.2) |
| 5 | Mobile browsers can strip EXIF, killing the `when` hint | Filename fallback, manual date edit, warning banner, laptop upload advice (6.2, 14) |
| 6 | No mtime available from browser uploads | Removed mtime fallback; `none` plus manual fix (6.2) |
| 7 | One provider's free tier can stall tagging | Gemini key rotation plus Groq fallback, per-provider rate limits (6.3) |
| 8 | Groq vision accepts few images per request | Separate `GROQ_BATCH_SIZE = 1` (6.3) |
| 9 | Query parsing latency on mobile | Groq text model first, 4 s timeout, cache, local fallback (7.1) |
| 10 | Names never match since AI cannot know them | Optional People editor in the viewer's info panel, standing in for face groups (6.6) |
| 11 | Server state for chips would break with multiple tabs | Stateless search: client sends concepts removed, overrides and filters each time (9) |
| 12 | Tagging in a separate service adds deploy work | In-process asyncio worker, resumes on restart (6.3) |
| 13 | Participant tests need separate libraries and conditions | Libraries and session links with hints on or off (5.2 D, 8, 9) |
| 14 | Untagged photos would silently be missing from search | Only tagged photos searched, with a visible "still processing" note (14) |
| 15 | Shared demo library tests interaction, not memory | Two setup options with results reported separately (15) |
| 16 | Build could overrun | Time-boxed steps and a cut list with must-keeps (13) |
| 17 | Hint rules, time filters, nearest time, logging and tests carried over from v1 review | Kept unchanged in 7, 8 and 12 |
| 18 | Drop action and Filter types were loosely written, inviting guesswork | Exact `Concept`, `Filter`, `HintRow`, `DropOption`, `DropAction` types and a client flow (9) |
| 19 | Paging by ids would need the client to build image URLs | Server returns all results as PhotoCards; client renders 60 at a time (9) |
| 20 | Session context could be lost when navigating between screens | `lib` and `session` params preserved on every link; missing-lib message (5.2) |
| 21 | With 30 to 60 photos, the old thresholds (12 results, count ≥ 2) would hide hints entirely | Thresholds lowered and moved to env: `HINT_MIN_RESULTS = 5`, `MIN_VALUE_COUNT = 1`, `DROP_ROW_MAX_RESULTS = 1` (7) |
| 22 | A random small library would not show the behaviours | Demo library recipe and pre-tested demo queries (6.0) |
| 23 | Railway's filesystem resets and the volume step added setup | All data and images in Neon (`photo_images` as BYTEA, kept out of search queries), long cache headers (8, 9, 11.3) |
| 24 | "Exact Google Photos UI" is vague for an AI tool | Screenshot-based design reference with pixel matching; tokens only as defaults; logo and wordmark as the only exceptions (5.1) |
| 25 | Neon free tier sleeps and the first request is slow | Retry once, progress bar, warm-up before demos (14) |
| 26 | Owner asked for no admin page | Upload button on the gallery using the native picker; date and people editing in the viewer's info panel (as in Google Photos); delete in the viewer; test mode via `/start` link; log download via one URL (5.2, 9) |
| 27 | Without an admin page, participants could upload or delete during tests | Test mode hides write actions and the backend rejects writes carrying a session id (5.2, 9) |
| 28 | Multiple libraries need a selector, which would need an admin page | One library (`LIBRARY_CODE`); the column stays for later (3, 9) |

Final check against the strategic goal: every feature exists to turn a crowded, wrong or empty first search into a found photo through recognition (hints) or one-step correction (drop a detail and nearest time). Nothing in scope improves search in general, and the primary metric, found rate, is the strategic goal measured at task level.

