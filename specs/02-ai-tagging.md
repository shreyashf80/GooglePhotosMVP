# 02-ai-tagging: Resumable tagging and tag normalization

Status: **Not started — specification only.**

Source of truth: [PRD.md](../PRD.md). Repository rules: [AGENTS.md](../AGENTS.md). If this spec or its copied excerpts conflict with the current PRD, the PRD wins except for the explicitly authorized AI-provider clarification recorded below. No application implementation is authorized by the creation of this file.

Read [OPEN-QUESTIONS.md](OPEN-QUESTIONS.md) and [DESIGN-REFERENCE.md](DESIGN-REFERENCE.md) for affected decisions.
## Goal
Turn pending thumbnails into validated searchable metadata with resilient provider fallback. Corresponds to build step 3.

## Requirements
- One startup asyncio worker in FastAPI, oldest pending first, batch size 4; reset interrupted `tagging` records to `pending` at startup.
- Send 400 px thumbnails, Gemini first then Groq, preserving exact prompt, models, SDKs, payload forms, JSON output and temperature from the source excerpts.
- Use centralized Gemini and Groq pools with healthy-key round-robin for normal requests and retries; four independently quota-bearing keys per provider are available, fewer configured keys must work. Per-key token buckets: Gemini 8 RPM/key, Groq 20 RPM/key. Groq batch size 1. Both lists come from comma-separated GEMINI_API_KEYS/GROQ_API_KEYS.
- Centralize selection/cooldowns/retries/fallback in the shared provider layer. A temporary 429 cools only that key, respects Retry-After, tries healthy peers and restores eligibility after cooldown. Preserve the specified 5/10/20 backoffs and non-rate-limit failure rules; never store unfiltered SDK errors or keys.
- Validate arrays and match by id; retry missing ids once alone. Invalid JSON retry once, then next provider. Coerce types exactly as section 6.3 specifies.
- Store AI fields/provider, compute de-duplicated normalized tags, mark tagged and invalidate metadata cache.
- Failed-photo retry returns them to pending through the API. All-rate-limited exhaustion is resolved as pending/retry, not failed. Gemini pool → vision-capable selected Groq pool → pending/retry when no eligible vision pool can run; never use OpenAI.

## Relevant PRD constraints
Sections 6.3–6.6, 7 opening paragraph, 9, 11.1 and 14. Prompts/defaults below are verbatim. Provider names/free-tier limits must be checked before provider implementation; any material provider change needs user notification. Do not guess people/place names.

## Implementation requirements
Implement `tagging.py`, `tags.py` and worker lifecycle in `main.py`, consuming shared `providers.py` from 00. Keep task-specific validation here; do not duplicate key selection, cooldowns, rate limits or fallback machinery. Store state in Neon for restart recovery. Normalize lowercase/trim/collapsed spaces and simple singularization (final s only when length >3 and not ending ss/us); keep phrases and component words. Tags union objects, animals, setting, event, colors, notable, visible_text words length ≥3, people_names and city. Caption/query matching uses the same normalization. Phase 07 adds People editing; support names in tag computation now. No face recognition or embeddings.

## API/data contracts
Implement `POST /api/retry-failed` → `{requeued}`; reject any `X-Session-Id` header with 403. Populate section 8 `ai_json`, `tags`, `tag_provider`, `tag_status`, `tag_error`. Status counts and photo cards from 01 reflect worker progress. The tagging JSON keys and event enum below are exact.

## Edge cases
Provider outage/rate exhaustion, no usable keys, malformed JSON, missing or unexpected ids, wrong scalar/list types, negative people count, unknown event, partial batch success, interrupted worker, failed retry and concurrent people edits. Names must survive retagging. Rate exhaustion lifecycle follows the resolved pool clarification; missing keys/cooling pools or unsupported Groq vision fallback retain pending work without a busy loop.

## Tests
`test_tags.py`: Christmas Trees yields christmas tree/christmas/tree; glass stays glass; cats becomes cat. Verify phrase/word dedup, visible text cutoff and People/city union. Use provider doubles to verify payload, key rotation, limits, backoff, invalid JSON, missing-id retry, fallback, success/failure and restart recovery. Live phase check: 20 photos become tagged; kill/restart mid-run and observe resumption. No provider keys in test output.

## Acceptance criteria
Step 3 succeeds; successful tags conform to exact schema/normalization and become searchable; retries update status correctly; restart does not lose work. Rate-limit behaviour follows AI-PROVIDER-POOLS: healthy peers remain usable, cooling keys recover and pool exhaustion retains pending work. Shared pool tests pass and no OpenAI dependency/configuration/integration exists.

## Dependencies
00–01. Live provider verification requires configured Gemini/Groq key lists and selected Groq vision capability verification. No further provider-selection decision is needed. Provider-double and normalization work can proceed independently.

## Definition of done
Tags tests and provider-state checks pass; 20-photo/restart journey has recorded evidence or is explicitly unverified for missing credentials; README explains processing/retry; STATUS does not mark live checks passed based only on doubles.

## Authorized AI-provider clarification

The user's 6 October 2026 clarification in [AI-PROVIDER-POOLS.md](AI-PROVIDER-POOLS.md) governs provider/key selection where it explicitly differs from PRD v3.1. Both Gemini and Groq use comma-separated backend-only key pools; no OpenAI integration is allowed. PRD remains authoritative for everything else. Copied PRD excerpts below remain verbatim historical source snapshots: their singular GROQ_API_KEY and generic all-fail rule are superseded as described in the clarification.

Tests/acceptance additionally include every relevant shared-pool case in AI-PROVIDER-POOLS: four-key rotation, partial/empty lists, peer retry after 429, Retry-After and cooldown expiry, full pool exhaustion, concurrency across both tasks and credential-safe errors. Tagging verifies Groq vision gating/pending recovery; parsing verifies timeout-bounded provider/local fallback. Normalized tags, prompts, API shapes and matching/hint algorithms remain unchanged.

## Normative PRD excerpts

The following are copied unchanged from PRD v3.1 for implementation context. Re-read the linked source before implementation if it changes.

### 6.3 Tagging worker
- Runs inside the FastAPI process as one background `asyncio` task started at app startup. It loops: take up to `TAG_BATCH_SIZE` (4) pending photos (oldest first), tag them, sleep as needed for rate limits, repeat. On startup, any photo with status `tagging` is reset to `pending`.
- Sends the 400 px thumbnails.
- **Provider order:** `TAG_PROVIDERS = "gemini,groq"`.
  - **Gemini:** SDK `google-genai`. Model `GEMINI_VISION_MODEL` (default `gemini-2.5-flash-lite`). Keys from `GEMINI_API_KEYS` (comma-separated), used round-robin. `contents = [PROMPT, "Photo id: {id1}", <PIL image>, "Photo id: {id2}", <PIL image>, ...]`, `response_mime_type="application/json"`, `temperature=0`.
  - **Groq (fallback):** SDK `groq`. Model `GROQ_VISION_MODEL` (default `meta-llama/llama-4-scout-17b-16e-instruct`). Images sent as base64 data URLs in OpenAI-style `image_url` content parts. Groq vision models accept a limited number of images per request, so batch size for Groq is `GROQ_BATCH_SIZE` (default 1). Ask for a JSON array response.
  - **Check model names and free-tier limits** in Google AI Studio and the Groq console before building; only the env values change.
- **Rate limiting:** a token bucket per provider and key: `GEMINI_RPM` (default 8 per key), `GROQ_RPM` (default 20).
- **Errors:** on 429, 500 or 503 retry the same provider with backoff 5, 10, 20 s, rotating Gemini keys; then switch to the next provider; if all fail, set `tag_status = "failed"` and `tag_error` (short message, never the key). The gallery's `Retry` snackbar action calls `POST /api/retry-failed`, which sets them back to `pending`.
- **Validation:** response must be a JSON array; match objects to photos by `id`; missing ids are retried once alone. Coerce types: strings lowercased and trimmed, lists of strings, `people_count` int ≥ 0, unknown `event` → `"other"`.
- On success: store fields, compute `tags` (6.5), set `tag_status = "tagged"`.

### 6.4 Exact tagging prompt (`PROMPT`)
```
You are labelling personal photos so a person can find them later by what they remember.
For EACH photo below, return one JSON object. Return a JSON array only, no other text.
Each object must have exactly these keys:
{
 "id": the photo id given before the image,
 "caption": one plain sentence, max 20 words, describing what is happening,
 "objects": up to 8 concrete things clearly visible (nouns, singular, e.g. "cat", "sofa", "cake"),
 "animals": animals visible (singular, e.g. "cat", "dog"), [] if none,
 "setting": the place type in 1 to 3 words (e.g. "living room", "beach", "restaurant", "stage", "street"),
 "indoor": true or false,
 "event": one of "wedding", "birthday", "party", "festival", "trip", "meal", "concert", "ceremony", "sport", "work", "school", "everyday", "document", "screenshot", "other",
 "people_count": number of people clearly visible (0 if none),
 "colors": up to 3 dominant colours of the main subject (e.g. "green", "gold"),
 "notable": up to 4 distinctive details someone might remember (e.g. "kitten", "christmas tree", "gold backdrop", "marker moustache"),
 "visible_text": short readable text in the image, "" if none
}
Use simple everyday words. Do not guess names of people or places. Do not mention the photo id in the caption.
```

### 6.5 Tags
`tags` = de-duplicated union of: `objects`, `animals`, `setting`, `event`, `colors`, `notable`, words of `visible_text` with length ≥ 3, `people_names`, and `city`.
Normalisation for every tag, caption word and query word: lowercase, trim, collapse spaces, then simple singular (strip a final `s` if length > 3 and the word does not end in `ss` or `us`). Multi-word tags are kept whole **and** each word is also added.

### 6.6 People names (optional)
AI cannot know names. In the viewer's info panel, the `People` row lets the researcher add names (for example `Kabir`, `Pooja`). Saved to `people_names` and added to `tags`. If no photo has names, the `who` facet falls back to people counts. This takes a few minutes for a demo library and stands in for Google Photos' face groups.

---

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

