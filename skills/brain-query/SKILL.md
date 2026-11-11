---
name: brain-query
description: Queries the Obsidian Second Brain vault (`brain/`) to retrieve technical notes, research summaries, and architectural decisions to answer questions or draft project documents.
---

# brain-query Skill

## Purpose
Enables automated agents and developers to search, read, and synthesize information stored across the Obsidian PARA vault (`brain/inbox/`, `brain/projects/`, `brain/areas/`, `brain/resources/`, `brain/archive/`) while maintaining explicit `[[wikilinks]]` traceability.

## Workflow Instructions
1. **Index Discovery:** Always scan `brain/index.md` first to understand the current structure and available entry points of the Second Brain.
2. **Resource Exploration:** Search the `brain/resources/` directory for relevant technical notes (e.g., API quotas, MCP architecture, similarity models).
3. **Traceability Citation:** When drafting documents, code explanations, or Architecture Decision Records (ADRs), explicitly cite the underlying source notes using `[[wikilinks]]` (e.g., `[[mcp-protocol-architecture]]`).
4. **Activity Logging:** Record significant query or synthesis actions in `brain/log.md` if they result in new architectural insights or documentation updates.