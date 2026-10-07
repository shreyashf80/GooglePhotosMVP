# Demo MVP implementation status

Updated: 7 October 2026. Scope: DEMO-MVP.md and the user's demo implementation instructions only. Full research specifications and implementation/STATUS.md remain unchanged.

| Demo milestone | Status | Evidence |
|---|---|---|
| Read demo/full PRD/AGENTS and inspect five references | Complete | Source documents read; all five JPEGs inspected |
| 24-photo curated library and local assets | Verified | 24 unique ids/files, JPEG signatures, source/attribution manifest |
| FastAPI contracts and deterministic search | Verified | Backend pytest suite passes |
| WHEN / WHO / ALSO and active filters | Verified | API tests plus browser 12→4, Rahul→5, outdoor seating→6 |
| Chip removal/restoration | Verified | Browser February remove restores 12 |
| Drop-query and nearest-year/month recovery | Verified | API tests; browser snowy-drop and year-replacement journeys |
| Gallery/search/viewer/local success | Verified | Browser hero, viewer info/source, disabled success action |
| URL restoration and reproducible states | Verified | Frontend tests plus browser narrowed/found refresh and short month URL |
| Frontend strict TypeScript and production build | Verified | npm run typecheck; production build succeeds |
| Five screenshot artifacts | Captured locally and deployed | implementation/screenshots/01–05 JPEGs and deployed/01–05 JPEGs |
| Railway/Vercel deployment configuration | Prepared | Procfile/railway.toml/.python-version, vercel.json/env examples, README steps |
| Public deployment and deployed smoke | Verified | Vercel production + Railway; live Chrome hero/refinement/recovery/success tested |
| Physical phone/Safari/mobile data checks | Not verified | Browser viewport verification is not a real-device test |

Automated evidence: 15 backend tests and 4 frontend URL-state tests pass. Backend currently emits a upstream Starlette TestClient/httpx deprecation warning; it does not fail tests or affect the running demo. Frontend uses no provider/database SDKs.

Browser evidence: 430 × 932 mobile viewport; actual input submit, February selection, refresh, target d01 open, This is it, found refresh, info/source, back to narrowed results, chip removal, Rahul and outdoor-seating hints, wrong-year nearest and snowy drop. No browser error/warning logs during these flows. Production runtime smoke also passed using next start: Home, broad search, February refinement and d01/success. At 1440 × 900, the application column measured 430 px wide and centered (left 505 px), with no horizontal document overflow. All five primary screenshots were recaptured from this production frontend; 06-desktop.jpg records desktop layout.

Demo-only refinements/deviations: local assets under public/demo-photos per the user's latest instruction; full February labels for recognition; ALSO display removes a compound phrase's redundant component labels when their photo sets are identical, without changing matching or score computation; Christmas normalization preserves the PRD's explicit test example. No research scope has been cut from the full specifications.

README includes exact local commands, screenshot URLs, source credits and hosting settings. No runtime or deployment secrets have been added. No AI/provider call, upload workflow, database, background worker or production study event/export implementation exists in this demo.

Deployment evidence (7 October 2026): frontend https://google-photos-mvp-lake.vercel.app, backend https://googlephotosmvp-production.up.railway.app. API health returned `{ok:true}`. API response confirmed exact production CORS origin and frontend asset URLs. Chrome at 430 × 932 verified 24/24 images loaded, broad 12, February 4, d01 success, refresh, return/chip removal, Rahul 5, outdoor seating 6, snowy-drop 12 and nearest-year 12. Captured five live states under screenshots/deployed/. No Chrome warning/error logs were captured. Temporary viewport override was reset. In-app browser verification failed because it blocked Railway requests; system Chrome worked.

Railway root /backend, Python 3.11, start command from Procfile/dashboard, public target port 8080. Vercel root frontend, Next.js, public API URL set for Production/Preview. Railway has only CORS_ORIGINS, DEMO_ASSET_BASE_URL and PORT user variables. No paid upgrade or deferred infrastructure was added. Railway dashboard showed trial availability of 30 days or $5; continued hosting depends on the account plan. Config as Code is deprecated for new services in the current Railway UI, so root/start/port settings were applied through the dashboard.
