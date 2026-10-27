---
name: brain-ingest
description: Ingests new research material or summaries into the Obsidian Second Brain vault.
---

# brain-ingest Skill

## Purpose
Automates the capture, formatting, and placement of research notes into the `brain/resources/` or `brain/inbox/` directories with proper [[wikilinks]].

## Execution Steps
1. Accept raw text or summary input from the user or agent session.
2. Format the note with a clear title, timestamp, and tags.
3. Save the file into the appropriate PARA directory (`brain/resources/` or `brain/inbox/`).
4. Update `brain/log.md` with an entry recording the ingestion.