# AGENTS.md — Search Hints MVP

## 1. Mission

Build the complete Search Hints MVP defined in `PRD.md`.

`PRD.md` is the product and engineering source of truth.

The objective is a working, testable, deployable MVP — not a scaffold, partial implementation, UI mockup, or proof of concept.

Work autonomously through implementation, testing, debugging, integration, and deployment preparation.

Do not stop merely because one feature, layer, or build phase is complete.

Continue until the acceptance criteria in `PRD.md` have been implemented and verified, except for steps that genuinely require human access or action.

---

## 2. Read the PRD First

Before writing or modifying code:

1. Read `PRD.md` completely.
2. Understand the:
   - product hypothesis
   - scope and non-goals
   - normal mode and test mode
   - user flows
   - UI requirements
   - photo ingestion pipeline
   - tagging pipeline
   - search algorithm
   - hint algorithm
   - drop-a-detail behaviour
   - nearest-time behaviour
   - database schema
   - API contract
   - repository structure
   - configuration
   - tests
   - acceptance criteria
   - build order
   - edge cases
   - deployment requirements
3. Inspect the existing repository before creating or changing files.
4. Inspect `frontend/design-reference/` before implementing or visually refining the frontend.

Do not begin implementation based only on a partial reading of the PRD.

---

## 3. Source of Truth

Use this priority order when making decisions:

1. `PRD.md`
2. Reference screenshots in `frontend/design-reference/`
3. Existing automated tests
4. Existing repository architecture and conventions
5. Reasonable engineering judgement

If implementation details are unspecified but the intended product behaviour is clear, make a reasonable engineering decision and continue.

Do not ask the user about trivial engineering decisions.

Ask the user only when information or access is genuinely required and cannot reasonably be inferred.

If something appears contradictory in the PRD, stop only that affected piece of work, explain the contradiction clearly, recommend the smallest reasonable resolution, and continue with unrelated work when possible.

---

## 4. Product Scope Discipline

Build only the MVP described in `PRD.md`.

Do not invent additional:

- screens
- settings
- dashboards
- authentication
- onboarding
- navigation
- AI features
- search modes
- admin interfaces
- analytics dashboards
- photo-management features
- infrastructure
- abstractions

unless they are technically necessary to implement a requirement in the PRD.

In particular, there is no admin page.

Photo upload happens from the Photos/gallery screen as specified in the PRD.

Normal mode is used by the researcher to prepare and manage the demo library.

Test mode is used by participants and must hide or disable researcher-only mutation actions as specified in the PRD.

Do not connect to the real Google Photos API.

Do not add embeddings or a vector database.

Do not implement face recognition.

Do not turn Search Hints into conversational search.

Do not silently expand the MVP.

---

## 5. Preserve Specified Behaviour

Where `PRD.md` specifies exact:

- copy
- labels
- thresholds
- colours
- dimensions
- algorithms
- prompts
- environment variables
- API paths
- request/response shapes
- model/provider order
- retry behaviour
- database fields
- test behaviour

implement them as written.

Do not change product behaviour merely because another implementation seems cleaner.

Do not change hint thresholds simply to make the UI appear to work.

Do not weaken acceptance criteria or tests to make failing code pass.

Fix the implementation instead.

---

## 6. Autonomous Working Style

Work continuously through the PRD build order.

For each phase:

1. Inspect the relevant PRD sections.
2. Implement the smallest complete version.
3. Run the relevant tests.
4. Inspect failures.
5. Fix the implementation.
6. Re-run the tests.
7. Verify the behaviour.
8. Continue to the next phase.

Do not stop after generating code and ask the user whether you should continue.

Do not stop after creating the backend.

Do not stop after creating the frontend.

Do not stop after the first successful test.

Do not repeatedly ask for approval between normal implementation steps.

Proceed autonomously whenever the next action is safe, reversible, and clearly supported by the PRD.

---

## 7. When to Ask the User

Ask the user when progress requires something only the user can reasonably provide or authorize.

Examples include:

- Neon database credentials
- Gemini API keys
- Groq API key
- Vercel authorization
- Railway authorization
- external account login
- deployment approval
- missing design-reference screenshots
- access to an external service
- an irreversible external action
- a genuine product contradiction that cannot safely be resolved from the PRD

When asking:

1. Explain exactly what is needed.
2. Explain why it is needed.
3. Give the user precise steps.
4. State exactly what value, file, credential, or confirmation should be provided afterward.
5. Continue with other work first if that work is not blocked.

Never ask the user to make an engineering decision that can reasonably be made from the PRD.

---

## 8. Secrets and Credentials

Never commit secrets.

Never print secrets into logs.

Never expose secrets in frontend code.

Never put secret values into documentation.

Never hard-code:

- `DATABASE_URL`
- Gemini API keys
- Groq API keys
- `EXPORT_KEY`
- deployment credentials
- other private tokens

Use environment variables exactly as defined by the PRD.

Keep `.env` files out of version control.

Maintain safe `.env.example` files containing placeholders only.

If credentials are required, ask the user for them at the point they are needed.

---

## 9. Backend Standards

Follow the backend architecture specified in `PRD.md`.

Keep responsibilities separated between the modules defined by the repository structure.

Configuration belongs in:

`backend/app/config.py`

Do not scatter configuration constants throughout the application.

Keep search requests stateless as specified in the PRD.

Search and hint computation must operate on metadata rather than loading image bytes.

Invalidate relevant in-memory caches whenever uploads, tagging, date edits, people edits, or deletes make cached search data stale.

Handle external AI provider failures gracefully.

Respect retry, fallback, timeout, and rate-limit behaviour from the PRD.

Never expose API keys in errors.

Prefer simple, readable implementation over unnecessary abstraction.

This is an MVP for a small curated library, not a large-scale production photo platform.

---

## 10. Frontend Standards

Use the frontend stack defined in `PRD.md`.

Configuration belongs in:

`frontend/lib/config.ts`

The frontend is mobile-first.

The intended participant experience should visually resemble the supplied Google Photos reference screenshots while respecting the branding exceptions in the PRD.

Before implementing or visually refining:

- Home/gallery
- Search
- Viewer
- Info panel
- navigation
- chips
- photo grid

inspect the corresponding files in:

`frontend/design-reference/`

Do not invent a generic SaaS design.

New Search Hints elements should visually feel native to the surrounding interface.

Preserve session context across navigation exactly as required by the PRD.

Normal mode and test mode must remain clearly separated in behaviour.

---

## 11. Upload Experience

There is no admin upload workflow.

Implement photo upload from the gallery/Home screen exactly as described in the PRD.

The upload flow must support:

- native device file picker
- multiple images
- immediate appearance in the gallery
- processing/tagging state
- per-photo processing indication
- retry behaviour
- missing-date indication
- HEIC/HEIF handling
- invalid-file handling
- upload limits

Do not create a separate upload page unless technically unavoidable and explicitly justified.

---

## 12. Search and Hints Are the Core

The primary product hypothesis is tested through the Search Hints interaction.

Treat the following as critical functionality:

- query concept parsing
- time parsing
- synonym matching
- result intersection
- active filters
- WHEN hints
- WHERE hints
- WHO'S IN IT hints
- ALSO IN THESE PHOTOS hints
- adaptive time buckets
- facet scoring
- hint eligibility
- hint thumbnails
- active chips
- removing chips
- drop-a-detail
- nearest-time recovery
- hints-on vs hints-off test conditions

Implement these according to the algorithms in the PRD.

Do not replace them with an approximate AI-generated recommendation system.

The deterministic logic described in the PRD is intentional because the MVP is testing a specific product hypothesis.

---

## 13. Testing Discipline

Tests are part of the implementation, not an optional cleanup phase.

Implement and run the backend unit tests specified in the PRD.

At minimum verify:

- date extraction
- filename date parsing
- EXIF precedence
- tag normalization
- singularization
- synonym matching
- time concepts
- nearest-time recovery
- concept removal
- drop options
- adaptive time buckets
- hint eligibility
- facet limits
- active-filter exclusion
- demo fixture behaviour

Run relevant tests after each backend phase.

Before declaring the backend complete, run the entire backend test suite.

Do not delete, skip, weaken, or rewrite a legitimate test merely because it fails.

Diagnose the implementation.

---

## 14. Frontend Verification

After implementing the frontend:

1. Run the frontend locally.
2. Run the production build.
3. Fix TypeScript errors.
4. Fix build errors.
5. Check browser console errors.
6. Check failed network requests.
7. Verify normal mode.
8. Verify test mode.
9. Verify navigation preserves session state.
10. Verify upload and processing states.
11. Verify Search Hints interactions.
12. Verify viewer and info-panel behaviour.
13. Verify responsive behaviour around the mobile target width.

Where practical, compare the rendered UI with the screenshots in `frontend/design-reference/`.

Do not consider a component finished simply because it compiles.

---

## 15. Integration Verification

Verify the application as a complete system.

At minimum test this journey:

Upload photo
→ photo appears in gallery
→ tagging completes
→ photo becomes searchable
→ broad search returns results
→ hints appear
→ tapping a hint narrows results
→ active chip appears
→ removing the chip restores results
→ wrong time query produces nearest-time recovery
→ photo opens in viewer.

Also verify:

Normal mode
→ upload available
→ date editing available
→ people editing available
→ delete available.

Test mode
→ upload hidden/blocked
→ editing hidden/blocked
→ delete hidden/blocked
→ hints respect session condition
→ actions are logged
→ "This is it" records found
→ event export works.

---

## 16. Error Handling

Do not implement only the happy path.

Handle the edge cases specified in `PRD.md`, especially:

- missing EXIF dates
- HEIC/HEIF files
- corrupt images
- oversized files
- interrupted uploads
- failed AI tagging
- provider rate limits
- invalid AI JSON
- query parser timeout/failure
- partially tagged libraries
- zero-result searches
- only-stopword queries
- cold database startup
- duplicate uploads
- repeated session links
- repeated "This is it" taps

User-facing failures should be understandable and should not expose implementation details or secrets.

---

## 17. Dependency Policy

Use established, maintained packages where the PRD calls for them.

Avoid adding large dependencies for trivial functionality.

Before adding a dependency, determine whether the existing stack already solves the problem.

Keep dependency versions compatible with the selected runtime.

Do not replace technologies explicitly selected in the PRD without a genuine technical blocker.

If an external model name or free-tier capability has changed, tell the user before making a material provider change.

Prefer making provider/model differences configurable through environment variables.

---

## 18. Code Quality

Optimize for:

- correctness
- readability
- simplicity
- testability
- clear separation of concerns

Avoid premature optimization.

Avoid unnecessary design patterns.

Avoid building generalized infrastructure for hypothetical future requirements.

Add comments where behaviour is non-obvious, particularly around:

- time parsing
- normalization
- hint scoring
- adaptive buckets
- nearest-time logic
- provider fallback
- session logging

Do not add comments that merely restate obvious code.

---

## 19. Keep the Repository Runnable

Do not leave the repository in a broken intermediate state when avoidable.

Keep setup instructions current.

Update `README.md` as implementation becomes real.

The README should eventually explain:

- project purpose
- architecture
- prerequisites
- environment variables
- local backend setup
- local frontend setup
- how to run tests
- how to upload the demo library
- how normal mode works
- how to create a test session
- how to export logs
- deployment setup
- known MVP limitations

Commands in the README should be tested when practical.

---

## 20. Deployment

Do not deploy until the local application is reasonably verified.

Follow the deployment architecture from the PRD.

Before deployment verify:

- tests pass
- frontend production build passes
- secrets are not committed
- `.env.example` files are complete
- CORS configuration is correct
- public backend URL configuration is correct
- database connection configuration is correct

If deployment requires the user's login, authorization, account creation, payment decision, or credential entry, ask the user at that point.

After deployment, perform the smoke tests specified in the PRD.

Do not assume successful deployment means the application works.

---

## 21. Progress Tracking

Maintain a concise implementation checklist while working.

Use the PRD build phases as the primary milestones.

Suggested states:

- [ ] Backend foundation
- [ ] Database/schema
- [ ] Photo ingestion
- [ ] Image storage/media routes
- [ ] Date extraction
- [ ] AI tagging worker
- [ ] Tag normalization
- [ ] Query parsing
- [ ] Search matching
- [ ] Hint engine
- [ ] Drop-a-detail
- [ ] Nearest-time recovery
- [ ] Backend tests
- [ ] Gallery/Home
- [ ] Gallery upload
- [ ] Search UI
- [ ] Hint UI
- [ ] Viewer
- [ ] Info panel
- [ ] Date editor
- [ ] People editor
- [ ] Test mode
- [ ] Session logging
- [ ] Event export
- [ ] Frontend production build
- [ ] End-to-end verification
- [ ] Deployment configuration
- [ ] Smoke test
- [ ] README
- [ ] Final acceptance review

Do not mark an item complete merely because code exists.

Mark it complete when the relevant behaviour has been verified.

---

## 22. Cut List

If time or external constraints force scope reduction, follow the cut order in `PRD.md`.

Do not independently remove core Search Hints functionality.

Never cut functionality the PRD explicitly identifies as essential unless the user approves the change.

If something must be cut, tell the user:

- what is being cut
- why
- what impact it has
- whether it affects the hypothesis being tested

---

## 23. Definition of Done

The project is not complete merely because:

- files were generated
- the backend starts
- the frontend loads
- tests exist
- one search works
- deployment succeeds

The MVP is complete when, to the extent possible with the available environment:

1. The required PRD scope is implemented.
2. Backend tests pass.
3. Frontend production build passes.
4. Core end-to-end flows work.
5. Search Hints behave according to the PRD.
6. Drop-a-detail works.
7. Nearest-time recovery works.
8. Gallery upload works.
9. Background tagging works.
10. Date editing works.
11. People-name editing works unless intentionally cut according to the PRD.
12. Normal mode behaves correctly.
13. Test mode behaves correctly.
14. Session logging works.
15. Event export works.
16. Required edge cases have been addressed.
17. The application is runnable from documented instructions.
18. The acceptance criteria in `PRD.md` have been reviewed one by one.
19. Any criteria that could not be verified are explicitly identified.
20. No known critical failures are being hidden.

---

## 24. Final Review

Before reporting completion:

1. Re-read the acceptance criteria in `PRD.md`.
2. Compare them against the implementation one by one.
3. Run the complete backend test suite.
4. Run the frontend production build.
5. Check for obvious runtime errors.
6. Check for accidentally committed secrets.
7. Review the main user journeys.
8. Review normal vs test mode.
9. Review the Search Hints algorithms against the PRD.
10. Review README/setup instructions.

Then provide a concise final report containing:

### Implemented
What was completed.

### Tests
What automated tests were run and their results.

### Verified manually
What flows were actually exercised.

### Not verified
Anything requiring external credentials, devices, accounts, or user action.

### Deviations
Any intentional deviation from `PRD.md` and why.

### Remaining issues
Known bugs or limitations.

### Run instructions
Exact commands needed to run the finished MVP.

Do not claim something was tested, deployed, or verified unless it actually was.

---

## 25. Core Principle

The purpose of this MVP is not to build a better general photo search engine.

The purpose is to test whether people who begin with incomplete memories can recover a target photo more successfully by **recognizing useful details from result-derived hints instead of having to recall and guess those details themselves**.

Protect that hypothesis throughout implementation.

When deciding between extra sophistication and faithfully testing the hypothesis, choose the latter.