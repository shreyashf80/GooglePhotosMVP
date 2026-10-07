# Search Hints implementation specifications

These documents decompose PRD v3.1; they do not authorize application implementation. [PRD.md](../PRD.md) is the product/engineering source of truth and wins over generated specifications except the explicitly authorized provider/key-selection clarification in [AI-PROVIDER-POOLS.md](AI-PROVIDER-POOLS.md). Read it completely together with [AGENTS.md](../AGENTS.md) before implementing. No application code, dependencies or deployment were created during specification work.

## Phase index and dependency order

| Spec | PRD build step | Implementable output | Dependencies |
|---|---|---|---|
| [00-foundation](00-foundation.md) | 1 | Config, schema, library, health, shared models | Neon for live verification |
| [01-photo-ingestion](01-photo-ingestion.md) | 2 | Upload, original metadata, images, gallery/detail/media/status APIs | 00 |
| [02-ai-tagging](02-ai-tagging.md) | 3 | Resumable worker, provider fallback, normalization, retry API | 00–01; provider keys for live verification |
| [03-search-engine](03-search-engine.md) | 4, first part | Parsing, matching, stateless filters, drop and nearest time | 00–02 contracts/normalization |
| [04-hint-engine](04-hint-engine.md) | 4, completion | Facets/buckets/scoring, full search response, complete backend suite | 03 |
| [05-gallery-ui](05-gallery-ui.md) | 5, first part | Shared mobile frontend, gallery/upload/status UI | 00–04 backend gate |
| [06-search-ui](06-search-ui.md) | 5, second part | Search/chips/hints/drop/recovery and result context | 03–05 |
| [07-photo-viewer](07-photo-viewer.md) | 5, completion | Viewer/info/date/People/delete and backend mutation routes | 01–02, 05–06 |
| [08-test-mode-logging](08-test-mode-logging.md) | 6 | Start links, persisted sessions, conditions, events/export | 00, 03, 05–07 |
| [09-deployment](09-deployment.md) | 7 | Integrated verification, hosting, demo preparation, smoke and final review | 00–08 locally verified |

The requested ten boundaries are retained. Steps 4 and 5 are split into adjacent specs without changing PRD order. Shared API models/schema are owned by 00; route behaviour belongs to the phase listed above. Test-mode mutation guards belong to each mutation endpoint from its introduction; 08 connects real sessions and completes lock verification. Date/People PATCH and DELETE belong to 07 because that is their specified UI phase. Fixtures/doubles let each algorithm phase be tested independently; they do not replace required live end-to-end checks.

## Authorized AI-provider clarification

[AI-PROVIDER-POOLS.md](AI-PROVIDER-POOLS.md) specifies centralized Gemini/Groq round-robin key pools, comma-separated backend GEMINI_API_KEYS/GROQ_API_KEYS, cooldowns/Retry-After, vision gating, fallback, secret handling and tests. 00 owns the shared providers.py/configuration; 02 and 03 integrate it; 09 verifies deployment settings. No OpenAI integration is permitted. No application code or .env file is created by this update.

## Execution rules

- Every phase has a goal, requirements, relevant constraints, implementation requirements, API/data contracts, edge cases, tests, acceptance criteria, dependencies and definition of done.
- Exact applicable PRD excerpts are included in each spec. They are snapshots, not a second source of truth. Reconcile with the current PRD before implementation.
- Do not implement non-goals or turn historical review-log entries into features. One library, Neon BYTEA storage, no admin, no chat, no embeddings and no real Google Photos API remain fixed.
- Do not mark work complete because files exist. Record automated and exercised manual evidence in [STATUS.md](../implementation/STATUS.md).
- Entire backend suite must pass before 05. Local app verification precedes deployment. Account access/credentials and actual deployment approval are requested only when needed.
- [OPEN-QUESTIONS.md](OPEN-QUESTIONS.md) identifies conflicts and incomplete contracts. Only affected work needs to pause; no suggested resolution is an approved change to PRD.
- [DESIGN-REFERENCE.md](DESIGN-REFERENCE.md) records all five images inspected and the resolved visual priority: screenshots guide appearance; explicit PRD structure, functionality, behaviour and colour/style requirements win. Q1 and Q2 are resolved; Q3–Q4 remain open. Replacement screenshots are not a prerequisite.
- No scope cuts are approved. Preserve the section 13 cut order if a later authorized reduction becomes necessary.

## Acceptance traceability

| PRD requirement/check | Primary owner | Completion gate |
|---|---|---|
| 12.1 dates: all five specified cases | 01 | Date suite before step 2 complete |
| 12.1 tags: phrase/singular/glass cases | 02 | Tags suite |
| 12.1 search: fallback/synonyms/time/nearest/drop/removal | 03 | Search suite |
| 12.1 hints: all nine specified cases | 04 | Hints suite and full backend gate |
| 12.2 #1 phone Home/Search visual layout | 05–06 | Phone browser and resolved reference comparison |
| 12.2 #2 30 phone/laptop uploads, processing, date and name edits | 01–02, 05, 07 | Actual device/upload/edit journey |
| 12.2 #3 broad hints/thumbs/tap/chip/remove | 04, 06 | API plus browser journey |
| 12.2 #4 wrong year nearest-time chip | 03, 06 | Browser recovery journey |
| 12.2 #5 off-mode hidden hints/drop/mutations | 08 | UI and backend lock checks |
| 12.2 #6 found and all actions exported in order | 08 | Actual journey compared with JSONL |
| 12.2 #7 hint taps <1 second mobile data | 09 | Measured after first parse |
| 12.2 #8 redeploy persists photos/sessions | 09 | Actual redeploy and readback |
| 12.2 #9 same-phone Home/Search/Viewer comparison | 05–07, 09 | Actual comparison under agreed reference guidance |
| 12.2 #10 every demo query's intended behaviour | 09 | Curated library and recorded pre-tests |
| 13 step 3: 20 tagged and restart resumes | 02 | Live tagging/restart |
| 11.3 deployed smoke | 09 | Health, five phone uploads, search, TEST/on, export |
| 14 edge cases | Relevant 01–08 owner; 09 reviews all | Specific checks in each spec plus final integration review |
| 15 research protocol/metrics/success bar | 09 documentation | Preserve protocol; do not claim unrun participant results |
| AGENTS final review, README and secrets | 09; each phase maintains docs | Criterion-by-criterion evidence and final report |

## Repository baseline

Inspected 6 October 2026: PRD.md, AGENTS.md, five JPEG references and incidental .DS_Store files. There is no application source, test suite, package manifest or README to preserve yet. The directory is not a Git repository (`git status` reports that fact); initializing/versioning it is deployment preparation, not completed here. No runtime tests/builds were run because no application exists and this task explicitly excludes implementation.
