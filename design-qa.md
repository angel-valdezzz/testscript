# TestScript folded landing — visual QA

final result: blocked

## Follow-up corrections — 2026-10-08

The owner requested the changes identified in the live-site audit. The README's User Guide now opens Overview without an additional Home link. All 30 built documentation pages have matching English/Spanish destinations, translated section mappings where TOC structure matches, and a shared Material preference scope (`/testscript/`). Spanish theme controls are localized.

The landing now sizes typography and spacing against viewport height, with the baseline outside the text flow and room beneath both actions. Fixed 760px minimum height and 350px text spacer have been removed. The existing folded raster was edited with the built-in image tool so the right reverse face and lower relief retain green continuity. The motion implementation was preserved. Asset dimensions: 1486 × 1059; 37,564 bytes.

Strict bilingual build, all 30 page language destinations/fragment IDs/theme scope, README navigation, 44 language snippets, Ruff and JavaScript syntax checks passed. Local preview remains subject to the previously recorded browser blocker. The independently requested published-site audit is accessible; checks of the published corrections will be recorded after deployment. No active-motion or multi-viewport visual pass is claimed here.

## Intended design

- Source visual truth: second displayed ImageGen option, `exec-ef9abec3-8a8f-49e8-9f76-68900d911119.png` in `/workspace/scratch/2ffb0fc245da/generated_images/`.
- Source dimensions: 1487 × 1058 pixels; desktop landing, no device frame.
- Intentional copy revision authorized by the owner: “Menos ruido. Más intención.” (white/lime) and “Para pruebas automatizadas Web y API, con estructura y claridad.”
- Artwork: `docs/assets/testscript-fold.webp`, 1487 × 1058 pixels, 43,686 bytes. Generated from the selected target with all UI removed, inspected before integration. It is the actual visual asset, not a code approximation.
- Intended state: Spanish landing, fixed dark surface, slow deformation, light response to pointer, normal documentation theme choice preserved.

## Browser evidence and blocker

- The managed preview started successfully.
- The cloud browser could not open the preview: `net::ERR_BLOCKED_BY_CLIENT`.
- Inspecting the resulting tab was then explicitly rejected by browser URL/security policy. No alternate browser, raw protocol, or indirect browser workaround was attempted.
- Browser-rendered implementation screenshot: unavailable.
- Viewport, CSS size, density normalization, same-frame full-view comparison: unavailable.
- Focused typography/layout comparison: blocked, because no implementation capture exists.
- Primary interactions and console errors: not verified in the browser. Their behavior must not be inferred from build success.

## Required fidelity surfaces

- Fonts/typography: large Arial/Helvetica sans heading, explicit white and lime spans, responsive type scale. Visual wrapping and font fidelity still require browser inspection.
- Spacing/layout rhythm: full-height composition, lower-left copy, upper folded artwork, responsive mobile composition. Actual overflow and proportions still require browser inspection.
- Colors/tokens: separate home stylesheet fixes the dark palette independently of the documentation color scheme. Theme persistence and both rendered states still require interaction checks.
- Image quality: standalone generated artwork inspected; the original silhouette, material and palette are retained. Browser crop/scale and WebGL deformation still require visual inspection.
- Copy/content: built English and Spanish headings, approved subtitle and sample-free markup checked. Both README locale selectors precede their separate documentation links.

## Verification completed

- `python scripts/build_docs.py`: both strict documentation builds passed.
- `python scripts/check_landing.py`: built locale state, unique IDs, valid internal links, asset availability, motion control, absence of sample/code/table blocks and README link separation passed.
- `python scripts/check_docs.py`: 15 pages per language and 44 snippets parsed.
- `python -m pytest -q`: 75 passed, 4 skipped (optional browser integration tests).
- `python -m ruff check src tests scripts`: passed.
- `node --check docs/assets/product.js`: passed.
- `git diff --check`: passed.

## Remaining visual verification checklist

1. Open the built Spanish and English landing in an accessible browser preview.
2. Compare against the selected target at the same viewport; inspect heading, typography, crop, proportions and mobile widths 320/390/768px.
3. Observe actual deformation over time and pointer response; test pause/resume.
4. Toggle light/dark, navigate to documentation, and confirm the home remains dark while documentation reflects the chosen theme.
5. Test language links, primary actions, keyboard focus, reduced motion, no-WebGL fallback and page visibility lifecycle.
6. Check console errors and save the implementation screenshot plus combined reference comparison.
7. Fix all P0/P1/P2 findings and record a passing visual QA.

The owner explicitly approved integration and publication on 2026-10-08 after being informed of the preview blocker. Publication may proceed under that instruction; no visual-QA pass is claimed.
