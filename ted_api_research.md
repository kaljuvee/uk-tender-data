# TED API Research Findings

## Overview

**TED (Tenders Electronic Daily)** is the official EU public procurement database, publishing procurement notices from the EU and EEA countries.

## API Information

### Base URL
- **Production**: `https://api.ted.europa.eu`
- **API Version**: v3 (latest)

### Search API Endpoint
- **Endpoint**: `POST /v3/notices/search`
- **Swagger**: https://api.ted.europa.eu/swagger-ui/index.html#/Search/search
- **Authentication**: **No API key required** (anonymous access)
- **Purpose**: Search and retrieve published procurement notices

### Key Features
- Anonymous access (no authentication needed)
- Expert query search capability
- Bulk download of notices in XML format
- Access to all published notices on TED website
- Supports filtering by various fields

### Request Format

```json
{
  "query": "string",
  "fields": [
    "field1",
    "field2"
  ],
  "pageSize": 100,
  "pageNum": 1,
  "sortField": "string",
  "sortOrder": "asc"
}
```

### Available Fields

The API supports hundreds of fields including:
- Notice identifiers
- Publication dates
- Buyer information
- Contract values
- Procurement categories
- Deadlines
- Award information
- And many more...

### Response Format

Returns notices in structured format with:
- Notice metadata
- Buyer information
- Tender details
- Lot information
- Award data
- Documents

### Data Format

- Primary format: **eForms** (new standard since Nov 2022)
- Legacy format: TED XML schema
- Export format: XML

## Integration Strategy

For our EU tender scraper:

1. **Use Search API** - No authentication required
2. **Query Structure** - Use expert queries to filter by date, status, etc.
3. **Pagination** - Handle multiple pages of results
4. **Data Parsing** - Parse XML/JSON response into our database schema
5. **Country Code** - Tag all entries with `country_code='EU'`

## Differences from UK API

| Feature | UK (Find a Tender) | EU (TED) |
|---------|-------------------|----------|
| Base URL | find-tender.service.gov.uk | api.ted.europa.eu |
| Authentication | Not required | Not required |
| Data Standard | OCDS | eForms |
| Format | JSON | JSON/XML |
| Endpoint | GET /api/1.0/ocdsReleasePackages | POST /v3/notices/search |
| Query Style | URL parameters | JSON body |

## Implementation Notes

- TED API uses POST requests with JSON body (different from UK GET requests)
- Response structure is different from OCDS format
- Will need to create a separate parser for TED data
- Can reuse database schema with country_code='EU'
- Same logging and error handling patterns as UK scraper
