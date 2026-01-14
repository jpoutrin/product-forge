# Product Forge Development Notes

## Critical: Always Edit Source Files

When fixing plugin issues, **always edit files in this project directory**, never in `~/.claude/plugins/cache/`. The cache is deployed from source via `claude plugin install`.

After changes, run `/forge-refresh --force` to redeploy.

## Python Compatibility

Hook scripts must support Python 3.9+. Use:
- `Optional[str]` not `str | None`
- `Optional[Path]` not `Path | None`
- `from typing import Optional`

## Claude Code Hook Schema

Prompt hooks must return JSON with `ok: boolean`:
```json
{"ok": true, "data": {...}}
```

Without `ok`, schema validation fails.
