---
title: Architecture Decision Record Governance and Traceability
tags: [adr, architecture, governance, traceability, SDLC]
status: research
---

# Architecture Decision Record Governance Workflow

## Purpose

Architecture Decision Records (ADRs) capture significant decisions, why they were made, alternatives considered, and consequences accepted. They prevent important context from living only in chat history or one engineer's memory.

The SDLC brief requires significant decisions under `docs/adr/`, each citing brain notes. It also requires traceability from requirement to issue, PR, test, skill, and brain note. See [[para-knowledge-management]], [[mcp-protocol-architecture]], and [[github-actions-ci-setup]].

## When to write an ADR

Write an ADR when a choice materially affects architecture, security, operations, or long-term maintenance. Examples: stdio vs HTTP, provider/fixture boundaries, SQLite cache and quota ledger, OAuth scope strategy, similarity policy, playlist confirmation, and quota reservation concurrency. Do not create one for every small refactor.

## Naming and location

Use unique monotonically increasing identifiers and descriptive kebab-case names:

```text
docs/adr/
  0001-use-mcp-stdio-for-local-client.md
  0002-isolate-youtube-provider.md
  0003-use-sqlite-for-local-cache.md
  0004-require-confirmation-before-playlist-write.md
```

Never reuse an ID. If a decision is superseded, create a new ADR and link both records. Preserve the old record for historical context.

## Recommended template

```markdown
# ADR-0004: Require Explicit Confirmation Before Playlist Writes

- Status: Proposed | Accepted | Deprecated | Superseded
- Date: YYYY-MM-DD
- Owners: team or role
- Requirements: FR-5, NFR-3
- Brain notes: [[prompt-injection-defense]], [[playlist-constraint-algorithm]]

## Context
What problem or constraint requires a decision?

## Decision
State the chosen approach precisely.

## Alternatives considered
List realistic options and why they were rejected.

## Consequences
Benefits, costs, risks, and operational implications.

## Security and privacy
Trust boundaries, permissions, and data handling.

## Validation
Tests, metrics, review evidence, and rollout checks.

## Traceability
- Issue: #...
- PR: #...
- Tests: ...
- Skill: [[video-to-playlist]]
```

Use explicit status and ISO 8601 dates. “Proposed” is not an approved production commitment.

## Traceability chain

```text
Requirement (FR/NFR/SK)
 -> GitHub Issue
 -> Pull Request
 -> Implementation
 -> Unit / integration / system test
 -> Agent Skill (where applicable)
 -> Brain note
 -> ADR (for significant decisions)
```

For FR-5, evidence could include the SRS requirement, an issue for the planner and confirmation gate, a PR with implementation, tests for duration parsing and confirmation, the `video-to-playlist` skill, [[playlist-constraint-algorithm]], [[prompt-injection-defense]], and an ADR for side-effect policy. Fill actual issue/PR IDs from the repository; never fabricate them.

## Traceability matrix

| Requirement | Issue | PR | Tests | Skill | Brain note | ADR |
|---|---|---|---|---|---|---|
| FR-1 | TBD | TBD | similarity unit/system | optional | [[cosine-similarity-tfidf]] | TBD |
| FR-3 | TBD | TBD | authorised-library integration | optional | [[oauth2-token-lifecycle]] | TBD |
| FR-5 | TBD | TBD | duration/confirmation/system | [[video-to-playlist]] | [[playlist-constraint-algorithm]] | TBD |
| NFR-1 | TBD | TBD | budget guard | optional | [[youtube-api-quotas]] | TBD |
| NFR-2 | TBD | TBD | offline fixture suite | optional | [[sqlite-fixture-caching]] | TBD |

Replace `TBD` with real repository references. Do not imply work is complete while evidence is missing.

## PR governance

Every code, skill, brain, or ADR change goes through a PR with at least one review. Reviewers check decision clarity, credible alternatives, honest consequences, relevant note links, accurate requirement/test references, and absence of secrets or personal data. AI-generated changes also require human review, and team members must be able to explain merged artifacts.

## Supersession workflow

1. Open an issue describing the problem.
2. Draft an ADR in a branch.
3. Link brain notes and requirement IDs.
4. Implement in a linked PR and add tests.
5. Review, merge, and update traceability.
6. If the decision changes, create a new ADR with a `Supersedes` link.

## Review checklist

- [ ] Unique ID and file under `docs/adr/`.
- [ ] Status, date, context, decision, alternatives, consequences.
- [ ] At least one relevant wikilink.
- [ ] Accurate requirement, issue, PR, and test references.
- [ ] Security and privacy impacts documented.
- [ ] Human review and CI checks completed.
- [ ] Superseded records link to replacement.

## Related notes

- [[para-knowledge-management]]
- [[github-actions-ci-setup]]
- [[mcp-protocol-architecture]]
- [[prompt-injection-defense]]
