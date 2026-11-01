---
title: FR-5 Playlist Constraint Planning Algorithm
tags: [algorithms, playlist, duration, ranking, FR-5]
status: research
---

# FR-5 Playlist Constraint Planning Algorithm

## Requirement interpretation

FR-5 accepts a natural-language request containing topic, target total duration, maximum per-video duration, and language. The system generates a compliant candidate playlist, presents it, and creates it in the user's account only after explicit confirmation.

Separate intent parsing from candidate selection. An AI model may parse the request, but its output must become a typed, validated object. The selection algorithm is deterministic and must not treat metadata as policy. See [[prompt-injection-defense]], [[cosine-similarity-tfidf]], and [[youtube-api-quotas]].

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

Validate positive durations, upper bounds, non-empty topic, allowed language codes, and candidate limits. Convert phrases such as “two hours” into seconds. Ask a clarifying question if “two-hour playlist” could mean exactly two hours or at most two hours.

## Candidate preparation

1. Search the official API for candidate videos.
2. Deduplicate by canonical video ID.
3. Hydrate duration and metadata in batches.
4. Exclude inaccessible videos and unknown durations where hard guarantees are needed.
5. Exclude videos longer than the maximum.
6. Rank using [[cosine-similarity-tfidf]] and documented secondary signals.
7. Preserve provenance for why each candidate passed or failed.

Parse ISO 8601 durations such as `PT1H2M3S` into integer seconds. Never compare duration strings lexicographically.

## Greedy baseline

A greedy algorithm is simple and explainable, but not globally optimal. One heuristic is to prioritise relevance, use relevance-per-second as a tie-breaker, and cap channel concentration:

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

This is an illustrative heuristic; state the objective explicitly. The greedy ranking prioritises relevance, so it may leave a duration gap that a subset-sum algorithm could fill better. Stable tie-breaking makes tests repeatable.

## Alternative optimisation

For small candidate sets, a 0/1 knapsack or subset-sum dynamic program can optimise duration fit while rewarding relevance:

\[
\max \sum_i x_i(w_r r_i-w_c c_i)
\]

subject to:

\[
\sum_i x_i d_i \le T+\epsilon,\quad x_i\in\{0,1\}
\]

Here \(r_i\) is relevance, \(d_i\) duration, \(c_i\) channel concentration penalty, \(T\) target seconds, and \(\epsilon\) permitted overshoot. Bound candidate count and time horizon to keep runtime predictable.

## Define target semantics

A duration target can mean “do not exceed,” “reach at least,” or “land within a tolerance window.” These are different constraints. Parse or clarify intent. If too few relevant candidates remain after filtering, report the shortfall and offer to broaden the topic, relax the max length, or increase tolerance. Never claim success when a hard constraint is violated.

## Confirmation and commit

Display playlist title/topic, item titles/channels/durations/scores, total duration, target/tolerance, language, and caveats. The algorithm creates a proposal, not a side effect. After explicit confirmation, revalidate the exact proposal, OAuth state, channel availability, and quota budget. Budget playlist creation and each item insertion; see [[youtube-api-quotas]].

## Tests

Test ambiguous and invalid requests, ISO duration parsing, empty candidates, all-too-long candidates, duplicate IDs, exact target, tolerance boundaries, over-target candidates, missing durations, channel caps, stable ties, quota rejection, and confirmation bypass. Add an end-to-end MCP test for FR-5.

## Related notes

- [[cosine-similarity-tfidf]]
- [[prompt-injection-defense]]
- [[youtube-api-quotas]]
- [[mcp-protocol-architecture]]
