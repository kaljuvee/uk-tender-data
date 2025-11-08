# UK Find a Tender API Research

## Key Findings

### OCDS API (Public Data Access)
- **Endpoint**: `https://www.find-tender.service.gov.uk/api/1.0/ocdsReleasePackages`
- **Authentication**: NOT REQUIRED for reading public tender data
- **Format**: JSON following OCDS version 1.1.5
- **Default Limit**: 100 records per request
- **Max Limit**: 100 records per request

### Query Parameters
- `limit`: Number of results (1-100, default 100)
- `cursor`: Pagination token for next set of results
- `updatedFrom`: Filter by earliest update date (YYYY-MM-DDTHH:MM:SS)
- `updatedTo`: Filter by latest update date (YYYY-MM-DDTHH:MM:SS)
- `stages`: Filter by contracting stage (planning, tender, award)

### Notice ID Formats
- Notice IDs: `nnnnnn-yyyy` (e.g., 001060-2020)
- Procurement IDs (ocids): `ocds-h6vhtk-hhhhhh`

### Response Structure
Each release contains:
- `ocid`: Procurement process ID
- `id`: Notice ID
- `date`: Publication date
- `tag`: Stage tags (planning, tender, award)
- `tender`: Main tender information
  - `title`: Tender title
  - `description`: Description
  - `value`: Contract value (amount, currency)
  - `status`: Current status
  - `classification`: CPV codes
  - `lots`: Individual lots
  - `items`: Procurement items
  - `documents`: Related documents
- `parties`: Buyer and supplier information
- `buyer`: Buyer details

### Rate Limiting
- HTTP 429: Too many requests (check Retry-After header)
- HTTP 503: Service unavailable (check Retry-After header)

### Submission API (Requires Authentication)
- **Authentication**: CDP API Key required
- **Header**: `CDP-Api-Key: YOUR_CDP_API_KEY`
- **Purpose**: For submitting notices (not needed for scraping)

## Implementation Strategy
1. Use OCDS API without authentication for public data access
2. Implement pagination using cursor parameter
3. Filter by date ranges to get recent tenders
4. Parse OCDS JSON format for tender details
5. Fallback to Playwright scraping if API fails
