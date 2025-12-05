---
description: Review QA test and capture element screenshots to enrich documentation
argument-hint: "<qa-test-file> [--url <url>] [--update]"
---

# enrich-qa-test

**Category**: Quality Assurance

## Usage

```bash
enrich-qa-test <qa-test-file> [--url <url>] [--update] [--elements-only]
```

## Arguments

- `<qa-test-file>`: Required - Path to the QA test procedure file (e.g., `qa-tests/active/QA-20250105-001-login.md`)
- `--url`: Optional - Override the test URL from the document
- `--update`: Optional - Automatically update the QA test file with screenshots
- `--elements-only`: Optional - Only capture element screenshots, skip full-page captures

## Purpose

This command reviews an existing QA test procedure, identifies UI elements mentioned in test steps, captures targeted screenshots of each element using Playwright, and enriches the documentation with visual references.

## Execution Instructions for Claude Code

When this command is run, Claude Code should:

### Phase 1: Parse QA Test Document

1. **Read the QA test file**
   - Extract metadata (Test ID, URL, feature name)
   - Parse all test cases (TC-###) and edge cases (EC-###)

2. **Extract element references from test steps**
   - Scan for bold text: **Element Name**
   - Scan for quoted elements: "Element Name"
   - Identify action + element patterns:
     - "Click the **Login** button"
     - "Enter text in the **Email** field"
     - "Select from the **Country** dropdown"

3. **Build element extraction list**
   ```
   Elements found in QA-20250105-001-login.md:

   TC-001:
   - Step 2: Email field (input)
   - Step 3: Password field (input)
   - Step 4: Login button (button)

   TC-002:
   - Step 1: Forgot password link (link)
   ```

### Phase 2: Capture Screenshots

1. **Navigate to test URL** using Playwright MCP
   ```
   browser_navigate → {url from metadata or --url}
   ```

2. **Take initial full-page snapshot**
   ```
   browser_snapshot → understand page structure
   browser_take_screenshot → screenshots/{test-id}/00-initial-state.png
   ```

3. **For each identified element:**
   - Locate element using accessibility tree or selectors
   - Capture element screenshot
   - Save to `screenshots/{test-id}/elements/{element-name}.png`

4. **Handle element states** (if applicable)
   - Default state
   - Hover state (if interactive)
   - Focus state (if input)
   - Error state (if validation element)

### Phase 3: Generate Element Reference

Create an element reference section:

```markdown
## Element Visual Reference

| Element | Screenshot | Location | Test Case |
|---------|------------|----------|-----------|
| Email field | ![](./elements/email-field.png) | Login form | TC-001 Step 2 |
| Password field | ![](./elements/password-field.png) | Login form | TC-001 Step 3 |
| Login button | ![](./elements/login-button.png) | Form footer | TC-001 Step 4 |
| Forgot password | ![](./elements/forgot-password-link.png) | Below form | TC-002 Step 1 |
```

### Phase 4: Update Documentation (if --update)

1. **Create elements directory**
   ```
   qa-tests/screenshots/{test-id}/elements/
   ```

2. **Insert Element Reference section** after Metadata

3. **Add inline screenshots** to test steps (optional)
   ```markdown
   | 2 | Enter "test@example.com" in **Email field** ![](./elements/email-field.png) | Email accepted | ☐ | |
   ```

4. **Update Screenshots section** in test document

## Output

### Without --update

```
📋 QA Test Analysis: QA-20250105-001-login.md

URL: https://staging.example.com/login
Test Cases: 3 | Edge Cases: 2

🔍 Elements Identified:

   TC-001: User Login Flow
   ├── Email field (input)
   ├── Password field (input)
   └── Login button (button)

   TC-002: Forgot Password
   └── Forgot password link (link)

   EC-001: Invalid Credentials
   └── Error message (alert)

📸 Screenshots Captured:

   screenshots/QA-20250105-001/
   ├── 00-initial-state.png
   └── elements/
       ├── email-field.png
       ├── password-field.png
       ├── login-button.png
       ├── forgot-password-link.png
       └── error-message.png

💡 Run with --update to add these to the QA test document
```

### With --update

```
📋 QA Test Enriched: QA-20250105-001-login.md

✅ Added Element Visual Reference section
✅ Captured 5 element screenshots
✅ Updated Screenshots metadata

   Modified: qa-tests/active/QA-20250105-001-login.md
   Created:  qa-tests/screenshots/QA-20250105-001/elements/
```

## Element Detection Patterns

The command scans for these patterns:

| Pattern | Example | Element Type |
|---------|---------|--------------|
| `**Name** button` | Click **Login** button | button |
| `**Name** field` | Enter in **Email** field | input |
| `**Name** link` | Click **Forgot password** link | link |
| `**Name** dropdown` | Select from **Country** dropdown | select |
| `**Name** checkbox` | Check **Remember me** checkbox | checkbox |
| `**Name** icon` | Click **menu** icon | button/icon |
| `**Name** tab` | Select **Settings** tab | tab |
| `**Name** modal` | Close **confirmation** modal | dialog |
| `"Name"` in quotes | Click "Submit" | inferred |

## Error Handling

```
⚠️  Element not found: "Premium badge"
    Possible reasons:
    - Element requires login/authentication
    - Element loads dynamically
    - Element name doesn't match visible text

    Skipping this element. Capture manually if needed.

❌ Could not navigate to URL
    Check that the URL is accessible and try again.

⚠️  Some elements require interaction to appear
    The following were not captured:
    - Error message (appears after form submission)
    - Success toast (appears after action)

    Consider capturing these during manual test execution.
```

## Integration with Skills

This command uses:
- `qa-element-extraction` - Element identification patterns
- `qa-screenshot-management` - Screenshot naming and organization
- `qa-test-management` - Test file structure

## Example Workflow

```bash
# 1. Create a QA test
/create-qa-test user-login --url https://staging.example.com/login

# 2. Write test cases manually or with qa-tester agent

# 3. Enrich with element screenshots
/enrich-qa-test qa-tests/active/QA-20250105-001-user-login.md --update

# 4. Review enriched documentation
cat qa-tests/active/QA-20250105-001-user-login.md
```

## Related Commands

- `/create-qa-test` - Create new QA test procedure
- `/list-qa-tests` - List existing QA tests

## Related Skills

- `qa-element-extraction` - Element identification methodology
- `qa-screenshot-management` - Screenshot organization standards
