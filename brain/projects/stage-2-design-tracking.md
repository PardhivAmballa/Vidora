---
title: Stage 2 Design Tracking
tags: [project, design, stage-2, fr-1, fr-2, fr-3, fr-4, fr-5]
status: active
---

# Stage 2: Design Tracking

## Objective

This project note tracks the design work for Stage 2 after completing the Stage 1 requirements and requirement baseline. The design work stays anchored to the SRS and the architecture notes so the implementation remains traceable and aligned to the product brief.

## Design anchors

- [[mcp-protocol-architecture]]
- [[youtube-api-quotas]]
- [[oauth2-token-lifecycle]]
- [[sqlite-fixture-caching]]
- [[playlist-constraint-algorithm]]
- [[prompt-injection-defense]]
- [[adr-governance-workflow]]

## Functional requirement traceability

- [[FR-1]]: Similar video ranking and metadata-based recommendation design
- [[FR-2]]: Similar channel ranking and metadata comparison design
- [[FR-3]]: Recommendation logic based on liked videos, subscriptions, and playlists
- [[FR-4]]: Engagement analysis and trend summary from user library data
- [[FR-5]]: Playlist proposal, confirmation gate, and post-confirmation creation flow

## Design tasks

### 1. Architecture and boundaries
- Finalize the MCP server boundary and provider contract.
- Confirm transport choices, validation flow, and error translation rules.
- Verify how quota, cache, and OAuth modules interact.

### 2. Similarity and recommendation design
- Define metadata normalization for video/channel similarity.
- Set ranking heuristics and confidence rules.
- Decide how FR-1 and FR-2 share the same recommendation pipeline.

### 3. Playlist creation and confirmation
- Define the playlist proposal payload and the confirmation gate.
- Validate duration parsing, max-length constraints, and language filtering.
- Ensure the write operation is gated by explicit user approval and server-side revalidation.

### 4. Security and governance
- Confirm minimum-scope OAuth requirements and re-authorization handling.
- Define prompt-injection protections for untrusted metadata.
- Ensure CI, tests, and ADR traceability remain linked to the design.

## Validation focus

- Unit tests for identifier parsing, duration logic, and similarity ranking
- Integration tests for provider and cache behaviour
- End-to-end MCP tests for FR-1 through FR-5
- Offline CI execution using fixtures and mocks only

## Related notes

- [[projects/]]
- [[resources/]]
- [[log|Activity Log]]
