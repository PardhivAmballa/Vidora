---
title: Google OAuth 2.0 Token Lifecycle
tags: [oauth2, google, security, authentication, NFR-3]
status: research
---

# Google OAuth 2.0 Token Lifecycle

## Context and key constraint

The server needs authorised access for user-specific operations such as reading liked videos, subscriptions, playlists, and creating playlists. Use Google OAuth 2.0 and request the minimum scopes required by implemented features.

The project brief highlights that refresh tokens issued while the OAuth consent screen is in **Testing** mode expire after seven days for the relevant external-user configuration. Design for re-authorisation rather than assuming refresh always works. Verify current Google documentation and consent-screen settings before deployment because behavior depends on app type, publishing status, scopes, and account configuration.

See [[mcp-protocol-architecture]], [[youtube-api-quotas]], and [[prompt-injection-defense]].

## Access token and refresh token

- **Access token:** short-lived credential sent to Google APIs.
- **Refresh token:** used to obtain a new access token, subject to revocation, expiry, policy, and consent-screen constraints.
- **Client secret:** OAuth application credential; not a user token and never committed.

Never put tokens in logs, fixtures, screenshots, AI prompts, or source control.

## Lifecycle

```text
Unauthenticated
  -> user completes consent
Authenticated
  -> access token expires
Refresh attempt
  -> success: Authenticated
  -> invalid_grant / revoked / expired: Reauthorization Required
  -> user consents again: Authenticated
```

Refresh failure is an expected state, not an unhandled stack trace. User-specific tools should fail closed and show a safe message explaining how to reconnect.

## Minimum scopes and local storage

Use read-only scopes for public metadata, account-data scopes for FR-3/FR-4, and playlist-management permission for FR-5. Do not request broad permissions “just in case.” Maintain a scope-to-feature table and verify granted scopes before enabling tools.

For local development:
1. Keep OAuth client configuration outside the repository or in an ignored local path.
2. Store token cache in a user-private directory with restrictive permissions.
3. Ignore client-secret and token files.
4. Never store tokens in fixtures or CI artifacts.
5. Prefer an OS keychain where practical; document limitations of a local token file.
6. Separate test credentials from personal development credentials.

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

On POSIX systems, a local token file can be restricted with `chmod 600`; Windows requires appropriate ACL handling. File permissions are only one layer of protection.

## Re-authorization behavior

- Detect refresh failures such as `invalid_grant`.
- Avoid repeatedly retrying a known-invalid token.
- Mark the account as requiring re-authorisation.
- Explain the next step without revealing credentials.
- After consent, verify granted scopes and account state.
- Handle accounts without a YouTube channel: playlist creation cannot proceed and must return an actionable explanation.

A successful token refresh does not guarantee the API call will succeed; missing scopes, inaccessible resources, quota exhaustion, and missing channel are distinct conditions.

## Testing

Use fake credentials and an injectable clock. Test absent token, successful refresh, seven-day test-mode expiry, revoked token, insufficient scopes, missing channel, safe storage, and absence of secrets from logs. CI must not need a real Google account. Live OAuth checks belong in a separately gated procedure.

## Related notes

- [[youtube-api-quotas]]
- [[sqlite-fixture-caching]]
- [[prompt-injection-defense]]
- [[adr-governance-workflow]]
