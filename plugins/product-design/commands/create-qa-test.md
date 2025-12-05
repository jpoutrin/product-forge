---
description: Create a new QA test procedure for a feature
argument-hint: "<feature-name> [--url <url>] [--priority <priority>]"
---

# create-qa-test

**Category**: Quality Assurance

## Usage

```bash
create-qa-test <feature-name> [--url <url>] [--priority <priority>] [--explore]
```

## Arguments

- `<feature-name>`: Required - Name of the feature to test (kebab-case)
- `--url`: Optional - Test environment URL for the feature
- `--priority`: Optional - Test priority (critical, high, medium, low). Default: medium
- `--explore`: Optional - Launch qa-tester agent to explore the feature via Playwright

## Execution Instructions for Claude Code

When this command is run, Claude Code should:

1. **Generate Test ID**
   - Format: `QA-YYYYMMDD-###-feature-name.md`
   - Use today's date
   - Find next sequential number for today

2. **Create Directory Structure** (if not exists)
   ```
   qa-tests/
   ├── draft/
   ├── active/
   ├── executed/
   ├── archived/
   └── screenshots/
   ```

3. **Prompt for Details** (if not provided)
   - Feature description
   - Test URL (if --url not specified)
   - Acceptance criteria
   - Prerequisites
   - Test data requirements

4. **Create QA Test File**
   - Place in `qa-tests/draft/` with status DRAFT
   - Include all required metadata
   - Generate test case placeholders based on feature

5. **Optional: Invoke qa-tester Agent**
   - If `--explore` flag is set, launch the qa-tester agent
   - Agent will navigate to URL and document test steps
   - Agent will take screenshots of key states

## File Template

```markdown
# QA Test Procedure: [Feature Name]

## Metadata
- **Test ID**: QA-YYYYMMDD-###
- **Feature**: [Feature name]
- **Application**: [App name]
- **URL**: [Test environment URL]
- **Created**: [YYYY-MM-DD]
- **Author**: [Name]
- **Status**: DRAFT
- **Priority**: [Critical|High|Medium|Low]
- **Estimated Time**: [X minutes]
- **PRD Reference**: [Link if applicable]

## Prerequisites
- [ ] [Required setup step 1]
- [ ] [Test account with appropriate permissions]
- [ ] [Test data prepared]

## Test Environment
- **URL**: [Test environment URL]
- **Browser**: Chrome (latest)
- **Credentials**: See password manager

---

## Test Cases

### TC-001: [Happy Path - Main Success Scenario]

**Objective**: Verify the main success flow for [feature]

**Preconditions**:
- User is logged in
- [Feature-specific preconditions]

#### Steps

| Step | Action | Expected Result | Pass/Fail | Notes |
|------|--------|-----------------|-----------|-------|
| 1 | Navigate to [URL] | [Page loads correctly] | ☐ | |
| 2 | [Action] | [Expected outcome] | ☐ | |
| 3 | [Action] | [Expected outcome] | ☐ | |

**Postconditions**: [Expected state after test]

---

### TC-002: [Validation Test]

**Objective**: Verify input validation for [feature]

| Step | Action | Expected Result | Pass/Fail | Notes |
|------|--------|-----------------|-----------|-------|
| 1 | [Submit with empty required field] | [Error message appears] | ☐ | |
| 2 | [Enter invalid format] | [Validation error shown] | ☐ | |

---

## Edge Cases & Error Scenarios

### EC-001: [Edge Case Description]

| Step | Action | Expected Result | Pass/Fail | Notes |
|------|--------|-----------------|-----------|-------|
| 1 | [Edge case action] | [Expected behavior] | ☐ | |

---

## Summary Checklist

### Critical Path
- [ ] TC-001: [Title]

### Validation
- [ ] TC-002: [Title]

### Edge Cases
- [ ] EC-001: [Title]

---

## Test Execution Log

| Date | Tester | Environment | Build | Result | Issues |
|------|--------|-------------|-------|--------|--------|
| | | | | | |

## Notes
- [Additional observations]
- [Known limitations]
```

## Example

```bash
# Create a basic QA test for login
create-qa-test user-login --url https://staging.example.com/login --priority critical

# Create a test and explore with Playwright
create-qa-test checkout-flow --url https://staging.example.com/checkout --explore

# Create a simple test, will prompt for URL
create-qa-test password-reset
```

## Output

```
Created: qa-tests/draft/QA-20250105-001-user-login.md

📋 QA Test Procedure: user-login
   Status: DRAFT
   Priority: Critical
   Location: qa-tests/draft/

Next steps:
1. Review and complete test cases
2. Add specific test data
3. Move to qa-tests/active/ when ready
```

## Integration with qa-tester Agent

When `--explore` flag is used:

1. Command creates the initial QA test file
2. Launches qa-tester agent with:
   - Feature name
   - URL to test
   - Path to QA test file
3. Agent navigates and documents steps
4. Agent takes screenshots to `qa-tests/screenshots/`
5. Agent updates the QA test file with discovered steps

## Related Commands

- `list-qa-tests` - List and filter existing QA tests
- `/prd-progress` - Check linked PRD implementation status
