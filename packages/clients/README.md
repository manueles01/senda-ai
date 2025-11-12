# @senda/clients

API clients for Senda platform integrations.

## Clients

- **PhorestClient**: Integration with Phorest salon management system
- **TelnyxClient**: Integration with Telnyx telephony services
- **GeminiClient**: Integration with Google Gemini AI
- **SendaApiClient**: Client for Senda FastAPI backend

## Usage

```typescript
import { SendaApiClient, PhorestClient } from '@senda/clients';

const apiClient = new SendaApiClient({
  baseUrl: 'http://localhost:8000',
});

const health = await apiClient.getHealth();

const phorestClient = new PhorestClient({
  baseUrl: process.env.PHOREST_BASE_URL,
  username: process.env.PHOREST_USERNAME,
  password: process.env.PHOREST_PASSWORD,
  businessId: process.env.PHOREST_BUSINESS_ID,
  branchId: process.env.PHOREST_BRANCH_ID,
});
```
