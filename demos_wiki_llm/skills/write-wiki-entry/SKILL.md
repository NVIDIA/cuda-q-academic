---
name: write-wiki-entry
description: Use when turning extracted research notes into a local Markdown wiki page with provenance, claims, limitations, tags, glossary terms, and open questions.
---

# Write Wiki Entry

Create a structured Markdown page that future answers can cite.

## Destination

Save entries in:

```text
wiki/entries/<short-slug>.md
```

Use lowercase slugs with hyphens.

## Entry Template

```markdown
---
title: "<paper or document title>"
authors: ["<author names>"]
year: "<year>"
source_url: "<URL or local path>"
document_type: "paper"
tags: ["cuda-q", "quantum-simulation"]
status: "draft"
---

# <Title>

## Why It Matters

## Short Summary

## Key Claims

- **Claim:** <specific claim>
  **Evidence:** <what the source showed>
  **Source anchor:** <section/page/figure/table/URL>

## Method Or Workflow

## Results And Scale

## Limitations And Caveats

## Relevance To Quantum Researchers

## Glossary Candidates

## Open Questions

## Source Notes
```

## After Writing

Update these files:

- `wiki/index.md`: add title, slug, tags, source, and one-line relevance.
- `wiki/glossary.md`: add or refine recurring terms.
- `wiki/open-questions.md`: add unresolved questions and cite the entry path.

## Citation Rule

The wiki entry is the evidence layer used by the query skill. Write entries so
that answer citations can point to the relevant local page and section.
