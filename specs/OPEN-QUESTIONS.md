# PRD contradictions, ambiguities and implementation blockers

Q1 and Q2 are resolved by user clarifications recorded below; Q3–Q4 and the other gaps remain unchanged. PRD remains authoritative except for the explicitly authorized AI-provider/key-selection changes; its text has not been changed. Pause only the affected implementation when a genuine contradiction requires a decision; unaffected foundation/algorithm work can proceed once implementation is authorized.

## Decisions to settle before affected implementation

### Q1 — Visual priority (05–07): resolved

**User decision, 6 October 2026:** PRD.md is authoritative for product structure, functionality and behaviour. The five screenshots in `frontend/design-reference/` guide visual appearance: typography, spacing, surfaces, iconography, navigation treatment, photo viewer appearance, proportions and overall Google Photos visual feel. Screenshots guide how PRD-defined elements look; they do not redefine functionality. If a screenshot conflicts with an explicit PRD requirement, the PRD wins, including explicit colour/style requirements.

**Application:** Use the PRD-required three-column gallery grid, not the screenshot's five columns. Build the PRD-defined Search screen and Search Hints experience, not conversational/Ask Photos search. Preserve active chips, result count, hint rows, `Not finding it?`, drop behaviour and all specified search interactions. Use screenshot visual treatments only where compatible with explicit PRD requirements.

**Status:** Resolved; no replacement screenshots or further visual-priority decision are prerequisites for implementation. This records visual guidance only and does not authorize application implementation. Q3–Q4 remain open.

### Q2 — Pool exhaustion and tagging fallback: resolved

**User clarification, 6 October 2026:** Use shared backend pools for all configured Gemini/Groq keys (four independently quota-bearing keys available per provider). Normal attempts use healthy-key round-robin; temporary 429 affects only its key, respects Retry-After, tries healthy peers and restores eligibility after cooldown. Missing individual keys do not crash the app. A provider is temporarily unavailable only when no healthy configured key is usable.

**Resolved tagging rule:** Gemini pool → existing selected Groq pool only if the configured model supports required vision input → pending/retry when eligible vision pools cannot currently run. All keys cooling/rate-limited is not failed. Keep existing invalid-JSON/non-rate-limit failure rules and retries. Query parsing is Groq pool → Gemini pool → existing local deterministic parser within the preserved timeout. No OpenAI anywhere.

**Explicit PRD differences:** Replace singular GROQ_API_KEY with comma-separated GROQ_API_KEYS; centralize both provider pools and shared state in providers.py; interpret RPM per key; gate Groq vision fallback by capability; temporary pool exhaustion/missing keys or unavailable vision fallback retains pending work instead of generic all-fail→failed. These are authorized clarifications, not unresolved conflicts. PRD.md stays unchanged; verbatim source excerpts are historical where superseded. Other algorithms, prompts, thresholds, UI and API contracts are unchanged.

**Needed:** No further provider-selection decision. Model capability/availability and live keys remain implementation prerequisites, not reasons to change models silently. See [AI-PROVIDER-POOLS.md](AI-PROVIDER-POOLS.md) for configuration, retry details and tests. Q3 (Night filter) and Q4 (logging provenance) remain open.

### Q3 — Night filters and missing hour fields (03–04)

**Evidence:** 7.3 says part-of-day filters also carry date and hour range. Section 9 Filter has start/end/date but no explicit hours. Night in 7.4 is 21:00–04:59; per-calendar-day Night combines 00:00–04:59 and 21:00–23:59, which a single contiguous start/end cannot encode for that calendar day.

**Impact:** The exact filter contract and same-day Night matching are incomplete. An undocumented extra field or a contiguous interval changes contract or results.

**Recommended smallest resolution:** Clarify that `date` identifies the calendar day and specifies the two Night hour intervals, and explicitly define how the existing start/end/label fields encode that rule (or amend the contract with the hour fields already called for in 7.3). Do not choose an arbitrary overnight-day convention.

**Needed:** PRD clarification of Night day membership and wire representation before part-of-day filters are implemented.

### Q4 — Query provenance required for logging but absent from response (03, 08)

**Evidence:** Section 8 requires every search event to carry parse_source (groq/gemini/fallback), but SearchResponse in section 9 does not contain it, and POST events accepts client-supplied data. The client cannot reliably know which backend fallback ran.

**Impact:** Accurate parser provenance cannot be fabricated from current client-visible response. Server-side instrumentation/enrichment is possible but must have clear ownership to avoid duplicate search events.

**Recommended smallest resolution:** Specify that the server enriches the client's search event with parser provenance from the query-parser cache, including time-only/stopword cases; retain the existing response shape. Alternatively explicitly add parse_source to SearchResponse. Agree ownership before implementation rather than silently changing types.

**Needed:** Decision on provenance transport/ownership. The suggested cache enrichment needs semantics for expired/missing entries and queries that never invoked a provider.

## Contract gaps that can be resolved with documented engineering judgment

These do not all require user decisions. Proposed interpretations below are not new requirements and must be recorded/tested when implemented; ask only if a conflict remains.

| Gap | PRD evidence | Smallest reasonable interpretation / work to document |
|---|---|---|
| Multipart field name | 6.1 says field `files`; 9 says multipart `files[]` | Treat `files[]` as notation for repeated `files` parts unless literal bracket spelling is intended; use one canonical name in API/client/tests and document it. |
| Per-file upload errors | 6.1 response omits error; 9 includes optional error but failed inputs have no persisted id/date/status | Successful records have exact required fields; explicitly define failure-item null/omitted fields and safe filename/error representation. Preserve sibling success and UI error copy. Do not invent persisted failed-upload photos. |
| Interrupted upload accounting | 14 requires success count though interrupted request may never return its response | Use existing gallery/status refresh and upload request granularity to account for received files; no new endpoint or de-duplication. Document how count is reconciled. |
| Crossing capacity within batch | 6.1/14 require 409 at/beyond 100 but do not define partial acceptance boundary | Enforce cap even under concurrent uploads and never exceed it; document whether a too-large batch is rejected before ingestion or accepts remaining slots, without discarding previous uploads. |
| Month-only nearest distance | 7.5 mentions month in any year, no distance metric/anchor | Document deterministic month-distance and bucket grouping convention, with earlier tie-break preserved. If annual wrap-around vs calendar ordering changes intended nearest result, ask before that case. |
| Replacement identity | Concept has id; DropAction replace has original concept_id and replacement with.id | Keep replaced concept trackable by the original id so later remove/override works; test repeat override/removal. Do not create duplicate active concepts. |
| Hint event value | 8 uses value for hints_shown/hint_tap; 9 HintRow values expose label/filter, not value | Derive categorical value from filter.value and time value from filter.label; document the event mapping without changing HintRow. |
| Empty/only-time provenance | 7.1 parser is for things; 8 source enum has no local-time value | Clarify under Q4; never claim groq/gemini if no provider was called. |
| Tie rules not supplied | 7.4 specifies row tie priority, not equal-count values/even median thumbnail ties | Use stable label/id order for incidental ties; do not change given row priorities or chronological time display. |
| Gallery cursor and request failures | 9 supplies cursor but no format; error statuses for nonexistent ids/invalid bodies unspecified | Choose stable opaque cursor and conventional safe validation/not-found errors; no new user-facing feature. |
| Invalid/reopened session | 14 defines resulting session link twice, /start itself creates a new session; invalid-id UI unspecified | Reopening `?session=id` resumes; opening /start creates a new session. Hide writes whenever session parameter exists; handle missing session safely without silently falling into normal mode. |
| Timer/counter restoration | 8 has persisted events/times; session GET lacks started_at/counters | Keep navigation context client-side; define restoration on full reload without altering GET response. Persisted backend duplicate guards remain necessary. |
| Search progress/cold timeout | 14 requires once-only timeout retry without specifying frontend timeout duration | Choose/document a timeout compatible with 1–3-second cold start and 4-second parser; retry once, not indefinitely. |
| Date header example | 5.2 gives Sat, Feb 11, 2024, but that date is Sunday | Format the actual calendar weekday; example illustrates format, not a mandated incorrect weekday. |

## Apparent conflicts resolved by the current PRD

- **Railway volume:** section 18 review-log #4 still says /data volume; #23 and operative sections 8/11.3 say Neon BYTEA/no volume. Use Neon and no volume; no decision needed.
- **lib parameter/multiple libraries:** historical #13/#20 mention separate libraries, lib propagation and missing-lib message. Operative sections 3/9 and #28 fix one LIBRARY_CODE and require session propagation; no selector, lib routing or missing-lib screen.
- **Threshold changes:** section 0 loosely allows changes if a test fails because of thresholds; AGENTS 5 explicitly disallows altering thresholds merely to pass. Keep prescribed defaults and fix implementation/fixture, not tests/thresholds.
- **People optional/cut list:** 6.6 calls People optional, but scope and 12.2 require it. Include WHO/People until an authorized cut, following section 13 order.
- **also demo fixture:** section 12 specifies four blanket photos but a multi-valued row needs at least two eligible values. Add another PRD-compatible distinctive tag to the 20–40-photo hand-written fixture; no scoring change is needed.
- **Screenshot .png names:** existing .jpeg counterparts are all present and inspected; do not rename or request them again merely for extension.

## External prerequisites, not decisions needed to create specs

- Neon pooled SSL connection string and a separate local-test branch for live DB checks.
- Four independent-quota Gemini keys and four independent-quota Groq keys are available; actual secrets will later be supplied through backend-only comma-separated GEMINI_API_KEYS and GROQ_API_KEYS. Fewer configured keys must work without startup failure. Check current models/free-tier limits in AI Studio/Groq before provider implementation, as 6.3 requires. Availability was not verified during this documentation-only task; model defaults are unchanged in specs.
- Railway/Vercel account authorization and deployment approval after local verification. No deployment attempted here.
- Curated 30–60-photo library, researcher date/name preparation, phone/laptop access and mobile data for manual criteria. No demo photos were provided or uploaded.
- Git/version-control setup: this directory is not currently a Git repository. Decide repository destination when deployment preparation needs it; do not create/publish one during this task.
- Own-photo consent/deletion procedures only if later study uses personal photos; present MVP uses the shared demo library. No multiple-library feature is implied.

No credential values should be put into this document or chat. Use local environment files or deployment secret settings when required. Unrelated foundation work does not need to wait for account/deployment access.
