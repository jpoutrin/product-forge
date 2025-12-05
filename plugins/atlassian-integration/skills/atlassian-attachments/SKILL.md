---
name: atlassian-attachments
description: Attach documents, screenshots, PDFs, and files to Jira issues and Confluence pages. Use when uploading evidence, documentation, or media to Atlassian products.
---

# Atlassian Attachments Skill

Attach files, screenshots, and documents to Jira issues and Confluence pages.

## Supported File Types

### Jira Attachments

| Category | Extensions | Max Size |
|----------|------------|----------|
| Images | `.png`, `.jpg`, `.jpeg`, `.gif`, `.svg`, `.webp` | 10 MB |
| Documents | `.pdf`, `.doc`, `.docx`, `.xls`, `.xlsx`, `.ppt`, `.pptx` | 10 MB |
| Text | `.txt`, `.md`, `.csv`, `.json`, `.xml`, `.yaml` | 10 MB |
| Archives | `.zip`, `.tar`, `.gz` | 10 MB |
| Code | `.js`, `.py`, `.java`, `.ts`, `.html`, `.css` | 10 MB |

### Confluence Attachments

| Category | Extensions | Max Size |
|----------|------------|----------|
| Images | `.png`, `.jpg`, `.jpeg`, `.gif`, `.svg` | 25 MB |
| Documents | `.pdf`, `.doc`, `.docx`, `.xls`, `.xlsx`, `.ppt`, `.pptx` | 100 MB |
| Media | `.mp4`, `.mov`, `.mp3` | 100 MB |
| Design | `.sketch`, `.fig`, `.psd`, `.ai` | 100 MB |

## Jira Attachment Workflows

### Attach Screenshot to Issue

```
Prompt: "Attach the screenshot at ./screenshots/bug-evidence.png to PROJ-123"

Steps:
1. Read the file from local path
2. Upload to Jira issue PROJ-123
3. Optionally add comment referencing attachment
```

### Attach Multiple Files

```
Prompt: "Attach all PNG files from ./qa-tests/screenshots/ to PROJ-456"

Steps:
1. List files matching pattern
2. Upload each file to the issue
3. Report success/failure for each
```

### Attach with Comment

```
Prompt: "Attach error-log.txt to BUG-789 with comment 'Stack trace from production'"

Steps:
1. Upload file to issue
2. Add comment mentioning the attachment
3. Link attachment in comment: [^error-log.txt]
```

## Confluence Attachment Workflows

### Attach to Page

```
Prompt: "Attach architecture-diagram.png to the 'System Design' page in TEAM space"

Steps:
1. Find page by title in space
2. Upload attachment to page
3. Return attachment URL for embedding
```

### Embed Image in Page

```
Prompt: "Add screenshot.png to the 'QA Results' page and embed it in the content"

Steps:
1. Upload attachment to page
2. Update page content with image macro:
   !screenshot.png|width=800!
```

### Attach PDF Documentation

```
Prompt: "Upload api-spec.pdf to the 'API Documentation' page"

Steps:
1. Upload PDF as attachment
2. Optionally add view file macro for inline preview
```

## Attachment Naming Conventions

### For QA Evidence

```
{test-id}-{description}-{timestamp}.{ext}

Examples:
- QA-20250105-001-login-error-20250105T143022.png
- QA-20250105-001-form-validation-20250105T143045.png
```

### For Bug Reports

```
{issue-key}-{description}.{ext}

Examples:
- BUG-123-stack-trace.txt
- BUG-123-screenshot-before.png
- BUG-123-screenshot-after.png
```

### For Documentation

```
{feature}-{version}-{type}.{ext}

Examples:
- auth-flow-v2-diagram.png
- api-v3-specification.pdf
- deployment-guide-v1.docx
```

## Jira Attachment Commands

### Add Attachment

```
Action: Add attachment to Jira issue
Issue: PROJ-123
File: /path/to/screenshot.png

Expected behavior:
- File uploaded to issue attachments
- Visible in Attachments section
- Downloadable by team members
```

### List Attachments

```
Action: List all attachments on PROJ-123

Response format:
- screenshot.png (234 KB) - Added by John on 2025-01-05
- error-log.txt (12 KB) - Added by Jane on 2025-01-04
```

### Delete Attachment

```
Action: Remove old-screenshot.png from PROJ-123

Note: Requires appropriate permissions
```

## Confluence Attachment Commands

### Add to Page

```
Action: Attach file to Confluence page
Space: TEAM
Page: "Sprint Review"
File: /path/to/presentation.pdf
```

### Embed in Content

```
Action: Embed image in page content
Space: TEAM
Page: "Architecture Overview"
File: system-diagram.png
Position: After "System Components" heading
Width: 800px
```

### Replace Attachment

```
Action: Update existing attachment
Space: TEAM
Page: "API Docs"
File: api-spec-v2.pdf
Replace: api-spec-v1.pdf
```

## Integration with QA Workflows

### Attach QA Test Evidence

When a QA test is executed:

1. **Capture screenshots during test**
   ```
   qa-tests/screenshots/QA-20250105-001/
   ├── 01-initial-state.png
   ├── 02-form-filled.png
   └── 03-error-state.png
   ```

2. **Create/update Jira issue**
   ```
   Create bug: "Login form validation not working"
   Project: QA
   ```

3. **Attach evidence**
   ```
   Attach all screenshots from qa-tests/screenshots/QA-20250105-001/
   to the created issue
   ```

4. **Add summary comment**
   ```
   "Test execution evidence attached:
   - [^01-initial-state.png] - Before test
   - [^02-form-filled.png] - Form with test data
   - [^03-error-state.png] - Error encountered"
   ```

### Sync QA Documentation to Confluence

```
Action: Upload QA test procedure to Confluence

Steps:
1. Convert QA markdown to Confluence format
2. Create/update page in QA space
3. Attach all element screenshots
4. Embed screenshots in page content
```

## Batch Operations

### Upload Directory Contents

```
Prompt: "Upload all files from ./release-assets/ to the 'v2.0 Release' Confluence page"

Behavior:
- Scan directory for supported files
- Upload each file as attachment
- Report progress and results
```

### Sync Screenshots to Issue

```
Prompt: "Sync screenshots from ./qa-tests/screenshots/PROJ-123/ to Jira issue PROJ-123"

Behavior:
- Compare local files with existing attachments
- Upload new files
- Optionally replace updated files
- Skip unchanged files
```

## Error Handling

### Common Errors

| Error | Cause | Resolution |
|-------|-------|------------|
| File too large | Exceeds size limit | Compress or split file |
| Unsupported type | Extension not allowed | Convert to supported format |
| Permission denied | No attach permission | Request project/space access |
| Issue not found | Invalid issue key | Verify issue exists |
| Page not found | Invalid page title/space | Check space key and page title |

### Handling Large Files

```
If file > max size:
1. For images: Compress or resize
2. For documents: Split into parts
3. For archives: Use cloud storage link instead

Alternative: Upload to cloud storage and link in description
```

## Best Practices

### Organization

1. **Use consistent naming** - Follow naming conventions above
2. **Group related files** - Attach all evidence for one issue together
3. **Add descriptions** - Include context in comments
4. **Clean up old attachments** - Remove outdated files

### Performance

1. **Compress images** before upload (PNG → optimized PNG or JPEG)
2. **Batch uploads** when attaching multiple files
3. **Check existing attachments** before uploading duplicates

### Security

1. **Redact sensitive data** from screenshots
2. **Check file contents** before uploading logs
3. **Use appropriate spaces/projects** for confidential docs

## Confluence Macros for Attachments

### Image Display

```
!filename.png!                    # Basic
!filename.png|width=600!          # With width
!filename.png|thumbnail!          # As thumbnail
```

### File Links

```
[^filename.pdf]                   # Download link
[View Document^filename.pdf]      # Custom link text
```

### Gallery View

```
{gallery:include=*.png}           # All PNG attachments
{gallery:include=screenshot-*}    # Matching pattern
```

### PDF Viewer

```
{viewfile:filename.pdf}           # Inline PDF viewer
{viewfile:filename.pdf|height=600}
```
