# Logging and Audit Trail

The forge-cli package includes comprehensive file-based logging with audit capabilities for tracking hook executions, validations, and operations.

## Log Location

By default, logs are stored at:
```
~/.claude/forge/logs/forge-cli.log
```

## Log File Rotation

Logs automatically rotate when they reach 10MB. The system keeps 5 backup files:
```
~/.claude/forge/logs/
├── forge-cli.log         # Current log file
├── forge-cli.log.1       # Most recent backup
├── forge-cli.log.2
├── forge-cli.log.3
├── forge-cli.log.4
└── forge-cli.log.5       # Oldest backup
```

## Environment Variables

Customize logging behavior using environment variables:

### `FORGE_LOG_LEVEL`
Set the logging verbosity level.

**Values:** `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

**Default:** `INFO`

**Example:**
```bash
# Enable debug logging
export FORGE_LOG_LEVEL=DEBUG
forge validate new-file

# Quiet logging (errors only)
export FORGE_LOG_LEVEL=ERROR
forge validate ownership
```

### `FORGE_LOG_DIR`
Override the default log directory.

**Default:** `~/.claude/forge/logs/`

**Example:**
```bash
# Use project-specific log directory
export FORGE_LOG_DIR=./logs
forge validate contains --contains "Task 1"

# Use custom absolute path
export FORGE_LOG_DIR=/var/log/forge
forge feedback save
```

### `FORGE_LOG_FILE`
Specify a custom log file name.

**Default:** `forge-cli.log`

**Example:**
```bash
# Use date-based log file
export FORGE_LOG_FILE="forge-$(date +%Y-%m-%d).log"
forge youtube "https://youtube.com/watch?v=..."

# Use operation-specific log
export FORGE_LOG_FILE="validation.log"
forge validate new-file
```

### `FORGE_LOG_CONSOLE`
Enable or disable console output (stderr).

**Values:** `1`, `0`, `true`, `false`, `yes`, `no`

**Default:** `true` (enabled)

**Example:**
```bash
# Disable console logging (file only)
export FORGE_LOG_CONSOLE=0
forge validate ownership

# Explicit enable
export FORGE_LOG_CONSOLE=1
forge feedback save
```

### `FORGE_LOG_MAX_BYTES`
Set maximum log file size before rotation (in bytes).

**Default:** `10485760` (10MB)

**Example:**
```bash
# Rotate at 5MB
export FORGE_LOG_MAX_BYTES=5242880
forge validate new-file

# Larger rotation threshold (50MB)
export FORGE_LOG_MAX_BYTES=52428800
forge youtube "..."
```

### `FORGE_LOG_BACKUP_COUNT`
Number of backup log files to keep.

**Default:** `5`

**Example:**
```bash
# Keep only 2 backups
export FORGE_LOG_BACKUP_COUNT=2
forge feedback save

# Keep 10 backups for long-term audit
export FORGE_LOG_BACKUP_COUNT=10
forge validate ownership
```

## Log Format

Each log entry includes:

```
YYYY-MM-DD HH:MM:SS | logger_name | LEVEL | message
```

**Example:**
```
2026-02-06 14:23:45 | forge_hooks | INFO | Logging initialized: /Users/user/.claude/forge/logs/forge-cli.log
2026-02-06 14:23:46 | forge_hooks | INFO | Running new-file validation: dir=specs, ext=.md, max_age=5
2026-02-06 14:23:46 | forge_hooks.audit | INFO | Validation: new-file - PASSED
```

## What Gets Logged

### Validation Commands
- Validation execution with parameters
- Validation results (PASSED/FAILED)
- Failure reasons
- Files involved

**Example:**
```
2026-02-06 14:23:45 | forge_hooks | INFO | Running ownership validation: dir=specs, ext=.md, max_age=5
2026-02-06 14:23:46 | forge_hooks.audit | WARNING | Validation: ownership - FAILED | Reason: Multiple tasks CREATE same file
```

### YouTube Transcript Fetching
- Video URL and ID
- Output path
- Success/failure status
- Error details if failed

**Example:**
```
2026-02-06 14:25:10 | forge_hooks | INFO | Fetching YouTube transcript: url=https://youtube.com/watch?v=abc123, output=.work/transcripts
2026-02-06 14:25:12 | forge_hooks | INFO | YouTube transcript saved: .work/transcripts/abc123.txt
2026-02-06 14:25:12 | forge_hooks.audit | INFO | Hook execution: youtube.fetch-transcript - SUCCESS | Details: {'video_id': 'abc123', 'output': '.work/transcripts/abc123.txt'}
```

### Feedback Operations
- Feedback save operations
- Number of items saved
- Parsing errors
- Loop prevention triggers

**Example:**
```
2026-02-06 14:30:00 | forge_hooks | INFO | Saving feedback from hook
2026-02-06 14:30:01 | forge_hooks | INFO | Saved 3 feedback items
2026-02-06 14:30:01 | forge_hooks.audit | INFO | Hook execution: feedback.save - SUCCESS | Details: {'count': 3}
```

## Viewing Logs

### Tail Live Logs
```bash
tail -f ~/.claude/forge/logs/forge-cli.log
```

### View Recent Activity
```bash
tail -n 100 ~/.claude/forge/logs/forge-cli.log
```

### Search for Validation Failures
```bash
grep "FAILED" ~/.claude/forge/logs/forge-cli.log
```

### Filter by Log Level
```bash
grep "ERROR" ~/.claude/forge/logs/forge-cli.log
grep "WARNING" ~/.claude/forge/logs/forge-cli.log
```

### View Audit Trail
```bash
grep "forge_hooks.audit" ~/.claude/forge/logs/forge-cli.log
```

### View Today's Activity
```bash
grep "$(date +%Y-%m-%d)" ~/.claude/forge/logs/forge-cli.log
```

## Configuration Examples

### Production: Minimal Logging
```bash
export FORGE_LOG_LEVEL=WARNING
export FORGE_LOG_CONSOLE=0
export FORGE_LOG_MAX_BYTES=52428800  # 50MB
export FORGE_LOG_BACKUP_COUNT=10
```

### Development: Verbose Logging
```bash
export FORGE_LOG_LEVEL=DEBUG
export FORGE_LOG_CONSOLE=1
export FORGE_LOG_DIR=./logs
```

### CI/CD: File-Only Logging
```bash
export FORGE_LOG_LEVEL=INFO
export FORGE_LOG_CONSOLE=0
export FORGE_LOG_DIR=/tmp/forge-ci-logs
export FORGE_LOG_FILE="forge-ci-${CI_JOB_ID}.log"
```

### Testing: Separate Test Logs
```bash
export FORGE_LOG_LEVEL=DEBUG
export FORGE_LOG_DIR=./test-logs
export FORGE_LOG_FILE="test-run-$(date +%Y%m%d-%H%M%S).log"
```

## Persistent Configuration

### Using direnv (.envrc)
```bash
# .envrc
export FORGE_LOG_LEVEL=DEBUG
export FORGE_LOG_DIR=./.forge-logs
```

### Using Shell Profile
```bash
# ~/.bashrc or ~/.zshrc
export FORGE_LOG_LEVEL=INFO
export FORGE_LOG_MAX_BYTES=5242880  # 5MB
```

### Using Docker
```dockerfile
ENV FORGE_LOG_LEVEL=INFO
ENV FORGE_LOG_DIR=/var/log/forge
ENV FORGE_LOG_CONSOLE=0
```

## Audit Trail Analysis

### Track Hook Executions
```bash
grep "Hook execution:" ~/.claude/forge/logs/forge-cli.log
```

### Count Validation Failures
```bash
grep "Validation:.*FAILED" ~/.claude/forge/logs/forge-cli.log | wc -l
```

### List All YouTube Downloads
```bash
grep "youtube.fetch-transcript - SUCCESS" ~/.claude/forge/logs/forge-cli.log
```

### Export Audit Data
```bash
grep "forge_hooks.audit" ~/.claude/forge/logs/forge-cli.log > audit-trail.txt
```

## Log Cleanup

Logs are automatically rotated, but you can manually clean old logs:

```bash
# Remove all backup logs (keep current only)
rm ~/.claude/forge/logs/forge-cli.log.*

# Remove logs older than 30 days
find ~/.claude/forge/logs -name "*.log*" -mtime +30 -delete

# Archive logs
tar -czf forge-logs-$(date +%Y%m%d).tar.gz ~/.claude/forge/logs/
```

## Integration with Monitoring

### Send Errors to Sentry/Bugsnag
Parse log files and forward ERROR level entries to monitoring services.

### Aggregate with ELK Stack
Configure Filebeat to ship logs to Elasticsearch for centralized logging.

### Alert on Failures
```bash
# Check for recent failures
if grep -q "FAILED" ~/.claude/forge/logs/forge-cli.log; then
    echo "Validation failures detected!" | mail -s "Forge Alert" admin@example.com
fi
```

## Security Considerations

- **Log Location**: Default log directory `~/.claude/forge/logs/` is user-specific
- **Permissions**: Log files are created with user read/write permissions only
- **Sensitive Data**: Logs may contain file paths and command arguments
- **Retention**: Configure `FORGE_LOG_BACKUP_COUNT` based on compliance requirements
- **Access Control**: Restrict access to log directory in shared environments

## Troubleshooting

### Logs Not Being Created
```bash
# Check log directory permissions
ls -la ~/.claude/forge/logs/

# Manually create directory
mkdir -p ~/.claude/forge/logs
chmod 700 ~/.claude/forge/logs

# Check disk space
df -h ~/.claude/forge/logs/
```

### Too Many Log Files
```bash
# Reduce backup count
export FORGE_LOG_BACKUP_COUNT=2

# Or disable rotation temporarily
export FORGE_LOG_MAX_BYTES=999999999999
```

### Cannot Find Logs
```bash
# Check where logs are being written
export FORGE_LOG_LEVEL=DEBUG
forge --version 2>&1 | grep "Logging initialized"
```

## Best Practices

1. **Development**: Use `DEBUG` level with console output enabled
2. **Production**: Use `INFO` or `WARNING` level with file-only logging
3. **CI/CD**: Use separate log files per job with job ID in filename
4. **Monitoring**: Regularly check for ERROR and WARNING entries
5. **Archival**: Periodically archive and compress old log files
6. **Privacy**: Avoid logging sensitive data (credentials, tokens, etc.)
