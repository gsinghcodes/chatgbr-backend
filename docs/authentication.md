# Authentication Architecture

## Overview

Two ways to authenticate: **email/password** and **GitHub OAuth**. Both converge on the same session model — a short-lived JWT access token (held client-side in `localStorage`) and a long-lived refresh token (stored server-side, hashed, delivered to the browser as an `httpOnly` cookie).

## Token model

| Token | Lifetime | Storage (client) | Storage (server) |
|---|---|---|---|
| Access token | Short (JWT, stateless) | `localStorage` | Not stored — verified via signature |
| Refresh token | 15 days | `httpOnly`, `secure`, `samesite=lax` cookie | Hashed, in `refresh_tokens` table |

**Why this split:**
- Access token in `localStorage` so it can be attached as `Authorization: Bearer <token>` on every API call.
- Refresh token in an `httpOnly` cookie so it's invisible to JS (XSS protection) — the browser sends it automatically, only to the backend.
- Refresh tokens are **hashed** at rest, same principle as passwords — a DB leak doesn't hand out usable tokens.

## `refresh_tokens` table

Tracks issued tokens per user for revocation support:

- `token_hash` — hash of the raw token (raw value never stored)
- `user_id`
- `expires_at`
- `revoked_at` — `NULL` while active; timestamped on logout/rotation. Never nulled back out — this is an audit trail, not a boolean flag.

## Flow 1 — Email/Password login

1. `POST /auth/login` — verify credentials, issue access token (JWT) + refresh token (created + hashed + persisted via `AuthService.create_refresh_token`)
2. Response body: `{ access_token }`. Refresh token is set via `Set-Cookie`, never appears in the JSON body.
3. Frontend stores `access_token` in `localStorage`.

## Flow 2 — GitHub OAuth login

1. `GET /auth/github` — generates a `state` value (CSRF protection), stores it in a short-lived `httponly` cookie, redirects to GitHub's authorize URL.
2. User approves on GitHub → GitHub redirects to `GET /auth/github/callback?code=...&state=...`.
3. Backend verifies `state` matches the cookie (constant-time compare), then:
   - Exchanges `code` for a GitHub access/refresh token
   - Fetches GitHub user profile + verified primary email
   - Creates or updates the local `User` record (storing GitHub identity + GitHub's own tokens for future API calls, e.g. repo listing)
   - Issues **our own** access token + refresh token (identical to the password flow, via `AuthService.create_refresh_token`)
4. Backend redirects the browser to `{FRONTEND_URL}/auth/github/callback?access_token=...`, **and sets the `refresh_token` cookie on this same redirect response** — this is the step that has to happen server-side, since a frontend page has no way to set an `httpOnly` cookie itself.
5. Frontend callback page reads `access_token` from the URL query param, stores it in `localStorage`, redirects to `/`.

```
User → GET /auth/github
     ← 302 to github.com (+ state cookie)
User → approves on GitHub
GitHub → GET /auth/github/callback?code&state
Backend → verify state → exchange code → create/update user
        → issue access_token + refresh_token
        → 302 to frontend (+ Set-Cookie: refresh_token)
Frontend → reads access_token from URL → localStorage → redirect to "/"
```

## Request authentication

Every `apiInstance` request attaches the access token via a request interceptor:

```
Authorization: Bearer <access_token>   (from localStorage, if present)
```

## Refresh flow (access token expiry)

1. Any request returns `401`.
2. Response interceptor on `apiInstance` catches it, calls `refreshToken()`.
3. `refreshToken()` is a **singleton in-flight promise** — if multiple requests 401 concurrently, only one `POST /auth/refresh` goes out; all callers await the same promise. Prevents a refresh stampede and duplicate token rotation races.
4. `POST /auth/refresh` reads the `refresh_token` cookie automatically (`withCredentials: true`), looks it up by hash, checks `revoked_at IS NULL` and `expires_at`, issues a new access token.
5. New access token is stored in `localStorage`; the original failed request is retried once (`_retry` flag prevents infinite loops if the retry also 401s).
6. If refresh itself fails (expired/revoked refresh token) → clear `localStorage`, redirect to `/login`.

## Logout

1. `POST /auth/logout` sends the `refresh_token` cookie automatically.
2. Backend hashes the incoming raw token, looks up the matching row, sets `revoked_at = now()` (doesn't delete/null the row — preserves the audit trail).
3. Backend clears the cookie via `delete_cookie` (must match the original `set_cookie` attributes — `httponly`, `secure`, `samesite`, `path` — or the browser won't recognize it as the same cookie).
4. Frontend clears `localStorage` and Redux auth state regardless of whether the API call succeeds (`finally` block) — local state shouldn't get stuck out of sync with a flaky network call.

## Session bootstrap (`AuthProvider`)

On app load, for any non-public route:
1. Check `localStorage` for an access token. None → redirect to `/login` immediately (no network round trip).
2. Token present → `GET /auth/me` to validate it and hydrate user state into Redux.
3. `401` on that call → the response interceptor's refresh flow kicks in automatically; if refresh also fails, the interceptor handles the redirect to `/login`.