# 🇬🇧 UK Public Tender Data

A comprehensive application for collecting, analyzing, and exporting UK government tender opportunities from the Find a Tender service.

## 🌟 Features

- **Automated Data Collection**: Command-line scraper that runs hourly via cron
- **PostgreSQL Storage**: Store data in PostgreSQL with `tendly` schema and multi-country support
- **Real-Time API Integration**: Fetch live data from Find a Tender OCDS API
- **Advanced Search**: Search and filter tenders by keywords, buyer, status, and date range
- **Analytics Dashboard**: Visualize tender data with interactive charts and statistics
- **Export Capabilities**: Export data to Excel, CSV, and JSON formats
- **Multi-Country Support**: Built-in `country_code` column for future expansion
- **Comprehensive Logging**: JSON logs for all scraping operations
- **Duplicate Detection**: Automatic prevention of duplicate tender records

## 📋 Requirements

- Python 3.11+
- PostgreSQL database
- OpenAI API key (for LangChain/LangGraph features)
- Cron (for scheduled scraping)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/kaljuvee/uk-tender-data.git
cd uk-tender-data
```

### 2. Create Virtual Environment

```bash
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
cp .env.sample .env
```

Edit `.env` and add your credentials:

```env
# PostgreSQL Database Connection
MAIN_DB_URL=postgresql://username:password@host:port/database

# OpenAI API Key (for LangChain/LangGraph)
OPENAI_API_KEY=your_openai_api_key_here

# Application Settings
COUNTRY_CODE=UK
```

### 5. Initialize Database

Run the database initialization script to create the `tendly` schema and tables:

```bash
python init_db.py
```

### 6. Run Initial Scrape

Fetch your first batch of tender data:

```bash
python tasks/scrape_tenders.py --limit 100 --days-back 30
```

### 7. Setup Automated Scraping (Optional)

Configure hourly scraping with cron:

```bash
bash tasks/setup_cron.sh
```

### 8. Run the Streamlit Application

```bash
streamlit run Home.py
```

The application will be available at `http://localhost:8501`

## 📁 Project Structure

```
uk-tender-data/
├── Home.py                      # Main Streamlit application
├── pages/
│   ├── Search_Tenders.py        # Search and filter interface
│   └── Analytics_Export.py      # Analytics and export interface
├── tasks/
│   ├── scrape_tenders.py        # Command-line scraper (runs hourly)
│   ├── setup_cron.sh            # Cron setup script
│   └── README.md                # Tasks documentation
├── utils/
│   ├── database.py              # PostgreSQL database operations
│   ├── api_scraper.py           # API scraping functionality
│   └── data_generator.py        # Data generation utilities
├── sql/
│   └── create_tables.sql        # PostgreSQL DDL (tendly schema)
├── logs/
│   ├── scrape_*.json            # JSON scraping logs
│   ├── cron.log                 # Cron execution logs
│   └── README.md                # Logs documentation
├── tests/
│   ├── test_database.py         # Database tests
│   ├── test_api_scraper.py      # API scraper tests
│   └── test_data_generator.py   # Data generator tests
├── init_db.py                   # Database initialization script
├── requirements.txt             # Python dependencies
├── .env.sample                  # Environment variables template
└── README.md                    # This file
```

## 🗄️ Database Schema

All tables are created in the `tendly` schema:

### tendly.tenders
Main tender information with country_code, notice_id, title, description, status, value, buyer details, classification, and timestamps.

### tendly.lots
Individual lots associated with tenders (one-to-many relationship).

### tendly.documents
Documents and attachments related to tenders.

### tendly.scraping_log
Audit trail of all scraping operations with country_code, timestamp, records fetched/inserted/duplicates, source, and status.

See `sql/create_tables.sql` for complete schema.

## 🤖 Automated Scraping

### Command-Line Scraper

The scraper runs as a command-line task and can be scheduled with cron:

```bash
# Basic usage
python tasks/scrape_tenders.py

# With options
python tasks/scrape_tenders.py --limit 100 --days-back 7 --stage tender

# Help
python tasks/scrape_tenders.py --help
```

### Scheduling with Cron

Setup hourly scraping:

```bash
bash tasks/setup_cron.sh
```

Or manually add to crontab:

```bash
# Run every hour at minute 0
0 * * * * cd /path/to/uk-tender-data && /path/to/venv/bin/python tasks/scrape_tenders.py --limit 100 --days-back 1 >> logs/cron.log 2>&1
```

### Logging

All scraping operations are logged:

- **JSON Logs**: `logs/scrape_YYYYMMDD_HHMMSS.json` - Structured logs with metadata
- **Cron Logs**: `logs/cron.log` - Console output from cron execution
- **Database Logs**: `tendly.scraping_log` - Audit trail in PostgreSQL

View latest scraping status:

```bash
ls -t logs/scrape_*.json | head -1 | xargs cat | jq .
```

## 📊 Streamlit Application

The Streamlit application provides a web interface for viewing and analyzing tender data:

### Home Page
- Database statistics and metrics
- Recent tenders table
- Detailed tender viewer

### Search Tenders
- Keyword search across titles and descriptions
- Filter by buyer name, status, and date range
- Detailed tender information display

### Analytics & Export
- Visualize tender distribution by status, buyer, and value
- Export filtered data to Excel, CSV, or JSON
- Download comprehensive reports

**Note**: The Streamlit app is for viewing data only. Data collection is handled by the command-line scraper in `tasks/`.

## 🧪 Testing

Run the test suite to verify all components:

```bash
# Test database operations
python tests/test_database.py

# Test API scraper
python tests/test_api_scraper.py

# Test data generator
python tests/test_data_generator.py
```

Test results are saved to `test-results/*.json`

## 🌍 Multi-Country Support

The application is designed to support multiple countries:

- All tables include a `country_code` column
- Database operations filter by country code
- Easy to extend to other countries (e.g., 'US', 'EU', 'CA')

To add a new country:
1. Set `COUNTRY_CODE` in `.env` to the new country code
2. Update the data generator with country-specific data
3. Configure the API scraper for the new country's tender service
4. Run the scraper with `--country CODE`

## 🔧 Configuration

### Environment Variables

- `MAIN_DB_URL`: PostgreSQL connection string
- `OPENAI_API_KEY`: OpenAI API key for LangChain features
- `COUNTRY_CODE`: Country code for tender data (default: UK)

### Scraping Parameters

- **Record Count**: 1-100 records per scraping session (API limit)
- **Procurement Stage**: planning, tender, award, or all
- **Date Range**: 1-365 days back from current date

## 📦 Dependencies

Core dependencies:

- `streamlit` - Web application framework
- `pandas` - Data manipulation and analysis
- `psycopg2-binary` - PostgreSQL adapter
- `requests` - HTTP library for API calls
- `python-dotenv` - Environment variable management
- `openpyxl` - Excel file operations

See `requirements.txt` for full list.

## 🚀 Deployment

### Streamlit Cloud

1. Fork this repository
2. Sign up at [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Add secrets in Streamlit Cloud dashboard
5. Deploy!

**Note**: For automated scraping, you'll need a separate server with cron.

### Server Deployment

For full functionality including automated scraping:

1. Deploy to a Linux server (Ubuntu, Debian, etc.)
2. Install Python 3.11+ and PostgreSQL
3. Clone repository and setup virtual environment
4. Configure environment variables
5. Initialize database
6. Setup cron for hourly scraping
7. Run Streamlit app with systemd or supervisor

See `DEPLOYMENT.md` for detailed deployment instructions.

## 📝 API Documentation

The application uses the Find a Tender API:

- **Base URL**: `https://www.find-tender.service.gov.uk/api/1.0/`
- **Endpoint**: `/ocdsReleasePackages`
- **Format**: OCDS (Open Contracting Data Standard)
- **Authentication**: Not required for public data
- **Rate Limit**: 100 records per request

## 🔍 Monitoring

### Check Scraping Status

```bash
# View latest log
ls -t logs/scrape_*.json | head -1 | xargs cat | jq .

# Check for errors
grep -l '"status": "error"' logs/scrape_*.json

# Daily summary
jq -s 'map(.records_inserted) | add' logs/scrape_$(date +%Y%m%d)*.json
```

### Database Queries

```sql
-- Recent scraping runs
SELECT * FROM tendly.scraping_log 
WHERE country_code = 'UK' 
ORDER BY timestamp DESC 
LIMIT 10;

-- Total records inserted today
SELECT SUM(records_inserted) FROM tendly.scraping_log 
WHERE country_code = 'UK' 
  AND DATE(timestamp) = CURRENT_DATE;

-- Latest tenders
SELECT notice_id, title, buyer_name, value_amount 
FROM tendly.tenders 
WHERE country_code = 'UK' 
ORDER BY created_at DESC 
LIMIT 10;
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Data source: [Find a Tender Service](https://www.find-tender.service.gov.uk/)
- Built with [Streamlit](https://streamlit.io/)
- Uses [OCDS](https://standard.open-contracting.org/) data standard
- Powered by [PostgreSQL](https://www.postgresql.org/)

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Lohusalu Capital Management** | UK Public Tender Data | Data from Find a Tender Service
