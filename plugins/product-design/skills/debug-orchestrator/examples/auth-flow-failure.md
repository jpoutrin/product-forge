# Example: Authentication Flow Failure

## Initial Issue Report

**User Report**: "Users can't log in - getting 'Authentication failed' error after entering correct credentials"

## Symptoms
- Login form submission shows generic "Authentication failed" message
- Affects ~40% of login attempts
- Users report credentials are correct (can log in via mobile app)
- No pattern by user, browser, or time of day
- Password reset doesn't help
- OAuth login (Google, GitHub) works fine

## Evidence Collected
```
Error shown to user: "Authentication failed. Please try again."
Browser console: No JavaScript errors
Login endpoint: POST /api/auth/login
Success rate: ~60% (down from 99.9% last week)
Mobile app login: 100% success rate (same backend!)
OAuth login: 100% success rate
```

## Orchestrator Analysis

**Hypothesis**: This is puzzling because:
- OAuth works (so auth system is generally functional)
- Mobile app works (so backend auth logic is correct)
- Only password-based web login fails intermittently
- Must be something specific to web form submission

**Potential causes**:
1. CSRF token validation failing
2. Cookie handling issue (SameSite, domain, etc.)
3. Password encoding issue (UTF-8, special characters)
4. Request body parsing inconsistency
5. Rate limiting triggering incorrectly
6. Session/token race condition

**Affected Layers**: Frontend form submission → API gateway → Backend auth service → Database

## Investigation Plan

### Agent 1: Chrome DevTools Web Debugger
**Scope**: Analyze login form and network requests
**Tasks**:
- Navigate to login page
- Inspect form submission
- Capture network request/response for failed login
- Check cookies being sent
- Verify request headers
- Test with different passwords (special chars, length)

### Agent 2: Network Inspector
**Scope**: Deep dive into HTTP traffic
**Tasks**:
- Compare successful vs failed login requests
- Check all headers (Content-Type, Authorization, CSRF)
- Inspect cookie behavior
- Look for subtle differences in request format
- Check response status codes and bodies

### Agent 3: Security Expert
**Scope**: Review authentication security
**Tasks**:
- Review CSRF token implementation
- Check OAuth vs password auth differences
- Verify session handling
- Review rate limiting configuration
- Check for timing attacks or race conditions

### Agent 4: Backend FastAPI Expert
**Scope**: Investigate backend auth endpoint
**Tasks**:
- Review /api/auth/login endpoint code
- Check request validation logic
- Review error handling (is it too generic?)
- Analyze backend logs for pattern in failures
- Compare OAuth vs password auth code paths

## Investigation Execution

```markdown
# Sequential investigation with findings feeding into next steps

Step 1: Web debugger - reproduce the issue
Step 2: Network inspector - compare success/failure
Step 3: Backend expert - review code and logs
Step 4: Security expert - validate auth implementation
```

## Agent Findings

### Chrome DevTools Web Debugger Results

```
Login page analysis:
✅ Form renders correctly
✅ Submit button triggers POST request
✅ No JavaScript errors

Network request captured (FAILED LOGIN):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
POST https://app.example.com/api/auth/login
Status: 401 Unauthorized

Request Headers:
  Content-Type: application/x-www-form-urlencoded
  Cookie: csrftoken=abc123xyz; sessionid=sess_456
  X-CSRF-Token: abc123xyz

Request Body (URL-encoded):
  username=user%40example.com&password=MyP%40ssw0rd%21&remember=true

Response:
  {"error": "Authentication failed"}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Network request captured (SUCCESSFUL LOGIN):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
POST https://app.example.com/api/auth/login
Status: 200 OK

Request Headers:
  Content-Type: application/x-www-form-urlencoded
  Cookie: csrftoken=abc123xyz; sessionid=sess_456
  X-CSRF-Token: abc123xyz

Request Body (URL-encoded):
  username=user@example.com&password=MyP@ssw0rd!&remember=true
                    ↑                      ↑
                 DIFFERENCE!           DIFFERENCE!

Response:
  {"token": "eyJ0eXAi...", "user": {...}}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 KEY FINDING: URL encoding differs between success/failure!
   Failed:  user%40example.com  (@ encoded as %40)
   Success: user@example.com    (@ not encoded)
```

### Network Inspector Deep Analysis

```
Comparison of 20 successful vs 20 failed requests:

Pattern discovered:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SUCCESSFUL requests:
- Content-Type: application/x-www-form-urlencoded
- Body: username=user@example.com&password=Pass@123
- Special chars @ ! NOT encoded in body

FAILED requests:
- Content-Type: application/x-www-form-urlencoded
- Body: username=user%40example.com&password=Pass%40123
- Special chars @ ! ARE encoded as %40 %21
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Hypothesis: Backend is double-decoding URL-encoded bodies
- Browser/client URL-encodes: user@example.com → user%40example.com
- Server auto-decodes: user%40example.com → user@example.com (correct)
- Server tries to decode AGAIN: user@example.com → ERROR (no change, but password hash fails)

Why intermittent?
- Some browsers/libraries URL-encode special chars
- Others send them raw (relying on framework encoding)
- Recent change must have affected encoding behavior
```

### Backend FastAPI Expert Results

```python
# /api/auth/login endpoint
from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse

@app.post("/api/auth/login")
async def login(
    username: str = Form(...),
    password: str = Form(...),
    remember: bool = Form(False)
):
    # Validate credentials
    user = await authenticate_user(username, password)
    if not user:
        return JSONResponse(
            status_code=401,
            content={"error": "Authentication failed"}
        )
    # ...

# Backend logs show pattern:
# FAILED logins - username in DB: "user@example.com"
#                 username received: "user%40example.com"
#                 Password hash match: FALSE (because username doesn't match!)

# Database lookup:
await db.query(User).filter(User.username == username).first()
# Fails because "user%40example.com" != "user@example.com"

# Git history reveals:
git log --since="7 days ago" -- api/auth.py

Commit a1b2c3d (2026-02-07):
  "fix: handle URL-encoded form data properly"

  @app.post("/api/auth/login")
  async def login(request: Request):
      # OLD (working):
      form_data = await request.form()
      username = form_data.get("username")

      # NEW (broken):
      body = await request.body()
      form_data = urllib.parse.parse_qs(body.decode())
      username = form_data.get("username")[0]
      # ↑ This manually decodes, but FastAPI ALREADY decoded!
      #   Result: double-decoding for some requests
```

### Security Expert Review

```
CSRF validation: ✅ Working correctly
OAuth flow: ✅ Working correctly (different code path, doesn't hit the bug)
Rate limiting: ✅ Not the issue (would affect all requests equally)

Root cause confirmed:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Recent commit (a1b2c3d) introduced manual form parsing that:
1. Manually URL-decodes form data using urllib.parse.parse_qs
2. But FastAPI already auto-decodes Form() parameters
3. Result: Double-decoding for requests that were already URL-encoded

Flow for FAILED requests:
  Browser: user@example.com (raw special chars in form)
  FastAPI: user@example.com (no encoding needed)
  Manual decode: urllib.parse.unquote("user@example.com") → "user@example.com"
  Database lookup: FAILS (username mismatch due to encoding artifacts)

Flow for SUCCESSFUL requests:
  Browser: user@example.com
  FastAPI: user@example.com
  Manual decode: No additional encoding
  Database lookup: SUCCESS

The intermittent nature is because:
- Some browsers send @ as @ (raw)
- Others send @ as %40 (encoded)
- Framework handles both correctly
- But manual decoding breaks the encoded ones
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Security implications:
⚠️  Error message "Authentication failed" is too generic
    Should distinguish between "user not found" vs "wrong password"
    But only in dev/staging, not production (prevents user enumeration)
```

## Root Cause Analysis

### Primary Cause
**Double-decoding of URL-encoded form data** (commit a1b2c3d)
- Developer tried to "fix" form parsing by manually decoding
- But FastAPI already handles URL decoding via `Form()` parameters
- Manual `urllib.parse.parse_qs()` caused double-decoding
- Double-decoded username didn't match database records
- Authentication failed even with correct password

### Why It's Intermittent
- Browser encoding behavior varies:
  - Some browsers send `@` as `@` (raw, relying on Content-Type)
  - Others send `@` as `%40` (pre-encoded for safety)
- FastAPI handles both correctly by default
- Manual decoding breaks the pre-encoded case

### Why Mobile App Works
- Mobile app sends JSON body (`Content-Type: application/json`)
- Different code path doesn't use form parsing
- No double-decoding issue

### Why OAuth Works
- OAuth uses token-based flow
- No username/password form submission
- Different endpoint entirely

## Recommended Fix

### Immediate Fix (Deploy Now)

```python
# REVERT the problematic commit
git revert a1b2c3d

# Or fix it properly:
@app.post("/api/auth/login")
async def login(
    username: str = Form(...),  # FastAPI handles decoding
    password: str = Form(...),
    remember: bool = Form(False)
):
    # Remove manual decoding - FastAPI does it correctly
    user = await authenticate_user(username, password)
    if not user:
        return JSONResponse(
            status_code=401,
            content={"error": "Authentication failed"}
        )

    # Generate token, set session, etc.
    return {"token": create_token(user), "user": user.dict()}
```

### Better Error Handling (For Debugging)

```python
# Add detailed logging (server-side only, not sent to client)
import logging
logger = logging.getLogger(__name__)

@app.post("/api/auth/login")
async def login(
    username: str = Form(...),
    password: str = Form(...)
):
    # Log the received username for debugging
    logger.info(f"Login attempt for username: {repr(username)}")

    user = await db.query(User).filter(User.username == username).first()

    if not user:
        logger.warning(f"User not found: {repr(username)}")
        return JSONResponse(
            status_code=401,
            content={"error": "Authentication failed"}
        )

    if not verify_password(password, user.hashed_password):
        logger.warning(f"Invalid password for user: {user.id}")
        return JSONResponse(
            status_code=401,
            content={"error": "Authentication failed"}
        )

    logger.info(f"Successful login: {user.id}")
    return {"token": create_token(user)}
```

### Add Tests to Prevent Regression

```python
# tests/test_auth.py
import pytest
from fastapi.testclient import TestClient

def test_login_with_special_characters():
    """Test that emails with @ and passwords with special chars work"""
    client = TestClient(app)

    # Test with URL-encoded data (as some browsers send)
    response = client.post(
        "/api/auth/login",
        data="username=user%40example.com&password=Pass%40123",
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200

    # Test with raw data (as other browsers send)
    response = client.post(
        "/api/auth/login",
        data="username=user@example.com&password=Pass@123",
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200

def test_login_with_unicode():
    """Test non-ASCII characters in password"""
    client = TestClient(app)

    response = client.post(
        "/api/auth/login",
        data={"username": "user@example.com", "password": "Пароль123"},  # Cyrillic
    )
    assert response.status_code == 200
```

## Verification Steps

1. **Deploy fix to staging**
   ```bash
   git revert a1b2c3d
   git commit -m "revert: remove manual form decoding (causes double-decode)"
   git push origin main
   # Deploy to staging
   ```

2. **Test both encoding scenarios**
   ```bash
   # Test URL-encoded (as curl sends)
   curl -X POST https://staging.example.com/api/auth/login \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=user%40example.com&password=Test%40123"
   # Expected: 200 OK

   # Test raw (as form sends)
   curl -X POST https://staging.example.com/api/auth/login \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=user@example.com&password=Test@123"
   # Expected: 200 OK
   ```

3. **Run test suite**
   ```bash
   pytest tests/test_auth.py -v
   # All auth tests should pass
   ```

4. **Monitor production after deployment**
   ```bash
   # Check login success rate
   grep "POST /api/auth/login" nginx-access.log | \
     awk '{print $9}' | sort | uniq -c
   # Expected: ~99% 200 status codes
   ```

## Prevention Measures

### 1. Add Integration Tests for Form Handling
```python
# tests/test_form_encoding.py
@pytest.mark.parametrize("username,password", [
    ("user@example.com", "Pass@123"),  # @ symbol
    ("user+tag@example.com", "Pass@123"),  # + and @
    ("user@example.com", "Пароль"),  # Unicode
    ("user@example.com", "P@ss!#$%"),  # Many special chars
])
def test_login_encoding(username, password):
    # Test both URL-encoded and raw forms
    pass
```

### 2. Add Logging for Debugging
```python
# Log encoding issues (dev/staging only)
if settings.DEBUG:
    logger.debug(f"Raw username bytes: {username.encode()}")
    logger.debug(f"Username repr: {repr(username)}")
```

### 3. Document Form Handling
```markdown
# docs/api-development.md

## Form Data Handling

FastAPI automatically handles URL decoding for Form() parameters.

❌ WRONG:
```python
body = await request.body()
form_data = urllib.parse.parse_qs(body.decode())  # Double-decoding!
```

✅ CORRECT:
```python
@app.post("/endpoint")
async def handler(field: str = Form(...)):
    # FastAPI handles decoding
    return {"field": field}
```
```

### 4. Add Pre-commit Hook
```yaml
# .pre-commit-config.yaml
- repo: local
  hooks:
    - id: check-form-parsing
      name: Check for manual form parsing
      entry: 'grep -rn "urllib.parse.parse_qs.*request.body()" --include="*.py"'
      language: system
      files: \.py$
```

## Lessons Learned

1. **Trust the framework**: FastAPI handles encoding/decoding correctly
2. **Don't fix what's not broken**: Manual parsing was unnecessary
3. **Test edge cases**: Special characters in forms are common
4. **Better error messages (dev only)**: Generic errors make debugging hard
5. **Consider browser differences**: Encoding behavior varies
6. **Add integration tests**: Unit tests missed this encoding issue
7. **Monitor login success rate**: Would have caught this immediately

## Timeline

```
2026-02-07: Commit a1b2c3d "fix form parsing" deployed
2026-02-08: First login failures reported (10% of attempts)
2026-02-09: Failure rate increases to 40%
2026-02-10: Investigation begins
2026-02-10: Root cause identified, fix deployed
2026-02-10: Login success rate restored to 99.9%

Impact: 3 days of degraded auth experience
```

## Follow-up Tasks

- [ ] Add form encoding tests to test suite
- [ ] Document form handling best practices
- [ ] Add pre-commit hook to catch manual form parsing
- [ ] Improve error logging (server-side only)
- [ ] Monitor login success rate with alerts
- [ ] Review all endpoints that use Form() parameters
- [ ] Add alert for login success rate < 95%
