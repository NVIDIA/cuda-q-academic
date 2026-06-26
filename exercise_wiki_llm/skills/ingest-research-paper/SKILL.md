---
name: ingest-research-paper
description: Use when extracting structured notes from a research paper, article, PDF text export, technical report, lab note, or source URL before writing a local research wiki entry.
---

# Ingest Research Paper

Extract durable notes that can become a cited local wiki entry.

## Workflow

1. Identify the source title, authors, year, URL or local path, and document
   type.
2. Choose the source access path:
   - For arXiv sources, prefer the HTML version when available. Use the source
     URL for provenance, then try the corresponding `/html/<arxiv-id>` page.
   - Use the PDF only when HTML is unavailable, incomplete, or needed for
     figures, equations, tables, or page-specific evidence.
   - Use a local PDF text export when network access is unavailable.
3. Read the abstract, introduction, method, results, limitations, and conclusion
   sections when available.
4. Extract only claims supported by the source.
5. Preserve source anchors as page numbers, section names, figure/table labels,
   line numbers, or stable URLs when available.
6. Produce extraction notes with the schema below.
7. If a source cannot be read, record what failed and what artifact is needed.

## Extraction Schema

```markdown
# Extraction Notes: <title>

- Source:
- Authors:
- Year:
- URL or path:
- Access path used: HTML, PDF, local text export, or other
- Source anchors used:

## One-Sentence Takeaway

## Problem

## Method

## Experimental or Evaluation Setup

## Key Claims

- Claim:
  Evidence:
  Source anchor:

## Results and Numbers

## Limitations

## Terms For Glossary

## Tags

## Open Questions

## Relevance To This Workshop
```

## Quality Bar

- Prefer concrete numbers, named systems, algorithms, hardware, and datasets.
- Separate what the paper demonstrates from what it proposes.
- Mark uncertainty explicitly when the source is vague.
- Do not infer beyond the paper just to make the entry more impressive.
