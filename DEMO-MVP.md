# Search Hints — submission Demo MVP

Status: **Plan only; implementation not started.** Created 6 October 2026.

## Purpose and authority

Deliver a polished, functional presentation demo in approximately four hours, including deployment/debug buffer. Demonstrate **vague memory → broad search → recognizable cues → refinement → target photo → successful retrieval** using curated photos and deterministic metadata.

This is a temporary, explicitly authorized submission scope. [PRD.md](PRD.md), [AGENTS.md](AGENTS.md) and [the full specifications](specs/README.md) remain the source of truth for the eventual research MVP. This document does not delete, rewrite, complete or invalidate any full-project specification or acceptance criterion. Where this demo intentionally differs, the differences below apply only to the submission demo. Do not represent the demo as the completed research MVP.

The current task authorizes creating this plan only. Do not implement application code, download photos, install dependencies, create hosting services or deploy until subsequent authorization. No credentials are needed to create this plan.

## Submission scope

Implement after authorization:

- Next.js App Router/TypeScript/Tailwind frontend, deployed to Vercel.
- FastAPI backend, deployed to Railway, loading one checked-in curated metadata JSON file.
- 24 local photo assets, gallery/date groups, deterministic search/results, removable query/filter chips, result counts, Search Hints and recovery.
- WHEN, WHO'S IN IT and ALSO IN THESE PHOTOS rows computed from current result metadata.
- Hint selection narrows results; chip removal broadens them and restores the earlier count.
- Not finding it? exposes drop-query/filter options. Implement straightforward year and month+year nearest-time recovery; no provider or database is needed.
- Full-screen photo viewer, return-to-search context, read-only photo information and a local This is it success action.
- Mobile-first visual polish and centered desktop presentation, with the same core screens/interactions at both sizes.

Temporarily defer Neon, persistence, AI/provider pools, tagging, upload/EXIF/processing, researcher edits/delete, production sessions/logging/export and study infrastructure. Authentication is a full-PRD non-goal, not a feature to add later merely because it appears in the requested defer list. Do not use OpenAI as a provider, dependency or integration. No external AI calls at all in this demo.

## Visual and interaction rules

Use the recorded [visual-priority decision](specs/DESIGN-REFERENCE.md): screenshots guide typography, spacing, surfaces, icons, navigation treatment, viewer proportions and Google Photos visual feel. Explicit PRD structure, behaviour and colour/style requirements win.

- White application surface; PRD primary/secondary/blue colour tokens and search/chip metrics. Three-column square photo grid with 2 px gaps, day grouping on Home and no headers on Search results.
- Search pill, back and clear controls, active chips, count, hint rows and Not finding it? keep PRD behaviour. Do not copy conversational/Ask Photos UI, backup warnings, memories, albums or Google branding.
- WHEN / WHO'S IN IT / ALSO IN THESE PHOTOS labels; 24 px circular hint thumbnails; `{value} · {count}`; horizontal chip rows. Selected filters appear in the active chip row.
- Home top bar and inert Collections/Create navigation match compatible reference styling; Photos/search navigation works. No fake Upload button or pending-processing states.
- Search empty state uses `Search the way you remember it` and examples `cafe in Goa`, `beach sunset`, `medicine` suitable for this curated library. This example substitution is demo-only.
- Retain PRD stopword/no-match/search-error/drop/nearest copy. A new query resets refinement state; clear resets the screen. Thin progress bar during requests; loading/error states support retry.
- Above 480 px, centered 430 px column with #F1F3F4 outer background. Do not add a separate desktop dashboard or wide-grid layout.
- Viewer uses black background, contained photo, white controls and working back/info. This is it appears for this demo without a production test session; local acknowledgement is not a recorded research outcome.
- Display a small `Demo library` label in existing Home/info chrome so stock imagery and curated metadata are not mistaken for a participant's real library. No new onboarding screen.

## Curated dataset

### Storage and fields

Planned metadata location: `backend/demo_data/photos.json`. Planned image assets: `frontend/public/demo/photos/{id}.jpg`. Planned attribution manifest: `frontend/public/demo/SOURCES.md`, available at `/demo/SOURCES.md` after deployment.

JSON root is an array of records. Each record contains:

| Field | Type and meaning |
|---|---|
| id | Stable string, d01–d24 |
| image_path | Frontend public path, e.g. `/demo/photos/d01.jpg` |
| taken_at | ISO date-time without timezone; chosen demo memory date |
| location | Human-readable curated location, e.g. Goa |
| city | Matching/facet metadata, e.g. goa |
| setting | Visible place type, e.g. cafe, beach, home |
| people_names | Array of fictional demo labels, e.g. rahul |
| people_count | Integer; consistent with visible people when relevant |
| tags | Normalized phrase/word array for deterministic matching |
| caption | Short description consistent with visible image |
| event | PRD-style event label, e.g. trip, meal, birthday, everyday |
| part_of_day | morning/afternoon/evening/night, consistent with taken_at |
| source_id | Reference to attribution manifest entry |

Every record is ready/searchable; API cards/details report `tag_status:"tagged"` solely for shape compatibility and details use `date_source:"manual"`. No AI tagging occurred. Gallery assets are compressed local JPEGs, not originals downloaded at runtime. A single reasonably sized image can serve thumbnail and viewer for this demo; separate generation/storage is deferred.

### Deliberate 24-photo distribution

| IDs | Scenario | Count | Dates | Recognition/distractor details |
|---|---|---|---|---|
| d01–d04 | Goa cafe visit | 4 | February 2024 | Two Rahul photos; outdoor/indoor seating, coffee/cold drink and pastry variations |
| d05–d08 | Goa cafe visit | 4 | April 2024 | Similar coffee/friends scenes; distinct seating/table composition |
| d09–d12 | Goa cafe visit | 4 | November 2024 | Similar cafe scenes that make the initial query genuinely broad |
| d13–d17 | Goa beach/sunset | 5 | Several 2023/2024 dates | Sunset/water/friends distractors; no cafe tag |
| d18–d21 | Medicine/prescription/illness | 4 | Several 2024 dates | Medication packaging, prescription-like blank/generic papers, illness/home details; no real patient data |
| d22–d24 | Birthday/social gathering | 3 | Several 2023/2024 dates | Cake/friends/balloons distractors, including a cafe setting outside Goa |

All 12 Goa cafe records have cafe and goa matching metadata. Spread their dates across the three months **within one year** so adaptive WHEN uses month buckets rather than years.

Cafe people labels:

- Rahul: d01, d02, d05, d06, d09 (5).
- Ananya: d04, d07, d10, d11 (4).
- Meera: d03, d08, d12 (3).

Cafe distinctive tags:

- coffee: d01, d02, d03, d05, d06, d07, d09, d10 (8).
- outdoor seating: d01, d03, d05, d08, d09, d11 (6).
- pastry: d02, d06, d12 (3).

Add corresponding singular/phrase component tags according to PRD normalization. Any additional tags must match visible image content; re-check scores if added. Dataset results/counts are computed, never hardcoded endpoint responses.

### Image sourcing and attribution

During the later build, select visually coherent, distinct images from Unsplash, Pexels or Wikimedia Commons only after checking each image's applicable license/download terms. Prefer readily reusable images with straightforward obligations; Wikimedia images have file-specific licenses, not one blanket Commons license. Do not use Google Images result thumbnails as a source.

Download authorized assets into frontend public storage rather than hotlinking at runtime. Record source page, creator, license/version/link, acquisition date, local filename and edits in SOURCES.md; provide any required visible credit/link in the existing photo info sheet. Choose another photo if license obligations cannot fit the deadline. Do not fetch any media during this planning task.

Metadata dates, Goa locations and names are fictional demonstration labels, not assertions about stock-image subjects or where/when those photos were taken. Identify this in SOURCES.md and the demo-library note. Coffee/seating/cake/medicine details must be visibly credible. Pick d01 first and make its target description unambiguous before choosing look-alike distractors; use 24 distinct images rather than duplicating one image to manufacture a broad set.

## Hero query and target photo

**Query:** `cafe in Goa`.

**Target:** `d01`, a visually distinctive outdoor cafe-table photo with coffee and a person labelled Rahul, demo date `2024-02-18T16:00:00`. Prefer a clear memorable table detail (e.g. a bright cup) for explaining the target, without adding a new search requirement.

Expected journey, derived from the dataset:

1. Submit cafe in Goa → **12 photos**; active cafe/Goa concepts.
2. See WHEN: Feb 2024 (4), Apr 2024 (4), Nov 2024 (4); WHO: Rahul (5), Ananya (4), Meera (3); ALSO includes coffee (8), outdoor seating (6), pastry (3), subject to the exact eligible-value selection/order.
3. Tap Feb 2024 → **4 photos** and active time chip. At N=4, hide hint rows according to the preserved N≥5 rule; do not lower the threshold to keep hints visible.
4. Open d01 among the four, recognizable from its image; press This is it → immediate success acknowledgement.
5. Return to results and remove Feb 2024 → **12 photos**, hints restored.

Alternative refinement for showing a people hint: restart broad query, tap Rahul → **5 photos**; removing Rahul restores 12. Select Feb 2024 if it remains eligible → **2 photos**, then open d01. Initial ALSO interaction: outdoor seating → **6 photos**, remove → 12. This exercises all three hint types without requiring all three to remain visible after every refinement.

Backup recovery demonstrations:

- `cafe in Goa 2025` → 0; nearest-time `2024 · 12`, replacement yields 12. Also offer Drop 2025 · 12.
- `cafe in Goa February 2025` → 0; nearest month+year is Nov 2024 (4), since it is closer than Feb/Apr 2024. Use this to explain nearest means time distance, not same month in a previous year.
- `cafe in Goa snowy` → 0; Drop snowy · 12. Unknown words must constrain search, not disappear silently.
- `medicine` → medication/document results, demonstrating a different visual memory category without requiring hints on a result set smaller than five.

## Deterministic search/hint behaviour

Reuse the applicable PRD algorithms instead of implementing canned answers:

- Extract standalone years and month names/abbreviations with adjacent years locally. Remove exact PRD stopwords and normalize with its singularization rules. Parse remaining concepts deterministically, using the existing small synonym map plus explicit demo aliases cafe↔café, coffee shop↔cafe and medicine↔medication. Recognize those supported phrases; no AI parser or expansive natural-language claims.
- Match every thing concept against normalized tags/caption whole words and every time concept against dates. Intersect all concepts and active filters; dates descending/null last/id tie-break. Return all result cards.
- Preserve stateless removed_concept_ids, concept_overrides and filters. Hint taps use returned filters; concept/filter removal recalculates against metadata. Keep original concept identity when overriding time.
- Hints from current results only: N≥5, MIN_VALUE_COUNT=1, MAX_ELIGIBLE_SHARE=0.85, MIN_FACET_SCORE=0.25, max 3 rows/max 4 values; retain PRD score formulas/row priority and median-date representative thumbnails.
- WHEN uses year→month→day adaptive buckets. Part-of-day hint buckets are deferred for this demo; store the metadata but do not implement an unresolved Night filter contract. WHO uses curated names; ALSO excludes query synonyms, selected filter values, setting/city/names and everyday/other. No WHERE row in this submission scope; location still participates in matching. Those facets remain in full specs.
- Drop row appears automatically at N≤1 or on want_drop; try removing each active concept/filter, only count>N, count-descending, max 4. Include nearest first for zero-result year/month+year queries, earlier on ties, with replace_concept action. Month-only nearest distance is deferred; normal month-only matching still works.
- No hint/value response should be manually injected to force screenshots. Design and test the fixture so the prescribed scoring naturally produces the promised rows. Duplicate phrase/component tags may create additional eligible ALSO values; labels/counts and exclusion remain deterministic.

## Minimum API endpoints and contracts

No database, mutation, session, upload, provider or export endpoint is needed.

| Method/path | Request | Response |
|---|---|---|
| GET /api/health | none | `{ok:true}` |
| GET /api/photos?cursor=&limit=60 | optional gallery cursor/limit | `{items:PhotoCard[], next_cursor:string|null}`; all 24 fit the first page |
| GET /api/photos/{id} | photo id | PhotoDetail; 404 for unknown id |
| POST /api/search | SearchRequest | SearchResponse |

Use PRD section 9 shapes:

```text
PhotoCard = {id, thumb_url, taken_at, tag_status}
PhotoDetail = {id, full_url, thumb_url, taken_at, date_source,
               city, setting, caption, people_names, tag_status}
SearchRequest = {query, removed_concept_ids:[], concept_overrides:[],
                 filters:[], hints_on:true, want_drop:false}
SearchResponse = {concepts, n_results, results:PhotoCard[], hints:HintRow[],
                  drop:DropOption[], untagged_count:0, message:string|null}
Concept = {id, label, kind:"thing"|"time", synonyms:[], year?, month?}
Filter = {facet:"when", level:"year"|"month"|"day", label, start, end}
       | {facet:"who"|"also", value, label}
HintRow = {facet, label, values:[{label, count, thumb_url, filter}]}
DropOption = {kind:"drop"|"nearest", label, count, action:DropAction}
DropAction = {type:"remove_concept", concept_id}
           | {type:"remove_filter", index}
           | {type:"replace_concept", concept_id, with:Concept}
```

Request field types/defaults mirror full PRD; [] notation above denotes arrays, not fixed-empty requirements. For supported dates, start inclusive/end exclusive and ISO-without-timezone semantics remain. Return empty concepts/results with exact stopword message for only-stopword input; safe validation errors never expose internals. hints_on:false suppresses hints/drop if supplied, but there is no demo condition/session management UI.

Backend returns absolute image URLs by combining `DEMO_ASSET_BASE_URL` (frontend origin) with image_path. thumb_url/full_url can be the same local asset for the demo. This intentionally differs from eventual Neon/backend media routes while preserving PhotoCard/Detail fields. No image proxy, backend media routes or runtime upstream hotlinking. Caption/place/People info is read-only.

This is it is frontend-local state, with `Thanks! You found it.` acknowledgement and disabled repeat button for that retrieval. It does not POST a research found event, claim a persisted session or fabricate elapsed-study metrics. Keep gallery/search/list origin and refinement state during viewer navigation using existing client context/sessionStorage as needed; no backend persistence.

## Minimal planned files and configuration

```text
backend/
  app/main.py       FastAPI routes, CORS, load fixture
  app/config.py     demo environment configuration
  app/models.py     compatible API types
  app/search.py     deterministic concepts/matching/recovery
  app/hints.py      metadata facets/scoring
  demo_data/photos.json
  tests/test_demo_search.py
  tests/test_demo_hints.py
  requirements.txt
  Procfile
  .env.example
frontend/
  app/layout.tsx
  app/page.tsx
  app/search/page.tsx
  app/photo/[id]/page.tsx
  components/       only gallery/search/hint/chip/nav/viewer pieces needed
  lib/config.ts     NEXT_PUBLIC_API_BASE_URL
  lib/api.ts
  lib/types.ts
  public/demo/photos/*.jpg
  public/demo/SOURCES.md
  .env.example
```

Use established FastAPI/uvicorn/Pydantic and pytest/httpx for meaningful tests; omit psycopg/Pillow/AI SDKs and worker dependencies from the demo dependency set. Keep task logic in the corresponding eventual modules, rather than a second elaborate mock service. Model/dependency details for the full MVP remain untouched in its specs.

Demo backend environment requirements:

```text
CORS_ORIGINS=http://localhost:3000
DEMO_ASSET_BASE_URL=http://localhost:3000
```

Frontend environment requirement:

```text
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

This frontend name is the requested demo configuration override; full specs keep NEXT_PUBLIC_API_URL. Read it centrally in frontend/lib/config.ts. No DATABASE_URL, AI keys or EXPORT_KEY are needed for the demo. PORT is assigned by Railway, not hardcoded. Keep actual environment files untracked.

## Vercel + Railway deployment plan

- Railway service root: backend/. One FastAPI web process; Procfile start `web: uvicorn app.main:app --host 0.0.0.0 --port $PORT`. Pin a Python 3.11+ runtime supported by the host and ensure fixture JSON is included in the deployed build. No volume or database.
- Enable a Railway public URL and health-check path /api/health. Set CORS_ORIGINS to the exact deployed Vercel origin (plus localhost only if local verification needs it). Set DEMO_ASSET_BASE_URL to that same frontend origin so image URLs resolve to checked-in assets.
- Vercel project root: frontend/. Framework Next.js; npm build/start scripts appropriate for Next.js. Set NEXT_PUBLIC_API_BASE_URL to the HTTPS Railway URL before building/redeploying. No frontend keys or secret configuration.
- Resolve the origins during setup: provision the frontend URL, provision the backend URL, configure both directions, then redeploy the frontend with its backend variable. Smoke-test image URLs and cross-origin search before taking screenshots. No hosting provider substitutions.
- If the repository still has no Git history/remote, initialize/version files locally during authorized build and use the user's chosen repository/deployment access. Hosting login/repository destination/service authorization are needed at deployment time; this plan neither publishes a repository nor creates a paid service.
- After local verification, obtain any required account/deployment authorization. Never spend the buffer silently waiting on credentials. Vercel/Railway deployment success is not proof that the API, images or hero flow works.

## Five screenshot states

Capture real browser states from the deployed app at a consistent phone-like viewport; no static replacement mockups or browser status bars fabricated in HTML. Save submission screenshots separately from the source design references.

| State | How to reach it | Required visible evidence |
|---|---|---|
| 1. Gallery/Home | Open / | Polished 3-column dated gallery with varied photos, Photos nav and usable search entry |
| 2. Initial vague results | Search cafe in Goa | Query, active concepts, 12 photos count and broad grid; hint rows may already be visible because threshold is satisfied |
| 3. Search Hints prominent | Same query, frame top of results at phone viewport | WHEN month chips, WHO names, ALSO visual details with thumbnail/counts; grid visible below where space permits |
| 4. Narrowed results | Tap Feb 2024 | Active time chip, 4 photos, distinct subset; rows correctly hidden at N<5; removal control visible |
| 5. Target/success | Open d01 and tap This is it | Correct contained target image, viewer chrome and visible success acknowledgement/disabled button |

States 2 and 3 are different captures/framing of the same legitimate broad-result state, not a hidden hints-off switch. If the screenshot needs all three rows visible, adjust compatible spacing/viewport framing, not counts or eligibility. Capture state 5 while the success message remains visible; repeat the demo from a reset query when needed.

## Four-hour build budget after implementation authorization

| Elapsed | Work | Exit check |
|---|---|---|
| 0–15 min | Minimal Next/FastAPI setup, demo config/contracts, deployment access preflight | Both run locally; identify hosting-access blockers early |
| 15–45 min | Choose/download 24 licensed assets, compress, attribution and metadata | Target/distractors distinct, all paths resolve, metadata/count matrix validated |
| 45–95 min | Deterministic backend, filters, scored hints, drop and simple nearest; tests | Hero 12→4→12, WHO/ALSO narrowing and recoveries pass before wiring frontend |
| 95–160 min | Gallery/search/chips/hints/viewer/local success with real API | Complete hero and back-navigation flow works locally |
| 160–185 min | Visual polish, mobile/desktop checks, production build, error fixes | Build passes, clean console/network, screenshot states attainable |
| 185–240 min | Railway/Vercel deployment, CORS/assets/debug, deployed smoke and screenshots | Public hero/recovery flows verified and five captures ready |

The final 55 minutes are reserved for deployment/debug/capture buffer, not additional features. Four hours is a planning target, not a guarantee of account approval/network availability. Source selection that threatens the budget should use simpler license-compatible images, not unlicensed assets or duplicated photos. Do not spend time on deferred infrastructure. Nearest year/month+year is simple deterministic logic here and stays in the planned demo; report any inability to complete it explicitly rather than hiding a missing recovery.

## Demo verification and definition of done

Automated backend checks:

- All 24 ids unique; local assets exist; date/part-of-day consistency; target and curated hero counts match the documented matrix.
- cafe in Goa returns 12; WHEN month buckets each count 4; all three required facet rows pass unmodified eligibility/scoring.
- Feb 2024 returns 4, Rahul returns 5, outdoor seating returns 6; removing each filter restores 12 exactly. Combined Feb/Rahul returns 2 including d01.
- Active filters/query synonyms do not reappear as eligible hints; N=4 hides rows; max 3 rows/4 values; common-to-all tag excluded.
- Zero-result snowy query offers Drop snowy · 12. Wrong year nearest replaces time and returns 12; month+year closest Nov 2024 returns 4; nearest ties earlier.
- Only stopwords message, clear/new-query reset, unknown photo 404, valid response shapes and optional hints-off suppression.

Frontend/integration/deployed checks:

- Frontend production build passes; no unexplained console errors, failed API requests or image 404s.
- Gallery/search/viewer work at roughly 390–430 px and centered desktop width; touch/keyboard submit, horizontally scrolling rows and clear/removal usable.
- Hero, WHO and ALSO taps, drop and nearest recoveries work through the real API. Search state survives viewer back; repeated local This is it does not repeat success for the same retrieval.
- Deployment health returns ok; correct CORS; absolute URLs point to downloaded frontend assets; source attribution obligations satisfied.
- Cold backend shows progress and recoverable retry; failures do not masquerade as results.
- Five deployed screenshot states captured and inspected; public frontend/backend URLs and exact local run instructions documented in implementation README when code exists.

Demo done means these demo checks pass. It does not satisfy full-PRD upload/tagging/session/persistence/study acceptance, and no full-project item should be marked complete on that basis. Record failures/unverified checks honestly, especially anything needing accounts or devices.

## Relationship to existing implementation specs

| Existing spec | Demo subset used | Temporarily deferred full requirements |
|---|---|---|
| 00-foundation | FastAPI/config/types/health/module separation | Neon schema/pool/library creation and database checks |
| 01-photo-ingestion | Gallery/detail response shapes | Upload, EXIF/HEIC, resizing pipeline, DB BYTEA/media/storage/status/retry |
| 02-ai-tagging | Tag normalization rules applied to fixture | All provider calls, validation/retries, worker, AI generation and live checks |
| AI-PROVIDER-POOLS | Security/no-OpenAI constraint remains | Pool code, keys, quotas/cooldowns/provider tests |
| 03-search-engine | Deterministic concepts, matching, filters, drop, year/month+year nearest | AI parsing/cache/provenance integration, production metadata cache invalidation, month-only nearest clarification |
| 04-hint-engine | WHEN/WHO/ALSO, scoring/limits/exclusion/thumb choice | WHERE and part-of-day hint buckets, full demo-fixture/live-library coverage |
| 05-gallery-ui | Layout/gallery/nav/visual tokens | Upload, processing, retry/no-date notice and mutation/session behaviour |
| 06-search-ui | Core search/chips/hints/recovery/context | Production session conditions/event hooks and full library processing behaviour |
| 07-photo-viewer | Viewer, read-only info, local success/return context | Date/People editing, delete, full session found semantics; swipe is optional after core gates and before buffer only |
| 08-test-mode-logging | None of production sessions; local acknowledgement only | /start, persisted sessions/events, on/off study links, export, timer/counters |
| 09-deployment | Same Vercel/Railway hosts, builds and demo smoke | Neon/model/credential setup, upload smoke, persistence redeploy checks and full research acceptance review |

Full open questions Q3 (Night filtering) and Q4 (parse_source transport) remain unresolved for the research MVP but do not block this demo because those paths are deferred. Resolved visual/provider decisions remain intact. No change to the full specs, PRD, AGENTS or full implementation STATUS is made by this plan.

## Current planning outcome

Only DEMO-MVP.md is created in this task. Dataset/photos are proposed, not acquired; APIs are defined, not implemented; counts are designed expectations, not tested results; hosting is planned, not provisioned. Next action after explicit implementation authorization is the first time-boxed build phase. Deployment will require account/repository access and any required approval when reached; actual AI/database credentials are unnecessary for this demo.


## Implementation authorization and evidence (6 October 2026)

The subsequent user request authorizes implementing this submission demo. The planning-only wording above records the earlier stage; it no longer blocks the demo build. Full PRD/specs remain intact. Implementation uses frontend/public/demo-photos/ per the latest instruction. See [README.md](README.md) for run/deploy/screenshot URLs and [implementation/DEMO-STATUS.md](implementation/DEMO-STATUS.md) for verified versus unverified outcomes.

Demo presentation refinement: ALSO hides phrase-component labels that select exactly the same photo set as their compound phrase; word-level matching and facet score calculations are preserved. Public hosting and physical-device checks are not claimed complete.
