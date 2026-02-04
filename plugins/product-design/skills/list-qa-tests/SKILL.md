---
name: list-qa-tests
description: List QA test procedures with status and priority
argument-hint: "[--status <status>] [--priority <priority>] [--format <format>]"
---

# list-qa-tests

**Category**: Quality Assurance

## Usage

```bash
list-qa-tests [--status <status>] [--priority <priority>] [--format <format>]
```

## Arguments

- `--status`: Optional - Filter by status (draft, active, executed, archived)
- `--priority`: Optional - Filter by priority (critical, high, medium, low)
- `--format`: Optional - Output format (table, list, json). Default: table

## Execution Instructions for Claude Code

When this command is run, Claude Code should:

1. **Scan QA Test Directories**
   ```
   qa-tests/
   ├── draft/      → Status: DRAFT
   ├── active/     → Status: ACTIVE
   ├── executed/   → Status: EXECUTED
   └── archived/   → Status: ARCHIVED
   ```

2. **Parse Each QA Test File**
   - Extract metadata from markdown header
   - Read: Test ID, Feature, Priority, Status, Estimated Time
   - Count test cases (TC-###) and edge cases (EC-###)

3. **Apply Filters**
   - Filter by status if `--status` provided
   - Filter by priority if `--priority` provided

4. **Calculate Metrics**
   - For executed tests: Extract last execution result
   - Count total tests per status
   - Count by priority

5. **Format and Display Results**
   - Sort by priority (critical first), then by date

## Output Formats

### Table Format (default)

```
QA Tests - Found 8 tests

Status   | Priority | Test ID              | Feature        | Cases | Last Run   | Result
---------|----------|----------------------|----------------|-------|------------|--------
ACTIVE   | Critical | QA-20250105-001      | user-login     | 5     | -          | -
ACTIVE   | High     | QA-20250104-002      | checkout       | 8     | -          | -
EXECUTED | Critical | QA-20250103-001      | payment        | 6     | 2025-01-04 | PASS
EXECUTED | Medium   | QA-20250102-003      | search         | 4     | 2025-01-03 | FAIL
DRAFT    | Low      | QA-20250105-002      | preferences    | 2     | -          | -

Summary:
- Draft: 1 | Active: 2 | Executed: 2 | Archived: 0
- Critical: 2 | High: 1 | Medium: 1 | Low: 1
```

### List Format

```
📋 QA Tests - 8 total

🟢 ACTIVE (2 tests)

   ⚠️  QA-20250105-001-user-login.md [Critical]
       Feature: User Login Flow
       Cases: 3 TC + 2 EC | Est: 15 min
       Location: qa-tests/active/

   📄 QA-20250104-002-checkout.md [High]
       Feature: Checkout Process
       Cases: 6 TC + 2 EC | Est: 30 min
       Location: qa-tests/active/

✅ EXECUTED (2 tests)

   ✓ QA-20250103-001-payment.md [Critical] - PASS
       Last run: 2025-01-04 by Jane
       Issues: None

   ✗ QA-20250102-003-search.md [Medium] - FAIL
       Last run: 2025-01-03 by John
       Issues: #123, #124

📝 DRAFT (1 test)

   📄 QA-20250105-002-preferences.md [Low]
       Feature: User Preferences
       Cases: 2 TC | Est: 10 min
```

### JSON Format

```json
{
  "total": 8,
  "summary": {
    "by_status": {
      "draft": 1,
      "active": 2,
      "executed": 2,
      "archived": 3
    },
    "by_priority": {
      "critical": 2,
      "high": 1,
      "medium": 1,
      "low": 1
    }
  },
  "tests": [
    {
      "test_id": "QA-20250105-001",
      "file": "qa-tests/active/QA-20250105-001-user-login.md",
      "feature": "user-login",
      "status": "active",
      "priority": "critical",
      "test_cases": 3,
      "edge_cases": 2,
      "estimated_time": 15,
      "last_execution": null
    }
  ]
}
```

## Examples

```bash
# List all QA tests
list-qa-tests

# List only active tests
list-qa-tests --status active

# List critical and high priority tests
list-qa-tests --priority critical
list-qa-tests --priority high

# List executed tests in list format
list-qa-tests --status executed --format list

# Export all tests as JSON
list-qa-tests --format json
```

## Error Handling

- If `qa-tests/` directory doesn't exist: Show message and offer to create it
- If no tests match filters: Show "No tests found matching criteria"
- If test file has invalid metadata: Show with status "UNKNOWN"

## Metrics Displayed

| Metric | Description |
|--------|-------------|
| Cases | Number of test cases (TC-###) |
| Edge Cases | Number of edge cases (EC-###) |
| Est Time | Estimated execution time from metadata |
| Last Run | Date of last execution (from execution log) |
| Result | Last execution result (PASS/FAIL) |
| Issues | Linked issue numbers from execution log |

## Integration with PRD Traceability

When listing tests, optionally show PRD links:

```bash
list-qa-tests --show-prd
```

Adds column showing which PRD requirements each test covers.

## Related Commands

- `create-qa-test` - Create a new QA test procedure
- `/prd-progress` - Check PRD implementation status
- `/task-list` - List implementation tasks
