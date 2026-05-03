# LLM Wiki Pattern

Last updated: 2026-05-03

## Summary

An LLM Wiki is a durable knowledge base where original material is stored under
`raw/` and synthesized pages are maintained under `wiki/`. The useful behavior
comes from repeated distillation: an LLM reads sources, updates stable pages,
and keeps claims traceable to the original inputs.

## Key Points

- Raw sources and synthesized knowledge should be kept separate so the wiki can
  improve without losing provenance. [source](../../raw/examples/karpathy-llm-wiki-note.md)
- The wiki should be navigable through indexes and related links, not just a
  pile of disconnected summaries. [source](../../raw/examples/karpathy-llm-wiki-note.md)
- This pattern is most useful for long-lived context such as agent memory,
  project knowledge, research notes, and team knowledge bases. [source](../../raw/examples/karpathy-llm-wiki-note.md)

## Related

- [Wiki Index](../index.md)
- [Source Catalog](../sources/source-catalog.md)

## Sources

- [Karpathy-style LLM Wiki source note](../../raw/examples/karpathy-llm-wiki-note.md)

## Open Questions

- Which source ingestion format should this repo standardize on for your daily
  workflow?
- Should source distillation be manual, scripted, or driven by a specific agent
  command?
