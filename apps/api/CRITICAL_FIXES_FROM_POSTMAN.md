# CRITICAL Phorest API Fixes (From Postman Collection)

## Issues Found and Fixed

### 🔴 CRITICAL BUG #1: Authentication Format

**Problem:** Missing `global/` prefix in authentication header

```python
# ❌ WRONG (our previous code):
auth_string = base64.b64encode(f"{username}:{password}".encode()).decode()

# ✅ CORRECT (from Postman):
auth_string = base64.b64encode(f"global/{username}:{password}".encode()).decode()
```

**Impact:** ALL Phorest API calls would fail with 401 Unauthorized

**Fixed in:** `apps/api/src/services/phorest.py:24`

---

### 🔴 CRITICAL BUG #2: Missing API Path Prefix

**Problem:** Missing `/third-party-api-server/` in the URL path

```python
# ❌ WRONG (our previous code):
url = f"{base_url}/api/business/{business_id}/..."

# ✅ CORRECT (from Postman):
url = f"{base_url}/third-party-api-server/api/business/{business_id}/..."
```

**Impact:** ALL Phorest API calls would fail with 404 Not Found or routing errors

**Fixed in:**
- Line 44: `find_client_by_phone` endpoint
- Line 80: `create_client` endpoint
- Line 102: `get_services` endpoint
- Line 118: `get_staff` endpoint
- Line 175: `check_availability` endpoint
- Line 243: `create_appointment` endpoint
- Line 264: `get_client_appointments` endpoint
- Line 280: `cancel_appointment` endpoint

---

### ✅ Minor Improvements

1. **Increased services page size:** Changed from 100 to 500 (matches Postman)
2. **Added Accept header:** Added `"Accept": "application/json"` to all requests
3. **Updated .env.example:** Added actual business/branch IDs and authentication notes

---

## Correct Endpoint Format (Verified from Postman)

### Base URL Structure:
```
https://api-gateway-us.phorest.com/third-party-api-server/api/business/{businessId}/branch/{branchId}/...
```

### Authentication Header:
```
Authorization: Basic base64("global/{username}:{password}")
```

### Example Endpoints:

**Get Services:**
```
GET /third-party-api-server/api/business/{businessId}/branch/{branchId}/service?size=500
```

**Get Staff:**
```
GET /third-party-api-server/api/business/{businessId}/branch/{branchId}/staff
```

**Check Availability:**
```
POST /third-party-api-server/api/business/{businessId}/branch/{branchId}/appointments/availability
Body:
{
  "startTime": "2025-11-14T00:00:00Z",
  "endTime": "2025-12-05T00:00:00Z",
  "clientServiceSelections": [
    {
      "serviceSelections": [{ "serviceId": "xyz123" }],
      "staffId": "abc456"  // Optional
    }
  ]
}
```

**Create Appointment:**
```
POST /third-party-api-server/api/business/{businessId}/branch/{branchId}/appointment
Body:
{
  "clientId": "client123",
  "startTime": "2025-11-15T10:00:00Z",
  "services": [
    {
      "serviceId": "xyz123",
      "staffId": "abc456"
    }
  ]
}
```

---

## Payload Format Notes (From Postman Collection)

### Availability Request Variations:

**1. Single service, no staff preference:**
```json
{
  "clientServiceSelections": [
    { "serviceSelections": [{ "serviceId": "xyz" }] }
  ]
}
```

**2. Single service, with staff:**
```json
{
  "clientServiceSelections": [
    {
      "serviceSelections": [{ "serviceId": "xyz" }],
      "staffId": "abc"
    }
  ]
}
```

**3. Multiple services (per-selection array):**
```json
{
  "clientServiceSelections": [
    { "serviceSelections": [{ "serviceId": "xyz1" }] },
    { "serviceSelections": [{ "serviceId": "xyz2" }] },
    { "serviceSelections": [{ "serviceId": "xyz3" }] }
  ]
}
```

**4. Multiple services (combined in one selection):**
```json
{
  "clientServiceSelections": [
    {
      "serviceSelections": [
        { "serviceId": "xyz1" },
        { "serviceId": "xyz2" },
        { "serviceId": "xyz3" }
      ]
    }
  ]
}
```

Our implementation uses format #2 (single service with staff), which is correct.

---

## Testing Notes

From the Postman collection pre-request script:

1. **Time Format:** ISO 8601 with 'Z' suffix (UTC)
   - Our code already does this: `now.isoformat() + "Z"`

2. **Default Time Window:** Now → +21 days
   - Our code uses 7 days (configurable via `days_ahead` parameter)

3. **Service ID Key:** Can be `serviceId` or `branchServiceId` (tenant-specific)
   - Our code uses `serviceId` (most common)

4. **Staff ID:** Optional in availability request, required for booking
   - Our code includes it in availability check

---

## What This Means

**Before these fixes:**
- 0% success rate on Phorest API calls
- Would get 401 Unauthorized (bad auth)
- Would get 404 Not Found (wrong path)

**After these fixes:**
- Should work with real Phorest account
- Ready for ngrok testing with Telnyx

---

## Next Steps

1. ✅ **Authentication fixed** - Now includes `global/` prefix
2. ✅ **API paths fixed** - All endpoints use correct path structure
3. ✅ **Payload format verified** - Matches Postman working examples
4. ⏭️ **Ready to test** - Start ngrok and make test call

The API should now work correctly with the Phorest backend!
