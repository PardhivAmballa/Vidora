---
title: YouTube Data API v3 Quota Economics
tags: [youtube, api, architecture, reliability, FR-1, FR-3, FR-5]
status: research
---

# YouTube Data API v3 Quota Economics

## Purpose and project context

The YouTube Video Intelligence MCP Server uses the official YouTube Data API v3 to discover videos, inspect metadata, analyse an authorised user's library, and create playlists. Quota is a finite daily resource. A single user request can fan out into search, metadata hydration, channel lookups, and playlist operations. The server therefore needs a quota-aware provider boundary and a pre-flight budget decision before any remote call.

The project brief specifies a default allocation of **10,000 units per day**, requires tracking cost per request, and requires rejecting a workflow that would exceed the remaining budget before making an API call. It prohibits scraping, unofficial APIs, and creating extra Google Cloud projects to obtain more quota. See [[mcp-protocol-architecture]], [[sqlite-fixture-caching]], and [[adr-governance-workflow]].

> **Operational caveat:** endpoint costs and allocations can change. Treat the table below as a design baseline, then verify the current official YouTube Data API quota-cost documentation before release. Keep costs in configuration rather than scattering constants through business logic.

## Quota model

Let \(Q_d\) be the daily allocation, \(Q_u\) the units consumed, \(Q_r = Q_d-Q_u\) the estimated remaining budget, \(C(w)\) the planned workflow cost, and \(R\) a safety reserve for retries and concurrent work.

A workflow may start only if:

\[
C(w) + R \le Q_r
\]

The estimate must include every endpoint call in the plan, not just the first search. Reserve expected maximum calls or use a conservative upper bound. If a cost is unknown, fail closed or require an explicitly configured estimate.

## Endpoint cost baseline

This is a planning baseline, **not a substitute for current official documentation**.

| Operation | Endpoint | Planning cost | Notes |
|---|---|---:|---|
| Discover candidate videos | `search.list` | 100 units/request | Usually expensive; pagination multiplies cost. |
| Read playlist entries | `playlistItems.list` | 1 unit/request | Every page is another call. |
| Hydrate video metadata | `videos.list` | 1 unit/request | Batch IDs where supported. |
| Read channel metadata | `channels.list` | 1 unit/request | Batch IDs and cache stable metadata. |
| Create playlist | `playlists.insert` | Verify current cost | Write costs must be explicitly budgeted. |
| Add playlist item | `playlistItems.insert` | Verify current cost | Each insertion may incur a separate cost. |

Centralise verified costs:

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

Do not silently assume write costs from this example. Confirm them against official documentation before release.

## Pre-flight budget checks

Use three stages: plan expected operations, estimate their cost, then atomically reserve budget before calls begin. A pure guard is easy to test:

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

In production, `remaining` must come from a durable ledger, not an in-memory counter that resets with the MCP process. Use a SQLite transaction or equivalent atomic reservation so concurrent requests cannot both spend the same balance. Define the daily reset boundary explicitly; UTC is a reasonable default.

Track both estimated and observed spend. Log operation name, request count, estimate, outcome, and correlation ID, but never OAuth tokens or sensitive user data. Include retry cost in the plan.

## Caching and batching

- Cache stable `videos.list` and `channels.list` metadata by canonical ID.
- Cache search results by normalised query and every response-affecting parameter.
- Use TTLs that reflect volatility; descriptions change less frequently than live status or view counts.
- Batch IDs where supported, respecting endpoint limits.
- Deduplicate IDs before hydration.
- Never let a cache hit bypass access checks for private or user-specific data.

See [[sqlite-fixture-caching]].

## Fixture isolation

CI must not call the live API. Use deterministic JSON fixtures or mocked provider responses. Live API tests belong in a separate scheduled/manual workflow with a fixed quota budget. Inject a `YouTubeProvider` interface and use `FakeYouTubeProvider` in unit and CI tests. Fail tests if a real provider is instantiated without an explicit live-test marker and credentials.

## Failure policy and observability

Handle `quotaExceeded` distinctly from transient network errors. Do not blindly retry quota errors. For transient failures, use bounded exponential backoff with jitter. Return an actionable MCP error when the budget guard rejects a workflow before any network call.

## Acceptance checklist

- [ ] Costs are centralised and verified against official docs.
- [ ] Insufficient-budget workflows are rejected before the first API call.
- [ ] Concurrent reservations cannot overspend the ledger.
- [ ] Cache keys include all response-affecting parameters.
- [ ] CI consumes zero YouTube quota.
- [ ] Live tests are separately gated and auditable.
- [ ] `quotaExceeded` has a regression test.

## Related notes

- [[sqlite-fixture-caching]]
- [[oauth2-token-lifecycle]]
- [[mcp-protocol-architecture]]
- [[adr-governance-workflow]]
