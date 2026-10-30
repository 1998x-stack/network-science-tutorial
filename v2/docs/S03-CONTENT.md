# S03 — 28-chapter full-content migration

## Source of truth and boundaries

- Original root `01.html` through `28.html` remain unchanged, browseable and offline-compatible.
- `v2/content/lessons/NN.html` is a **verbatim article HTML snapshot** (excluding site chrome and duplicate H1). This is a deliberate fidelity-preserving intermediate representation, **not MDX**. Converting to MDX requires a follow-on AST conversion with validated math/table semantics.
- `v2/content/lessons/NN.json` is machine-readable chapter metadata with source Git blob SHA, headings and example paths.
- `v2/content/examples/NN/*.txt` are faithful extracts of code snippets. `.txt` intentionally avoids claiming they are runnable Python; shell/SQL/pseudocode may occur in the book.
- `v2/content/quizzes/NN.json` contains **draft, ungraded** exercise prompts, derived from the chapter's curriculum topics, not extracted authored questions.
- `v2/apps/web/lessons/NN.html` is a generated static reader containing the full original article, S02 chapter summary, source link and sample code file links.
- Known ERRATA remains authoritative; migrating a historical error is not scientific endorsement or correction.

## Commands (from repository root)

```bash
python3 v2/scripts/migrate_lessons.py
python3 v2/scripts/build_web.py
python3 v2/scripts/migrate_lessons.py --check
python3 v2/scripts/build_web.py --check
python3 v2/scripts/check_web.py
python3 -m unittest discover -s v2/tests -v
node --test v2/tests/web/shared.test.cjs
python3 scripts/check_site.py .
```

The pipeline is idempotent, deterministic, and has no network fetch. `--check` prevents changes and fails on mismatches. `source_git_blob` binds every migrated snapshot to the Git SHA of its original HTML file. For chapter edits, change root source first, rerun migration and review the generated diff. Do **not** hand-edit snapshots.

## Scientific review backlog

1. Chapter 01: four odd-degree vertices in Seven Bridges of Königsberg.
2. Chapter 04: distinguish G(n,p) and G(n,M).
3. Chapter 11: k-core need not be connected.
4. Chapter 12: model-dependent epidemic thresholds and compartment conventions.
5. Chapter 16: prevent temporal/graph-structure leakage for prediction tasks.
6. Chapter 20: review time-respecting paths and proper HTML entity handling.
7. Chapter 22: distinguish inductive/tranductive **training setups** from the capabilities of GNN layers.
8. Chapter 25: numeric speed claims require reproducible performance benchmarks.

Each proposed correction should include references and tests and should be made in its own subsequent content-review PR rather than silently changing original evidence during S03.
