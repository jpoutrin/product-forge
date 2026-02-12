# Example: Multi-Layer Performance Degradation

## Initial Issue Report

**User Report**: "App has become noticeably slower over the past week. Page loads that took 1-2 seconds now take 5-10 seconds."

## Symptoms
- All pages affected (not isolated to one feature)
- Progressive degradation (getting worse over time)
- Both authenticated and public pages slow
- Users reporting "spinning loader" before content appears
- Mobile users particularly affected

## Evidence Collected
```
Lighthouse scores (before vs now):
- Performance: 92 → 45 (dramatic drop)
- First Contentful Paint: 1.2s → 6.8s
- Largest Contentful Paint: 2.1s → 9.2s
- Time to Interactive: 2.5s → 11.4s

User complaints: 23 support tickets in past 3 days
Peak complaint hours: All day (not traffic-related)
Browser distribution: All browsers affected equally
```

## Orchestrator Analysis

**Hypothesis**: Multiple potential causes:
1. Recent deployment introduced performance regression
2. Database query performance degraded
3. Third-party service latency increased
4. Asset bundle size grew significantly
5. CDN/caching configuration changed
6. Memory leak causing progressive slowdown

**Affected Layers**: All layers potentially involved

## Investigation Plan

### Agent 1: Chrome DevTools Performance Tracer
**Scope**: Profile client-side performance
**Tasks**:
- Record performance trace on homepage load
- Analyze Performance Insights
- Identify slow JavaScript execution
- Check for layout thrashing
- Measure resource loading times

### Agent 2: Network Inspector
**Scope**: Analyze network waterfall
**Tasks**:
- List all network requests with timing
- Identify slow requests (>1s)
- Check for request blocking/queuing
- Measure total transfer size
- Analyze caching behavior

### Agent 3: Git History Reviewer
**Scope**: Find recent changes that might have caused regression
**Tasks**:
- Review git log for past week
- Identify deployments coinciding with slowdown
- Look for package.json changes
- Check for new dependencies
- Find large commits

### Agent 4: Backend Performance Expert
**Scope**: Check API and database performance
**Tasks**:
- Review slow query logs
- Check database connection metrics
- Analyze API endpoint timing
- Review cache hit rates
- Check for N+1 queries

## Investigation Execution

```markdown
# Launch sequential investigation (each informs the next)

Step 1: Performance trace (establish baseline)
Task: chrome-devtools performance_start_trace

Step 2: Network analysis (identify bottlenecks)
Task: network-inspection list_network_requests

Step 3: Git history (find suspects)
Task: Bash agent to review git log

Step 4: Backend investigation (if API calls are slow)
Task: Python expert to review backend
```

## Agent Findings

### Chrome DevTools Performance Trace Results

```
Performance Insights (Critical Issues):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️  Render Blocking Resources: 8 resources (4.2s delay)
   - main.js: 1,847 KB (uncompressed!)
   - vendor.js: 3,254 KB
   - styles.css: 287 KB
   - fonts.css: 145 KB

⚠️  Long Tasks: 23 tasks > 50ms
   - main.js parse: 1,847 KB → 2,300ms parse time
   - Lodash tree not shaken: Full library loaded (71 KB)
   - Moment.js full locale data: 267 KB

⚠️  Layout Thrashing: 47 forced reflows
   - Source: components/Table.tsx line 234
   - Reading offsetHeight inside loop

⚠️  Main Thread Blocking: 8.2s total blocking time
   - JavaScript execution: 6.1s
   - Style calculation: 1.4s
   - Layout: 0.7s

Core Web Vitals:
- LCP: 9.2s (Poor) - caused by render blocking JS
- FID: 340ms (Poor) - main thread blocked
- CLS: 0.08 (Good)
```

### Network Inspector Results

```
Total requests: 127
Total transfer size: 6.2 MB (up from 1.8 MB last week!)
Critical path requests: 14 (blocking page render)

Slowest requests:
1. /assets/main.js - 1,847 KB - 3.2s download
2. /assets/vendor.js - 3,254 KB - 5.1s download
3. /api/analytics/events - 247ms (called 8 times per page!)
4. /fonts/Inter-Regular.woff2 - 156 KB - 890ms

Caching issues:
- main.js: Cache-Control: no-cache (should be immutable!)
- vendor.js: Cache-Control: no-cache
- fonts: No cache headers at all

Resource hints missing:
- No preload for critical fonts
- No preconnect for third-party domains
```

### Git History Analysis

```bash
# Commits from past week
git log --since="7 days ago" --oneline

a1b2c3d (2026-02-08) feat: add real-time analytics dashboard
  ↳ Added 'analytics-js' package (243 KB)
  ↳ Imports entire lodash library
  ↳ Calls /api/analytics/events on every page

e4f5g6h (2026-02-07) chore: upgrade dependencies
  ↳ React 18.2 → 18.3
  ↳ Added 'moment.js' for date formatting (540 KB with locales!)

h7i8j9k (2026-02-06) refactor: move to CSS-in-JS
  ↳ Added 'styled-components' (78 KB)
  ↳ Converted all components to styled

k0l1m2n (2026-02-05) fix: remove old webpack config
  ↳ Changed caching headers to no-cache (WHOOPS!)
```

### Backend Performance Expert Results

```python
# Slow query log analysis
Top slow queries:
1. SELECT * FROM analytics_events WHERE user_id = ? ORDER BY created_at DESC
   - Avg time: 247ms
   - Executions: 1,247/hour (up from 12/hour!)
   - Missing index on (user_id, created_at)
   - Called 8 times per page load

2. SELECT * FROM users u JOIN posts p ON u.id = p.user_id
   - Avg time: 189ms
   - N+1 query pattern in feed generation

# API endpoint timing
/api/analytics/events: p95 = 312ms (up from 15ms)
- No caching
- No rate limiting
- Called on every page view

# Cache hit rate
Redis cache: 23% hit rate (down from 87%!)
- Cache keys changed in recent deployment
- Old pattern: "user:123:profile"
- New pattern: "user_profile_123" (doesn't match existing keys!)
```

## Root Cause Analysis

### Primary Causes

1. **Bloated JavaScript Bundle** (a1b2c3d commit)
   - Added full `analytics-js` library (243 KB)
   - Imported entire `lodash` library instead of specific functions
   - Added `moment.js` with all locale data (540 KB)
   - Bundle grew from 1.2 MB → 5.1 MB (4x increase!)

2. **Broken Caching** (k0l1m2n commit)
   - Changed Cache-Control headers to `no-cache`
   - Broke browser caching for all static assets
   - Every page load re-downloads all JS/CSS (6+ MB)

3. **Analytics Spam** (a1b2c3d commit)
   - New analytics dashboard calls `/api/analytics/events` 8x per page
   - Database missing index on (user_id, created_at)
   - No API response caching
   - Adds 2+ seconds per page load

4. **Cache Key Mismatch** (h7i8j9k commit)
   - Refactoring changed cache key format
   - Redis cache hit rate dropped 23% → 87%
   - Most requests bypassing cache, hitting database

### Contributing Factors

- No bundle size monitoring in CI
- No performance testing before deployment
- No alerts on bundle size increases
- No alerts on cache hit rate drops

## Recommended Fix

### Immediate Rollback (Do Now)
```bash
# Revert the caching config change
git revert k0l1m2n
# Deploy immediately to restore browser caching
```

### Critical Fixes (Deploy Today)

**1. Fix JavaScript Bundle**
```javascript
// Before (imports entire library)
import _ from 'lodash';
import moment from 'moment';

// After (import only what's needed)
import debounce from 'lodash/debounce';
import groupBy from 'lodash/groupBy';
import { format } from 'date-fns';  // Replace moment.js

// Remove unused analytics features
import { trackPageView } from 'analytics-js';  // Only import one function
```

**2. Restore Cache Headers**
```nginx
# Static assets with content hash → cache forever
location /assets/ {
    add_header Cache-Control "public, max-age=31536000, immutable";
}

# HTML → never cache
location / {
    add_header Cache-Control "no-cache, no-store, must-revalidate";
}
```

**3. Fix Analytics API Spam**
```typescript
// Before: Call on every render
useEffect(() => {
  trackAnalytics();
}, []);

// After: Debounce and deduplicate
const trackAnalytics = useMemo(
  () => debounce(() => {
    // Only track once per session
    if (!sessionStorage.getItem('tracked')) {
      api.trackPageView();
      sessionStorage.setItem('tracked', 'true');
    }
  }, 1000),
  []
);
```

**4. Add Database Index**
```sql
-- Add missing index
CREATE INDEX CONCURRENTLY idx_analytics_user_created
ON analytics_events(user_id, created_at DESC);

-- Add caching to analytics endpoint
-- (Redis cache for 5 minutes)
```

**5. Fix Cache Key Format**
```python
# Restore old cache key format
def get_cache_key(resource: str, id: int) -> str:
    return f"{resource}:{id}:profile"  # Old format
    # Not: f"{resource}_profile_{id}"  # New format
```

### Expected Impact

| Metric | Before | After Fix | Improvement |
|--------|--------|-----------|-------------|
| Bundle size | 5.1 MB | 1.4 MB | 73% reduction |
| First Contentful Paint | 6.8s | 1.3s | 81% faster |
| Largest Contentful Paint | 9.2s | 2.2s | 76% faster |
| Time to Interactive | 11.4s | 2.6s | 77% faster |
| API calls per page | 8 | 1 | 87% reduction |
| Cache hit rate | 23% | 85% | 270% increase |

## Verification Steps

1. **Bundle Analysis**
   ```bash
   npm run build
   npx webpack-bundle-analyzer dist/stats.json
   # Verify: main.js < 500 KB, vendor.js < 1 MB
   ```

2. **Lighthouse Testing**
   ```bash
   lighthouse https://staging.example.com --view
   # Target scores: Performance > 90, FCP < 1.5s, LCP < 2.5s
   ```

3. **Cache Validation**
   ```bash
   curl -I https://staging.example.com/assets/main.js
   # Should see: Cache-Control: public, max-age=31536000, immutable
   ```

4. **Network Monitoring**
   ```bash
   # Check analytics API calls reduced
   grep "/api/analytics/events" nginx-access.log | wc -l
   # Should be 1/8th of previous rate
   ```

5. **Database Performance**
   ```sql
   -- Verify index is used
   EXPLAIN ANALYZE
   SELECT * FROM analytics_events
   WHERE user_id = 123
   ORDER BY created_at DESC;
   -- Should show "Index Scan using idx_analytics_user_created"
   ```

## Prevention Measures

### 1. Add Bundle Size Monitoring
```yaml
# .github/workflows/bundle-size.yml
- name: Check bundle size
  run: |
    npm run build
    SIZE=$(stat -f%z dist/main.js)
    if [ $SIZE -gt 524288 ]; then  # 512 KB limit
      echo "Bundle too large: $SIZE bytes"
      exit 1
    fi
```

### 2. Add Performance Testing
```yaml
# .github/workflows/lighthouse-ci.yml
- name: Run Lighthouse CI
  run: |
    npx @lhci/cli@0.12.x autorun
    # Fails if Performance score < 90
```

### 3. Add Cache Monitoring
```yaml
# alerts/cache-hit-rate.yml
- alert: LowCacheHitRate
  expr: redis_cache_hit_rate < 0.7
  for: 5m
  annotations:
    summary: "Cache hit rate below 70%"
```

### 4. Add Database Query Monitoring
```python
# middleware/query_monitor.py
@app.middleware("http")
async def monitor_queries(request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start

    if duration > 0.5:  # Log slow requests
        logger.warning(f"Slow request: {request.url} took {duration}s")

    return response
```

### 5. Enforce Import Rules
```javascript
// .eslintrc.js
rules: {
  'no-restricted-imports': [
    'error',
    {
      paths: [
        {
          name: 'lodash',
          message: 'Import specific functions: import debounce from "lodash/debounce"',
        },
        {
          name: 'moment',
          message: 'Use date-fns instead: import { format } from "date-fns"',
        },
      ],
    },
  ],
}
```

## Lessons Learned

1. **Monitor bundle size in CI**: Catch regressions before production
2. **Never disable caching without review**: Has massive performance impact
3. **Import specific functions**: Don't import entire libraries
4. **Test cache changes carefully**: Wrong keys = cache misses
5. **Index database columns used in WHERE**: Especially with ORDER BY
6. **Rate limit analytics calls**: Don't spam APIs on every render
7. **Use performance budgets**: Fail CI if budgets exceeded

## Timeline

```
2026-02-05: Caching disabled (k0l1m2n commit)
2026-02-06: CSS-in-JS refactor changed cache keys
2026-02-07: Heavy dependencies added (moment.js)
2026-02-08: Analytics spam introduced
2026-02-09: User complaints start
2026-02-10: Investigation begins

Total degradation: 5 days of accumulated issues
```

## Follow-up Tasks

- [ ] Add bundle size monitoring to CI
- [ ] Add Lighthouse CI to prevent performance regressions
- [ ] Set up alerts for cache hit rate < 70%
- [ ] Document bundle size best practices
- [ ] Audit all dependencies for tree-shaking opportunities
- [ ] Replace moment.js with date-fns everywhere
- [ ] Add performance testing to staging deployment
- [ ] Create performance budget dashboard
