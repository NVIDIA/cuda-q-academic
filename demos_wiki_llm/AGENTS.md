# Research Wiki Agent Guide

This folder is a workshop environment for building and querying a local research
wiki. Treat the wiki as the only trusted knowledge base for workshop answers.

## Goal

Ingest research papers or technical documents into local Markdown wiki entries,
then answer questions with citations to the wiki pages that support the answer.

## Hard Rules

1. Use the local skills in `skills/` for ingestion, wiki writing, and querying.
2. When ingesting multiple documents, use one subagent per document when the
   current Codex environment supports subagents.
3. Save generated entries under `wiki/entries/`.
4. Keep `wiki/index.md`, `wiki/glossary.md`, and `wiki/open-questions.md`
   updated after ingestion.
5. Do not answer research questions from general model knowledge when the user
   asks to use the wiki.
6. Every substantive answer claim must cite the local wiki page that contains
   the supporting evidence.
7. If the wiki does not contain enough evidence, say that clearly and list what
   evidence is missing.
8. Cite original papers only through the wiki entry unless the user explicitly
   asks you to inspect the source document again.
9. Do not create `wiki/comparison-matrix.md` unless the user asks for the
   optional comparison-matrix add-on.

## Core Wiki Files

- `wiki/index.md`: map of entries, topics, tags, and source documents.
- `wiki/glossary.md`: short definitions of recurring concepts.
- `wiki/open-questions.md`: unresolved questions, limitations, and follow-ups.
- `wiki/entries/`: one Markdown entry per ingested paper or document.

## Demo Workflow

To build the instructor example:

```text
Read AGENTS.md. Use one subagent per paper to ingest every source listed in
documents/paper-sources.md. Save the wiki entries, then update the index,
glossary, and open questions. Do not create the optional comparison matrix.
```

To query the wiki:

```text
Read AGENTS.md and answer the questions in prompts/demo-questions.md using only
the local wiki. Cite the wiki pages that support each answer.
```

## Optional Add-ons

The workshop starts with local files and web links only. Later extensions could
connect the same workflow to Slack, Outlook, Teams, Zotero, arXiv feeds,
Semantic Scholar, Notion, Obsidian, or a lab file share.
