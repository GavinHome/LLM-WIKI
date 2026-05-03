# Agent Instructions For This LLM Wiki

This repo is an LLM-maintained wiki. Treat it as a durable knowledge system,
not a chat transcript.

## Source Of Truth

- `raw/` contains source material. Do not rewrite source files unless the user
  explicitly asks for cleanup.
- `wiki/` contains synthesized knowledge. Update these pages when new source
  material changes the understanding of a topic.
- PDFs and EPUBs should usually have a companion Markdown note in `raw/papers/`
  or `raw/books/` before their claims are distilled into `wiki/`.
- If a wiki statement is important, non-obvious, or factual, cite at least one
  source file from `raw/`.

## Update Workflow

1. Identify relevant source files in `raw/`.
2. Read existing pages in `wiki/` before creating new ones.
3. Update the most specific existing page when possible.
4. Create a new page only when the concept does not fit an existing page.
5. Add backlinks or index entries so the page is discoverable.
6. Run `python3 scripts/wiki_check.py`.

## Page Standards

Every wiki page should include:

- A short summary.
- Key points or decisions.
- Links to related wiki pages.
- Source links back to `raw/`.
- A `Last updated` date.

Use relative Markdown links. Prefer lowercase kebab-case filenames.

## Handling Uncertainty

- Mark uncertain statements as `Open question` or `Inference`.
- Do not collapse contradictory sources into false certainty.
- If sources disagree, name the disagreement and cite both sides.

## What Not To Do

- Do not paste large raw documents into wiki pages.
- Do not create orphan pages.
- Do not invent citations.
- Do not remove raw material just because it has been summarized.
