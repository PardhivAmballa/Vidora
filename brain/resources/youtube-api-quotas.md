---
title: YouTube Data API v3 Quota Economics
tags: [youtube, api, architecture, reliability, FR-1, FR-3, FR-5]
status: research
---

# YouTube Data API v3 Quota Economics

## Purpose and project context

The project statement makes the quota constraint explicit: Vidora must track quota cost per request and reject any workflow that would exceed the remaining daily budget before making an API call. The default daily allocation is 10,000 units per day, and the project forbids scraping, unofficial APIs, and creating extra Google Cloud projects just to increase quota.

This is not a soft preference. It is a core product requirement because the server may fan out into search requests, metadata hydration, channel lookups, library analysis, and playlist writes. The system therefore needs a durable budget ledger and a pre-flight guard that runs before any remote call.

See [[mcp-protocol-architecture]], [[sqlite-fixture-caching]], and [[adr-governance-workflow]].

> Operational caveat: endpoint costs and billing rules can change. Treat the values below as a design baseline and verify the current official documentation before release. Keep the cost map in configuration, not spread across business logic.

## Quota model

Let \(Q_d\) be the daily allocation, \(Q_u\) the units consumed, \(Q_r = Q_d - Q_u\) the estimated remaining budget, \(C(w)\) the planned workflow cost, and \(R\) a safety reserve for retries and concurrent work.

A workflow may start only if:

\[
C(w) + R \le Q_r
\]

The estimate must include the full planned call chain, not only the first search. When a cost is uncertain, fail closed and require an explicit configured estimate. A zero-cost assumption is not acceptable.

## Endpoint cost baseline

This is a planning baseline rather than a substitute for official documentation.

| Operation | Endpoint | Planning cost | Notes |
|---|---|---:|---|
| Discover candidate videos | `search.list` | 100 units/request | Pagination can multiply cost quickly. |
| Read playlist entries | `playlistItems.list` | 1 unit/request | Every page is another network call. |
| Hydrate video metadata | `videos.list` | 1 unit/request | Batch IDs where supported. |
| Read channel metadata | `channels.list` | 1 unit/request | Batch IDs and cache stable metadata. |
| Create playlist | `playlists.insert` | Verify current cost | Write costs must be explicitly budgeted. |
| Add playlist item | `playlistItems.insert` | Verify current cost | Each insertion may incur a separate cost. |

A centralised configuration is the safest pattern:

```python
DEFAULT_COSTS = {
    "search.list": 100,
    "playlistItems.list": 1,
    "videos.list": 1,
    "channels.list": 1,
}
DAILY_LIMIT = 10_000
SAFETY_RESERVE = 250
```

Do not silently assume write costs from this example. Confirm them against official documentation before release, and never hard-code live API assumptions in business logic.

## Pre-flight budget checks

Use three stages: plan expected operations, estimate the total cost, and reserve budget before the first remote call. A simple guard is easy to test:

```python
class QuotaExceededBeforeCall(RuntimeError):
    pass

def ensure_budget(estimated_cost: int, remaining: int, reserve: int = 0) -> None:
    if estimated_cost < 0:
        raise ValueError("estimated_cost cannot be negative")
    if estimated_cost + reserve > remaining:
        raise QuotaExceededBeforeCall(
            f"workflow needs {estimated_cost} + {reserve} reserve; "
            f"only {remaining} units remain"
        )
```

In production, `remaining` must come from a durable ledger, not an in-memory counter that resets when the MCP process restarts. Use SQLite transactions (or equivalent) so concurrent requests cannot overspend the same balance. Define the daily reset boundary explicitly; UTC is a reasonable default.

Track both estimated and observed spend. Log operation name, request count, estimate, outcome, and correlation ID, while avoiding OAuth tokens, personal metadata, and secret values. Any retry or fallback path should also be included in the quota estimate.

## Caching and batching

- cache stable `videos.list` and `channels.list` metadata by canonical ID;
- cache search results by normalised query and all response-affecting parameters;
- use TTLs that reflect volatility; descriptions are less volatile than live status or counts;
- batch IDs where the API allows it;
- deduplicate IDs before hydration;
- never let a cache hit bypass access checks for private or user-specific data.

This is required because the project statement specifically emphasises quota discipline and fixture-based CI.

See [[sqlite-fixture-caching]].

## Fixture isolation and live tests

CI must not call the live API. Use deterministic JSON fixtures or mocked provider responses for unit and integration tests. Live API tests belong in a separate scheduled or manually triggered workflow with a strict fixed quota budget. Inject a `YouTubeProvider` interface and fail tests if a real provider is instantiated without an explicit live-test marker and credentials.

## Failure policy and observability

Handle `quotaExceeded` as a distinct failure mode, not as a transient network error. Do not blindly retry quota exhaustion. For transient failures, use bounded exponential backoff with jitter. When the budget guard rejects a workflow before the first API call, the MCP layer should return an actionable error rather than a generic failure.

## Acceptance checklist

- [ ] costs are centralised and current against official docs;
- [ ] over-budget workflows are rejected before the first API call;
- [ ] concurrent reservations cannot overspend the ledger;
- [ ] cache keys include all response-affecting parameters;
- [ ] CI consumes zero YouTube quota;
- [ ] live tests are separately gated and auditable;
- [ ] `quotaExceeded` has a regression test.

## Related notes

- [[sqlite-fixture-caching]]
- [[oauth2-token-lifecycle]]
- [[mcp-protocol-architecture]]
- [[adr-governance-workflow]]
