# Phorest API Endpoint Verification

## Issues Found

### 1. Base URL - Gateway Region
**Current (.env.example):** `https://api-gateway-eu.phorest.com`
**Expected:** `https://api-gateway-us.phorest.com` (user specified US gateway)

**Action:** Update .env.example and notify user to update their .env file

### 2. Client Search Endpoint
**Documentation:** `GET /api/business/{businessId}/client`
**Our Code:** `GET /api/business/{businessId}/branch/{branchId}/client`

**Analysis:** Other endpoints (services, staff, reviews) all include branch ID. The documentation may show both patterns. Need to test which works.

**Status:** VERIFY - may be correct as-is

### 3. Endpoints Verified as Correct

✅ **Services:** `GET /api/business/{businessId}/branch/{branchId}/service`
✅ **Availability:** `POST /api/business/{businessId}/branch/{branchId}/appointments/availability`
✅ **Reviews:** `GET /api/business/{businessId}/branch/{branchId}/review`

### 4. Staff Endpoint
**Our Code:** `GET /api/business/{businessId}/branch/{branchId}/staff`
**Documentation:** Shows individual staff endpoint with `{staffId}` parameter

**Status:** VERIFY - the list endpoint (without staffId) should exist

### 5. Appointment Creation
**Our Code:** `POST /api/business/{businessId}/branch/{branchId}/appointment`
**Documentation:** Page returned 404

**Status:** VERIFY - endpoint path may be correct but documentation unavailable

## Request Body Structures (from our code)

### Check Availability Request
```json
{
  "startTime": "ISO8601 timestamp with Z",
  "endTime": "ISO8601 timestamp with Z",
  "clientServiceSelections": [
    {
      "serviceSelections": [{"serviceId": "string"}],
      "staffId": "string"
    }
  ]
}
```

### Create Appointment Request
```json
{
  "clientId": "string",
  "startTime": "ISO8601 timestamp",
  "services": [
    {
      "serviceId": "string",
      "staffId": "string"
    }
  ]
}
```

## Next Steps

1. Update .env.example with correct US gateway URL
2. Test all endpoints with actual credentials
3. If client search fails, try without branch ID parameter
4. Verify staff listing endpoint returns array
5. Test appointment creation endpoint
