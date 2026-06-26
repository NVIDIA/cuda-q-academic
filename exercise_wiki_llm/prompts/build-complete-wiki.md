# Build The Complete Wiki

Use this prompt from this exercise folder to build the local wiki:

```text
Read AGENTS.md. Use one subagent per paper to ingest every source listed in
documents/paper-sources.md. For each source, use the local
skills/ingest-research-paper skill and then the local skills/write-wiki-entry
skill. Save entries under wiki/entries/. After all papers are ingested, update
wiki/index.md, wiki/glossary.md, and wiki/open-questions.md. Do not create
wiki/comparison-matrix.md unless I ask for the optional add-on.
```

Expected result:

- `wiki/entries/` contains one entry per paper.
- `wiki/index.md` lists entries, tags, and source links.
- `wiki/glossary.md` contains terms that appear across the papers.
- `wiki/open-questions.md` lists unresolved issues and future work.
