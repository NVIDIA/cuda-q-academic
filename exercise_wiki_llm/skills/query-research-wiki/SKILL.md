---
name: query-research-wiki
description: Use when answering questions from a local research wiki, especially when answers must be grounded in wiki pages, cite supporting local entries, or say when evidence is missing.
---

# Query Research Wiki

Answer from the local wiki only.

## Required Behavior

1. Search `wiki/index.md`, `wiki/glossary.md`, `wiki/open-questions.md`, and
   `wiki/entries/*.md`.
2. Ignore `wiki/entries/README.md`; it is a placeholder, not evidence.
3. Cite the local wiki page that supports every substantive answer claim.
4. Prefer citations to the most specific entry section available.
5. If the wiki does not contain enough evidence, say:

   ```text
   I do not have enough evidence in the local wiki to answer that.
   ```

   Then list the missing evidence or suggested papers to ingest.
6. Do not fill gaps from general model knowledge unless the user explicitly asks
   for a non-wiki answer.

## Answer Shape

Use this structure for research questions:

```markdown
<direct answer with citations to local wiki pages>

Evidence:
- <claim> — <wiki path and section>
- <claim> — <wiki path and section>

Gaps:
- <missing or weak evidence, if any>
```

## Citation Examples

Use local paths:

```markdown
CUDA-Q state-vector simulation was used for the applied CO2-capture workflow
[wiki/entries/cuda-q-co2-mof.md].
```

If a section is known:

```markdown
The reported limitation was active-space simplification
[wiki/entries/cuda-q-co2-mof.md#limitations-and-caveats].
```

## Empty Wiki Behavior

If `wiki/entries/` is missing or contains only `README.md`, do not answer from
memory. Explain that the wiki has not been built yet and point the user to
`prompts/build-complete-wiki.md`.
