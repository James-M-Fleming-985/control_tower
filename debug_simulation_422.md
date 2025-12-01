# Debugging 422 Error for /api/v1/simulations/

## Problem
- Frontend: `InteractionSimulator.tsx:187` making POST to `/api/v1/simulations/`
- Backend: Returns 422 Unprocessable Entity
- Error message shows: `Error: [object Object],[object Object],[object Object]`

## Root Cause
422 errors mean **data validation failed**. The request body doesn't match the expected schema.

## Debugging Steps

### 1. Check Railway Logs for Validation Details

Railway logs should show FastAPI validation errors. Look for:
```
INFO:     100.64.0.7:28390 - "POST /api/v1/simulations/ HTTP/1.1" 422 Unprocessable Entity
```

**You need the full error response!** FastAPI returns detailed validation errors like:
```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 2. Add Console Logging in Frontend

In `InteractionSimulator.tsx` around line 187, add logging BEFORE the fetch:

```typescript
// Log the request payload
console.log('Simulation Request Payload:', JSON.stringify(requestData, null, 2));

try {
  const response = await fetch('https://lifequality-production.up.railway.app/api/v1/simulations/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(requestData)
  });
  
  // Log the response status and body
  console.log('Response status:', response.status);
  const responseData = await response.json();
  console.log('Response data:', responseData);
  
  if (!response.ok) {
    // This will show the actual validation errors
    console.error('Validation errors:', responseData.detail);
    throw new Error(JSON.stringify(responseData.detail));
  }
} catch (error) {
  console.error('Error details:', error);
}
```

### 3. Fix the Error Display in Line 202

The error message shows `[object Object],[object Object],[object Object]` because you're not properly stringifying the error details.

Change line 199-202 from:
```typescript
throw new Error(`${errorDetails}`);  // This creates [object Object]
```

To:
```typescript
throw new Error(JSON.stringify(errorDetails, null, 2));  // This shows actual data
```

### 4. Check Backend API Schema

The backend API expects specific fields. Common requirements for simulation endpoints:

```python
# Backend model (FastAPI/Pydantic)
class SimulationCreate(BaseModel):
    # Required fields - check what your backend expects
    architect_id: Optional[str]
    actors: List[Dict[str, Any]]  # Actor configurations
    interaction_type: str
    duration: Optional[int]
    parameters: Optional[Dict[str, Any]]
```

### 5. Common Causes of 422 Errors

✅ **Check these in your frontend request:**

1. **Missing required fields**
   - `architect_id` might be null/undefined
   - `actors` array might be empty
   - Required fields not being sent

2. **Wrong data types**
   - Sending string instead of number
   - Sending null instead of required value
   - Sending object instead of array

3. **Invalid values**
   - Empty arrays where non-empty expected
   - Invalid enum values
   - Negative numbers where positive expected

4. **Field name mismatches**
   - Frontend sends `architectId` (camelCase)
   - Backend expects `architect_id` (snake_case)

### 6. Quick Fix to Try

Based on the logs showing successful `/api/v1/architect/default` and `/api/v1/actors/` calls, the issue is likely in how you're constructing the simulation request.

**Check if you're including all required data:**

```typescript
const simulationRequest = {
  architect_id: architectData?.id || 'default',  // Make sure this isn't null
  actors: actors.map(actor => ({
    id: actor.id,
    name: actor.name,
    type: actor.type,
    // Include ALL required actor fields
  })),
  interaction_type: selectedInteractionType,  // Make sure this is set
  parameters: {
    // Include any required parameters
  }
};
```

### 7. Test with cURL

Test the endpoint directly to see the exact error:

```bash
curl -X POST https://lifequality-production.up.railway.app/api/v1/simulations/ \
  -H "Content-Type: application/json" \
  -d '{
    "architect_id": "default",
    "actors": [],
    "interaction_type": "test"
  }'
```

This will show you the exact validation error from FastAPI.

## Next Steps

1. ✅ Add console.log to see what data you're sending
2. ✅ Check Railway logs for the full error response
3. ✅ Fix the error message display (JSON.stringify)
4. ✅ Compare your request with backend schema
5. ✅ Test with cURL to isolate the issue

## Expected Solution

Once you see the actual validation errors, you'll see something like:
```json
{
  "detail": [
    {
      "loc": ["body", "architect_id"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

Then you can fix the frontend to include the missing/incorrect fields.
