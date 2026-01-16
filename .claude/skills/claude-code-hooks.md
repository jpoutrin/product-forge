# Claude Code Hooks Reference

Complete reference for developing Claude Code hooks - command hooks, prompt hooks, data flow, testing, and debugging patterns.

## Hook Types

### Command Hooks

Execute shell commands at lifecycle events.

```json
{
  "type": "command",
  "command": "python3 ${CLAUDE_PLUGIN_ROOT}/scripts/my-hook.py",
  "timeout": 10
}
```

**Stdin**: Receives JSON hook context (see Data Flow section)
**Stdout**: Ignored unless hook fails
**Exit code**: Non-zero fails the hook chain

### Prompt Hooks

Run a prompt through Claude (Haiku by default) at lifecycle events.

```json
{
  "type": "prompt",
  "prompt": "Analyze this session and respond with JSON: {\"ok\": true, \"data\": {...}}",
  "timeout": 60
}
```

**Required**: Response must include `"ok": true` or `"ok": false` for schema validation
**Output**: NOT passed to subsequent hooks (see Data Flow)

## Hook Events

| Event | Trigger | Common Use Cases |
|-------|---------|------------------|
| `Stop` | Session ends (exit, Ctrl+C) | Notifications, cleanup, analysis |
| `Notification` | Claude requests user attention | Desktop alerts, sounds |
| `PreToolUse` | Before tool execution | Validation, logging |
| `PostToolUse` | After tool execution | Auditing, side effects |

## Data Flow

### What Command Hooks Receive (stdin)

```json
{
  "session_id": "uuid-string",
  "transcript_path": "/path/to/session.jsonl",
  "cwd": "/current/working/directory",
  "permission_mode": "default|acceptEdits",
  "hook_event_name": "Stop",
  "stop_hook_active": false
}
```

### Critical: Prompt Hook Output is NOT Piped

**Prompt hooks return JSON to Claude Code, but this output is NOT passed to subsequent command hooks.**

To access prompt hook results from a command hook:
1. Read the `transcript_path` file
2. Parse the JSONL to find the prompt hook's response
3. Extract your data from there

### Environment Variables

| Variable | Description |
|----------|-------------|
| `CLAUDE_PLUGIN_ROOT` | Plugin installation directory |
| `CLAUDE_SESSION_ID` | Current session UUID |

## Execution Order

Hooks in the same array execute **sequentially** in order:

```json
{
  "hooks": [
    { "type": "command", "command": "first.sh" },   // Runs 1st
    { "type": "prompt", "prompt": "..." },          // Runs 2nd
    { "type": "command", "command": "third.sh" }    // Runs 3rd
  ]
}
```

**Best practice**: Put notification/logging hooks first to confirm the event fires, before dependent logic.

## Testing Hook Scripts

### Direct Testing with Mock Input

```bash
# Test with mock JSON
echo '{"session_id": "test-123", "cwd": "/tmp", "hook_event_name": "Stop"}' | python3 my-hook.py 2>&1

# Test with specific data structure
echo '{"feedback": [{"type": "bug", "title": "Test"}]}' | python3 save-feedback.py 2>&1
```

### Debug Logging Pattern

Add to hook scripts to capture actual stdin:

```python
import sys
from pathlib import Path
from datetime import datetime

def parse_input_with_debug():
    raw_input = sys.stdin.read()

    # Write to debug file
    debug_file = Path.home() / ".claude" / "learnings" / "debug-stdin.txt"
    debug_file.parent.mkdir(parents=True, exist_ok=True)
    with open(debug_file, "a") as f:
        f.write(f"\n=== {datetime.now().isoformat()} ===\n")
        f.write(f"Raw input ({len(raw_input)} chars):\n")
        f.write(raw_input if raw_input else "(empty)")
        f.write("\n")

    return json.loads(raw_input) if raw_input.strip() else {}
```

### Verify Debug Output

```bash
cat ~/.claude/learnings/debug-stdin.txt
```

## Reading Transcript Files

Transcript files are JSONL (one JSON object per line):

```python
from pathlib import Path
import json

def read_transcript(transcript_path: str) -> list:
    """Read all entries from a transcript file."""
    entries = []
    with open(transcript_path, 'r') as f:
        for line in f:
            if line.strip():
                entries.append(json.loads(line))
    return entries

def find_prompt_hook_response(entries: list, prompt_substring: str) -> dict:
    """Find the response to a specific prompt hook."""
    for entry in reversed(entries):  # Recent entries first
        if entry.get('type') == 'assistant':
            content = entry.get('content', '')
            # Look for JSON response matching your prompt
            if prompt_substring in str(entry):
                return entry
    return {}
```

## Common Patterns

### Notification-First Pattern

Always notify before complex logic to confirm hook fires:

```json
{
  "hooks": [
    { "type": "command", "command": "notify.sh Stop" },
    { "type": "prompt", "prompt": "Analyze session..." },
    { "type": "command", "command": "save-results.py" }
  ]
}
```

### Graceful Degradation

Hook scripts should exit 0 even on errors to not block the hook chain:

```python
def main():
    try:
        # Hook logic
        pass
    except Exception as e:
        print(f"[hook] Error (non-fatal): {e}", file=sys.stderr)
    return 0  # Always succeed
```

### Python 3.9+ Compatibility

Hook scripts must support Python 3.9+:

```python
# Good
from typing import Optional
def foo(x: Optional[str] = None) -> Optional[Path]:

# Bad (3.10+ only)
def foo(x: str | None = None) -> Path | None:
```

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| Hook never runs | Event not triggering | Add notify hook first to confirm |
| Empty stdin | Normal for some events | Check `hook_event_name` in context |
| Prompt output missing | Output not piped | Read from `transcript_path` instead |
| Hook times out | Processing too slow | Increase `timeout` or optimize |
| JSON parse error | Invalid response format | Ensure `"ok": true/false` in prompt hooks |

## Redeploying After Changes

Always redeploy plugins after editing hook scripts:

```bash
/forge-refresh --force
```

Or for a specific plugin:

```bash
/forge-refresh --force claude-code-dev
```
