# Search Hints — submission demo

A working photo-retrieval demo: start with a vague memory, recognize a detail in the result-derived hints, narrow the photos and find the target. Next.js frontend + FastAPI backend + 24 local Pexels images and curated deterministic metadata. No AI services, database, uploads or production study logging are used.

The full research MVP remains specified in PRD.md, AGENTS.md and specs/. Demo scope is in DEMO-MVP.md; verified implementation evidence is in implementation/DEMO-STATUS.md. Existing full specifications are unchanged.

## Run locally

Prerequisites: Python 3.11+ and Node.js 22.18+ (Node 24 LTS recommended). Photo assets are already included; no download is needed to run the app.

From the repository root, start the backend:

```sh
cd backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

In another terminal, from the repository root:

```sh
cd frontend
npm ci
cp .env.example .env.local
npm run dev
```

Open http://localhost:3000. The backend reads backend/demo_data/photos.json; frontend assets are under frontend/public/demo-photos/. Configuration lives in backend/app/config.py and frontend/lib/config.ts. The UI only uses frontend/lib/api.ts to talk to the backend, so the full research backend can replace the demo without restructuring the screens.

## Presentation flow

1. Search **cafe in Goa**: 12 photos with WHEN, WHO'S IN IT and ALSO IN THESE PHOTOS.
2. Tap **February 2024 · 4**: 4 photos remain and the selected time appears as a removable chip.
3. Open the **first photo, d01**: two men at an outdoor cafe table, a takeaway cup in the foreground.
4. Tap **This is it**. Success remains visible until leaving; refresh preserves it.
5. Return and remove February: 12 results and hints return.

Other demonstrations: Rahul → 5 photos; Outdoor Seating → 6; `cafe in Goa snowy` → Drop snowy → 12; `cafe in Goa 2025` → nearest 2024 → 12; `cafe in Goa February 2025` → nearest Nov 2024 → 4. Medicine/medication returns four photos.

All counts come from deterministic metadata matching. WHEN uses adaptive year/month/day buckets; the February hero intentionally reaches four results, below the five-result hint threshold. ALSO suppresses redundant component-word labels when a phrase selects exactly the same photos; word-level search matching and facet scores remain intact. Row order follows scores, so ALSO may appear above WHO.

## Reproducible screenshot URLs

Use the deployed frontend origin in place of localhost. These are real app states, not screenshot-only screens:

| State | URL |
|---|---|
| Home | `/` |
| Broad search / hints | `/search?q=cafe+in+Goa` |
| February refinement | `/search?q=cafe+in+Goa&month=2024-02` |
| Target before success | `/photo/d01?back=%2Fsearch%3Fq%3Dcafe%2Bin%2BGoa%26month%3D2024-02` |
| Target success restored | `/photo/d01?back=%2Fsearch%3Fq%3Dcafe%2Bin%2BGoa%26month%3D2024-02&found=1` |

Interactive refinements serialize the full filters/removals/overrides into the URL, so refresh and viewer return preserve state. The month shortcut above is accepted for presentation convenience. Success is a local acknowledgement, not a persisted participant record.

Five screenshots captured from the local working app are in implementation/screenshots/: 01-gallery.jpg, 02-broad-results.jpg, 03-search-hints.jpg, 04-february-results.jpg, 05-found-photo.jpg. States 2 and 3 show the same valid broad-search state with full-page versus viewport framing.

## Tests and production build

From the repository root:

```sh
backend/.venv/bin/python -m pytest backend/tests -q
npm --prefix frontend test
npm --prefix frontend run typecheck
npm --prefix frontend run build
```

Backend tests verify counts/intersection/chip restoration/aliases/time/recovery/eligibility/bounds/contracts/assets. Frontend tests verify URL state round-trip, screenshot month shorthand and safe viewer return. Browser verification is recorded separately, including mobile and desktop layout. The Node test runner uses native TypeScript stripping, hence Node 22.18+.

To preview a production frontend build while the backend is running:

```sh
cd frontend
npm run build
npm start
```

## API

- GET /api/health → `{ok:true}`.
- GET /api/photos?cursor=&limit=60 → `{items, next_cursor}`.
- GET /api/photos/{id} → photo detail (404 for unknown ids).
- POST /api/search → PRD-shaped concepts/results/hints/drop; sends query, removed_concept_ids, concept_overrides, filters, hints_on and want_drop.

Gallery cursors are the last returned photo id. Media URLs point at the frontend's local assets. No media proxy or mutation/session/export routes are included. Status `tagged` means fixture-ready, not AI-tagged.

## Deploy to Railway and Vercel

Deployed and smoke-tested on 7 October 2026:

- Frontend: https://google-photos-mvp-lake.vercel.app
- Backend health: https://googlephotosmvp-production.up.railway.app/api/health
- GitHub: https://github.com/shreyashf80/GooglePhotosMVP

Railway variables: `CORS_ORIGINS=https://google-photos-mvp-lake.vercel.app`, `DEMO_ASSET_BASE_URL=https://google-photos-mvp-lake.vercel.app`, `PORT=8080`. Vercel Production/Preview uses `NEXT_PUBLIC_API_BASE_URL=https://googlephotosmvp-production.up.railway.app`. Preview origins require their own CORS entry.

Live Chrome smoke passed: 24 loaded gallery images, 12→4 February refinement, d01/success, refresh restoration, chip removal, Rahul→5, outdoor seating→6, snowy drop→12 and nearest 2024→12. Five deployed screenshots are in `implementation/screenshots/deployed/`. The in-app browser blocked Railway requests; Chrome verification succeeded.

Railway currently uses trial credit (dashboard showed 30 days or $5 remaining). Continued hosting after the trial requires the account owner to review its plan. No paid upgrade was made.

For recreating the deployment:

1. Push this project to your chosen Git repository. Do not publish .env files, .venv, node_modules or .next; .gitignore excludes them.
2. Create a Vercel project using that repository, root directory **frontend**, framework **Next.js**, Node **24.x**, build command `npm run build`. Record its production URL. Vercel's supported runtime guidance: https://vercel.com/docs/functions/runtimes/node-js/node-js-versions.
3. Create a Railway service from the same repository, root directory **backend**. Use start command `uvicorn app.main:app --host 0.0.0.0 --port $PORT`, target port `8080` and health path `/api/health`; requirements.txt, Procfile and .python-version are included. Configure these in the Railway dashboard for new services: its current UI reports Config as Code deprecated and unavailable for new opt-ins. The existing railway.toml is retained as a reference. No database or volume. Generate its public domain. Railway's FastAPI guide: https://docs.railway.com/guides/fastapi.
4. Set Railway variables to the actual frontend origin (no trailing path):
   - `CORS_ORIGINS=https://YOUR-FRONTEND.vercel.app`
   - `DEMO_ASSET_BASE_URL=https://YOUR-FRONTEND.vercel.app`
5. Set Vercel `NEXT_PUBLIC_API_BASE_URL=https://YOUR-BACKEND.up.railway.app` for Production and Preview as appropriate, then redeploy. This variable is compiled into the frontend; changing it requires a new build. Preview origins must be explicitly added to Railway CORS_ORIGINS if testing them.
6. Verify `/api/health`, gallery images, broad search, February narrowing, chip removal, viewer/success, drop and nearest recovery. Inspect console/network requests. Capture the five states from the deployed origin only after this smoke test passes.

Backend env defaults are localhost origins; frontend .env.example contains only the public API base URL. No credentials for Gemini, Groq or Neon belong in this demo's environment. One backend instance is sufficient; startup simply loads the included JSON.

## Images and limitations

Photo credits, source pages, Pexels License links and download/edit details are in frontend/public/demo/SOURCES.md and sources.json. Each viewer's info sheet links its source. The dataset's dates, Goa/Mumbai locations and people names are fictional demonstration metadata, clearly marked in the UI/credits; they are not claims about actual stock-photo subjects. No original patient records are used. Runtime loads only bundled local images and fonts.

This is the submission demo, not the research MVP. Neon, uploads, EXIF, tagging/providers/pools, edit/delete, study sessions/export, WHERE and part-of-day hints remain deferred under DEMO-MVP.md. Viewer swiping is omitted; explicit back navigation works. Queries are deterministic metadata searches, not an AI natural-language service. Found state is local and never logged as a research outcome. Public deployment and live Chrome smoke are verified. Physical-phone tests and mobile-data latency remain unverified.
