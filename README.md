# LLM Wiki

This repository is a small, agent-friendly knowledge base inspired by Andrej
Karpathy's "LLM Wiki" pattern.

The goal is to keep raw source material separate from distilled wiki pages:

- `raw/` stores original inputs: notes, transcripts, articles, papers, code
  readings, meeting notes, and copied source excerpts.
- `wiki/` stores curated Markdown pages written and maintained by an LLM.
- `templates/` stores reusable source and wiki page templates.
- `scripts/` stores lightweight maintenance tools.

## Workflow

1. Add source material under `raw/`.
2. Ask an LLM agent to read the relevant files and update `wiki/`.
3. Keep every important wiki claim traceable to source files in `raw/`.
4. Run the checker before committing:

```bash
python3 scripts/wiki_check.py
```

## Website

This repo can publish the curated wiki as a GitHub Pages site. The source of
truth remains Markdown, and `scripts/build_site.py` generates static HTML in
`_site/`.

After GitHub Pages deploys, the site is available at:

https://gavinhome.github.io/LLM-WIKI/

Build locally:

```bash
python3 scripts/build_site.py
```

When changes are pushed to `main`, `.github/workflows/pages.yml` checks links,
builds the site, and deploys it to GitHub Pages.

## Directory Layout

```text
.
├── .github/
├── AGENTS.md
├── README.md
├── raw/
│   ├── inbox/
│   └── examples/
├── scripts/
├── templates/
└── wiki/
    ├── index.md
    ├── concepts/
    ├── projects/
    └── sources/
```

## How To Ask An Agent To Update This Wiki

Use prompts like:

```text
Read raw/inbox/my-note.md and update the wiki.
Create or update pages under wiki/.
Preserve source traceability and add links from wiki/index.md.
Run scripts/wiki_check.py when done.
```

## Principles

- Prefer stable pages over one-off answers.
- Link concepts together.
- Preserve uncertainty and contradictions.
- Cite source files with relative links.
- Keep raw inputs unmodified unless explicitly cleaning metadata.
