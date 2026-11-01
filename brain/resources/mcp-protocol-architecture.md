---
title: MCP Protocol Architecture for YouTube Video Intelligence
tags: [mcp, architecture, tools, resources, prompts, FR-1, FR-5]
status: research
---

# MCP Protocol Architecture

## Purpose

The Model Context Protocol (MCP) standardises how an AI application discovers and invokes capabilities exposed by a server. Here, the MCP server is a controlled adapter between a conversational AI client and the official YouTube Data API v3. The client interprets user intent and chooses a tool; the server validates arguments, enforces policy, executes deterministic logic, and returns structured results.

The project brief names Claude, ChatGPT, and Gemini as examples. Actual support depends on each product's current MCP integration and transport support; do not assume every client supports every transport. See [[youtube-api-quotas]], [[prompt-injection-defense]], and [[adr-governance-workflow]].

## Logical architecture

```text
User
  -> Conversational AI client
  -> MCP transport and protocol
  -> MCP server: Tools / Resources / Prompts
  -> Application services
       -> Similarity engine (TF-IDF + cosine)
       -> Playlist constraint planner
       -> Quota manager and cache
       -> OAuth/token manager
  -> YouTubeProvider interface
  -> Official YouTube Data API v3
```

Keep protocol concerns out of domain logic. Tool handlers should validate input, call a use-case service, convert results to MCP content, and map expected failures to safe errors.

## Transports

### stdio

A local client launches the server as a subprocess. MCP messages use standard input/output; diagnostics belong on standard error. This is a useful local default because it avoids opening a listening port.

- Never print banners or debug text to stdout.
- Keep credentials in environment variables or protected local configuration.
- Treat inherited environment variables as potentially sensitive.
- Do not commit real secrets or token files.

Illustrative configuration (adapt to the chosen client's current schema):

```json
{
  "mcpServers": {
    "youtube-video-intelligence": {
      "command": "python",
      "args": ["-m", "youtube_mcp.server"],
      "env": {
        "YOUTUBE_CLIENT_SECRETS_FILE": "/secure/path/client_secret.json"
      }
    }
  }
}
```

### HTTP

HTTP transport may suit separated or deployed clients. It adds authentication, TLS, origin policy, request limits, session management where applicable, and network-exposure concerns. Bind to loopback for local-only development unless remote access is an explicit requirement. Record transport choice in an ADR; see [[adr-governance-workflow]].

## Tools, Resources, and Prompts

### Tools

Tools are callable operations with validated inputs. Suggested tools:

| Tool | Purpose | Side effect |
|---|---|---|
| `find_similar_videos` | Rank videos using metadata | Read-only |
| `find_similar_channels` | Rank channels using metadata | Read-only |
| `analyse_my_library` | Aggregate authorised likes, subscriptions, and playlists | Read-only |
| `propose_playlist` | Build candidate playlist under FR-5 | None |
| `create_confirmed_playlist` | Create after explicit approval | Write |
| `get_quota_status` | Report quota ledger state | Read-only |

Bind confirmation to a specific proposal ID, account, title, and item list. A vague confirmation string is not a sufficient safeguard.

### Resources

Resources expose readable context such as project policy, quota status, cached metadata, or generated analysis reports. Define identifiers and access rules. Do not expose OAuth tokens, raw personal-library exports, or unbounded datasets.

### Prompts

A prompt can package the `video-to-playlist` workflow: summarise a seed video, find similar videos, propose a playlist, request confirmation, create it, and report analysis. A prompt is guidance, not an authorisation boundary. Server-side checks remain mandatory.

## Provider boundary

```python
from typing import Protocol, Sequence

class YouTubeProvider(Protocol):
    def search_videos(self, query: str, *, max_results: int = 25) -> Sequence[dict]: ...
    def get_videos(self, video_ids: Sequence[str]) -> Sequence[dict]: ...
    def get_channels(self, channel_ids: Sequence[str]) -> Sequence[dict]: ...
```

The production implementation wraps the official client library. A fixture implementation returns deterministic JSON. Convert external responses to internal DTOs so provider schema changes do not leak through the application.

## Errors and testing

Expected error classes include invalid arguments, unavailable resources, pre-flight quota rejection, OAuth re-authorisation required, missing YouTube channel, and transient provider failure. Avoid raw stack traces and provider response bodies in client-facing errors.

Test service logic, MCP tool discovery/invocation, fixture-backed provider contracts, and end-to-end FR-1 to FR-5. Keep live tests isolated. Include tests for hostile metadata, OAuth expiry, malformed IDs, and confirmation bypass.

## Design principles

1. Least privilege: minimum OAuth scopes.
2. Separation of transport, use cases, provider, and storage.
3. Explicit and auditable side effects.
4. Deterministic tests.
5. Traceability from requirements to tools, tests, skills, ADRs, and notes.

## Related notes

- [[youtube-api-quotas]]
- [[sqlite-fixture-caching]]
- [[prompt-injection-defense]]
- [[adr-governance-workflow]]
