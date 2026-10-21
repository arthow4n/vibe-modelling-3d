---
name: documentation-writing
description: Write or restructure substantial repository documentation so humans can immediately see what the object is, what is done, what to print or do next, and what to ignore, while preserving detailed engineering investigations and historical records cleanly. Apply within the documents affected by the task, not as a routine repository audit.
---

# Documentation writing

Write for a human browsing the repository first; keep agent bookkeeping and historical trails out of the way of immediate understanding. When someone opens a `README.md`, they should know within 10 seconds:
1. **What this object is.**
2. **What is done / working right now.**
3. **What I can or should do next** (which exact file to print, with what settings)—and **what I should *not* do** (which files, variants, or branches are rejected, broken, or closed).
4. **Where to find the deep engineering history** if they want to dig into past iterations or calculations.

Use this skill for substantial object records, technical guides, decision explanations and documentation restructuring. A small factual/link correction needs only a proportionate edit and validation.

## Core readability rules (anti-clutter contract)

1. **Answer "What now?" at the very top ("At a Glance").**
   Every object `README.md` (which must exist at `model/<object>/README.md` as the single entry point) begins with a short, scannable top section before any history or deep mechanics:
   - **Purpose:** 1–2 plain-English sentences on what the object is and what it fits.
   - **Current Status & Action:** Explicit bullets or a compact callout stating:
     - **Do / Ready to print:** The current recommended variant or active print trial, with direct `[STEP](...)` and `[STL](...)` links.
     - **Do not print / Closed:** Explicitly name superseded, broken, or discontinued variants/branches so the user never wastes filament or wonders if an older file is still active.
   - **Current Print Setup:** A clean, compact table or bullet list of the active printable files, material, layer height, supports, and any required slicer profile/overrides.

2. **Replace in place—never stack dated patch banners.**
   Do **not** prepend `**2026-10-20 update:**`, `**Latest printable model:**`, or `**Current phase:**` paragraphs above older "current" paragraphs when a task finishes. Stacking reverse-chronological banners turns the top of a document into an unreadable archaeological dig. Instead:
   - Rewrite the top "Current Status" and "Current Design" sections in place to reflect the new reality.
   - Move the superseded phase's narrative, tables, and old slice commands down into a clearly separated `## History & Superseded Iterations` section (or into a dedicated `notes/` file).

3. **One entry point per object—no redirect chains.**
   Never leave a model without a root `model/<object>/README.md`, and never create chains where `notes/README.md` points to `short_lap.md`, which points to `wall_comparison.md`, which points to `grip_human.md`. `model/<object>/README.md` is always the authoritative current summary and navigation hub; files in `notes/` are scoped deep-dives or historical phase records that link back to `README.md`.

4. **Keep the root `README.md` a scannable catalog, not a project changelog.**
   The root `README.md` `# Models` section is for browsing the repository. Each model entry must stay concise (typically 4–8 lines):
   - A 1-line description and link to `model/<object>/README.md`.
   - **Status / What works:** What has been physically printed and accepted vs. what is unprinted or discontinued.
   - **Current files / Next step:** Direct links to the active printable files (or "None — complete" / "Discontinued").
   - **Standard status & provenance:** Compact Test pieces / Final object status and Provenance / Agent effort links.
   Never dump multi-paragraph iteration logs, FEA numbers, or SVG galleries into the root `README.md`.

5. **Quarantine agent bookkeeping, CLI plumbing, and epistemic disclaimers.**
   Agents need exact provenance, SHA256/JSON receipts, `product_verification` CLI commands (`--variant`, `INCONCLUSIVE` boolean crops), and scope limits—humans reading the design story do not want them injected into every second sentence.
   - **Do not** repeat "STL slicing does not verify Orca's GUI STEP import", "PETG properties are uncalibrated", or "exact printed git hash is unknown" in every paragraph.
   - State scope limits and physical unknowns **once**, clearly and concisely, in a dedicated `## Verification, Limits & Print Status` section near the bottom of the README.
   - Keep `product_verification` CLI invocations, JSON receipt links, and per-phase `Attribution` blocks compact and at the bottom of the file (or in `notes/`).

## Explain engineering changes in human + technical terms

When explaining why the current design is the way it is:
- **Lead with the practical consequence:** State the previous problem, what changed, why it was chosen, and what it means in practice.
- **Pair numbers with everyday intuition:** When citing a consequential force, deflection, or dimension (e.g. a `12.6 N` side load or `0.6 mm` catch), pair it with a familiar physical interpretation (e.g. "about 1.3 kgf—roughly the weight of a full 1.25 L bottle pressing sideways on one catch") while keeping the limit clear (static push vs. drop impact).
- **Use visuals at the decision point:** Link or embed annotated SVGs/renders where geometry, contact, or toolpaths are hard to picture in prose. Distinguish completed digital checks, physical print results, and unprinted proposals. Define every diagram colour as a physical part, material, or empty region, and state when role colours represent the same actual material. For nested/compliant structures, pair an assembly section with labelled before/load views showing what flexes into which space; do not rely on colour alone to convey the mechanism.
- **Use short tables for comparable options:** Use tables for comparing variants, dimensions, or print settings; use clear paragraphs and subheadings for explanations.

## Organize by reading depth

Structure each object's documentation into three clean layers:

1. **Top of `model/<object>/README.md` (The 10-second scan):**
   - What it is, Current Status (What to do / What not to do), Current Printable Files & Slicer Setup.
2. **Middle of `model/<object>/README.md` (The current engineering summary):**
   - How the current design works, key dimensions/improvements over the previous version, visual diagrams, and practical test/installation steps.
3. **Bottom of `model/<object>/README.md` & `notes/` (History, verification & agent records):**
   - Print status block, consolidated verification/limitations summary, concise chronological index of past iterations (with details in `notes/`), and attribution.

Agents are encouraged to write thorough, detailed engineering records in `notes/` whenever useful—including negative results, rejected alternatives, failed experiments, and solver diagnostics. There is no length limit on `notes/` investigations; keeping them out of the top-level reading flow is what makes both the human summary and the deep notes usable.

## Preserve evidence, links, and verification contracts

Cleaning up clutter must **never** destroy engineering facts or break automated verification:
- **Preserve all unique facts:** Keep every physical observation, user print report, dimension, negative result, rejected variant rationale, and historical attribution—relocate superseded detail to history sections or `notes/` rather than deleting it.
- **Protect `product_verification` and incoming `#anchor` links:** Automated verification plans (`verification.py`, `notes/verification_sources.json`, and JSON receipts) and cross-document links depend on specific file paths and `#heading-slug` anchors. When renaming, consolidating, or moving a heading that is referenced elsewhere, **always** preserve the target anchor using an explicit `<a id="original-anchor-slug"></a>` tag (or keep the exact heading text) in the target file.
- **Keep status categories honest:** Keep `PASS`, `FAIL`, `UNKNOWN`, `INCONCLUSIVE`, and `N/A` distinct. Never present a CAD check or slicer smoke test as a physical print result, and never reactivate discontinued work.

## Validation before handoff

1. **10-second human scan check:** Read the top of each edited `README.md` as the user. Is it immediately obvious what works, what file to print, what settings to use, and what old files/ideas to ignore? Are there any stacked date banners left at the top?
2. **Preservation & link check:** Verify that all relocated numbers, print reports, limitations, and attributions are intact, and verify that all markdown links and `#anchor` targets (especially those in `verification.py` and `verification_sources.json`) resolve cleanly.
3. **Scope-appropriate testing:** Documentation-only edits require link/anchor and `product_verification` checks, not fresh CAD exports or slicer runs.
