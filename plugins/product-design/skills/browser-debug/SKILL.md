---
name: browser-debug
description: Capture browser console, network, and performance logs for debugging. Auto-loads when debugging browser issues, analyzing errors, or investigating page behavior. Provides systematic log capture workflow using Chrome DevTools MCP.
---

# Browser Debug Skill

Comprehensive browser log capture for AI-led debugging using Chrome DevTools MCP.

Works with any Chromium-based browser: **Dia, Chrome, Edge, Brave, Opera, etc.**

## When to Use This Skill

This skill auto-loads when:
- Debugging browser console errors
- Investigating network request failures (API errors, CORS issues)
- Analyzing page performance issues
- Reproducing and diagnosing user-reported bugs
- Conducting systematic browser debugging sessions
- Working with web applications during development

## Browser Compatibility

**✅ Supported Browsers** (Chromium-based):
- **Dia** (primary - Chromium-based browser)
- Google Chrome
- Microsoft Edge
- Brave Browser
- Opera
- Vivaldi
- Any browser using Chrome DevTools Protocol

**Why Chromium?** These browsers all use the Chrome DevTools Protocol, which provides consistent debugging APIs across platforms.

## Log Capture Workflow

### Step 1: Initialize Session
Create timestamped session directory for organized log storage:
- Directory: `~/browser-logs/sessions/YYYYMMDD-HHMMSS-{page-description}/`
- Symlink: `~/browser-logs/latest/` points to most recent session
- Configurable via `~/.claude/forge/config/browser-capture.yaml`

### Step 2: Capture Console Logs
Use Chrome DevTools MCP to capture all console messages with filtering:

**Error messages** (critical):
```python
mcp__plugin_product-design_chrome-devtools__list_console_messages(
    pageIdx=0,
    pageSize=100,
    types=["error"],
    includePreservedMessages=True  # Last 3 navigations
)
```

**Warnings** (important):
```python
mcp__plugin_product-design_chrome-devtools__list_console_messages(
    pageIdx=0,
    pageSize=100,
    types=["warn"],
    includePreservedMessages=True
)
```

**All logs** (context):
```python
mcp__plugin_product-design_chrome-devtools__list_console_messages(
    pageIdx=0,
    pageSize=100,
    types=["error", "warn", "info", "log", "debug"],
    includePreservedMessages=True
)
```

**Output files**:
- `console-error.log` - Only errors
- `console-warn.log` - Only warnings
- `console-all.log` - All console output

### Step 3: Capture Network Activity
Capture network requests with filtering:

**Failed requests** (4xx, 5xx errors):
```python
# List all requests first
mcp__plugin_product-design_chrome-devtools__list_network_requests(
    pageIdx=0,
    pageSize=100,
    resourceTypes=["xhr", "fetch", "document"],  # Exclude static assets
    includePreservedRequests=False
)

# Then filter for failures (status >= 400)
```

**XHR/Fetch API calls**:
```python
mcp__plugin_product-design_chrome-devtools__list_network_requests(
    pageIdx=0,
    pageSize=100,
    resourceTypes=["xhr", "fetch"],
    includePreservedRequests=False
)
```

**Get detailed request data**:
```python
mcp__plugin_product-design_chrome-devtools__get_network_request(
    reqid=67890,
    responseFilePath="/path/to/session/response-67890.json",
    requestFilePath="/path/to/session/request-67890.json"
)
```

**Output files**:
- `network-errors.log` - Failed requests only
- `network-all.log` - All network activity
- `network-detail.json` - Full request/response data

### Step 4: Capture Performance (Optional)
For performance debugging, capture trace data:

```python
# Start performance tracing
mcp__plugin_product-design_chrome-devtools__performance_start_trace(
    reload=False,  # Capture current session
    autoStop=False
)

# ... perform operations ...

# Stop and save trace
mcp__plugin_product-design_chrome-devtools__performance_stop_trace(
    filePath="/path/to/session/performance-trace.json.gz"
)
```

**Output file**:
- `performance-trace.json.gz` - Chrome DevTools-compatible trace

### Step 5: Analyze and Report
Generate debugging report with findings and recommendations:

1. **Parse captured logs** - Identify error patterns, failed requests, performance issues
2. **Correlate errors** - Match console errors with network failures
3. **Provide insights** - Root cause analysis and recommendations
4. **Suggest fixes** - Code changes or configuration updates

## Quick Reference: Forge CLI Command

For automated capture, use the `forge browser-capture` command:

```bash
# Capture everything
forge browser-capture --page "Dashboard" --all

# Capture only console errors
forge browser-capture --console --errors-only

# Capture network requests (exclude static resources)
forge browser-capture --network --exclude-static

# Custom output directory
forge browser-capture --page "Login Flow" --output ./test-logs --all
```

**Command options**:
- `--page` - Page description for session naming
- `--console` - Capture console messages only
- `--network` - Capture network requests only
- `--performance` - Capture performance trace only
- `--all` - Capture all logs (default)
- `--output` - Custom output directory
- `--exclude-static` - Exclude images, fonts, stylesheets
- `--errors-only` - Only capture errors and warnings

## Integration with Existing Skills

This skill complements other Product Forge debugging skills:

### Console Debugging Skill
**When to use**: Deep analysis of console error messages
- Use `/console-debugging` after capturing logs
- Provides detailed error analysis and stack trace interpretation
- Focus on JavaScript errors, syntax issues, runtime exceptions

### Network Inspection Skill
**When to use**: Detailed network request investigation
- Use `/network-inspection` after capturing network logs
- Analyzes API calls, CORS issues, authentication failures
- Request/response header analysis

### Debug Orchestrator Skill
**When to use**: Complex multi-layer debugging across frontend/backend
- Use `/debug-orchestrator` to coordinate browser + backend debugging
- Orchestrates multiple debugging skills for end-to-end investigation
- Manages complex debugging workflows

## Configuration

**Config file**: `~/.claude/forge/config/browser-capture.yaml`

Auto-created on first run with sensible defaults:

```yaml
output_dir: ~/browser-logs

console:
  levels: [error, warn, info, log]
  include_preserved: true  # Last 3 navigations

network:
  exclude_types: [image, font, stylesheet, media]
  save_errors_separately: true
  capture_bodies: false

performance:
  enabled: false  # Enable on-demand
  duration_seconds: 10

filters:
  exclude_urls:
    - "*.map"
    - "*analytics*"
    - "*tracking*"
  exclude_console_patterns:
    - "Download the React DevTools"

output:
  create_symlink: true  # Create 'latest' symlink
  max_sessions: 50      # Future: auto-cleanup
```

**Customization**:
- Edit `~/.claude/forge/config/browser-capture.yaml`
- Command-line options override config values
- Invalid config falls back to safe defaults

## Common Debugging Patterns

### Pattern 1: Error Investigation
1. Navigate to page with error in browser
2. Reproduce error or problematic behavior
3. Capture console errors immediately:
   ```bash
   forge browser-capture --console --errors-only
   ```
4. Analyze error messages in `console-error.log`
5. Check network logs for related API failures

### Pattern 2: Network Debugging
1. Navigate to page with API issues
2. Trigger API calls (login, data fetch, etc.)
3. Capture network activity:
   ```bash
   forge browser-capture --network --exclude-static
   ```
4. Review `network-errors.log` for failed requests
5. Examine `network-detail.json` for request/response details

### Pattern 3: Performance Analysis
1. Navigate to slow-loading page
2. Start performance trace before action:
   ```bash
   forge browser-capture --page "Slow Page" --performance
   ```
3. Perform slow operation
4. Analyze trace in Chrome DevTools (load `performance-trace.json.gz`)
5. Identify bottlenecks and optimization opportunities

### Pattern 4: Comprehensive Debugging
1. Start comprehensive capture:
   ```bash
   forge browser-capture --page "Full Debug Session" --all
   ```
2. Allow AI agent to interact with page
3. Logs automatically captured in organized structure
4. Review session directory for all artifacts
5. Use other skills for detailed analysis

## Best Practices

### During Debugging Sessions

1. **Always create timestamped session directories** - Keeps debugging history organized
2. **Start with errors, then warnings, then info logs** - Prioritize critical issues
3. **Exclude noisy logs** - Filter analytics, tracking, and development tools
4. **Save logs for later analysis** - Don't rely on memory or screenshots
5. **Document reproduction steps** - Note exact steps to reproduce issues

### File Organization

1. **Use descriptive page names** - `--page "User Login Flow"` not `--page "page1"`
2. **Check the 'latest' symlink** - Quick access to most recent session
3. **Archive old sessions** - Move to `archive/` folder after investigation
4. **Share session directories** - Entire folder contains all debugging context

### Integration with Development

1. **Capture before reporting bugs** - Include session directory with bug reports
2. **Use in CI/CD pipelines** - Automated log capture on test failures
3. **Create test fixtures** - Save successful sessions as baseline comparisons
4. **Review before deployments** - Check logs for warnings before production

## Troubleshooting

### Browser Not Responding

**Problem**: MCP tools timeout or return empty results

**Solutions**:
- Ensure browser is running with DevTools enabled
- Check Chrome DevTools Protocol port is accessible
- Restart browser if DevTools connection is stale
- Verify browser is Chromium-based (not Safari/Firefox)

### Large Log Volumes

**Problem**: Sessions with thousands of messages are slow

**Solutions**:
- Use `--errors-only` to capture critical messages
- Increase filters in config to exclude noisy patterns
- Use `--exclude-static` for network logs
- Capture in smaller time windows

### Sensitive Data in Logs

**Problem**: Logs may contain tokens, passwords, PII

**Solutions**:
- Add redaction patterns to config `filters.exclude_console_patterns`
- Don't share logs publicly without sanitization
- Use `capture_bodies: false` in config to exclude request/response bodies
- Review logs before sharing with team

### Missing Dependencies

**Problem**: `pyyaml` module not found

**Solutions**:
```bash
cd /Users/jeremiepoutrin/projects/github/jpoutrin/product-forge
uv pip install -e .
```

## Example Output

After running `forge browser-capture --page "Dashboard" --all`:

```
Capturing console logs...
Capturing network logs...
Capturing performance trace...

✅ Browser logs captured successfully!

📁 Session: /Users/jeremiepoutrin/browser-logs/sessions/20260218-143022-Dashboard/
   ✓ console messages: 47
   ✓ network requests: 23
   ✓ performance trace saved

💡 Use browser-debug skill for automated analysis
```

**Session directory structure**:
```
20260218-143022-Dashboard/
├── console-error.log       # 3 errors
├── console-warn.log        # 12 warnings
├── console-all.log         # 47 total messages
├── network-errors.log      # 2 failed requests
├── network-all.log         # 23 requests
├── network-detail.json     # Full request data
└── performance-trace.json.gz  # Performance profile
```

## Further Reading

- [Chrome DevTools Protocol Documentation](https://chromedevtools.github.io/devtools-protocol/)
- [Product Forge Console Debugging Skill](/console-debugging)
- [Product Forge Network Inspection Skill](/network-inspection)
- [Product Forge Debug Orchestrator Skill](/debug-orchestrator)

---

**Version**: 1.0.0
**Last Updated**: 2026-02-18
**Maintainer**: Product Forge Team
