# Design reference inspection

All five existing JPEG files were visually inspected in full on 6 October 2026. Their filenames differ from the `.png` examples in PRD 5.1; this is a format/naming difference, not a missing-file blocker. Each is 720 × 1600 pixels; screenshot pixels must be interpreted at device scale rather than used blindly as CSS pixels. Status/navigation bars are operating-system chrome, not application screens to recreate.

| Reference | Observed content | Applicable use and conflicts |
|---|---|---|
| [home.jpeg](../frontend/design-reference/home.jpeg) | Dark brown surface, logo/Backup is off/header icons/initial circle, large memories cards, centered month headers, five-column grid; floating Photos/Collections/Create pill and separate search button | Header icon proportions and bottom-nav structure are references. PRD requires no logo, 3-column square grid, day headers and Upload; no memories/videos/backup feature. Dark styling conflicts with explicit white/blue tokens and selected-nav treatment. |
| [search-empty.jpeg](../frontend/design-reference/search-empty.jpeg) | Already-submitted First flight query, Ask Photos-style search badge, thumbs up/down, backup warning, no-match prose, bottom Search or follow up pill | This is not the pre-typing empty state requested by 5.1. No suggestion chips or standard top search pill are visible. Do not copy conversation, feedback or backup behaviour. |
| [search-results.jpeg](../frontend/design-reference/search-results.jpeg) | Moon query, AI prose response, backup warning, isolated result images and November 2021 label, bottom follow-up pill | This is conversational search, not the specified 3-column results with native suggestion chips. It cannot define hint-chip metrics. Written Search Hints layout/copy/behaviour remains authoritative. |
| [viewer.jpeg](../frontend/design-reference/viewer.jpeg) | Black viewer, top back/date/time/star/overflow, contained photo, Share/Edit/Add to/Bin actions | Strong reference for image/action layout. PRD only activates Delete; star/share/image Edit/Add to stay inert. Info tap/swipe and test-mode This is it are specified additions. |
| [viewer-info.jpeg](../frontend/design-reference/viewer-info.jpeg) | Photo above dark rounded sheet, drag handle, date/time and pencil, Add a caption, Albums card, backup/file/camera details, Add a location | Use sheet composition/date pencil styling. PRD content is date/time, city or setting, read-only AI caption and People editor; do not add albums, caption editor, backup details, camera metadata or location editing. |

## Resolved visual priority

User decision recorded on 6 October 2026: PRD.md governs product structure, functionality and behaviour. All five screenshots guide typography, spacing, surfaces, iconography, navigation treatment, photo viewer appearance, proportions and overall Google Photos visual feel. They guide the appearance of PRD-defined elements, not the features or interactions to build.

Where a screenshot conflicts with an explicit PRD requirement, the PRD wins, including colour/style requirements. Use the specified three-column gallery grid and day grouping. Build the PRD Search screen with active chips, result count, hint rows, `Not finding it?`, drop behaviour and specified search interactions; do not substitute the screenshot's conversational/Ask Photos experience.

Native Search Hints rows have no direct equivalent in the supplied screenshots. Use the PRD's explicit chip and hint metrics (32 px chip, 8 px radius, 14 px weight 500, 24 px hint thumbnail and row-label styling), with compatible screenshot typography, spacing and visual treatment. Replacement references are not an implementation prerequisite.

Q1 in OPEN-QUESTIONS is resolved. No existing screenshot or PRD text was altered. Re-inspect the corresponding reference before frontend implementation/refinement; application implementation remains unauthorized in this documentation-only task.
