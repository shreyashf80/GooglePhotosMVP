# Demo MVP implementation status

Updated: 6 October 2026. Scope: DEMO-MVP.md and the user's demo implementation instructions only. Full research specifications and implementation/STATUS.md remain unchanged.

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
| Five screenshot artifacts | Captured locally | implementation/screenshots/01–05 JPEGs; not deployed captures |
| Railway/Vercel deployment configuration | Prepared | Procfile/railway.toml/.python-version, vercel.json/env examples, README steps |
| Public deployment and deployed smoke | Not verified | Requires hosting/repository access and authorization |
| Physical phone/Safari/mobile data checks | Not verified | Browser viewport verification is not a real-device test |

Automated evidence: 15 backend tests and 4 frontend URL-state tests pass. Backend currently emits a upstream Starlette TestClient/httpx deprecation warning; it does not fail tests or affect the running demo. Frontend uses no provider/database SDKs.

Browser evidence: 430 × 932 mobile viewport; actual input submit, February selection, refresh, target d01 open, This is it, found refresh, info/source, back to narrowed results, chip removal, Rahul and outdoor-seating hints, wrong-year nearest and snowy drop. No browser error/warning logs during these flows. Production runtime smoke also passed using next start: Home, broad search, February refinement and d01/success. At 1440 × 900, the application column measured 430 px wide and centered (left 505 px), with no horizontal document overflow. All five primary screenshots were recaptured from this production frontend; 06-desktop.jpg records desktop layout.

Demo-only refinements/deviations: local assets under public/demo-photos per the user's latest instruction; full February labels for recognition; ALSO display removes a compound phrase's redundant component labels when their photo sets are identical, without changing matching or score computation; Christmas normalization preserves the PRD's explicit test example. No research scope has been cut from the full specifications.

README includes exact local commands, screenshot URLs, source credits and hosting settings. No runtime or deployment secrets have been added. No AI/provider call, upload workflow, database, background worker or production study event/export implementation exists in this demo.
