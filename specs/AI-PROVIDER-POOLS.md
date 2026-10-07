# Centralized backend AI provider pools

Status: **Specification only; no implementation.** User clarification recorded 6 October 2026. This clarification explicitly supersedes conflicting PRD v3.1 provider/key-selection details; all other PRD behaviour remains authoritative. PRD.md is unchanged.

## Goal and scope

Support the project's four independently quota-bearing Gemini keys and four independently quota-bearing Groq keys through shared backend pools. Both tagging and query parsing use the same selection, health, cooldown, rate-limit and retry/fallback machinery. Do not use OpenAI as a provider, SDK dependency, configuration variable, fallback or optional integration anywhere in this project. The PRD's description of Groq's OpenAI-style image payload denotes a wire format only; it does not authorize an OpenAI service or dependency.

## Configuration and `.env.example` requirements

- `backend/app/config.py` reads `GEMINI_API_KEYS` and `GROQ_API_KEYS` as comma-separated strings, trims entries and ignores empty entries. Accept all configured usable keys, including fewer than four; four is available capacity, not a startup requirement. Deduplicate identical entries so one credential is not counted as separate quota.
- Replace the original singular `GROQ_API_KEY` requirement with plural `GROQ_API_KEYS`. Do not require a singular variable or silently depend on it.
- When implementation is authorized, `backend/.env.example` must contain empty `GEMINI_API_KEYS=` and `GROQ_API_KEYS=` entries with comments explaining comma-separated backend-only keys and separate per-key quotas. No real key, sample secret or account/project identifier belongs in examples.
- Keep existing model defaults, provider priorities, `TAG_BATCH_SIZE=4`, `GROQ_BATCH_SIZE=1`, `GEMINI_RPM=8`, `GROQ_RPM=20` and `QUERY_TIMEOUT_S=4`. RPM limits apply separately to each configured key, not one aggregate provider bucket. These configured allowances are not claims about current vendor free tiers.
- Credentials are supplied later through backend environment variables only; never hardcode, commit, log, return through APIs, store in errors/events, expose to the frontend or include actual values in documentation. Sanitize SDK/provider errors and request headers/payload logging before recording anything; key fingerprints/account identifiers are unnecessary.

## Implementation ownership and architecture

00 owns pool configuration/interfaces and a small shared `backend/app/providers.py` module. This additional backend module is technically necessary to satisfy the user's explicit centralization instruction; it does not change the FastAPI/Neon/single-worker architecture. 02 integrates tagging and 03 integrates text parsing. Do not duplicate pool cursors, per-key buckets, cooldown state, retry schedules or fallback policy in tagging.py/search.py. Provider SDK clients, response/error classification and vision-capability gating belong to this shared backend layer; exact prompts and task-specific JSON validation stay with their task owners.

Maintain one shared pool per provider in the single backend process. Selection/state updates must be concurrency-safe across the tagging worker and query requests. Key/cooldown state is in-process and can rebuild on restart; photos remain persisted and resumable through Neon. No new infrastructure, frontend controls, API endpoints or database fields are required.

## Round-robin selection

Each pool holds all configured keys and a cursor. For every actual outbound attempt, scan cyclically from the cursor, skip keys in cooldown, unusable keys and keys without available per-key rate allowance, choose the next healthy usable key, consume its allowance, and advance the cursor past it. Normal traffic therefore spreads across healthy keys rather than exhausting one first. Retries use the same selector and can pick a different healthy key within the same provider. Query cache hits/local parsing consume no provider key.

A single-key failure does not disable a provider. Permanent credential/configuration errors may mark that particular key unusable, with only sanitized diagnostics; temporary 429 never permanently disables it. Missing/empty pools do not crash startup. A provider is temporarily unavailable for an attempt only when no healthy configured key is currently usable. Capability failure for a selected vision model is separate from key health: rotating keys cannot make an unsupported model support images.

## Temporary 429 and retry rules

On a temporary 429, mark only the affected key unavailable until its cooldown deadline; preserve healthy peers. Respect valid Retry-After (seconds or HTTP-date). When absent/unusable, use the existing 5/10/20-second backoff progression for tagging; when supplied, do not retry that key earlier than Retry-After or the applicable backoff deadline. Another healthy key may be tried immediately; a key's cooldown does not force the whole pool to sleep. Once the deadline expires and rate allowance is available, the key is eligible again automatically. Do not loop indefinitely inside one request or reset cooldowns by alternating modules.

Preserve the existing bounded retry/fallback handling for 500/503, invalid JSON and missing ids: 500/503 backoffs 5/10/20 seconds, invalid JSON retry once, missing ids retry once alone. Pool selection is shared, while tagging-specific validation remains in tagging.py. Existing non-rate-limit failure rules still allow failed after eligible providers exhaust their specified retries. Generic safe error text must never contain a credential or unfiltered SDK exception.

Query parsing preserves the existing 4-second timeout and deterministic fallback. Try other healthy keys/providers only while the query-parsing timeout budget allows; do not wait through tagging's 5/10/20-second cooldowns on an interactive query. When unavailable or out of time, fall back locally. Late/in-flight provider results must not extend the user-facing timeout or suppress local fallback.

## Photo-tagging provider order

1. Gemini pool, using the configured `GEMINI_VISION_MODEL` and exact tagging prompt/payload.
2. Groq pool only if the existing configured `GROQ_VISION_MODEL` supports the required image/vision input. Keep the model default unchanged; verify capability before provider implementation/live use, as the PRD requires. Do not silently select a replacement model.
3. If no eligible vision pool can currently run because keys are missing/cooling/rate-limited or Groq's selected model lacks required vision support, retain/requeue the photo as pending and retry when a usable provider is available, with backoff rather than a busy loop. Keep gallery processing indication. Never fall back to OpenAI or fabricate tags.

Rate-only pool exhaustion is the specific exception to PRD 6.3's generic all-fail→failed rule, consistent with PRD 14. It is now resolved by the user clarification. Unsupported Groq vision fallback is also explicitly a pending/retry case. These exceptions do not convert exhausted malformed JSON or non-rate-limit provider errors into indefinite retries when the PRD otherwise calls for failed.

## Query-parsing provider order

1. Groq pool with `GROQ_TEXT_MODEL`.
2. Gemini pool with `GEMINI_TEXT_MODEL`.
3. Existing local deterministic parser using exact PRD time parsing, stopwords, synonyms and normalization.

Maintain exact parsing prompt, cache behaviour, concept contracts and logging source enum. Key choice never changes the reported provider source. Pool exhaustion is graceful fallback, not an API error exposing provider internals. The existing parse_source transport question (Q4) is unchanged.

## Contracts and edge cases

Pools supply task modules an available client/attempt outcome and retry timing without exposing key values through external APIs. Handle partial configuration, all-empty configuration, concurrent calls, one/all keys cooling, independent provider pools, cooldown expiry, invalid Retry-After, rejected credentials, provider outage and unsupported vision. Do not assume four keys share quota or one provider's failure disables the other. Preserve pending/tagging/tagged/failed schema and stateless search contract.

## Tests and acceptance criteria

Add meaningful pool tests, for example `backend/tests/test_providers.py`, using fake clocks/clients and synthetic fixture values, never actual credentials:

- Parse comma-separated lists, trim/ignore empties/deduplicate; zero/one/four keys work without startup crash.
- Normal calls traverse each healthy key cyclically for both providers; one provider's cursor/quota does not affect the other.
- Per-key token buckets enforce Gemini/Groq configured RPM independently; aggregate traffic does not exhaust one key before selection advances.
- A 429 excludes only its key, advances to a healthy peer, respects seconds/date Retry-After, uses bounded fallback backoff when absent and automatically restores eligibility after expiry.
- All four keys cooling makes only that provider unavailable; task moves to its next eligible provider. No busy loop or immediate retry against a cooling key.
- Tagging with all eligible pools unavailable remains pending and resumes after eligibility returns; unsupported selected Groq vision skips image calls and remains pending when Gemini cannot run.
- Permanent single-key rejection does not disable healthy peers; temporary 429 never causes permanent rejection.
- Concurrent tagging/query calls share health/cooldown/allowance consistently; no duplicated state or rate oversubscription.
- Query pool exhaustion/timeout falls through Groq→Gemini→local within the preserved timeout; time-only/cache-hit paths do not spend keys.
- Existing invalid-JSON/missing-id/non-rate-limit retries, restart recovery and tagged metadata tests still pass.
- Error/API/event/log output and frontend configuration contain no supplied credential values. Dependencies/configuration contain no OpenAI integration.

## Dependencies and definition of done

Read 00, 02, 03, 09 and OPEN-QUESTIONS together with this clarification. No further provider-selection decision is required; actual keys are added later to backend environment settings. Current Groq vision capability/free-tier availability must be checked before live implementation; no such check or API call was performed during this documentation-only update. Record unavailable live verification honestly. Pool tests, task integration and full backend suite must pass before frontend implementation. This file creates no code and changes no implementation status to complete.
