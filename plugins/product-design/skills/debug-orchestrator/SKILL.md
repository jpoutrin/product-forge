---
name: debug-orchestrator
description: Use when facing complex, multi-layered debugging issues that require coordinated investigation across different domains (frontend, backend, database, network, etc). Spawns specialized debug expert agents to handle specific aspects of the investigation.
user-invocable: true
---

# Debug Orchestrator

Coordinate complex debugging investigations by spawning and managing specialized debug expert agents. Use this when a debugging issue spans multiple domains or requires deep expertise in specific areas.

## When to Use

Invoke this skill when:
- Debugging issue involves multiple layers (UI, API, database, network)
- Root cause is unclear and requires systematic investigation
- Issue requires domain-specific expertise (e.g., React performance, SQL query optimization, network protocol analysis)
- Multiple hypotheses need to be tested in parallel
- Previous debugging attempts have failed or been incomplete

## Do NOT Use For

- Simple, single-domain bugs (use direct debugging instead)
- Issues with obvious root causes
- Syntax errors or compilation failures
- Basic troubleshooting that doesn't require expert coordination

## Orchestration Strategy

### 1. Issue Analysis

First, analyze the debugging request to understand:
- **Symptoms**: What's broken or behaving incorrectly?
- **Context**: What was the user doing when the issue occurred?
- **Scope**: Which systems/layers are potentially affected?
- **Evidence**: Logs, error messages, screenshots, network traces

### 2. Expert Agent Selection

Based on the analysis, spawn appropriate specialist agents:

#### Available Debug Experts

| Agent Type | When to Use | Example Issues |
|------------|-------------|----------------|
| `product-design:web-debugger` | Browser-based issues, DOM manipulation, JavaScript errors | React component not rendering, event handlers failing, XHR errors |
| `product-design:console-debugging` | JavaScript runtime errors, console warnings, client-side logs | Uncaught exceptions, deprecation warnings, third-party library errors |
| `product-design:network-inspection` | API calls, HTTP requests, network failures | 404 errors, CORS issues, slow API responses, failed requests |
| `python-experts:django-expert` | Django-specific backend issues | ORM queries, middleware errors, view logic, template rendering |
| `python-experts:fastapi-expert` | FastAPI async issues, request validation | Async handler errors, Pydantic validation, dependency injection |
| `devops-data:cto-architect` | System design issues, architecture decisions | Distributed system failures, scaling issues, design flaws |
| `security-compliance:mcp-security-expert` | Security-related bugs, authentication issues | Auth failures, permission errors, input validation bypasses |

### 3. Investigation Protocol

For each spawned agent:

1. **Assign clear scope**: Define what the agent should investigate
2. **Provide context**: Share relevant logs, code, and reproduction steps
3. **Set expectations**: Specify what output format is needed (root cause analysis, fix recommendations, etc.)
4. **Coordinate findings**: Collect results from all agents

### 4. Synthesis and Resolution

After agents complete their investigations:
- Correlate findings across different domains
- Identify root cause from expert insights
- Propose comprehensive fix that addresses all identified issues
- Verify fix doesn't introduce regressions

## Usage Pattern

```markdown
# Debugging Investigation: [Issue Title]

## Issue Summary
[Brief description of the problem]

## Evidence
- Error messages: [paste errors]
- Logs: [relevant log excerpts]
- Screenshots: [paths to screenshots]
- Reproduction steps: [how to trigger the issue]

## Investigation Plan
1. [Domain 1]: Spawn [agent-type] to investigate [specific aspect]
2. [Domain 2]: Spawn [agent-type] to investigate [specific aspect]
3. [Domain 3]: Spawn [agent-type] to investigate [specific aspect]

## Agent Assignments
- Agent 1 (web-debugger): Investigate browser console errors and DOM state
- Agent 2 (network-inspection): Analyze failed API calls and response codes
- Agent 3 (django-expert): Check backend logs and ORM query performance

## Expected Outputs
- Root cause analysis from each domain
- Specific code locations causing the issue
- Recommended fixes with code examples
```

## Parallel Execution

For independent investigations, spawn agents in parallel:

```bash
# Launch multiple debug agents concurrently
Task tool with multiple invocations:
1. web-debugger agent → investigate client-side errors
2. network-inspection agent → analyze API failures
3. django-expert agent → check backend logs
```

## Sequential Investigation

For dependent investigations, proceed sequentially:

```markdown
Step 1: Network inspection to identify failing endpoint
→ Result: POST /api/users/create returns 500

Step 2: Backend investigation (django-expert) on that specific endpoint
→ Result: Database constraint violation

Step 3: Database schema review to understand constraint
→ Result: Missing foreign key validation
```

## Examples

See `examples/` directory for complete debugging scenarios:
- `examples/frontend-api-failure.md` - UI component breaks due to API changes
- `examples/performance-degradation.md` - Multi-layer performance investigation
- `examples/auth-flow-failure.md` - Authentication issue spanning frontend and backend

## Output Format

After investigation, provide:

```markdown
# Debugging Results: [Issue Title]

## Root Cause
[Clear explanation of what's causing the issue]

## Contributing Factors
1. [Factor 1 from Agent A findings]
2. [Factor 2 from Agent B findings]
3. [Factor 3 from Agent C findings]

## Recommended Fix
[Step-by-step fix with code examples]

## Verification Steps
1. [How to verify the fix works]
2. [How to prevent regression]

## Prevention
[How to avoid this issue in the future]
```

## Best Practices

1. **Start broad, narrow down**: Begin with high-level investigation, then drill into specifics
2. **Share context freely**: Give agents all relevant information upfront
3. **Time-box investigations**: Set reasonable timeouts for agent investigations
4. **Document findings**: Keep a running log of discoveries from each agent
5. **Cross-validate**: Have agents verify each other's findings when domains overlap
6. **Consider race conditions**: For timing-sensitive bugs, investigate sequencing and concurrency
7. **Check recent changes**: Review git history for related code changes that might have introduced the bug

## Anti-Patterns

❌ **Spawning too many agents at once**: Limit to 3-4 parallel agents to avoid overwhelming coordination
❌ **Vague agent instructions**: Always provide specific investigation scope
❌ **Ignoring obvious causes**: Check simple explanations before orchestrating complex investigation
❌ **Not sharing agent findings**: Ensure all agents have access to collective knowledge
❌ **Over-engineering simple bugs**: Use direct debugging for straightforward issues

## Integration with Existing Tools

This skill complements existing debugging tools:
- Use `/product-design:console-debugging` for immediate console analysis
- Use `/product-design:network-inspection` for quick network checks
- Use this skill when those tools reveal a need for deeper, multi-domain investigation

## Workflow Example

```markdown
User: "The checkout flow is broken - payment processing fails intermittently"

Orchestrator Analysis:
- Symptom: Intermittent payment failures
- Affected layers: Frontend (React), API (FastAPI), Payment Gateway (Stripe), Database
- Evidence needed: Console logs, network traces, backend logs, payment gateway logs

Investigation Plan:
1. Spawn web-debugger: Check for JavaScript errors during checkout
2. Spawn network-inspection: Analyze payment API calls and response codes
3. Spawn fastapi-expert: Review payment endpoint implementation and error handling
4. Spawn security-compliance: Verify API key handling and secure communication

Parallel Execution:
→ Launch all 4 agents with specific scopes
→ Wait for completion
→ Synthesize findings

Synthesis:
- Web-debugger: Found uncaught promise rejection in payment handler
- Network-inspection: Saw 429 rate limit errors from Stripe API
- FastAPI-expert: Confirmed missing retry logic for rate-limited requests
- Security: Verified API keys are properly secured

Root Cause: Missing retry logic + no error handling for rate limits

Fix: Implement exponential backoff retry logic with proper error handling
```
