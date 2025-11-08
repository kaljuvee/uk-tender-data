# UK Tender Scraper

A Streamlit-based application for scraping and analyzing UK government tender opportunities from the Find a Tender service.

## Features

- **API Integration**: Fetch real tender data from the UK Find a Tender OCDS API
- **Synthetic Data Generation**: Generate realistic test data using Faker
- **Advanced Search**: Filter tenders by keywords, buyer, and status
- **Analytics Dashboard**: Visualize tender statistics and trends
- **Data Export**: Export tender data in CSV, JSON, or Excel formats
- **SQLite Database**: Store and manage tender data locally
- **Duplicate Detection**: Automatically prevent duplicate tender entries

## Tech Stack

- **Frontend**: Streamlit
- **Backend**: Python 3.11
- **Database**: SQLite
- **Data Processing**: Pandas
- **Web Scraping**: Requests (API), Playwright (fallback)
- **AI/LLM**: LangChain, LangGraph, OpenAI
- **Data Generation**: Faker

## Installation

### Prerequisites

- Python 3.11 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/kaljuvee/uk-tender-data.git
cd uk-tender-data
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.sample .env
# Edit .env and add your OpenAI API key
```

4. Initialize the database:
```bash
python -c "from utils.database import TenderDatabase; TenderDatabase()"
```

## Usage

### Running the Application

Start the Streamlit application:

```bash
streamlit run Home.py
```

The application will open in your default web browser at `http://localhost:8501`.

### Application Pages

1. **Home** (`Home.py`)
   - Overview dashboard with key statistics
   - Recent tenders list
   - Detailed tender information viewer

2. **Scrape Tenders** (`pages/1_Scrape_Tenders.py`)
   - Fetch real data from Find a Tender API
   - Generate synthetic test data
   - Configure scraping parameters (records, date range, stage filters)
   - View scraping history and logs

3. **Search Tenders** (`pages/2_Search_Tenders.py`)
   - Search by keywords in title/description
   - Filter by buyer organization
   - Filter by tender status
   - View detailed tender information in tabs

4. **Analytics & Export** (`pages/3_Analytics_Export.py`)
   - View tender statistics and charts
   - Analyze tenders by status and category
   - Top buyers by count and value
   - Export data in multiple formats (CSV, JSON, Excel)

## API Information

### Find a Tender OCDS API

The application uses the UK government's Find a Tender service API:

- **Endpoint**: `https://www.find-tender.service.gov.uk/api/1.0/ocdsReleasePackages`
- **Authentication**: Not required for public data
- **Format**: JSON (OCDS version 1.1.5)
- **Rate Limit**: 100 records per request

### Query Parameters

- `limit`: Number of records (1-100, default 100)
- `stages`: Filter by stage (planning, tender, award)
- `updatedFrom`: Earliest update date (YYYY-MM-DDTHH:MM:SS)
- `updatedTo`: Latest update date (YYYY-MM-DDTHH:MM:SS)
- `cursor`: Pagination token

## Database Schema

### Tables

**tenders**
- Main tender information (notice_id, title, description, status, value, buyer details, etc.)

**lots**
- Individual lots associated with tenders (one-to-many relationship)

**documents**
- Documents and attachments related to tenders

**scraping_log**
- Audit log of scraping operations

See `sql/create_tables.sql` for complete schema.

## Testing

Run the test suite:

```bash
# Test database functionality
python tests/test_database.py

# Test API scraper
python tests/test_api_scraper.py

# Test data generator
python tests/test_data_generator.py
```

Test results are saved to `test-results/*.json`.

## Project Structure

```
uk-tender-scraper/
├── Home.py                      # Main application entry point
├── pages/                       # Streamlit pages
│   ├── 1_Scrape_Tenders.py     # Scraping interface
│   ├── 2_Search_Tenders.py     # Search and filter
│   └── 3_Analytics_Export.py   # Analytics and export
├── utils/                       # Utility modules
│   ├── database.py             # Database operations
│   ├── api_scraper.py          # API scraping logic
│   └── data_generator.py       # Synthetic data generation
├── sql/                         # Database files
│   ├── create_tables.sql       # Database schema
│   └── tenders.db              # SQLite database (created at runtime)
├── tests/                       # Test files
│   ├── test_database.py
│   ├── test_api_scraper.py
│   └── test_data_generator.py
├── test-results/                # Test output (JSON)
├── requirements.txt             # Python dependencies
├── .env.sample                  # Environment variables template
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
OPENAI_API_KEY=your_openai_api_key_here
GITHUB_USERNAME=your_github_username
GITHUB_TOKEN=your_github_token
```

### Scraping Parameters

Configure scraping in the sidebar:

- **Number of Records**: 10-500 (default: 100)
- **Data Source**: API (real) or Synthetic (test)
- **Stage Filter**: planning, tender, award, or all
- **Days to Look Back**: 7-365 (default: 30)

## Data Sources

### Find a Tender Service

Official UK government procurement portal:
- Website: https://www.find-tender.service.gov.uk/
- API Documentation: https://www.find-tender.service.gov.uk/apidocumentation
- Data Standard: Open Contracting Data Standard (OCDS) 1.1.5

### Synthetic Data

Generated using the Faker library with realistic UK-specific data:
- UK government organizations
- CPV classification codes
- UK addresses and postcodes
- Realistic tender titles and descriptions

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is for demonstration and educational purposes.

## Contact

For questions or support, please open an issue on GitHub.

## Acknowledgments

- UK Government Find a Tender Service
- Open Contracting Partnership (OCDS)
- Lohusalu Capital Management

---

**Note**: This application is a proof of concept for educational purposes. Always comply with the Find a Tender service's terms of use and rate limits when accessing their API.
