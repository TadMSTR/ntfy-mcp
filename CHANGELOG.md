# Changelog

All notable changes to ntfy-mcp are documented here.

## [Unreleased]

## [0.1.1] — 2026-04-20

### Fixed
- Empty-string env var bug: `os.getenv("VAR", default)` returns `""` when set but blank. Switched to `os.getenv("VAR") or default` for `NTFY_URL`, `NTFY_TOKEN`, and `NTFY_DEFAULT_TOPIC`.
- Header injection: user-supplied values (title, tags, click, icon) are now passed through `_clean()`, which strips `\r` and `\n` before writing to HTTP headers.
- Topic path traversal: topics containing `/` or `..` are now rejected with `{"ok": false, "error": "Invalid topic: ..."}` instead of silently hitting an unintended ntfy path.

### Changed
- Bumped `fastmcp` from `>=2.0.0` to `>=3.2.4` (patches a path traversal CVE in the SSE endpoint).
- Removed empty `lifespan` context manager and unused `ctx: Context` parameter from `server.py`. Clears `asynccontextmanager` and `Context` imports.
- Removed `apt-get install curl` from Dockerfile — not used at runtime; httpx handles all HTTP calls.
- Added `testpaths = tests` to `pytest.ini` so bare `pytest` works without specifying the directory.

### Added
- `.env.example` for quick setup reference.
- `requirements-dev.txt` (`pytest>=8.0.0`, `pytest-asyncio>=0.23.0`) so test dependencies are tracked.
- GitHub Actions CI workflow (`.github/workflows/ci.yml`): test matrix across Python 3.11/3.12/3.13 and pip-audit dependency scan.
- CI badge and Built-with-Claude-Code badge in README.
- Test for topic path traversal rejection (`test_send_notification_rejects_path_traversal_topic`).

## [0.1.0] — 2026-04-15

### Added
- Initial release: `send_notification` MCP tool proxying push notifications to ntfy via streamable-HTTP transport.
- Support for title, priority, tags, markdown, click URL, and icon header parameters.
- Bearer token authentication via `NTFY_TOKEN` env var.
- Docker-first deployment with configurable port via `MCP_PORT`.
