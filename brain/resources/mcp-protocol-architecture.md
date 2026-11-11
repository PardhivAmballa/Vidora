---
title: MCP Protocol Architecture for YouTube Video Intelligence
tags: [mcp, architecture, tools, resources, prompts, FR-1, FR-5]
status: research
---

# MCP Protocol Architecture

## Purpose

The project statement defines Vidora as an MCP server that lets a conversational AI client discover, analyse, and curate YouTube videos for an authorised user using the official YouTube Data API v3. The architecture is intentionally narrow: the AI client handles intent and presentation, while the MCP server is the policy boundary that validates arguments, enforces quota and OAuth rules, and performs only the operations the user has explicitly allowed.

This matters because the system is not just a search wrapper. It is a controlled automation layer for FR-1 to FR-5, with a strong requirement that playlist creation only happens after human confirmation and that write operations are tied to a specific proposal, not just vague user intent.

See [[youtube-api-quotas]], [[prompt-injection-defense]], [[oauth2-token-lifecycle]], and [[adr-governance-workflow]].

## System view

```text
User
  -> Conversational AI client
  -> MCP transport and protocol
  -> MCP server: Tools / Resources / Prompts
       -> Validation layer
       -> Similarity scoring (TF-IDF + cosine)
       -> Playlist constraint planner
       -> Quota manager and cache
       -> OAuth / token manager
  -> Provider boundary
  -> Official YouTube Data API v3
```

The key rule is simple: protocol concerns stay separate from domain logic. Tool handlers validate the input, call an application service, convert the response to MCP content, and translate failures into safe, user-facing errors. They should not silently recover from quota rejection, expired OAuth, malformed IDs, or confirmation bypass.

## Transport choices

### stdio

This is the default local transport. A client starts the server as a subprocess and speaks JSON-RPC over standard input/output. Standard error is reserved for diagnostics; stdout should stay clean and machine-readable.

Requirements for this project:

- never print banners or debug logs to stdout;
- keep secrets in environment variables or a protected local config;
- treat inherited environment variables as sensitive;
- never commit real credentials, token files, or client secrets.

### HTTP

HTTP is optional for remote or hosted deployments, but it adds more operational concerns: authentication, TLS, CORS/origin controls, session handling, request limits, and network exposure. Bind to loopback unless there is an explicit requirement for remote access. Record the transport decision in an ADR.

## Tools, resources, and prompts

### Tools

The product needs tools that are explicit and narrow. Good examples include:

| Tool | Purpose | Side effect |
|---|---|---|
| `find_similar_videos` | Rank videos using metadata | Read-only |
| `find_similar_channels` | Rank channels using metadata | Read-only |
| `recommend_videos_for_user` | Analyse authorised likes, subscriptions, and playlists | Read-only |
| `propose_playlist` | Build a candidate playlist under FR-5 | None |
| `create_confirmed_playlist` | Execute a playlist write after explicit approval | Write |
| `get_quota_status` | Return remaining budget and recent ledger state | Read-only |

Important: confirmation must be bound to a concrete proposal ID, a specific user account, and the exact playlist payload. A free-form confirmation such as “yes” is not enough.

### Resources

Resources should expose only read-only or policy-safe context: quota status, cached metadata, approved proposal state, or generated reports. They must not expose raw OAuth tokens, user-library exports, or unbounded datasets. The project brief explicitly forbids shipping real user data in fixtures or logs.

### Prompts

A prompt can package the `video-to-playlist` workflow:

1. summarise the seed video;
2. find similar videos (FR-1);
3. propose a playlist and ask for confirmation;
4. create the playlist only after approval (FR-5);
5. report a brief analysis of the result.

A prompt is guidance, not an authorisation boundary. The server still enforces validation, OAuth, quota, and confirmation checks.

## Provider boundary

The provider boundary isolates the YouTube API and keeps the rest of the system independent from external schema drift.

```python
from typing import Protocol, Sequence

class YouTubeProvider(Protocol):
    def search_videos(self, query: str, *, max_results: int = 25) -> Sequence[dict]: ...
    def get_videos(self, video_ids: Sequence[str]) -> Sequence[dict]: ...
    def get_channels(self, channel_ids: Sequence[str]) -> Sequence[dict]: ...
```

Production implementations wrap the official client library. Fixture-backed implementations return deterministic JSON, so unit and CI tests remain reproducible. Internal DTO conversion keeps external API churn from leaking into business logic.

## Error handling and testing

Expected failure modes include invalid arguments, unavailable resources, quota rejection, OAuth re-authorization required, missing YouTube channel, malformed metadata, and transient provider errors. Return user-safe messages without dumping raw stack traces or provider payloads.

Testing must cover:

- tool discovery and invocation through MCP;
- provider contract behaviour with fixtures;
- end-to-end verification of FR-1 through FR-5;
- hostile metadata and prompt injection;
- OAuth expiry and missing-channel cases;
- quotaExceeded before any live API call;
- confirmation bypass attempts.

The project statement also requires that live API tests remain separate from CI and use a fixed quota budget. CI should operate on mocks or recorded fixtures only.

## Design principles

1. least privilege for OAuth scopes;
2. separation of transport, use cases, provider, and storage;
3. explicit and auditable side effects;
4. deterministic, fixture-driven testing;
5. traceability from requirements to tools, tests, skills, ADRs, and notes.

## Related notes

- [[youtube-api-quotas]]
- [[sqlite-fixture-caching]]
- [[prompt-injection-defense]]
- [[oauth2-token-lifecycle]]
- [[adr-governance-workflow]]
