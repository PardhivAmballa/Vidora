---
title: PARA Knowledge Management for Engineering
tags: [obsidian, para, second-brain, documentation, SDLC]
status: research
---

# PARA Knowledge Management for Engineering

## Why PARA fits

PARA organises knowledge by its relationship to action. It distinguishes active deliverables from ongoing responsibilities, reusable reference material, and inactive historical context. In this project the second brain is engineering evidence: requirements, decisions, skills, test results, and review notes should link to one another.

The SDLC brief specifies this structure and the `brain-ingest`, `brain-refine`, and `brain-query` workflows. It requires every ADR and skill to cite a distilled note, brain changes to pass through PRs, and contributions to be visible in commit history. See [[adr-governance-workflow]] and [[github-actions-ci-setup]].

## PARA taxonomy

### Projects

`brain/projects/` holds work with a defined outcome and completion horizon: stage checklists, sprint plans, FR-5 implementation, demo preparation, and release tasks. Include objective, owner, status, next action, deadline, and issue/PR links. When complete, summarise durable learning in Resources and move inactive project records to Archive.

### Areas

`brain/areas/` holds ongoing responsibilities without a fixed end date: quota governance, OAuth/security maintenance, CI ownership, documentation standards, and release management. Describe standards and recurring checks rather than one-off tasks.

### Resources

`brain/resources/` contains reusable knowledge:
- [[youtube-api-quotas]]
- [[mcp-protocol-architecture]]
- [[cosine-similarity-tfidf]]
- [[oauth2-token-lifecycle]]
- [[sqlite-fixture-caching]]
- [[prompt-injection-defense]]
- [[playlist-constraint-algorithm]]
- [[github-actions-ci-setup]]
- [[adr-governance-workflow]]

A useful resource note states the question it answers, findings, implementation examples, trade-offs, validation, provenance, and related notes. Flag fast-changing API facts for re-verification.

### Archive

`brain/archive/` holds inactive but historically useful material: superseded plans, completed stage notes, old experiments, and decisions replaced by newer ADRs. Archive rather than erase evidence explaining how the design evolved.

### Inbox

`brain/inbox/` is temporary capture for unprocessed material. Review each item, summarise/link/move it, or remove it according to retention policy. It is not a permanent dumping ground.

## Vault structure

```text
brain/
  index.md
  log.md
  inbox/
  projects/
  areas/
  resources/
  archive/
```

`brain/index.md` is the entry point and should link to active projects, areas, core resources, and the activity log. Keep it a navigation map, not a duplicate copy of every note.

## Note template

```markdown
---
title: Descriptive title
tags: [topic, requirement-id]
status: research
---

# Title

## Context
What question does this note answer?

## Findings
Distilled knowledge, assumptions, and source links.

## Decision implications
Architecture or implementation consequences.

## Validation
Tests and facts to verify.

## Related notes
- [[another-note]]
```

Use kebab-case filenames that match wikilinks. One note should have one primary purpose; split topics when they have independent lifecycles.

## Workflow skills

- **brain-ingest:** capture material, create a note, place it in inbox/resources, and log it.
- **brain-refine:** resolve duplicates, improve titles, move notes into PARA, fix links, add traceability.
- **brain-query:** answer questions or draft documents from vault notes and cite support.

AI assistance is allowed, but the team remains responsible for every merged line and claim.

## Governance and quality

- Every significant note change uses a PR.
- Every ADR and skill links to at least one distilled note.
- Every stage ends with a short review.
- `brain/log.md` records meaningful ingestion, refinement, and AI-assisted sessions.
- Notes contain no secrets, tokens, or real user data.
- CI checks frontmatter and broken links.

Avoid over-categorising, duplicate notes, orphan notes, stale API claims, untraceable decisions, and diary-like activity logs.

## Related notes

- [[github-actions-ci-setup]]
- [[adr-governance-workflow]]
- [[mcp-protocol-architecture]]
