---
name: MCP Security
description: Automatic security guidance for MCP servers, multi-agent systems, and text-to-SQL pipelines using 5-layer defense architecture
version: 1.0.0
triggers:
  - mcp security
  - agent security
  - text-to-sql
  - prompt injection
  - authorization
  - trust boundary
  - user context
  - multi-agent
  - sql injection
  - guardrails
---

# MCP Security Skill

This skill automatically activates when working with MCP servers, multi-agent systems, or text-to-SQL pipelines. It enforces security best practices and the 5-layer defense architecture.

## Core Principle

**Security is NOT a peer agent. Security is INFRASTRUCTURE.**

```
❌ Security Agent (can be prompt-injected)
✅ Security Guardrails (deterministic, cannot be "convinced")
```

## Automatic Behaviors

When this skill activates, Claude will:

### 1. Identify Security Concerns

Automatically flag when code involves:
- User input to LLM pipelines (prompt injection risk)
- LLM-generated SQL queries (P2SQL injection risk)
- Multi-agent communication (trust boundary risk)
- User context propagation (identity spoofing risk)
- Database access from agents (data exfiltration risk)

### 2. Recommend 5-Layer Architecture

For any agent pipeline, suggest implementing:

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Layer 1: INPUT GUARDRAILS          ┃
┃ • Rate limiting  • Length limits   ┃
┃ • Injection detection (ML+regex)   ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
           │
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Layer 2: AUTHORIZATION GATE        ┃
┃ • User→Role mapping  • RBAC/ABAC  ┃
┃ • Schema filtering before agent    ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
           │
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Layer 3: SQL VALIDATION            ┃
┃ • AST parsing  • DDL/DML blocklist ┃
┃ • Table allowlist  • RLS injection ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
           │
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Layer 4: EXECUTION SANDBOX         ┃
┃ • Read-only conn  • Timeout        ┃
┃ • Cost limits  • Row limits        ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
           │
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Layer 5: OUTPUT GUARDRAILS         ┃
┃ • PII masking  • Audit logging     ┃
┃ • Result limits  • SIEM export     ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

### 3. Enforce Security Patterns

When reviewing or writing code, automatically check for:

#### User Context Propagation
```python
# ✅ CORRECT: Signed, immutable context
@dataclass(frozen=True)
class UserContext:
    user_id: str
    permissions: FrozenSet[str]
    exp: int

    def to_jwt(self, secret: str) -> str:
        return jwt.encode({...}, secret, algorithm="HS256")

# ❌ WRONG: Mutable, unsigned context
class UserContext:
    user_id: str  # Can be modified!
    permissions: list  # Mutable!
```

#### Authorization Checks
```python
# ✅ CORRECT: Check at point of action
async def execute_query(sql: str, user_ctx: UserContext):
    if not auth_gate.check_table_access(user_ctx, table):
        raise PermissionDenied()
    return await db.execute(sql)

# ❌ WRONG: Trusting previous checks
async def execute_query(sql: str):
    # Assumes caller already checked permissions!
    return await db.execute(sql)
```

#### Prompt Injection Detection
```python
# ✅ CORRECT: Both pattern and ML detection
INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"you\s+are\s+now\s+a",
]

def validate_input(text: str) -> bool:
    # Pattern check
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return False
    # ML check
    result = injection_detector(text)
    return result["label"] != "INJECTION"

# ❌ WRONG: No input validation
def process(user_input: str):
    return llm.generate(user_input)  # Direct to LLM!
```

### 4. Flag Security Anti-Patterns

Automatically warn when detecting:

| Anti-Pattern | Warning |
|--------------|---------|
| Security as peer agent | "⚠️ Security should be guardrails, not an agent" |
| Full schema to LLM | "⚠️ Filter schema by user permissions first" |
| No SQL validation | "⚠️ Always validate generated SQL before execution" |
| Trusting agent output | "⚠️ Verify at every hop, never trust previous checks" |
| Mutable user context | "⚠️ User context must be immutable and signed" |
| No audit logging | "⚠️ All security decisions must be logged" |

## Security Checklist Generation

When building MCP servers or agent pipelines, generate:

```
📋 Security Checklist for [Component Name]

Authentication & Authorization
- [ ] Implement OAuth 2.0/OIDC
- [ ] Use signed JWTs (HMAC-SHA256 minimum)
- [ ] Verify tokens at EVERY agent hop
- [ ] Implement RBAC with Cerbos

Input Security
- [ ] Rate limiting (per user, per session)
- [ ] Input length limits (max 1000 chars)
- [ ] Prompt injection detection (pattern + ML)
- [ ] SQL keyword blocking in natural language

Data Security
- [ ] Schema filtering before agent access
- [ ] Column-level ACL
- [ ] Row-level security policies
- [ ] PII detection and masking

Execution Security
- [ ] Read-only database connections
- [ ] Query timeouts (30s max)
- [ ] Cost estimation via EXPLAIN
- [ ] Row count limits (10K max)

Audit & Monitoring
- [ ] Log all queries and results
- [ ] Track authorization decisions
- [ ] Alert on suspicious patterns
- [ ] SIEM integration
```

## Critical Security Rules

### 1. Never Trust, Always Verify
Every agent must independently verify user context. Never assume previous agents checked.

### 2. Immutable Core Identity
```python
# User identity MUST be:
# - Cryptographically signed (JWT)
# - Immutable (frozen dataclass)
# - Short-lived (15 min expiration)
```

### 3. Authorization at Point of Action
```python
# Check permissions when EXECUTING, not just at entry
@tool
def run_query(sql: str):
    # Verify permissions HERE, right before execution
    verify_authorization(current_user, sql)
    return execute(sql)
```

### 4. Defense in Depth
No single layer is foolproof. Each layer catches what previous layers missed.

### 5. Fail Closed
```python
# If ANY security check fails, REJECT
def process(input: str):
    if not layer1_check(input):
        raise SecurityError("Layer 1 failed")  # Don't try to fix
    if not layer2_check(input):
        raise SecurityError("Layer 2 failed")  # Don't try to fix
    # Only proceed if ALL checks pass
```

## Dependencies for Security

```toml
[project]
dependencies = [
    # Agents
    "pydantic-ai>=0.1",
    "langgraph>=0.2",

    # Security
    "transformers>=4.35",  # Injection detection
    "sqlparse>=0.4",       # SQL parsing
    "pyjwt>=2.8",          # Token handling
    "cerbos>=0.10",        # Authorization

    # Database
    "asyncpg>=0.29",       # PostgreSQL async

    # Observability
    "opentelemetry-api>=1.20",
    "opentelemetry-sdk>=1.20",
]
```

## Research References

When discussing security, reference:

| Topic | Source |
|-------|--------|
| P2SQL Injection | arxiv:2308.01990 |
| SQLShield (70% improvement) | Cambridge NLP |
| Trust Paradox in Multi-Agent | arxiv:2510.18563 |
| OAuth for Agents (MIT) | arxiv:2501.09674 |
| OWASP LLM Top 10 | owasp.org |

## Integration with Other Agents

### CTO Architect
When CTO designs systems, this skill ensures:
- Security architecture is part of system design
- 5-layer defense is included in technical specs
- Authorization patterns are defined upfront

### FastMCP Expert
When building MCP servers, ensure:
- All tools verify user context
- Schema is filtered per user
- Output is sanitized

### Python Testing Expert
When writing tests, include:
- Prompt injection tests
- SQL injection tests
- Authorization bypass tests
- PII leakage tests
```

## Warning Triggers

Automatically warn user when:

1. **User input goes directly to LLM**
   > "⚠️ SECURITY: User input should pass through input guardrails before reaching LLM"

2. **SQL generated without validation**
   > "⚠️ SECURITY: Generated SQL must be validated and checked against table allowlist"

3. **Agent trusts previous agent's check**
   > "⚠️ SECURITY: Each agent must independently verify authorization"

4. **User context is mutable**
   > "⚠️ SECURITY: User context must be immutable and cryptographically signed"

5. **No audit logging present**
   > "⚠️ SECURITY: All security decisions and data access must be logged"
