---
title: FR-5 Playlist Constraint Planning Algorithm
tags: [algorithms, playlist, duration, ranking, FR-5]
status: research
---

# FR-5 Playlist Constraint Planning Algorithm

## Requirement interpretation

FR-5 is the core user-value feature in the project statement: a natural-language request may specify a topic, total duration, maximum video length, and language, and the system must build a playlist that fits those constraints, present it for explicit user confirmation, and only then create it in the user's YouTube account.

The requirement is intentionally strict: the system must separate intent parsing from candidate selection. A model may interpret the request, but its output must be converted into a typed and validated constraint object before the planner reads it. The ranking algorithm must be deterministic and must never let metadata override policy or human confirmation. See [[prompt-injection-defense]], [[cosine-similarity-tfidf]], and [[youtube-api-quotas]].

## Constraint schema

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class PlaylistConstraints:
    topic: str
    target_seconds: int
    max_video_seconds: int
    language: str | None = None
    tolerance_seconds: int = 300
    candidate_limit: int = 100
```

Validation must include:

- positive target duration;
- positive maximum per-video duration;
- non-empty topic text;
- allowed language codes or `None`;
- bounded candidate count;
- explicit handling of ambiguous phrases such as “two hours” when they could mean “exactly two hours” or “at most two hours.”

Convert phrases such as “two hours” into seconds before evaluation. Parse ISO 8601 durations such as `PT1H2M3S` into integer seconds, and never compare duration strings lexicographically.

## Candidate preparation

1. search the official API for candidate videos;
2. deduplicate by canonical video ID;
3. hydrate duration and metadata in batches;
4. reject inaccessible videos and unknown durations where a hard guarantee is required;
5. exclude videos longer than the maximum allowed duration;
6. rank using [[cosine-similarity-tfidf]] and documented secondary signals;
7. preserve provenance for why each candidate passed or failed.

The planner should never trust unresolved metadata without validation. If there are too few valid candidates, the planner should say so and suggest broadening the topic or relaxing the max length, rather than pretending the entire constraint set is satisfied.

## Greedy baseline

A greedy baseline is simple, explainable, and easy to test. It prioritises relevance, uses relevance-per-second as a tie-breaker, and caps channel concentration to avoid a playlist dominated by a single channel.

```python
def curate(candidates, constraints):
    valid = [
        c for c in candidates
        if 0 < c.duration_seconds <= constraints.max_video_seconds
        and 0.0 <= c.relevance <= 1.0
    ]
    valid.sort(key=lambda c: (
        -c.relevance,
        -(c.relevance / c.duration_seconds),
        c.video_id,
    ))

    selected, total, channel_counts = [], 0, {}
    ceiling = constraints.target_seconds + constraints.tolerance_seconds
    for c in valid:
        if total + c.duration_seconds > ceiling:
            continue
        if channel_counts.get(c.channel_id, 0) >= 3:
            continue
        selected.append(c)
        total += c.duration_seconds
        channel_counts[c.channel_id] = channel_counts.get(c.channel_id, 0) + 1
        if total >= constraints.target_seconds:
            break

    return {
        "videos": selected,
        "total_seconds": total,
        "target_seconds": constraints.target_seconds,
        "within_tolerance": abs(total - constraints.target_seconds)
            <= constraints.tolerance_seconds,
    }
```

This is illustrative, not the only acceptable design. The important point is that the planner states its objective explicitly and makes its selection criteria inspectable. Stable tie-breaking keeps tests deterministic.

## Alternative optimisation

For smaller candidate sets, a 0/1 knapsack or subset-sum dynamic program can optimise duration fit while maintaining relevance. The formal objective can be framed as:

\[
\max \sum_i x_i(w_r r_i - w_c c_i)
\]

subject to:

\[
\sum_i x_i d_i \le T + \epsilon, \quad x_i \in \{0, 1\}
\]

Here \(r_i\) is relevance, \(d_i\) is duration, \(c_i\) is a concentration penalty, \(T\) is target seconds, and \(\epsilon\) is the permitted overshoot. Bound candidate count and time horizon to keep runtime predictable.

## Semantics of “target duration”

The term “target duration” can mean different things:

- not to exceed the limit;
- reach at least the target;
- land within a tolerance window.

These are different constraints and should be disambiguated before the planner commits. When a planner cannot satisfy the hard constraints, it must fail explicitly and offer a retry with a broader topic, more relaxed max duration, or larger tolerance. It must never claim success when a hard constraint is violated.

## Confirmation and commit

Before a write occurs, the system should display:

- playlist title/topic;
- each item's title, channel, duration, and score;
- total duration and target comparison;
- language and any caveats;
- the exact proposal ID and a content hash for the proposal.

The algorithm creates a proposal, not a write. After explicit confirmation, the system must revalidate the exact proposal, OAuth state, channel availability, and quota budget before creating the playlist. This prevents a malformed or stale plan from being committed. See [[youtube-api-quotas]].

## Tests

The planner needs tests for:

- ambiguous or invalid requests;
- ISO duration parsing;
- empty or nearly empty candidates;
- all candidates exceeding max length;
- duplicate IDs;
- exact target and tolerance boundaries;
- over-target selections;
- missing durations;
- channel caps;
- stable ties;
- quota rejection before execution;
- confirmation bypass attempts.

An end-to-end MCP test should verify FR-5 as a user-facing workflow rather than only a value function.

## Related notes

- [[cosine-similarity-tfidf]]
- [[prompt-injection-defense]]
- [[youtube-api-quotas]]
- [[mcp-protocol-architecture]]
