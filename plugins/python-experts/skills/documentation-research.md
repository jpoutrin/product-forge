---
name: Documentation Research
description: Enforces online documentation research before any technical implementation to ensure up-to-date best practices
version: 1.0.0
triggers:
  - implement
  - code
  - build
  - create
  - develop
  - technical
  - django
  - fastapi
  - fastmcp
  - react
  - typescript
  - python
---

# Documentation Research Skill

This skill automatically activates before any technical implementation to ensure all code follows current best practices by researching official documentation online.

## Core Principle

**NO IMPLEMENTATION WITHOUT DOCUMENTATION RESEARCH**

Before writing ANY code, Claude MUST:
1. Search and read official documentation online
2. Verify current best practices
3. Check for deprecated patterns
4. Report findings to user
5. Only then proceed with implementation

## Automatic Behaviors

When this skill activates, Claude will:

### 1. Identify Required Documentation

Based on the task, identify relevant documentation sources:

| Technology | Primary Documentation | Additional Resources |
|------------|----------------------|---------------------|
| Django | docs.djangoproject.com | Django REST Framework docs |
| FastAPI | fastapi.tiangolo.com | Pydantic docs, SQLAlchemy docs |
| FastMCP | FastMCP GitHub/docs | MCP Protocol specification |
| React | react.dev | TypeScript handbook |
| TypeScript | typescriptlang.org/docs | DefinitelyTyped |
| Python | docs.python.org | PyPI package docs |
| pytest | docs.pytest.org | Plugin documentation |

### 2. Research Protocol

```
Step 1: Search Official Documentation
   → Use WebSearch or WebFetch for official docs
   → Focus on latest stable version
   → Check for version-specific features

Step 2: Verify Current Version
   → Identify the latest stable release
   → Note any breaking changes
   → Check migration guides if relevant

Step 3: Review Best Practices
   → Read recommended patterns
   → Note anti-patterns to avoid
   → Check security recommendations

Step 4: Check for Updates
   → Review recent changelog
   → Look for deprecation notices
   → Identify new features

Step 5: Document Findings
   → Summarize key findings
   → List best practices to follow
   → Note patterns to avoid
```

### 3. Report Format

Before ANY implementation, report findings:

```
📚 Documentation Research Summary
══════════════════════════════════════════════════════════

🔍 Technology: [Framework/Library Name]
📦 Version: [Current Version]
📅 Last Checked: [Date]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ CURRENT BEST PRACTICES
─────────────────────────
• [Best practice 1]
• [Best practice 2]
• [Best practice 3]

⚠️ DEPRECATED PATTERNS (Avoid)
─────────────────────────────
• [Deprecated pattern 1] - Use [alternative] instead
• [Deprecated pattern 2] - Removed in [version]

🆕 NEW FEATURES TO CONSIDER
──────────────────────────
• [Feature 1] - Available since [version]
• [Feature 2] - Recommended for [use case]

🔒 SECURITY CONSIDERATIONS
─────────────────────────
• [Security note 1]
• [Security note 2]

📖 SOURCES
──────────
• [URL 1]
• [URL 2]

══════════════════════════════════════════════════════════
Ready to proceed with implementation? (yes/no)
```

## Technology-Specific Research

### Django Research Checklist

```
□ Check Django version (4.x, 5.x)
□ Review Class-Based Views vs Function-Based Views guidance
□ Check ORM query optimization docs
□ Review authentication backends
□ Check middleware ordering requirements
□ Review CSRF protection requirements
□ Check static/media file handling
□ Review Django REST Framework patterns (if using DRF)
```

### FastAPI Research Checklist

```
□ Check FastAPI version
□ Review Pydantic V2 migration (if applicable)
□ Check async/await best practices
□ Review dependency injection patterns
□ Check OAuth2/JWT implementation
□ Review response models and status codes
□ Check background task patterns
□ Review OpenAPI schema customization
```

### FastMCP Research Checklist

```
□ Check FastMCP version
□ Review MCP protocol specification
□ Check tool definition patterns
□ Review resource provider patterns
□ Check prompt template syntax
□ Review Claude Code integration
□ Check error handling requirements
□ Review testing approaches
```

### React/TypeScript Research Checklist

```
□ Check React version (18.x features)
□ Review hooks best practices (useEffect, useCallback, useMemo)
□ Check TypeScript strict mode settings
□ Review state management recommendations
□ Check data fetching patterns (TanStack Query, SWR)
□ Review form handling libraries
□ Check component composition patterns
□ Review testing library usage
```

### Python Testing Research Checklist

```
□ Check pytest version and plugins
□ Review fixture patterns
□ Check async testing setup
□ Review mocking best practices
□ Check coverage configuration
□ Review parameterized testing
□ Check CI/CD integration
□ Review test organization patterns
```

## Search Strategies

### Using WebSearch

```python
# Search for specific documentation
WebSearch("Django 5.0 class based views best practices")
WebSearch("FastAPI Pydantic V2 migration guide")
WebSearch("React 18 useEffect best practices 2024")
WebSearch("FastMCP tool definition example")
```

### Using WebFetch

```python
# Fetch specific documentation pages
WebFetch("https://docs.djangoproject.com/en/5.0/topics/class-based-views/")
WebFetch("https://fastapi.tiangolo.com/tutorial/")
WebFetch("https://react.dev/reference/react/useEffect")
```

## Enforcement Rules

1. **No Code Without Research**
   - If research step is skipped, STOP and research first
   - Do not rely on training data alone
   - Always verify against current documentation

2. **Version Verification**
   - Always check which version is being used
   - Ensure patterns match the version
   - Note version-specific features

3. **Deprecation Awareness**
   - Check for deprecated APIs before using
   - Use recommended alternatives
   - Avoid patterns marked for removal

4. **Security First**
   - Always check security documentation
   - Follow security best practices
   - Note any security advisories

## Integration with Technical Agents

All technical specialist agents MUST:

1. **Before Implementation**
   - Invoke this skill automatically
   - Complete documentation research
   - Report findings to user

2. **During Implementation**
   - Reference documentation in comments
   - Follow documented patterns
   - Use recommended APIs

3. **After Implementation**
   - Verify code matches documentation
   - Update if patterns changed
   - Document any deviations

## Example Research Flow

```
User: "Create a Django model for users"

Claude (documentation-research skill activates):

1. Searches: "Django 5.0 custom user model best practices"
2. Fetches: Django auth documentation
3. Reports findings:

📚 Documentation Research Summary
══════════════════════════════════

🔍 Technology: Django
📦 Version: 5.0

✅ CURRENT BEST PRACTICES
• Always use AbstractUser or AbstractBaseUser for custom users
• Create custom user model BEFORE first migration
• Use get_user_model() instead of direct User import
• Define AUTH_USER_MODEL in settings

⚠️ DEPRECATED PATTERNS
• Extending default User model via Profile (legacy)
• Using username as primary identifier (email preferred)

🔒 SECURITY CONSIDERATIONS
• Use Django's password hashers
• Implement rate limiting on login
• Never store plain text passwords

📖 SOURCES
• https://docs.djangoproject.com/en/5.0/topics/auth/customizing/

══════════════════════════════════
Ready to proceed? (yes/no)

User: "yes"

Claude: Now implements following documented best practices...
```

## Quality Assurance

Before implementation is considered complete:
- [ ] Documentation was researched online
- [ ] Latest version patterns are used
- [ ] No deprecated patterns in code
- [ ] Security best practices followed
- [ ] Code comments reference documentation
