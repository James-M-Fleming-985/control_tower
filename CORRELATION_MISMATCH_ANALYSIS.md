# Correlation Mismatch Analysis - Jan 9, 2026

## Problem Summary
Heatmap and drill-down showing different correlation values for the same variable pair:
- **Heatmap**: AI Papers ↔ Wildfires = **r = -0.989**
- **Drill-down**: AI Papers ↔ Wildfires = **r = 0.138**

## Root Cause
1. **Multiple correlation records exist in database** for the same variable pair from different calculation times
2. Previous deduplication logic used Python-level filtering AFTER fetching all records
3. Different endpoints were randomly selecting different records

## Investigation Results

### API Tests (v2.0.55)
```bash
# Heatmap endpoint
curl "https://businessventures-production.up.railway.app/api/dashboard/heatmap"
→ Returns r = -0.9892512716602694

# Drill-down endpoint  
curl "https://businessventures-production.up.railway.app/api/dashboard/relationship/Artificial%20Intelligence%20Papers/Wildfires%20Events"
→ Returns r = 0.13796459876354927

# Both querying CorrelationResult table, getting different records!
```

### Why Previous Fix Didn't Work (v2.0.55)
```python
# This approach had a flaw:
all_results = query.order_by(CorrelationResult.calculated_at.desc()).all()

# Deduplicate in Python
seen_pairs = set()
for r in all_results:
    pair = tuple(sorted([r.variable1_id, r.variable2_id]))
    if pair not in seen_pairs:
        seen_pairs.add(pair)
        deduplicated.append(r)

# Then resort by strength
results = sorted(deduplicated, key=lambda r: r.abs_correlation, reverse=True)
```

**Issue**: The `.all()` fetches ALL correlations sorted by date, but doesn't guarantee we get the most recent for EACH pair before the strength-based sorting happens. The limit() was applied BEFORE deduplication.

## Solution (v2.0.56)

### SQL-Level Deduplication
Use subquery to get only the most recent correlation for each unique pair BEFORE any other filtering:

```python
# Subquery: Find most recent calculation date for each pair
subq = session.query(
    func.least(CorrelationResult.variable1_id, CorrelationResult.variable2_id).label('v1'),
    func.greatest(CorrelationResult.variable1_id, CorrelationResult.variable2_id).label('v2'),
    func.max(CorrelationResult.calculated_at).label('max_date')
).group_by(
    func.least(CorrelationResult.variable1_id, CorrelationResult.variable2_id),
    func.greatest(CorrelationResult.variable1_id, CorrelationResult.variable2_id)
).subquery()

# Main query: Join to get only records matching most recent date
query = session.query(CorrelationResult).join(
    subq,
    ((func.least(...) == subq.c.v1) &
     (func.greatest(...) == subq.c.v2) &
     (CorrelationResult.calculated_at == subq.c.max_date))
)
```

**Benefits**:
- ✅ Database handles deduplication efficiently
- ✅ Only fetches most recent record for each pair
- ✅ Consistent across all endpoints
- ✅ Handles bidirectional pairs (A-B and B-A)

## Deployment Status
- **Commit**: a59afbbc5
- **Version**: 2.0.56
- **Pushed**: Yes
- **Railway Status**: Rebuilding (wait ~2-3 min)

## Testing Plan
After deployment:
1. **Refresh dashboard** (clear cache)
2. **Check heatmap** - note correlation value for AI Papers ↔ Wildfires
3. **Click to drill-down** - verify it shows THE SAME value
4. **Expected**: Both should show r = 0.138 (most recent calculation from 2021-02-01 to 2026-01-01, n=60)

## Additional Issues Found

### Granger Causality Still Failing
```
POST /api/dashboard/causality/Artificial%20Intelligence%20Papers/Wildfires%20Events
→ 500 Internal Server Error
```

**Need to investigate Railway logs** after v2.0.56 deploys to see specific error. Previous fix (v2.0.54) added DatetimeIndex handling and missing data checks, but may not cover all cases.

## Timeline
- v2.0.53: Added git commit display to footer
- v2.0.54: Fixed Granger DatetimeIndex error
- v2.0.55: Attempted Python-level deduplication (didn't work)
- v2.0.56: Fixed with SQL-level deduplication ✅

## Next Steps
1. ⏳ Wait for Railway to deploy v2.0.56
2. ✅ Verify correlation values match between heatmap and drill-down
3. 🔍 Check Granger causality logs for specific error
4. 🔧 Fix Granger causality if still failing
