# PRD: Search Hints (MVP prototype)

**Project:** Google Photos, memory-based photo retrieval
**Owner:** Shravani
**Version:** 3.1 (no admin page, upload from the gallery, small demo library, Neon storage, Google Photos UI match)
**Build budget:** 5 to 6 hours, one person, using an AI coding tool
**Frontend:** Next.js (App Router, TypeScript, Tailwind) on Vercel, mobile-first
**Backend:** FastAPI (Python 3.11+) on Railway, stateless
**Database and image storage:** Neon Postgres free tier (photos stored as compressed JPEG bytes)
**AI:** Gemini (free tier, several keys) for photo tagging, Groq (free tier) for fast query parsing, each as fallback for the other
**Library size:** small and curated, 30 to 60 photos. The goal is to **showcase every behaviour clearly, not scale** (section 6.0).

---

## 0. How to use this document with an AI coding tool

Give the AI tool this whole file and say:

> "Build the prototype exactly as specified in this PRD. Follow the repo structure in section 10, the API contract in section 9, the data model in section 8, the algorithms in section 7, the UI spec in section 5 and the build order in section 13. Do not add features listed under Non-goals. Where the PRD gives exact text, prompts, colours or numbers, use them as written. After each build step, run the tests in section 12 before moving on."

Rules for the AI tool:
- Do not invent extra screens, settings or features.
- Do not change hint algorithm thresholds unless a test in section 12 fails because of them.
- Backend config lives in `backend/app/config.py` (read from env vars with defaults). Frontend config lives in `frontend/lib/config.ts`. Never hard-code values elsewhere.
- Never log or return API keys. Never commit `.env` files.
- Match the Google Photos app from the screenshots in `frontend/design-reference/`, except: no Google or Google Photos logo or wordmark (section 5.1).

---

## 1. Summary

When a user searches their photo library with the one detail they are sure of (for example "my cat on couch" or "Kabir"), search often returns dozens to hundreds of look-alikes. Today the user has to guess the missing detail (usually *when*) and retype, or scroll.

**Search Hints** shows, above the results, a few rows of tappable hints built from the results themselves: **When**, **Where**, **Who's in it**, **Also in these photos**. Each hint shows a count and a small thumbnail, so the user **recognizes** the missing detail instead of recalling it. Tapping a hint narrows the results and new hints appear. When results are wrong or empty, a **Not finding it?** row lets the user drop one part of the query at a time, and suggests the nearest time if a year or month they typed has no photos.

The prototype is a mobile web app that looks and behaves like the Google Photos mobile app. The researcher uploads photos through the browser; the backend tags them with a free-tier vision model, the way Google Photos labels photos automatically.

---

## 2. Background and problem

### 2.1 Strategic goal
Increase the percentage of users who successfully retrieve a photo they remember but cannot precisely describe when they start searching.

### 2.2 What research showed (discovery engine + 6 observed search sessions)
| Question | Finding |
|---|---|
| Which photos are hard to find? | Shared moments in crowded categories: one event among many, one of several trips to the same place, one of hundreds of photos of the same person or pet. Photos with visible text, landmarks or a unique name were easy (5 of 6 found in 1 or 2 searches). |
| What do people remember? | Who was there (often by nickname), the occasion, one striking visual detail, why they took it. Event or person remembered exactly: 5 of 6. |
| What have they forgotten? | When (exact date 0 of 6, often off by a year), the place name, the album, the app's word for the thing. |
| How do they search? | They type their strongest cue in 1 or 2 words. It matches hundreds. Then they guess the time ("kabir february", "lonavala 2023", then "2024"), then scroll. 0 of 6 found the photo on the first search; 4 of 6 found it only by scrolling. |
| What helped? | The one time the app showed a time cue (a date chip), the user recognized the year and the photo. Only 1 of 6 recoveries came from something the results showed. |

### 2.3 Problem statement
Users start with the one detail they are sure of, which matches many photos. To narrow it down they must recall the detail they are worst at (usually when, sometimes where or the right word), so they guess or scroll. The library already holds those details for every photo but never offers them.

### 2.4 Hypothesis this MVP tests
If search shows the details that split the current results (time, place, people, other visible things) as recognizable, tappable hints, users will narrow to the target photo by recognition instead of guessing, and more vague searches will end with the photo found, faster.

---

## 3. Target user and scope

**Target user:** frequent users with large libraries built over several years, looking for a shared moment (event, trip, person, pet) that sits among many similar photos, usually 1 to 3 years old, often because someone else is waiting for it.

**In scope**
- One photo library, uploaded from an **Upload button on the Photos (gallery) screen**, with automatic AI tagging and date extraction. There is **no admin page**.
- A Google Photos style gallery, search screen and photo viewer on mobile web.
- Editing a photo's date and adding people names from the viewer's info panel, the way Google Photos does it. Deleting a photo from the viewer.
- Search with hints, drop a detail, nearest time.
- Test mode started from a URL, with hints on or off, a "This is it" action, and an event log downloadable from one URL.

**Out of scope (Non-goals). The AI tool must not build these.**
- Any admin or settings page.
- Login, accounts or OAuth.
- Multiple libraries in the UI (the database keeps a `library_code` column for later, but the app uses one library, `LIBRARY_CODE`).
- Connecting to a real Google Photos account or API.
- Conversational or chat search.
- Teaching the app new words or labels.
- Face recognition or face clustering.
- Photo editing (filters, crop), sharing, albums, favourites, a trash bin. Icons for these may appear to match the real app, but do nothing.
- Video files.
- Embedding models or vector databases.
- Native apps or PWA install. Desktop layouts beyond a centred mobile column.

---

## 4. User stories

1. As a user who typed "my cat on couch" and got 150 photos, I see hints like "Old sofa · 90" and "Kitten · 45" with thumbnails, tap the one I recognize, and get a much smaller set.
2. As a user who typed "kabir 2025" and got nothing, I see "Nothing in 2025. Closest: 2024 · 60" and "Drop 2025 · 400", and tap one instead of guessing again.
3. As a user who typed "green lehenga" and got the wrong photos, I tap "Not finding it?" and see what happens if I drop each word.
4. As a user who tapped a wrong hint, I remove its chip with one tap and get back to the previous results.
5. As the researcher, I tap Upload on the gallery, pick photos from my phone or laptop, and see them appear in the grid and finish processing.
6. As the researcher, I fix a wrong date or add a person's name from a photo's info panel, like in Google Photos.
7. As the researcher, I send a participant a test link with hints on or off, and later download a log of everything they did from one URL.

---

## 5. User experience

### 5.1 Visual style: match the Google Photos app
The user-facing screens (Home, Search, Viewer) must match the current Google Photos mobile app as closely as possible in layout, spacing, sizes, colours, icons, chip styles, grid and motion, so participants behave exactly as they do in the real app.

**Design reference (do this before building the frontend, 15 minutes):** take phone screenshots of the current Google Photos app and save them in `frontend/design-reference/`:
1. `home.png`: the Photos tab, scrolled to show date headers and the grid.
2. `search-empty.png`: the search screen before typing.
3. `search-results.png`: results for any query, showing the suggestion chips row if present.
4. `viewer.png`: one photo open, with the bottom actions visible.
5. `viewer-info.png`: the info panel swiped up.
The AI tool must match these screenshots pixel-for-pixel where possible (measure spacing from them) and use the tokens below only where the screenshots don't decide. New elements that don't exist in the real app (hint rows, "Not finding it?", drop row) must use the same chip and text styles as the real app's suggestion chips, so they look native.

**Only exceptions to an exact copy:** no Google or Google Photos logo and no "Google Photos" wordmark (use a neutral placeholder where the logo sits, for example a grey circle, or leave it out), and no account avatar photo (use a plain initial circle). This keeps the prototype from being mistaken for the real app if its link is shared, and changes nothing about how participants search.

**Default tokens (used where screenshots don't decide):**

| Token | Value |
|---|---|
| App name in UI | none |
| Font | `Google Sans Flex` if available on Google Fonts at build time (it is open-licensed); otherwise `Roboto`. Load via `next/font/google`, weights 400 and 500 |
| Icons | Material Symbols Outlined (Google Fonts, free), via `<link>` or `material-symbols` npm package |
| Background | `#FFFFFF` |
| Primary text | `#1F1F1F` |
| Secondary text | `#444746` |
| Primary / links / active nav | `#0B57D0` |
| Search bar surface | `#F0F4F9`, height 48 px, fully rounded |
| Chip | height 32 px, radius 8 px, border 1 px `#C4C7C5`, text 14 px 500; selected: bg `#D3E3FD`, no border, text `#041E49` |
| Grid gap | 2 px |
| Section date header | 14 px 500 `#1F1F1F`, padding 16 px left, 12 px top |
| Bottom nav | copy the items, icons and labels in `home.png`; only Photos and the search entry work, other items are visible but do nothing (no navigation, no error) |
| Viewer | full-screen black `#000000`, white icons |

**Layout width:** mobile-first. On screens wider than 480 px, render the app in a centred 430 px column with a light grey `#F1F3F4` page background, so desktop testing still looks like a phone.

### 5.2 Screens

**Two modes, decided by the URL:**
- **Normal mode** (no `session` parameter): everything works, including Upload, edit and delete. Nothing is logged. This is how the researcher sets up the library and demos the feature.
- **Test mode** (`?session={id}` present): Upload, edit and delete are hidden; "This is it" appears in the viewer; every action is logged. All internal links (bottom nav, search pill, grid taps, back arrow) must keep the `session` parameter.

**Starting test mode:** the researcher opens `/start?p={participantId}&hints={on|off}&task={optional text}`. This page calls `POST /api/sessions`, then immediately redirects to `/search?session={id}` (or `/` if `home=1` is also given). The researcher hands the phone over, or sends the resulting link. No page or form is shown on `/start` other than a brief spinner.

**A. Photos (gallery, home), route `/`**
- Top bar as in `home.png`. On the right, an **Upload** icon button (Material Symbol `upload` or `add_photo_alternate`, matching the real app's icon size and colour). Hidden in test mode.
- Tapping Upload opens the device's native picker: `<input type="file" accept="image/*" multiple>` (on phones this offers the gallery and camera). No custom upload screen.
- After picking: a snackbar at the bottom, styled like Google Photos, `Uploading {n} photos…`, then `Processing {n} photos…` while tagging runs, then it disappears. Uploaded photos appear in the grid immediately (at their photo date), each with a small circular spinner in the bottom-right corner until tagged.
- If some fail: snackbar `{k} photos couldn't be processed` with a `Retry` action. A file that is not an image or is over 20 MB: snackbar `{filename} couldn't be uploaded`.
- If any photos have no date: a one-line notice under the top bar, `{k} photos have no date. Open one and tap ⓘ to add it.`, dismissible.
- Grid: all photos, newest first, grouped by day with headers like `Sat, Feb 11, 2024` (photos with no date go under `No date` at the end). 3 columns, square thumbnails, 2 px gap, lazy-loaded images.
- Bottom nav with Photos active. Tap a photo: opens the Viewer.
- Empty library (normal mode): centred text `No photos yet` and a filled button `Upload photos` that opens the picker.
- While tagging is pending, the gallery polls `GET /api/status` every 5 s and refreshes spinners.

**B. Search, route `/search`**
```
┌─────────────────────────────────────┐
│ ←  [ cat on couch            ✕ ]    │  search bar (autofocus when empty)
│ [cat ✕] [couch ✕] [2023 ✕]          │  active chips row (horizontal scroll)
│ 48 photos            Not finding it? │
├─────────────────────────────────────┤
│ WHEN                                 │
│ (◉ 2022 · 20) (◉ 2023 · 18) (◉ …)   │  hint chips, horizontal scroll
│ WHERE                                │
│ (◉ Living room · 30) (◉ Balcony · 12)│
│ ALSO IN THESE PHOTOS                 │
│ (◉ Blanket · 14) (◉ Kitten · 9)      │
├─────────────────────────────────────┤
│ ▢ ▢ ▢   results grid, 3 columns      │
│ ▢ ▢ ▢                                 │
└─────────────────────────────────────┘
```
- Empty state before searching: the search bar and the text `Search the way you remember it` with example chips `my cat on couch`, `beach sunset`, `birthday cake` that fill the search box when tapped (they are examples only; they do not count as hints).
- Hint chip: 24 px circular thumbnail on the left, then label `{value} · {count}`. Rows scroll horizontally; the row label sits above the chips, 12 px 500, uppercase, letter-spacing 0.5 px, `#444746`.
- Submit on Enter or the keyboard's search key. Show a thin indeterminate progress bar under the search bar while waiting.
- Results grid: same as home, no date headers, newest first, show 60 then load 60 more on scroll.

**C. Viewer, route `/photo/{id}`**
- Layout as in `viewer.png`: full-screen photo (contain) on black, back arrow top-left, top-right icons as in the real app. Swipe left or right moves to the next or previous photo in the list the user came from (gallery order or search results).
- Bottom action bar as in `viewer.png`. Only **Delete** works (normal mode only): confirm dialog `Delete this photo?` with `Cancel` and `Delete`; then return to the previous screen. Other icons are visual only.
- **Info panel** (swipe up or tap ⓘ, as in `viewer-info.png`): date and time, place (city if known, else setting), and the AI caption shown as the description. In normal mode:
  - A pencil next to the date opens a native date-time input; saving sets `date_source = "manual"` and re-sorts the photo.
  - A `People` row with `Add name` chips: type a name, press Enter to add, ✕ to remove. Saves to `people_names`. This stands in for Google Photos' face tagging.
- **Test mode only:** a bottom button `This is it` (filled, `#0B57D0`, white text) above the action bar. Tapping it logs `found`, shows a snackbar `Thanks! You found it in mm:ss`, and disables the button.

**D. Log download (no page):** the researcher opens `{API}/api/export?key={EXPORT_KEY}` in a browser to download all sessions' events as one JSONL file. Optional `&session={id}` downloads one session.

### 5.3 Behaviour rules on the Search screen
| Situation | What the user sees |
|---|---|
| Results N ≥ 5 (`HINT_MIN_RESULTS`) and hints on | Up to 3 hint rows, then results. |
| Results 2 to 4 | Results only; "Not finding it?" link visible. |
| Results 0 to 1 | "Not finding it?" row shown automatically above results. |
| Tap "Not finding it?" | The drop row appears regardless of N. |
| Tap a hint chip | It becomes an active chip; results and hints recompute; that value never appears again as a hint. |
| Tap ✕ on an active chip | That concept or filter is removed; everything recomputes. |
| Tap ✕ in the search bar | Clears the query, chips and results. |
| Test mode with hints off | No hint rows and no drop row; search and results work the same. |
| Normal mode (no session) | Hints are on; nothing is logged; no "This is it" button. |

### 5.4 Exact UI copy
- Search placeholder: `Search your photos`
- Empty search screen: `Search the way you remember it`
- Results count: `{N} photos` / `1 photo`
- Row labels: `WHEN`, `WHERE`, `WHO'S IN IT`, `ALSO IN THESE PHOTOS`
- Hint chip: `{value} · {count}`
- Link: `Not finding it?`
- Drop row label: `NOT FINDING IT? TRY`
- Drop chip: `Drop {concept label} · {count}`
- Nearest time chip: `Nothing in {requested}. Closest: {bucket label} · {count}`
- No results and no drop options: `No photos match. Try fewer words, or something you can see in the photo.`
- Only stopwords typed: `Type something you remember about the photo.`
- Search error: `Something went wrong. Try again.`
- Found: `Thanks! You found it in {mm:ss}`

---

## 6. Photo ingestion and tagging (backend)

### 6.0 Demo library recipe (small, curated, shows every behaviour)
With few photos, hints only appear if the library is built so searches return several look-alikes. Upload **30 to 60 photos** chosen to create these patterns, then fix any wrong dates from each photo's info panel so the time spread is real:

| Pattern | Photos | Shows |
|---|---|---|
| One pet (or object) in the same spot across 3 different years or homes, for example the cat on a couch | 10 to 14 | **When** hints (years), **Where** hints (two rooms or homes), **Also in** hints (blanket, kitten, toy) |
| One person across 3 or 4 events in different months | 8 to 12 | **When** at month level, **Who** hint (set names in the People field), event-based **Also in** hints |
| Two trips or outings with similar scenery (beach, hills) | 8 to 10 | **Where** hints (two cities if GPS exists, else settings), drop a detail |
| Several photos from one single day (a party or wedding) | 5 to 8 | **When** at part-of-day level (afternoon vs evening) |
| A few distinctive photos (a receipt, a landmark, a sign with text) | 3 to 5 | Contrast: these are found in one search, no hints needed |

Then pre-test these demo queries and keep the ones that show the behaviour cleanly:
`my cat on couch` (several hint rows), `{person name}` (Who and When), `beach` (Where), `{person name} 2025` where no 2025 photos exist (nearest time), `cat on bed with red blanket` (drop a detail).

### 6.1 Upload
`POST /api/photos` (multipart, field `files`, many files). Called by the gallery's Upload button. Rejected with 403 when the request carries a session id (test mode), and with 409 once the library holds `MAX_PHOTOS_PER_LIBRARY` photos.
For each file:
1. Reject if not an image by content (Pillow fails to open) or > 20 MB. HEIC/HEIF opened via `pillow-heif` (register opener at startup).
2. `id` = UUID4 hex, first 12 characters.
3. Read metadata from the **original bytes** (6.2) before any resizing.
4. Apply EXIF orientation (`ImageOps.exif_transpose`), convert to RGB, encode and store **in Neon** (table `photo_images`, section 8):
   - `full`: longest side 1280 px, JPEG quality 80 (about 150 to 300 KB).
   - `thumb`: longest side 400 px, JPEG quality 75 (about 25 to 40 KB).
   - The original is not kept. At 60 photos this uses roughly 20 MB of Neon's free 0.5 GB.
5. Insert DB row with `tag_status = "pending"`.
6. Enqueue for tagging (6.3).
Response: list of `{id, original_filename, taken_at, date_source, tag_status}`.

### 6.2 Date and place rules
**Date (`taken_at`, ISO 8601, no timezone)**, first that succeeds:
1. EXIF `DateTimeOriginal` (36867), else `DateTimeDigitized` (36868), else `DateTime` (306). Format `YYYY:MM:DD HH:MM:SS`. `date_source = "exif"`.
2. Original filename patterns (first match wins), `date_source = "filename"`:
   - WhatsApp `IMG-20240115-WA0001.jpg`: `(20\d{2})(\d{2})(\d{2})-WA`
   - `IMG_20240115_183045.jpg`, `PXL_20240115_183045123.jpg`: `(20\d{2})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})`
   - `Screenshot_20240115-183045.png`, `Screenshot 2024-01-15 at 18.30.45.png`, `photo_2024-01-15_18-30-45.jpg`: `(20\d{2})-?(\d{2})-?(\d{2})`
   - Validate month 1 to 12, day 1 to 31.
3. Otherwise `taken_at = null`, `date_source = "none"`. (Browser uploads have no reliable file times, so there is no mtime fallback.)
4. The date can be edited from the viewer's info panel; `date_source = "manual"`.

**GPS:** EXIF GPS IFD to decimal degrees, else null. **City:** if GPS exists and the optional `reverse_geocoder` package is installed, the nearest city name; else null. Never call an online geocoder.

**Important for the researcher:** phone browsers sometimes strip metadata on upload. If dates come back as `none`, either upload from a laptop (files downloaded from Google Photos web keep their EXIF date) or set dates from each photo's info panel. The gallery shows a notice when any photo has no date.

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

## 7. Search and hint logic (backend, `search.py` and `hints.py`)

All computed in memory per request from the library's tagged photos (load metadata from Neon, never the image bytes; cache per library in process memory, invalidate on upload, edit or tag). Only photos with `tag_status = "tagged"` are searchable. Target: under 300 ms per request, excluding the query-parsing call.

**Small-library thresholds:** this MVP runs on 30 to 60 photos, so thresholds are set low enough that hints appear on small result sets. All are env vars and can be raised for larger libraries later.

### 7.1 Query parsing
Input: query string. Output: list of **concepts** `{id, label, synonyms[], kind}` where `kind` is `"thing"` or `"time"`; `id` is a short stable slug of the label.

1. **Time concepts (local regex, no AI):**
   - Month name or 3-letter abbreviation with an optional adjacent year → `{kind:"time", label:"Feb 2024", month:2, year:2024}` or `{label:"February", month:2, year:null}`.
   - Standalone year `\b(19|20)\d{2}\b` → `{kind:"time", label:"2024", year:2024}`.
   - Remove matched text from the query.
2. **Stopwords removed** (`STOPWORDS`): `my, me, our, the, a, an, on, at, in, with, of, and, photo, photos, picture, pictures, pic, pics, image, images, that, this, from, when, was, were, i, we, us, some, find, show`.
3. **Thing concepts:** call the query parser (provider order `QUERY_PROVIDERS = "groq,gemini"`, Groq model `GROQ_TEXT_MODEL` default `llama-3.1-8b-instant`, Gemini model `GEMINI_TEXT_MODEL` default `gemini-2.5-flash-lite`), timeout `QUERY_TIMEOUT_S` = 4 s, JSON output. Cache results by lowercase query in memory. On any failure, fall back to: one concept per remaining word, synonyms = the word plus entries from `SYNONYMS`.

**Exact query prompt:**
```
Turn this photo search into concepts. Return JSON only:
{"concepts":[{"label":"...","synonyms":["...","..."]}]}
Rules: one concept per distinct thing the user mentioned (object, animal, person name, place, event, colour, activity).
"label" is the user's word. "synonyms" has 2 to 6 everyday words a photo label might use for the same thing, singular, lowercase, including the label itself.
Do not add concepts the user did not mention. Ignore filler words.
Search: "{query}"
```
Example: `"my cat on couch"` → `cat: [cat, kitten, kitty]`, `couch: [couch, sofa, settee]`.

**`SYNONYMS` (fallback, keep small):** `couch↔sofa, cat↔kitten, dog↔puppy, kid↔child, baby↔infant, beach↔sea, food↔meal, cake↔dessert, car↔vehicle, mountain↔hill, wedding↔marriage, party↔celebration, mom↔mother, dad↔father`.

### 7.2 Matching
- A photo matches a **thing** concept if any normalised synonym equals any tag, or appears as a whole word in the normalised caption.
- A photo matches a **time** concept if `taken_at` has that year (and month, if given; a month with no year matches that month in any year). Photos with `taken_at = null` never match time concepts.
- **Results** = photos matching **all** concepts **and** all active filters.
- Sort: `taken_at` descending, nulls last, ties by id.

### 7.3 Active filters
Added by tapping hints; sent by the client on every search request (the server is stateless).
- `when` filters: `{facet:"when", level:"year"|"month"|"day"|"part_of_day", label, start, end}` with ISO `start` inclusive and `end` exclusive; part-of-day filters also carry `date` and the hour range. A photo passes if `taken_at` falls in the range. The filter keeps its own level even if later rows use a finer level.
- Other filters: `{facet, value}`. Single-valued facets: equal value. Multi-valued facets (`also`, `who` with names): value is in the photo's list.

Query concepts and filters are shown together as removable chips, in the order added.

### 7.4 Hint facets
Computed on the current results (size N), only when hints are on and N ≥ `HINT_MIN_RESULTS` (5).

| Facet | Row label | Value per photo (`None` = excluded from counts) |
|---|---|---|
| `when` | WHEN | Adaptive time bucket (below) |
| `where` | WHERE | `city` if at least 2 different cities appear among results; otherwise `setting` |
| `who` | WHO'S IN IT | If any result has `people_names`: each name (multi-valued). Otherwise `people_count` bucket: `0 → "No people"`, `1 → "1 person"`, `2-4 → "2 to 4 people"`, `5+ → "5 or more people"` |
| `also` | ALSO IN THESE PHOTOS | Each tag (multi-valued), excluding synonyms of query concepts, values already used as filters, the photo's `setting`, `city`, names, and event values `everyday` and `other` |

**Adaptive time bucket:** the coarsest level that gives at least 2 buckets each with ≥ `MIN_VALUE_COUNT` photos: **year** (`2023`) → **month** (`Feb 2024`) → **day** (`11 Feb 2024`) → **part of day** (`Morning` 05:00-11:59, `Afternoon` 12:00-16:59, `Evening` 17:00-20:59, `Night` 21:00-04:59). Chosen fresh for each request.

**Eligible values:** count `c ≥ MIN_VALUE_COUNT` (default 1 for the small demo library; set 2 for larger libraries) and `c ≤ MAX_ELIGIBLE_SHARE × N` (0.85). A value present in every result is never eligible.

**Facet score:**
- Single-valued facets (`when`, `where`, `who` without names): `coverage = sum(c)/N`; `balance = entropy(c/sum(c)) / ln(k)` with k eligible values (0 if k < 2); `score = coverage × balance`.
- Multi-valued facets: choose up to 4 eligible values with counts closest to N/2; `score = mean(1 − |c − N/2| / (N/2))`; 0 if fewer than 2 chosen.

**Rows shown:** facets with `score ≥ MIN_FACET_SCORE` (0.25), highest first, max `MAX_HINT_ROWS` (3). Tie-break: when, where, who, also.
**Values per row:** max `MAX_VALUES_PER_ROW` (4). `when`: the 4 eligible buckets with the highest counts, displayed chronologically. Others: highest count first.
**Thumbnail per value:** among photos with that value, the one at the median `taken_at` (nulls last), fallback lowest id.

### 7.5 Not finding it? (drop a detail and nearest time)
Returned when N ≤ `DROP_ROW_MAX_RESULTS` (1) or when the client sends `want_drop: true`.
1. For each query concept and each active filter, the result count with that item removed (others kept). Include only if count > N. Order by count descending, max 4.
2. **Nearest time:** if a time concept exists and results with it are 0, take results without it, group them at the granularity the user typed (year; month+year; or month in any year), and offer the bucket nearest in time to the request (ties: earlier). It goes first. Tapping it replaces the time concept with that bucket.
3. If nothing has count > 0, the client shows the "No photos match" copy.

---

## 8. Data model (Neon Postgres, `DATABASE_URL`)

Use `psycopg` (v3) with a small connection pool (`psycopg_pool`, max 5). Create tables on startup if they don't exist. Use the Neon **pooled** connection string with `sslmode=require`. Types below are Postgres: `TEXT` for ids and ISO timestamps, `JSONB` for JSON fields, `BYTEA` for images, `SERIAL` for the events id.

```sql
CREATE TABLE libraries (
  code TEXT PRIMARY KEY,            -- lowercase letters, digits, dash; 2 to 24 chars
  name TEXT NOT NULL,
  created_at TEXT NOT NULL
);
CREATE TABLE photos (
  id TEXT PRIMARY KEY,
  library_code TEXT NOT NULL REFERENCES libraries(code) ON DELETE CASCADE,
  original_filename TEXT,
  taken_at TEXT,                    -- ISO 8601 or NULL
  date_source TEXT NOT NULL,        -- exif | filename | manual | none
  lat REAL, lon REAL, city TEXT,
  width INTEGER, height INTEGER,
  tag_status TEXT NOT NULL,         -- pending | tagging | tagged | failed
  tag_error TEXT,
  tag_provider TEXT,                -- gemini | groq
  ai_json JSONB,                    -- the tagging object
  people_names JSONB DEFAULT '[]',
  tags JSONB DEFAULT '[]',
  created_at TEXT NOT NULL
);
CREATE INDEX idx_photos_lib ON photos(library_code, tag_status);
CREATE TABLE photo_images (
  photo_id TEXT PRIMARY KEY REFERENCES photos(id) ON DELETE CASCADE,
  thumb BYTEA NOT NULL,             -- JPEG, longest side 400
  full_img BYTEA NOT NULL           -- JPEG, longest side 1280
);
CREATE TABLE sessions (
  id TEXT PRIMARY KEY,              -- 8-char random
  library_code TEXT NOT NULL REFERENCES libraries(code) ON DELETE CASCADE,
  participant TEXT NOT NULL,
  task TEXT NOT NULL,
  hints_on INTEGER NOT NULL,        -- 0 or 1
  created_at TEXT NOT NULL,
  started_at TEXT,                  -- set by the first event
  found_at TEXT
);
CREATE TABLE events (
  id SERIAL PRIMARY KEY,
  session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
  ts TEXT NOT NULL,
  event TEXT NOT NULL,
  data JSONB NOT NULL
);
```
Image bytes live in their own table so search queries never load them.

**Event types and `data`:**
| event | data |
|---|---|
| `task_start` | `{}` (sent once when the session page first loads) |
| `search` | `{query, concepts:[labels], n_results, parse_source:"groq"|"gemini"|"fallback"}` |
| `hints_shown` | `{rows:[{facet, values:[{value,count}]}]}`, only when rows change |
| `hint_tap` | `{facet, value, count, n_before, n_after}` |
| `drop_shown` | `{options:[{label,count}]}` |
| `drop_tap` | `{removed, kind, n_before, n_after}` |
| `chip_remove` | `{removed, n_before, n_after}` |
| `not_finding_tap` | `{n_results}` |
| `open_photo` | `{id, position_in_results}` |
| `found` | `{id, seconds_since_start, searches, hint_taps, drop_taps}` |

Export format: JSONL, one event per line, with `session_id, participant, task, hints_on, ts, event, data`.

---

## 9. API contract (FastAPI, prefix `/api`)

All endpoints work on the single library `LIBRARY_CODE` (created on startup if missing). The frontend sends header `X-Session-Id` on every request while in test mode; write endpoints (upload, edit, delete, retry) return 403 when that header is present. There is no other auth: keep links private (see 11.4).

| Method and path | Request | Response |
|---|---|---|
| `GET /api/health` | | `{ok:true}` |
| `POST /api/photos` | multipart `files[]` | `[{id, original_filename, taken_at, date_source, tag_status, error?}]` |
| `GET /api/status` | | `{total, tagged, pending, tagging, failed, no_date}` |
| `POST /api/retry-failed` | | `{requeued}` |
| `GET /api/photos?cursor=&limit=60` | | `{items:[PhotoCard], next_cursor}` sorted by taken_at desc, nulls last |
| `GET /api/photos/{id}` | | `PhotoDetail` |
| `PATCH /api/photos/{id}` | `{taken_at?, people_names?}` | `PhotoDetail` (recomputes tags, invalidates the search cache) |
| `DELETE /api/photos/{id}` | | `{ok:true}` |
| `POST /api/search` | `SearchRequest` | `SearchResponse` |
| `POST /api/sessions` | `{participant, task, hints_on}` | `{id}` |
| `GET /api/sessions/{id}` | | `{id, task, hints_on}` |
| `POST /api/sessions/{id}/events` | `{event, data, ts}` | `{ok:true}` |
| `GET /api/export?key={EXPORT_KEY}&session={id?}` | | `application/x-ndjson` download; 401 if the key is wrong |
| `GET /media/thumbs/{id}.jpg`, `/media/full/{id}.jpg` | none | | JPEG read from `photo_images`, `Content-Type: image/jpeg`, `Cache-Control: public, max-age=604800, immutable` (ids never change, so browsers and Vercel cache them and Neon is hit once per image) |

**Types (JSON):**
```
PhotoCard   = {id, thumb_url, taken_at, tag_status}
PhotoDetail = {id, full_url, thumb_url, taken_at, date_source, city, setting, caption, people_names, tag_status}
SearchRequest = {
  query: string,
  removed_concept_ids: string[],   // concepts the user removed with ✕ or drop
  concept_overrides: Concept[],    // e.g. nearest-time replacement
  filters: Filter[],
  hints_on: boolean,
  want_drop: boolean
}
SearchResponse = {
  concepts: Concept[],             // active concepts after removals and overrides
  n_results: number,
  results: PhotoCard[],            // ALL results (max 100, small objects); client renders 60 at a time
  hints: HintRow[],
  drop: DropOption[],
  untagged_count: number,          // photos in the library not yet tagged
  message: string | null           // e.g. only-stopwords copy
}
Concept    = {id, label, kind:"thing"|"time", synonyms: string[], year?: number, month?: number}
Filter     = {facet:"when", level:"year"|"month"|"day"|"part_of_day", label, start, end, date?}
           | {facet:"where"|"who"|"also", value, label}
HintRow    = {facet, label, values: {label, count, thumb_url, filter: Filter}[]}
DropOption = {kind:"drop"|"nearest", label, count, action: DropAction}
DropAction = {type:"remove_concept", concept_id}
           | {type:"remove_filter", index}
           | {type:"replace_concept", concept_id, with: Concept}
```

**Client flow (stateless server):**
- New query typed: send `{query, removed_concept_ids:[], concept_overrides:[], filters:[], hints_on, want_drop:false}`.
- Hint tapped: append that value's `filter` to `filters` and resend.
- Chip ✕ on a concept: add its id to `removed_concept_ids` and resend. Chip ✕ on a filter: remove it from `filters` and resend.
- Drop option tapped: apply its `action` the same way (`replace_concept` goes into `concept_overrides`) and resend.
- "Not finding it?" tapped: resend with `want_drop:true`.
`thumb_url` and `full_url` are absolute URLs built from env `PUBLIC_BASE_URL`.
**CORS:** allow origins from env `CORS_ORIGINS` (comma-separated, for example the Vercel URL and `http://localhost:3000`).

---

## 10. Repo structure

```
search-hints/
  README.md
  backend/
    app/
      main.py            FastAPI app, routers, startup (DB init, worker start, HEIF opener)
      config.py          env vars with defaults (section 11)
      db.py              Neon Postgres pool (psycopg), schema creation
      models.py          Pydantic request/response models
      ingest.py          upload handling, resizing, metadata (6.1, 6.2)
      tagging.py         worker, providers, prompt, rate limits, validation (6.3, 6.4)
      tags.py            normalisation and tag building (6.5)
      search.py          query parsing, matching, drop and nearest time (7.1, 7.2, 7.5)
      hints.py           facets, buckets, scoring (7.3, 7.4)
      sessions.py        sessions, events, export
    tests/
      test_dates.py  test_tags.py  test_search.py  test_hints.py
      fixtures/mini_library.json   (20 to 40 hand-written tagged photos, no images)
    requirements.txt     fastapi, uvicorn[standard], python-multipart, pillow, pillow-heif,
                         psycopg[binary], psycopg_pool, google-genai, groq, python-dotenv,
                         pytest, httpx
                         (optional, commented: reverse_geocoder)
    Procfile             web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    .env.example
  frontend/
    design-reference/    Google Photos screenshots (5.1), used only while building
    app/
      layout.tsx         font, mobile column wrapper, Material Symbols link
      page.tsx           Photos gallery (with Upload button)
      search/page.tsx    Search screen
      photo/[id]/page.tsx  Viewer
      start/page.tsx     creates a test session and redirects (no UI)
    components/
      SearchBar.tsx  ActiveChips.tsx  HintRow.tsx  HintChip.tsx  DropRow.tsx
      PhotoGrid.tsx  BottomNav.tsx  Snackbar.tsx  InfoSheet.tsx  UploadButton.tsx
      PeopleEditor.tsx  DateEditor.tsx  ConfirmDialog.tsx
    lib/
      api.ts             typed fetch wrappers for every endpoint
      config.ts          NEXT_PUBLIC_API_URL
      session.ts         reads ?session=, adds X-Session-Id header, sends events, counters, timer
      types.ts           mirrors section 9 types
    tailwind.config.ts   colour tokens from 5.1
    .env.example         NEXT_PUBLIC_API_URL=
```

---

## 11. Configuration and deployment

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

### 11.2 Local run
```
cd backend && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && cp .env.example .env   (fill keys and the Neon DATABASE_URL)
uvicorn app.main:app --reload --port 8000
cd ../frontend && npm install && cp .env.example .env.local   (NEXT_PUBLIC_API_URL=http://localhost:8000)
npm run dev
```

### 11.3 Deploy
- **Neon:** create a project (free tier), copy the **pooled** connection string into `DATABASE_URL`. Use a separate Neon branch for local testing so test data never mixes with the demo library.
- **Railway (backend):** new service from the `backend/` folder, start command from `Procfile`. No volume is needed, because all data lives in Neon. Run **one instance only** (the tagging worker runs in-process). Set all env vars; `PUBLIC_BASE_URL` = the Railway public URL; `CORS_ORIGINS` = the Vercel URL.
- **Vercel (frontend):** import the repo with root directory `frontend/`; set `NEXT_PUBLIC_API_URL` to the Railway URL.
- **Smoke test after deploy:** `/api/health` returns ok; on a phone, tap Upload on the gallery and add 5 photos; spinners clear; a search returns them; `/start?p=TEST&hints=on` opens test mode; `/api/export?key=...` downloads its events.

### 11.4 Privacy
- Photos are stored in Neon and sent as small thumbnails to Gemini or Groq for tagging. Free tiers may use data to improve the providers' products.
- If participants upload their own photos, read them: "Small copies of your photos will be sent to Google Gemini or Groq to generate short descriptions, and stored on a private test server. They are deleted after the study." Do not upload without a yes. Delete their photos after the session.
- There is no login: anyone with the app link can upload, edit or delete in normal mode. Do not share the link publicly; share only `/start` test links, which lock those actions. The 100-photo cap limits abuse.

---

## 12. Acceptance criteria and tests

### 12.1 Backend unit tests (must pass before building the frontend)
**Dates (`test_dates.py`)**
- `IMG-20240115-WA0001.jpg` → 2024-01-15, source `filename`.
- `PXL_20231203_183045123.jpg` → 2023-12-03 18:30:45.
- `Screenshot 2024-01-15 at 18.30.45.png` → 2024-01-15.
- `IMG_20241345_000000.jpg` (month 13) → no match, `none`.
- An image with EXIF `DateTimeOriginal` uses it over the filename.

**Tags (`test_tags.py`)**
- `"Christmas Trees"` → contains `christmas tree`, `christmas`, `tree`.
- `"glass"` stays `glass`; `"cats"` → `cat`.

**Search (`test_search.py`, fixture, query parser in fallback mode)**
- `"my cat on couch"` → concepts `cat`, `couch`; a photo tagged `kitten` and `sofa` matches.
- `"kabir 2025"` → one thing concept, one time concept (year 2025).
- `"kabir 2025"` with 0 results while Kabir photos exist in 2024 and 2023 → nearest-time option `2024`.
- `"kabir feb 2025"` with 0 results while Kabir photos exist in Nov 2024 and Mar 2023 → nearest-time option `Nov 2024`.
- Drop options never show a count ≤ current N.
- Removing a concept via `removed_concept_ids` restores the earlier count exactly.

**Hints (`test_hints.py`)**
- 40 results all in 2023 across 4 months → `when` uses month buckets.
- 30 results on one day → `when` uses part-of-day buckets.
- A tag on 100% of results never appears in `also`.
- With `MIN_VALUE_COUNT = 2`, a value with count 1 never appears; with the default 1, it can.
- N = 4 → no hint rows; N = 5 with two distinct years → a `when` row appears.
- Demo fixture: 12 "cat on couch" photos across 2022, 2023 and 2024, in two rooms, 4 with a blanket → the query `my cat on couch` returns `when`, `where` and `also` rows.
- At most 3 rows, at most 4 values each.
- A value used as an active filter never appears again.
- A `when` filter at year level still applies after rows switch to month level.

### 12.2 Manual acceptance checks
1. On a phone browser (Chrome Android or Safari iOS), Home and Search look like the Google Photos app: search pill, 3-column grid with 2 px gaps, date headers, bottom nav, chip styling per 5.1.
2. Tapping Upload on the gallery opens the phone's photo picker; 30 photos upload from a phone and from a laptop; spinners clear as tagging finishes; editing a date in the info panel moves the photo in the grid; adding a name in People makes it searchable.
3. A broad search shows at least one hint row with thumbnails; tapping a hint shrinks results and adds a chip; ✕ restores the previous count.
4. A query with a wrong year shows the nearest-time chip.
5. `/start?p=P1&hints=off` opens test mode: no hint rows, no drop row, and no Upload, edit or delete anywhere.
6. In test mode, "This is it" logs `found`; `/api/export?key=...` downloads JSONL containing every action in order.
7. After the first query-parsing call, each hint tap updates in under 1 s on mobile data.
8. Redeploying the backend keeps photos and sessions (all data is in Neon).
9. Side by side with the real Google Photos app on the same phone, Home, Search and Viewer are hard to tell apart, except for the missing logo.
10. Every demo query from 6.0 shows the behaviour it is meant to show.

---

## 13. Build order (5 to 6 hours)

| Step | Time | Output | Done when |
|---|---|---|---|
| 1 | 30 min | Backend skeleton: config, DB schema, health, default library created on startup | `/api/health` ok locally |
| 2 | 45 min | Upload, resizing, dates, media routes | `test_dates.py` passes; uploaded thumbs load in the browser |
| 3 | 45 min | Tagging worker with Gemini, Groq fallback, retries | 20 photos reach `tagged`; killing the server mid-run and restarting resumes |
| 4 | 60 min | `search.py`, `hints.py`, search endpoint, fixture tests | All unit tests pass |
| 5 | 75 min | Frontend: layout, gallery grid with Upload button and snackbars, Search screen with chips, hint rows, drop row, Viewer with info panel | Manual checks 1 to 4 pass locally on a phone-sized window |
| 6 | 30 min | `/start` test mode, write-locking, event logging, export URL | Manual checks 5 and 6 pass |
| 7 | 30 min | Deploy Railway and Vercel (Neon already set up), upload the demo library (6.0), smoke test | Manual checks 7 to 10 pass |

**Cut list if time runs short (in this order):** city lookup, `who` facet and the People editor, part-of-day buckets, swipe between photos in the viewer, Delete in the viewer. Never cut: Upload button, date editing, hints, drop a detail, nearest time, test mode and logging.

---

## 14. Edge cases

| Case | Required behaviour |
|---|---|
| Photo has no date | Excluded from `when` counts and time matching; shown in results last and under "No date" on Home. |
| Mobile upload strips EXIF | Dates show `none`; the gallery shows the no-date notice (5.2 A); fix from the info panel. |
| HEIC file | Converted via pillow-heif; if conversion fails, that file gets the "couldn't be uploaded" snackbar. |
| Corrupt or non-image file | Rejected with the "couldn't be uploaded" snackbar; others continue. |
| Upload interrupted (screen locked, network drop) | Files already received are kept; the snackbar shows how many succeeded; the user can upload the rest again. |
| Tagging provider returns invalid JSON | Retry once, then the next provider, then `failed`. |
| All providers rate-limited | Photos stay `pending` with spinners; worker keeps retrying with backoff; snackbar stays on `Processing…`. |
| Someone opens the app link (not a test link) and deletes photos | Accepted risk for a prototype; keep the main link private; re-upload from the laptop folder if needed. |
| Search while some photos untagged | Only tagged photos are searched; Search screen shows a small grey note `{k} photos are still being processed` if k > 0. |
| Query parser fails or times out | Use local fallback; log `parse_source: "fallback"`. |
| Only stopwords typed | Show the copy from 5.4; no request results. |
| All results identical on every facet | No hint rows; "Not finding it?" link still shown. |
| Library over 100 photos | Upload rejected beyond the limit with a clear message. |
| Neon cold start (free tier sleeps when idle) | First request may take 1 to 3 s; frontend shows the progress bar and retries once on timeout. Open the app once before a demo to wake it. |
| Session link opened twice | Same session; `task_start` only logged if `started_at` is empty. |
| "This is it" tapped twice | Second tap ignored. |
| Railway redeploy | Nothing lost: data and images live in Neon; in-memory caches rebuild on first request. |
| Duplicate uploads | Allowed; no de-duplication. |

---

## 15. Test plan with participants

**Library setup:**
- **Now (this MVP): shared demo library** built from the recipe in 6.0. Before each task, show the participant the target photo for 5 seconds, then hide it and wait 2 minutes (talk about something else), so they search from a fading memory, not a fresh one. Then: "Find the photo you saw." This tests the interaction honestly at small scale.
- **Later: own library.** Each participant uploads their own photos into their own library, with consent. Stronger evidence for real memory; needs more photos and time.

**Task:** "Find the photo you saw. Tell me what you remember as you search." Two target photos per participant (each from a crowded pattern in 6.0), 5 minute cap each.
**Conditions (counterbalanced):** A = session with hints off; B = session with hints on. Each photo gets its own session link.
**Participants:** 6 to 8 frequent Google Photos users.

| Metric | Definition | Primary? |
|---|---|---|
| Found rate | Tasks ending with `found` within 5 minutes | Primary |
| Time to find | `seconds_since_start` at `found` | Primary |
| Searches typed | Count of `search` events | Secondary |
| Recovery after a miss | Of tasks where the first search did not end in `found`, share later found | Secondary |
| Hint use | `hint_tap` and `drop_tap` counts; share of finds where the last action before opening the photo was a hint or drop tap | Secondary |
| Recognition moments | Think-aloud quotes like "oh, that's the one at the old flat" | Qualitative |

**Success bar (fixed before testing):** hints on beats hints off on found rate **and** median time to find, for at least 5 of 8 participants, with no participant calling the hints confusing. If not met, the hypothesis in 2.4 is weakened.

---

## 16. Risks and mitigations

| Risk | Mitigation |
|---|---|
| AI tags miss what users remember | `notable` field in the prompt; drop a detail; log searches with 0 results to see what was missed. |
| Dates lost on mobile upload | Laptop upload recommended; manual date edit; warning banner. |
| Free-tier limits or model names change | All in env vars; two providers with fallback; resumable worker. |
| Small library makes hints look trivial | Curated demo recipe (6.0) built so each hint type has a real choice to make; demo queries pre-tested. |
| Neon free-tier storage or compute limits | Images compressed (about 20 MB for 60 photos); 100-photo cap; images cached a week by browsers. |
| Prototype search weaker than Google Photos | Main comparison is hints on vs off within the same prototype. |
| Participants confused by a look-alike app | It mirrors Google Photos layout so behaviour transfers; brief participants that it is a prototype. |
| Privacy of participant photos | Consent script, private links, delete library after study. |
| Overlap with existing Photos suggestions and Ask Photos | Note in findings; the test isolates result-derived, splitting hints. |

---

## 17. Later (not in MVP)
- Face clustering so `who` works without manual names.
- Learning the user's own words (for example "Didi" means Pooja).
- Hints inside one crowded moment by sub-scene.
- Real integration through Google's picker or on-device inside the app.

---

## 18. PRD review log

| # | Gap found | Fix |
|---|---|---|
| 1 | v1 required exporting and indexing a local folder | Browser upload with server-side processing (6.1) |
| 2 | v1 ran in Streamlit on a laptop, not testable on a phone | Next.js mobile-first web on Vercel, FastAPI on Railway (5, 11.3) |
| 3 | "Looks like Google Photos" could lead to copying brand assets | Material 3 look with Roboto and Material Symbols; explicit no-logo, no-name rule (5.1) |
| 4 | Railway's filesystem resets on redeploy | Volume at `/data` required; persistence is an acceptance check (11.3, 12.2) |
| 5 | Mobile browsers can strip EXIF, killing the `when` hint | Filename fallback, manual date edit, warning banner, laptop upload advice (6.2, 14) |
| 6 | No mtime available from browser uploads | Removed mtime fallback; `none` plus manual fix (6.2) |
| 7 | One provider's free tier can stall tagging | Gemini key rotation plus Groq fallback, per-provider rate limits (6.3) |
| 8 | Groq vision accepts few images per request | Separate `GROQ_BATCH_SIZE = 1` (6.3) |
| 9 | Query parsing latency on mobile | Groq text model first, 4 s timeout, cache, local fallback (7.1) |
| 10 | Names never match since AI cannot know them | Optional People editor in the viewer's info panel, standing in for face groups (6.6) |
| 11 | Server state for chips would break with multiple tabs | Stateless search: client sends concepts removed, overrides and filters each time (9) |
| 12 | Tagging in a separate service adds deploy work | In-process asyncio worker, resumes on restart (6.3) |
| 13 | Participant tests need separate libraries and conditions | Libraries and session links with hints on or off (5.2 D, 8, 9) |
| 14 | Untagged photos would silently be missing from search | Only tagged photos searched, with a visible "still processing" note (14) |
| 15 | Shared demo library tests interaction, not memory | Two setup options with results reported separately (15) |
| 16 | Build could overrun | Time-boxed steps and a cut list with must-keeps (13) |
| 17 | Hint rules, time filters, nearest time, logging and tests carried over from v1 review | Kept unchanged in 7, 8 and 12 |
| 18 | Drop action and Filter types were loosely written, inviting guesswork | Exact `Concept`, `Filter`, `HintRow`, `DropOption`, `DropAction` types and a client flow (9) |
| 19 | Paging by ids would need the client to build image URLs | Server returns all results as PhotoCards; client renders 60 at a time (9) |
| 20 | Session context could be lost when navigating between screens | `lib` and `session` params preserved on every link; missing-lib message (5.2) |
| 21 | With 30 to 60 photos, the old thresholds (12 results, count ≥ 2) would hide hints entirely | Thresholds lowered and moved to env: `HINT_MIN_RESULTS = 5`, `MIN_VALUE_COUNT = 1`, `DROP_ROW_MAX_RESULTS = 1` (7) |
| 22 | A random small library would not show the behaviours | Demo library recipe and pre-tested demo queries (6.0) |
| 23 | Railway's filesystem resets and the volume step added setup | All data and images in Neon (`photo_images` as BYTEA, kept out of search queries), long cache headers (8, 9, 11.3) |
| 24 | "Exact Google Photos UI" is vague for an AI tool | Screenshot-based design reference with pixel matching; tokens only as defaults; logo and wordmark as the only exceptions (5.1) |
| 25 | Neon free tier sleeps and the first request is slow | Retry once, progress bar, warm-up before demos (14) |
| 26 | Owner asked for no admin page | Upload button on the gallery using the native picker; date and people editing in the viewer's info panel (as in Google Photos); delete in the viewer; test mode via `/start` link; log download via one URL (5.2, 9) |
| 27 | Without an admin page, participants could upload or delete during tests | Test mode hides write actions and the backend rejects writes carrying a session id (5.2, 9) |
| 28 | Multiple libraries need a selector, which would need an admin page | One library (`LIBRARY_CODE`); the column stays for later (3, 9) |

Final check against the strategic goal: every feature exists to turn a crowded, wrong or empty first search into a found photo through recognition (hints) or one-step correction (drop a detail and nearest time). Nothing in scope improves search in general, and the primary metric, found rate, is the strategic goal measured at task level.
