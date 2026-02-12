# Example: Frontend-API Failure Investigation

## Initial Issue Report

**User Report**: "User profile page shows 'Failed to load user data' error intermittently"

## Symptoms
- Profile page loads successfully ~80% of the time
- 20% of requests show error message
- Error occurs more frequently during peak hours
- No errors in browser console (confusing!)

## Evidence Collected
```
Error message shown to user: "Failed to load user data"
Browser: Chrome 120
URL: https://app.example.com/profile
Time: 2026-02-10 14:23 UTC (peak traffic)
```

## Orchestrator Analysis

**Hypothesis**: This could be:
1. API timeout during high load
2. Authentication token expiration
3. Rate limiting kicking in
4. Network connectivity issue
5. Backend database connection pool exhaustion

**Affected Layers**: Frontend React component, API gateway, Backend API, Database

## Investigation Plan

### Agent 1: Web Debugger
**Scope**: Investigate client-side behavior
**Tasks**:
- Navigate to /profile page
- Capture console messages (including network errors)
- Inspect component state when error occurs
- Check localStorage/sessionStorage for auth tokens
- Monitor XHR/fetch requests

### Agent 2: Network Inspector
**Scope**: Analyze HTTP traffic
**Tasks**:
- List all network requests to /api/users/profile
- Identify failed requests (status codes, timing)
- Check request headers (auth tokens)
- Analyze response bodies for error messages
- Measure request timing (TTFB, duration)

### Agent 3: Python FastAPI Expert
**Scope**: Review backend endpoint
**Tasks**:
- Read /api/users/profile endpoint code
- Check error handling and timeout configuration
- Review database query in the endpoint
- Analyze logs for this endpoint around 14:23 UTC
- Check rate limiting configuration

## Investigation Execution

```markdown
# Launch parallel investigation
Task 1: web-debugger
Prompt: "Navigate to https://app.example.com/profile. Take a snapshot and monitor network requests. Try refreshing 10 times to reproduce the intermittent 'Failed to load user data' error. Document console logs and network failures."

Task 2: network-inspection
Prompt: "List all network requests to /api/users/profile from the last hour. Focus on failed requests (4xx, 5xx) and slow requests (>2s). Capture full request/response details including headers and timing."

Task 3: python-experts:fastapi-expert
Prompt: "Review the /api/users/profile endpoint implementation. Check for timeouts, error handling, database queries, and rate limiting. Review backend logs from 14:20-14:30 UTC on 2026-02-10."
```

## Agent Findings

### Web Debugger Results
```
✅ No JavaScript errors in console
✅ Component renders correctly
❌ Network tab shows: GET /api/users/profile → 504 Gateway Timeout
⚠️  Request takes 30+ seconds before timeout
✅ Auth token present and valid
```

### Network Inspector Results
```
Total requests in last hour: 1,247
Failed requests: 243 (19.5%)
Failure pattern:
- 504 Gateway Timeout: 243 requests
- Timing: All failures took 30-31 seconds
- Time distribution: 85% failures between 14:00-15:00 UTC (peak hours)
- Headers: Valid auth tokens on all requests
- User-Agent: Mixed (not browser-specific)
```

### FastAPI Expert Results
```python
# /api/users/profile endpoint
@router.get("/users/profile")
async def get_user_profile(
    user_id: str = Depends(get_current_user)
):
    # Database query with NO timeout configured
    user = await db.execute(
        select(User)
        .where(User.id == user_id)
        .options(
            joinedload(User.posts),  # N+1 query risk
            joinedload(User.followers),  # N+1 query risk
            joinedload(User.following)  # N+1 query risk
        )
    )
    return user

# Backend logs show:
# 2026-02-10 14:23:15 - WARNING - Database connection pool exhausted (50/50)
# 2026-02-10 14:23:16 - ERROR - Query timeout on User.posts relationship
# 2026-02-10 14:23:45 - ERROR - Gateway timeout after 30s
```

## Root Cause Analysis

### Primary Cause
**Database query inefficiency during high load**
- The endpoint uses eager loading for relationships (posts, followers, following)
- These are N+1 queries that become expensive with many relationships
- During peak traffic, database connection pool gets exhausted (50 concurrent connections max)
- Queries waiting for available connections timeout
- No query timeout configured, so slow queries hold connections for 30+ seconds
- Gateway times out at 30s, returning 504 to client

### Contributing Factors
1. **No connection pooling limits**: Single query can hold connection indefinitely
2. **No query timeout**: Slow queries don't fail fast
3. **No caching**: Every profile request hits database
4. **No pagination**: Loading ALL posts/followers in one query
5. **No monitoring**: No alerts on connection pool exhaustion

## Recommended Fix

### Immediate Fix (Deploy Today)
```python
# 1. Add query timeout
from sqlalchemy import select
from sqlalchemy.orm import joinedload

@router.get("/users/profile")
async def get_user_profile(
    user_id: str = Depends(get_current_user)
):
    # Set 5-second timeout for this query
    async with db.begin():
        db.connection().execution_options(timeout=5.0)

        # Limit relationships to avoid N+1
        user = await db.execute(
            select(User)
            .where(User.id == user_id)
            .options(
                joinedload(User.posts).limit(10),  # Only recent posts
                # Don't eager load followers/following
            )
        )

    # Fetch counts separately (faster)
    follower_count = await db.scalar(
        select(func.count(Follower.id)).where(Follower.user_id == user_id)
    )

    return {
        "user": user,
        "stats": {
            "follower_count": follower_count,
            # Load full lists on-demand via separate endpoints
        }
    }

# 2. Add Redis caching
from fastapi_cache import Cache
from fastapi_cache.decorator import cache

@router.get("/users/profile")
@cache(expire=60)  # Cache for 60 seconds
async def get_user_profile(user_id: str = Depends(get_current_user)):
    # ... same code as above
```

### Short-term Improvements (This Week)
1. **Increase connection pool size** to 100 connections
2. **Add database query monitoring** (pg_stat_statements)
3. **Implement pagination** for posts/followers
4. **Add load balancer health checks** that fail if connection pool > 80% full

### Long-term Architecture (Next Sprint)
1. **Separate read/write databases** (replica for reads)
2. **Implement GraphQL** to let clients specify exactly what data they need
3. **Move social graph** (followers/following) to dedicated service
4. **Add CDN caching** for static profile data

## Verification Steps

1. **Deploy fix to staging**
   ```bash
   git checkout -b fix/profile-timeout
   # Apply code changes
   pytest tests/api/test_users.py
   git commit -m "fix(api): add timeout and caching to profile endpoint"
   git push origin fix/profile-timeout
   # Deploy to staging
   ```

2. **Load testing**
   ```bash
   # Simulate peak traffic
   ab -n 10000 -c 100 https://staging.example.com/api/users/profile
   # Expected: < 1% 504 errors
   ```

3. **Monitor production**
   - Watch connection pool metrics (should stay < 60% full)
   - Monitor endpoint p95 latency (should be < 500ms)
   - Check error rate (should be < 0.1%)

4. **Rollback plan**
   If fix causes issues: `kubectl rollout undo deployment/api-server`

## Prevention Measures

1. **Add monitoring alerts**:
   - Alert when connection pool > 70% full
   - Alert when endpoint p95 latency > 1s
   - Alert when error rate > 1%

2. **Add database query linting**:
   ```python
   # Add to CI pipeline
   pytest --sqlalchemy-query-timeout=5
   # Fails if any query takes > 5s in tests
   ```

3. **Enforce query patterns**:
   - No eager loading of collections without limits
   - Always set query timeouts
   - Always cache read-heavy endpoints

4. **Load testing in CI**:
   ```yaml
   # .github/workflows/load-test.yml
   - name: Load test critical endpoints
     run: ab -n 1000 -c 50 ${{ secrets.STAGING_URL }}/api/users/profile
   ```

## Lessons Learned

1. **Always set query timeouts**: Default "wait forever" is dangerous
2. **Watch connection pool metrics**: They're early warning signs
3. **Cache read-heavy endpoints**: Especially during peak traffic
4. **Lazy load relationships**: Don't eagerly load collections
5. **Test under load**: Intermittent issues often only appear under traffic

## Follow-up Tasks

- [ ] Apply same timeout pattern to all database queries
- [ ] Audit all endpoints for N+1 query patterns
- [ ] Implement connection pool monitoring dashboard
- [ ] Add load testing to CI pipeline
- [ ] Document query performance best practices for team
