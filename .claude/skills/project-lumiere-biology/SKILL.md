---
name: project-lumiere-biology
description: Author or review Project Lumiere (Biology) multimodal tasks - an adversarial, image-based life-science question set where a frontier vision-language model is expected to fail. Use when the user mentions Project Lumiere, Lumiere biology, lab-image tasks (gels, western blots, flow cytometry, plates, histology, cytology, cytogenetics, hematology, microscopy, phylogenetics, ELISA, PCR gels), GTFA, distractors, model failure reasons, image descriptions, or reviewing/scoring a Lumiere task.
---

# Project Lumiere (Biology)

## Purpose
Author multimodal biological-research tasks: a **real** lab image (or up to 5 related images) plus an expert-level prompt a frontier VLM is expected to get **wrong**. Goal is an adversarial eval set exposing failure modes: axis confusion, magnification mismatch, signal-vs-artifact discrimination, miscounting dense fields, over-reliance on text cues. Failed or subpar own-lab assay images are encouraged. If the model gets the task right, redesign / swap image / retire; never deliver as-is.

## Task deliverable (fields, in order)
1. **Image(s)**: labeled "Image 1:", "Image 2:", ... (numbering must match the prompt)
2. **Prompt**
3. **Step-by-step solution** (numbered, closes with the GTFA)
4. **GTFA** (ground-truth final answer, written verbatim, never just a letter)
5. **Answer format** (Integer / Decimal / Ordered list / Unordered list / short text; decimal places specified)
6. **Image description** (one per image/panel)
7. **Distractors**: exactly 5
8. **Model answer** + **Failure reason** (both models must fail; 1-3 sentence diagnosis)
9. **Image source & license** (+ DOI/URL for external images; "Original - internal lab image" for own images)

## Image rules
- PNG or JPEG only. Under 5 MB, ~2,000 px long edge. Max 5 images per task. No transparent backgrounds.
- Original resolution; no screenshots of screenshots; no dark-mode screenshots; must be legible to a human reviewer.
- No enhancing, sharpening, color-correcting. Real artifacts are signal.
- Keep all axis labels, lane labels, scale bars, color legends, MW ladder marks. Never crop them.
- No artificial digital annotations (arrows, circles, boxes, callouts, highlights, segmentation). Native instrument/wet-lab marks (handwritten lane labels, sample IDs, dates, scale bars) are fine.
- Minimal annotations; the model must not be able to read the answer directly off the image.
- **No synthetic or schematic data** in Life Science. Real data only.
- Reference images by number ("Image 2", "Panel A"), never by file name.
- Use multi-image when the answer needs integration across views, scale, or magnifications.

## Licensing
| Source | OK? |
|---|---|
| Original - internal lab image | Yes |
| CC BY 2.0/3.0/4.0 | Yes (attribute; don't modify) |
| CC BY-SA | Yes |
| CC0 | Yes (still record source URL) |
| CC BY-NC / -ND / -NC-ND | No |
| All Rights Reserved / no license stated | No |
| BioRender (or similar tool) figures | No, hard block even inside a CC BY paper |
| bioRxiv / preprints | No |
| Images meant for future publications | No |

- Source article must be peer-reviewed/published and meet the project date cutoff.
- Figure license can differ from paper license: check the figure caption. Open access is not reuse rights.
- Reuse rule: a figure used as the sole image in one task cannot be the sole image in another; reuse only combined with previously unused figures.
- Sourcing hubs: PMC OA subset, PLoS, Frontiers, MDPI, eLife, Nature OA, NIH Open-i, Wikimedia Commons, BioImage Archive, IDR, Figshare, Harvard Dataverse, TCIA, PIDAR.

## Assay subtypes in scope (pick the assigned one; image and prompt must match)
- **Gel & Western**: agarose, SDS-PAGE, western (chemi/fluor), 2D gels, native PAGE
- **Flow cytometry**: FSC/SSC gating, fluorescence histograms, dot/contour quadrant, compensation + FMO, bead assays
- **Petri dishes & plates**: colony morphology/hemolysis, agar assays (zone of inhibition), multi-well colorimetric (ELISA/MTT/CV), primary vs cell line morphology
- **Histopathology**: H&E, IHC, special stains
- **Cytology**: Pap, FNA, body fluid, liquid-based
- **Cytogenetics**: metaphase spreads, G-banded karyograms, FISH
- **Hematology**: Wright-stained films, bone marrow, blood-cell fields
- **Microbiology**: Gram/other stains, parasitology & mycology mounts
- **Cell & molecular imaging**: IF/confocal, brightfield culture
- **Agri-food & environmental**: food/water micro, plant pathology, algae/diatoms
- **Protein-ligand**: molecular diagrams, molecular structure
- **Other**: ELISA, PCR gels, lateral flow, clonogenic/crystal violet, wound-healing time series, plasmid maps, phylogenetics

## Prompt rules (Quality Bar)
A peer in the lab must be able to answer from the image alone. Prompt must be:
- **Image-dependent**: not answerable from assay class alone.
- **Single question, single unambiguous answer**: no stacked questions (two analyses = two tasks).
- **Not multiple choice**, explicit or implied (implied MC needs >= 10 plausible answer options). Ask for the answer directly.
- **Not a pure counting question**: the count must feed a classification/judgement/quantity.
- Conventions, rounding, units, labeling scheme, and tie-break rules spelled out (e.g., "label panels alphabetically left-to-right by row", "two decimals, no % symbol", "ranked list separated by >").
- Short final answer (never a long sentence). Typos only matter if they change meaning.
- Biosafety: see guardrail words below.

## Step-by-step solution rules
- Numbered "Step N:". Early steps record **observations only**; interpretation goes in later steps.
- Anchored in visual evidence, name the underlying biology, **show all arithmetic** (dilutions, unit conversions, averages, SEM = SD/sqrt(n)).
- Walk through every panel/lane/bar/item; state inclusions/exclusions explicitly.
- Close with "Final Answer: <GTFA>".

## Image description rules
- One per image/panel. Describe only what is visible; **never state the final answer**.
- Detailed enough that a reader could derive the answer from prompt + description without seeing the image (typically >= 200 words). Cover layout, background, axes/ticks/labels/units, legend, band/bar/point positions and relative sizes, scale bars, artifacts.
- Must match the image exactly (no mismatched labels/values).

## Distractors
- Exactly 5, same format as the GTFA, each plausible to a non-expert but dismissible by an expert.
- Each maps to a specific reasoning error models actually make (miscount, wrong node, skipped zero-height bar, wrong unit, off-by-one rounding, wrong order, etc.).

## Model testing
- Test against frontier models; **both must fail**.
- Record Model answer and **Failure reason**: name the failure mode in one sentence, then 1-3 sentences on where/what/why (see golden examples: e.g., missing blank positions, wrong MRCA node, dot-diameter error-bar convention, mis-ranking VZ thickness).
- If the model passes first try: redesign prompt toward a tighter failure mode, swap image, or retire.

## Golden example patterns (5 reference tasks)
1. **Neurobiology** (4-panel GFAP/Hoechst organoid IF): label panels, filter by GFAP-positive VZ, rank VZ thickness -> `D > B > A` (ordered list).
2. **Genetics** (bar chart % wt mtDNA): count dogs with <= 10% wt incl. invisible zero-height bars -> `80.49` (decimal, 2 dp).
3. **Cell biology** (RdRp inhibition gel + dose-response): SEM overlap logic, controls, triplicates -> `15` (integer).
4. **Ecology/Evolution** (phylogeny): read bootstrap at each MRCA, rank -> `C, F, D, B, E, A` (ordered list).
5. **Biochemistry** (mass photometry + FP + gels, 3 images): species that can drive product at 200 nM -> `RdRp, nsp8/12` (unordered list).
Common thread: multi-step visual reading, explicit conventions in the prompt, hidden traps (zero-height bars, nearest-node confusion, error-bar overlap), single canonical answer.

## Biosafety guardrails (reword if present in prompt/description/solution)
Keep the task on the **interpretation** side. Avoid or reword: virus/virulent, toxin, mutant/mutation, transformation, vector, gain of function, knockout, variant, pathogen, resistance, immunization, evasion, contamination; stabilization, optimization, delivery mechanism, dissemination, particle size, cultivation, purification, isolation, lyophilization, fermentation, synthesize/purify; propagate, amplify (a pathogen), passage, enrich, scale up, titre optimisation; enhance virulence/transmissibility, immune escape; weaponise, aerosolise, payload; select agent, BSL-3/4, named high-consequence agents; evade detection, bypass screening; "how to produce", "step-by-step protocol for", "recipe", "optimal conditions to maximise". Context matters: only a problem when pointing at producing/enhancing/misusing material rather than reading an image.

## Submission checklist (21 items)
**Image (3)**: matches assigned supertype/subtype; PNG/JPEG; original resolution and labeled "Image 1:", "Image 2:"...
**Licensing (6)**: License row filled (type + URL/DOI + attribution); own images = "Original - internal lab image"; allowed license only; no BioRender; peer-reviewed + within date cutoff; not previously the sole image elsewhere.
**Prompt/Solution/GTFA (4)**: image-dependent; specific and unambiguous with conventions spelled out; solution numbered, visual-evidence anchored, names biology, shows arithmetic, ends with GTFA; GTFA verbatim and unambiguous in isolation.
**Model testing (3)**: both models failed; Failure reason 1-3 sentences; redesign if model passed.
**Image description (4)**: present for every image/panel; sufficient to derive answer; no verbatim answer; matches the image.
**Distractors (1)**: five, each plausible to a non-expert.

## Review mode
Claim via Handshake AI dashboard -> Project Lumiere -> Available Tasks -> Stage "Awaiting Review (Review 1)". Add feedback per section (Major / Minor / Praise / General), copy the exact error tag, point to location, suggest fix. Minor errors fixable in < 25 min and in your expertise: fix yourself and leave a general comment. Approve only with zero major and zero minor errors. Typo/grammar only blocks if it changes meaning. Stacked questions are not allowed; when in doubt ask in #lumiere-reviewer.

**Score rubric** (>= 3 passes): 5 = no errors; 4 = 1-2 minor; 3 = 3-4 minor; 2 = any major or > 4 minor (send back); 1 = no effort or 3+ major (flag to team lead).

**Major tags**: Prompt - multiple answers; Prompt - invalid; Image - no/invalid source; Answer - incorrect; Answer - ambiguous; Answer - long; Image - unclear; Image - format; Image - edited; License - invalid (external images only, never for own images); Model - invalid failure; Task - wrong subtype; Model - few failures; Other.
**Minor tags**: Model - justification; Solution - partial; Distractors - mismatched; Answer - format (type or decimals wrong); Grammar; Other.

## Other notes
- LaTeX: verify KaTeX support / rendering (stackedit.io, overleaf.com) before submitting.
- Profession field: O*NET OnLine for exact occupation title + SOC code.
- Cytogenetics answers: ISCN nomenclature. Graded calls: use published WHO/CAP criteria.
