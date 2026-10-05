# Project Vertex

Project Vertex is the working name for the finance reasoning question work
described in three source documents:

- `Finance_Reasoning_Questions_Guide.pdf` (project guide, 8 pages)
- `Finance_Reasoning_Questions_Guide_1.pdf` (same guide plus the "Multi-hop task" section, 15 pages)
- `golden_example.pdf` (Golden Example: building a rigorous analytical task, and the trap library)

The goal of the project is to write multi-hop finance questions that AI models
cannot shortcut, together with the verified answers used to grade them.

## Folder layout

| Path | What it holds |
| --- | --- |
| `README.md` | This overview |
| `INSTRUCTIONS.md` | The distilled rules, depth targets, review criteria and trap library |
| `CHECKLIST.md` | Pre-submission checklist, one line per rule that decides acceptance |
| `templates/` | Blank templates for the five deliverables per question |
| `tasks/` | One folder per question (`tasks/Q001-short-slug/`) built from the templates |

## The one-paragraph version

Every question is a chain of nodes. A retrieval node looks up one atomic fact
from an authoritative source. A compute node performs one exact operation on
values already in hand and never rounds until the final answer. Past the opening
look-ups, every retrieval must be keyed by the result of an earlier step. The
chain must contain at least 3 chained retrieval hops (4 to 6 is the goal), run
6 to 9 steps long, ask 3 interconnected questions that converge on one shared
final answer, rely only on settled historical facts, and stump both Model 1 and
Model 2 on at least one final answer each. The prompt names only the publishing
authority, never a URL, CIK, accession number or filing date.

## Workflow per question

1. Plan the chain on paper as nodes (N1, N2, ...) and count layers and hops.
2. Open every source and record each value with its citation, twice.
3. Write the natural-language prompt (prose, ending in explicit questions).
4. Run Model 1, then Model 2. Confirm each got at least one final answer wrong.
5. Write the reasoning chain, let the reasoning graph be derived, verify it.
6. Build the rubric: finals on top, one row per intermediate step below.
7. Run `CHECKLIST.md`. Submit only if every line passes.
