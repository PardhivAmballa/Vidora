---
title: Google OAuth 2.0 Token Lifecycle
tags: [oauth2, google, security, authentication, NFR-3]
status: research
---

# Google OAuth 2.0 Token Lifecycle

## Context and design constraint

The system needs authorised access for user-specific operations such as reading liked videos, subscriptions, playlists, and creating playlists. The project statement makes this explicit: use Google OAuth 2.0, request the minimum necessary scopes, store tokens securely, and handle re-authorisation gracefully when the OAuth consent screen is in Testing mode.

This is a high-risk area because failures here are not merely UX issues. An expired refresh token or missing scope can block FR-3, FR-4, and FR-5 entirely, and a missing YouTube channel can prevent playlist creation even when OAuth succeeds.

See [[mcp-protocol-architecture]], [[youtube-api-quotas]], and [[prompt-injection-defense]].

## Token model

- **Access token:** short-lived credential sent to Google APIs.
- **Refresh token:** long-lived credential used to mint new access tokens; may expire or be revoked.
- **Client secret:** OAuth application credential; never committed to the repository.

Never place tokens in logs, screenshots, AI prompts, fixtures, or source control. The project brief explicitly requires no secrets in the repo and no real user data or personal credentials in test assets.

## Lifecycle

```text
Unauthenticated
  -> user completes consent
Authenticated
  -> access token expires
Refresh attempt
  -> success: Authenticated
  -> invalid_grant / revoked / expired: Re-authorization Required
  -> user consents again: Authenticated
```

Refresh failure is expected operational behavior, not an unhandled exception. User-specific tools should fail closed and present a safe message telling the user to reconnect their YouTube account.

## Scope discipline and local storage

Use the minimum scopes that match the implemented feature set:

- read-only/public metadata for discovery and similarity scoring;
- user library access for FR-3 and FR-4;
- playlist write access only for FR-5.

Do not request broad permissions “just in case.” The server should maintain a scope-to-feature table and verify the granted scopes before enabling any tool that depends on them.

For local development:

1. keep OAuth client configuration outside the repository or in a local ignored path;
2. store token caches in a user-private directory with restrictive permissions;
3. ignore client-secret and token files;
4. never store tokens in fixtures or CI artifacts;
5. prefer OS keychain or secure local storage when available;
6. separate personal development credentials from test credentials.

Example `.gitignore` entries:

```gitignore
.env
.env.*
!.env.example
client_secret*.json
token*.json
*.token
credentials/
```

On POSIX systems, a local token file can be restricted with `chmod 600`; on Windows, use appropriate ACL permissions. File permissions are not the whole protection story, but they are a necessary baseline.

## Re-authorization and missing-channel handling

The project brief notes that refresh tokens issued while the OAuth consent screen is in Testing mode can expire after seven days for some external-user configurations. The application must therefore design for re-authorisation rather than assuming refresh always works.

Operational rules:

- detect refresh failures such as `invalid_grant`;
- avoid retry loops against a known-invalid token;
- mark the associated account as needing re-authorization;
- explain the next step without revealing credentials;
- verify granted scopes and account state after consent;
- handle the missing-channel case explicitly: a Google account without a YouTube channel cannot create playlists.

A successful token refresh still does not guarantee the API call will succeed. Missing scopes, inaccessible resources, quota exhaustion, and missing channel are distinct failure states and must be handled separately.

## Testing requirements

Use fake credentials and an injectable clock. At minimum, tests should cover:

- absent token;
- successful refresh;
- seven-day test-mode expiry;
- revoked token;
- insufficient scopes;
- missing channel;
- secure storage and redaction behaviour;
- absence of secrets from logs and fixtures.

CI must not require a live Google account. Live OAuth checks belong in a separately gated procedure or scheduled workflow.

## Related notes

- [[youtube-api-quotas]]
- [[sqlite-fixture-caching]]
- [[prompt-injection-defense]]
- [[adr-governance-workflow]]
