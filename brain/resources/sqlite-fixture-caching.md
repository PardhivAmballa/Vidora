---
title: SQLite Response Cache and JSON Fixtures
tags: [sqlite, caching, testing, ci, quota, NFR-1, NFR-2]
status: research
---

# SQLite Response Cache and JSON Fixtures

## Goals

The system needs two separate mechanisms:

1. **Runtime cache:** reduces repeat calls to the official API and conserves quota.
2. **Test fixtures:** deterministic snapshots used by tests so CI consumes zero YouTube quota.

Runtime entries expire and need invalidation. Fixtures are versioned test data and should not change just because the live API changes. See [[youtube-api-quotas]] and [[mcp-protocol-architecture]].

## Cache keys

A key must include all parameters that can affect a response. A search key may include endpoint, normalised query, language, region, ordering, page token, and result count. Hash canonical JSON instead of concatenating ambiguous strings.

```python
import hashlib, json

def make_cache_key(endpoint: str, params: dict) -> str:
    canonical = json.dumps(
        {"endpoint": endpoint, "params": params},
        sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
```

Never include secrets in keys. For user-specific data, partition by a stable non-secret account identifier and enforce access control to prevent cross-account leakage.

## SQLite schema

```sql
CREATE TABLE IF NOT EXISTS api_cache (
    cache_key TEXT PRIMARY KEY,
    endpoint TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    created_at INTEGER NOT NULL,
    expires_at INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_api_cache_expiry ON api_cache(expires_at);
```

Use a separate table for quota accounting. SQLite transactions should make ledger reservations atomic. WAL mode can improve local reader/writer concurrency, but transactions should remain short and lock contention should be handled explicitly.

## Cache implementation sketch

```python
import json
import sqlite3
import time

class SQLiteCache:
    def __init__(self, path: str):
        self.path = path

    def get(self, key: str):
        with sqlite3.connect(self.path, timeout=5) as con:
            row = con.execute(
                "SELECT payload_json, expires_at FROM api_cache WHERE cache_key = ?",
                (key,),
            ).fetchone()
        if row is None:
            return None
        payload, expires_at = row
        if expires_at <= int(time.time()):
            self.delete(key)
            return None
        return json.loads(payload)

    def set(self, key: str, endpoint: str, payload, ttl_seconds: int):
        now = int(time.time())
        serialized = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
        with sqlite3.connect(self.path, timeout=5) as con:
            con.execute(
                "INSERT INTO api_cache "
                "(cache_key, endpoint, payload_json, created_at, expires_at) "
                "VALUES (?, ?, ?, ?, ?) "
                "ON CONFLICT(cache_key) DO UPDATE SET "
                "endpoint=excluded.endpoint, payload_json=excluded.payload_json, "
                "created_at=excluded.created_at, expires_at=excluded.expires_at",
                (key, endpoint, serialized, now, now + ttl_seconds),
            )

    def delete(self, key: str):
        with sqlite3.connect(self.path, timeout=5) as con:
            con.execute("DELETE FROM api_cache WHERE cache_key = ?", (key,))
```

Production hardening should add payload size limits, corruption handling, cache metrics, cleanup policy, and privacy controls.

## Provider and fixture isolation

Inject a provider interface. `FixtureYouTubeProvider` should read named JSON fixtures and return the same DTO shape as the production provider. Never use a live API as a hidden fallback when a fixture is missing.

```text
tests/
  fixtures/youtube/
    videos_python_intro.json
    search_distributed_systems.json
    channels_cs_education.json
  unit/
  integration/
```

Fixtures should be synthetic or sanitised. Do not copy real likes, subscriptions, OAuth responses, or private playlist data into the repository.

## TTL and invalidation

Use endpoint-specific TTLs. Search results may need a shorter TTL than channel descriptions; live status and counts can change quickly. After writes, invalidate affected cache entries. Expose retrieval timestamps when freshness matters and avoid promising real-time data from cached responses.

## Tests

- cache hit avoids provider call;
- miss calls provider and stores result;
- expired entry is a miss;
- changed parameters produce distinct keys;
- JSON round-trip preserves DTO fields;
- malformed fixture gives a clear error;
- fixture mode never uses the network;
- budget rejection happens before provider invocation;
- concurrent quota reservations cannot overspend.

## Related notes

- [[youtube-api-quotas]]
- [[oauth2-token-lifecycle]]
- [[github-actions-ci-setup]]
