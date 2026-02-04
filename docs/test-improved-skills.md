# Test Your Improved Skills - Quick Reference

## ✅ Changes Deployed

- **9 knowledge skills** now auto-load with `user-invocable: false`
- **5 critical action skills** have natural trigger phrases
- All changes deployed via `/forge-refresh --force`

---

## Quick Test Prompts

Copy and paste these to test if skills are working better:

### Knowledge Skills (Should Auto-Load Silently)

```
Create a Django model for User with email and password fields
```
Expected: Django naming conventions applied automatically

```
Help me build an MCP server with a database query tool
```
Expected: MCP security patterns mentioned automatically

```
Write a Python function to validate email addresses
```
Expected: Type hints and PEP standards applied automatically

```
Design test cases for a login form
```
Expected: Equivalence partitioning mentioned automatically

---

### Action Skills (Should Trigger from Natural Phrases)

#### PRD Management
```
Help me organize my PRD files
```
```
Update my PRD status to approved
```
```
Track my product requirements
```

#### Parallel Development
```
Run multiple agents on this feature
```
```
Split this work across parallel agents
```
```
Parallelize this development task
```

#### MCP Security
```
Secure my MCP server against attacks
```
```
Prevent prompt injection in my tool
```
```
Add proper authorization to my MCP
```

#### Network Debugging
```
Debug this failing API call
```
```
Check what's happening with network requests
```
```
Find which requests are failing
```

#### Console Debugging
```
Check what errors are in the console
```
```
Debug these JavaScript warnings
```
```
Investigate the browser logs
```

---

## What to Watch For

### ✅ Good Signs
- Skills mentioned without you asking
- Relevant patterns/guidelines automatically applied
- Context-aware responses
- Skills trigger from casual language

### ⚠️ Warning Signs
- Need to explicitly name skills
- Wrong skill triggers
- Skills don't trigger when they should
- Generic responses without skill context

---

## Report Results

After testing, note:
1. Which phrases worked well
2. Which skills triggered appropriately
3. Any unexpected behavior
4. Suggestions for improvement

Keep these notes for Phase 4 planning.

---

## Next Steps

If testing shows positive results:
- Continue to Phase 4 (10 more skills)
- See `skills-rewrites-ready-to-apply.md`
- Monitor for 1 week before full rollout

If testing shows issues:
- Document specific problems
- Adjust descriptions
- Test again
- Rollback if needed: `git checkout HEAD~1 -- plugins/*/skills/*/SKILL.md`
