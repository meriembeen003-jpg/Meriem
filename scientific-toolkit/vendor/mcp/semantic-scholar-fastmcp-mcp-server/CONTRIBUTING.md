# Contributing

Thanks for your interest in contributing! This repo is maintained primarily by a single maintainer, so small, well-scoped PRs with clear context and basic verification go a long way.

## Before You Open a PR

- Keep PRs focused (one logical change set).
- Avoid including secrets (API keys, bearer tokens, emails tied to private accounts).
- If you add a new behavior that binds ports / starts servers, make it configurable (env toggle + host/port), and document it.

## Local Setup

```bash
python3 -m pip install -r requirements.txt
```

## Suggested Local Checks

Run at least the unit tests that don’t require external API access:

```bash
python3 -m pytest -q test/test_bridge.py test/test_rate_limiter.py
```

Optional sanity checks:

```bash
python3 -m compileall -q semantic_scholar run.py
```

If your change touches real API calls, please describe what you tested (and whether it requires `SEMANTIC_SCHOLAR_API_KEY`).

## Review Priorities (What Maintainers Look For)

- **Safety**: do not log `x-api-key`/`Authorization`; redact secrets in debug/error logs.
- **Defaults**: avoid surprising default behavior changes; keep new features behind env flags where appropriate.
- **Rate limiting**: keep limits consistent and avoid per-ID “buckets” that bypass throttling.
- **Connection reuse**: prefer the shared HTTP utilities (`semantic_scholar/utils/http.py`) rather than creating new clients per request.
- **Docs**: update `README.md` when adding env vars, endpoints, or behavior changes.

## PR Description Guidance

Please include:

- What and why (1–3 sentences)
- User-facing impact (config changes, new endpoints, behavior changes)
- How you tested (commands + results)

