# Search Hints implementation status

Updated: 6 October 2026.

**Current authorization:** specification creation only. Application implementation is intentionally stopped. PRD.md and AGENTS.md read completely; all five design references inspected; ten phase specs and supporting analysis created. No application source, schema, dependency installation, tests, build, AI call or deployment has been implemented/run.

Source of truth: [PRD.md](../PRD.md). Plan: [specs/README.md](../specs/README.md). Decisions/gaps: [OPEN-QUESTIONS.md](../specs/OPEN-QUESTIONS.md).

## Recorded visual-priority decision

Q1 is resolved: PRD.md governs product structure, functionality, behaviour and explicit colour/style requirements. The five screenshots guide compatible typography, spacing, surfaces, iconography, navigation treatment, viewer appearance, proportions and Google Photos visual feel. Keep the PRD three-column grid and Search Hints interactions; do not implement screenshot conversational search. No replacement references are required. Other questions remain unchanged; all implementation phases remain Not started.

## Recorded AI-provider clarification

Centralized backend Gemini/Groq pools use comma-separated GEMINI_API_KEYS and GROQ_API_KEYS, healthy-key round-robin, per-key quotas, temporary 429 cooldown/Retry-After and recovery. Tagging: Gemini → vision-capable selected Groq → pending/retry when no eligible vision pool can run. Parsing: Groq → Gemini → deterministic local parser. No OpenAI integration. Q2 is resolved; Q3/Q4 remain open. PRD unchanged; no application code, real keys or .env files added. See [AI-PROVIDER-POOLS.md](../specs/AI-PROVIDER-POOLS.md) for full tests and configuration requirements.

## Phases

| Phase | PRD step | Implementation status | Verification status |
|---|---|---|---|
| [00-foundation](../specs/00-foundation.md) | 1 | Not started | Not run |
| [01-photo-ingestion](../specs/01-photo-ingestion.md) | 2 | Not started | Not run |
| [02-ai-tagging](../specs/02-ai-tagging.md) | 3 | Not started; provider-pool clarification resolved | Not run |
| [03-search-engine](../specs/03-search-engine.md) | 4a | Not started; affected contract gaps recorded | Not run |
| [04-hint-engine](../specs/04-hint-engine.md) | 4b | Not started; part-of-day decision pending | Not run |
| [05-gallery-ui](../specs/05-gallery-ui.md) | 5a | Not started; visual priority resolved | Not run |
| [06-search-ui](../specs/06-search-ui.md) | 5b | Not started; visual priority resolved | Not run |
| [07-photo-viewer](../specs/07-photo-viewer.md) | 5c | Not started; visual priority resolved | Not run |
| [08-test-mode-logging](../specs/08-test-mode-logging.md) | 6 | Not started; provenance decision pending | Not run |
| [09-deployment](../specs/09-deployment.md) | 7 | Not started; credentials/authorization later | Not run |

## Verification gates

- [ ] Step 1: Neon schema/default library and local health verified.
- [ ] Step 2: dates suite and browser thumbnails pass.
- [ ] Step 3: tags suite, 20 tagged photos, worker restart resumption verified.
- [ ] Step 4: entire backend suite passes before frontend implementation.
- [ ] Step 5: frontend build/runtime and local manual checks 1–4 pass.
- [ ] Step 6: on/off session locks/logging/export and manual checks 5–6 pass.
- [ ] Step 7: local integration, deployment configuration/secrets review, authorized deployment and smoke pass.
- [ ] Final: manual checks 7–10, criterion-by-criterion acceptance, README and honest final report complete.

## Acceptance evidence ledger

| Criterion | State | Evidence |
|---|---|---|
| 12.1 dates | Not run | No implementation |
| 12.1 tags | Not run | No implementation |
| 12.1 search | Not run | No implementation |
| 12.1 hints | Not run | No implementation |
| 12.2 #1 phone Home/Search | Not verified | Requires implementation/device; visual priority resolved |
| 12.2 #2 30 uploads, date/name edits | Not verified | Requires implementation/photos/phone/laptop |
| 12.2 #3 hints/chips/count restoration | Not verified | Requires implementation |
| 12.2 #4 nearest-time chip | Not verified | Requires implementation |
| 12.2 #5 hints-off test mode | Not verified | Requires implementation |
| 12.2 #6 found and ordered export | Not verified | Requires implementation |
| 12.2 #7 mobile-data latency | Not measured | Requires working app/mobile data |
| 12.2 #8 redeploy persistence | Not verified | Requires deployment authorization/live redeploy |
| 12.2 #9 same-phone visual comparison | Not verified | Requires implementation/device; visual priority resolved |
| 12.2 #10 all demo queries | Not verified | Requires curated library and implementation |

## Updating this file during later authorized implementation

Use Not started → In progress → Implemented, verification pending → Verified. Use Blocked only for an actual prerequisite and name the affected check; continue unaffected work. Record test commands/results and exercised manual flows as evidence. Failed or unavailable checks are not completed checks. No scope cuts or deviations have been approved. Specifications are ready for review, not proof that acceptance criteria pass.
