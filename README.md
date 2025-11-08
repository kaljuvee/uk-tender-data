# 🇬🇧 UK Tender Scraper

A comprehensive Streamlit application for scraping, analyzing, and exporting UK government tender opportunities from the Find a Tender service.

## 🌟 Features

- **Data Collection**: Scrape tender data from Find a Tender API with configurable parameters
- **PostgreSQL Storage**: Store data in PostgreSQL with `tendly` schema and multi-country support
- **Synthetic Data Generation**: Generate realistic test data using Faker library
- **Advanced Search**: Search and filter tenders by keywords, buyer, status, and date range
- **Analytics Dashboard**: Visualize tender data with interactive charts and statistics
- **Export Capabilities**: Export data to Excel, CSV, and JSON formats
- **Multi-Country Support**: Built-in `country_code` column for future expansion to other countries
- **Duplicate Detection**: Automatic detection and prevention of duplicate tender records
- **Scraping History**: Complete audit trail of all scraping operations

## 📋 Requirements

- Python 3.11+
- PostgreSQL database
- OpenAI API key (for LangChain/LangGraph features)
- GitHub account (for deployment)

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

This will:
- Create the `tendly` schema in your PostgreSQL database
- Create tables: `tenders`, `lots`, `documents`, `scraping_log`
- All tables include a `country_code` column for multi-country support

### 6. Run the Application

```bash
streamlit run Home.py
```

The application will be available at `http://localhost:8501`

## 📁 Project Structure

```
uk-tender-data/
├── Home.py                      # Main Streamlit application
├── pages/
│   ├── 1_Scrape_Tenders.py     # Data scraping interface
│   ├── 2_Search_Tenders.py     # Search and filter interface
│   └── 3_Analytics_Export.py   # Analytics and export interface
├── utils/
│   ├── database.py             # PostgreSQL database operations
│   ├── api_scraper.py          # API scraping functionality
│   └── data_generator.py       # Synthetic data generation
├── sql/
│   └── create_tables.sql       # PostgreSQL DDL (tendly schema)
├── tests/
│   ├── test_database.py        # Database tests
│   ├── test_api_scraper.py     # API scraper tests
│   └── test_data_generator.py  # Data generator tests
├── init_db.py                  # Database initialization script
├── requirements.txt            # Python dependencies
├── .env.sample                 # Environment variables template
└── README.md                   # This file
```

## 🗄️ Database Schema

All tables are created in the `tendly` schema with the following structure:

### tenders
- `id` (SERIAL PRIMARY KEY)
- `country_code` (VARCHAR(2)) - Country identifier (e.g., 'UK')
- `notice_id` (VARCHAR(100) UNIQUE)
- `ocid` (VARCHAR(100))
- `title` (TEXT)
- `description` (TEXT)
- `status` (VARCHAR(50))
- `stage` (VARCHAR(50))
- `publication_date` (TIMESTAMP)
- `value_amount` (DECIMAL(15,2))
- `value_currency` (VARCHAR(3))
- `buyer_name` (VARCHAR(255))
- `buyer_id` (VARCHAR(100))
- `buyer_email` (VARCHAR(255))
- `buyer_address` (TEXT)
- `classification_id` (VARCHAR(50))
- `classification_description` (TEXT)
- `main_procurement_category` (VARCHAR(50))
- `cpv_codes` (TEXT)
- `legal_basis` (VARCHAR(100))
- `created_at` (TIMESTAMP DEFAULT NOW())

### lots
- `id` (SERIAL PRIMARY KEY)
- `country_code` (VARCHAR(2))
- `tender_id` (INTEGER REFERENCES tendly.tenders)
- `lot_id` (VARCHAR(100))
- `title` (TEXT)
- `description` (TEXT)
- `value_amount` (DECIMAL(15,2))
- `value_currency` (VARCHAR(3))

### documents
- `id` (SERIAL PRIMARY KEY)
- `country_code` (VARCHAR(2))
- `tender_id` (INTEGER REFERENCES tendly.tenders)
- `document_id` (VARCHAR(100))
- `title` (VARCHAR(255))
- `document_type` (VARCHAR(50))
- `url` (TEXT)
- `date_published` (TIMESTAMP)

### scraping_log
- `id` (SERIAL PRIMARY KEY)
- `country_code` (VARCHAR(2))
- `timestamp` (TIMESTAMP DEFAULT NOW())
- `records_fetched` (INTEGER)
- `records_inserted` (INTEGER)
- `records_duplicates` (INTEGER)
- `source` (VARCHAR(50))
- `parameters` (TEXT)
- `status` (VARCHAR(20))
- `error_message` (TEXT)

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

## 📊 Usage

### Home Page
- View database statistics and recent tenders
- Generate synthetic test data
- Monitor database health

### Scrape Tenders
- Configure scraping parameters (record count, stage, date range)
- Scrape data from Find a Tender API
- View scraping history and logs

### Search Tenders
- Search by keywords across titles and descriptions
- Filter by buyer name, status, and date range
- View detailed tender information

### Analytics & Export
- Visualize tender distribution by status, buyer, and value
- Export filtered data to Excel, CSV, or JSON
- Download comprehensive reports

## 🌍 Multi-Country Support

The application is designed to support multiple countries:

- All tables include a `country_code` column
- Database operations filter by country code
- Easy to extend to other countries (e.g., 'US', 'EU', 'CA')

To add a new country:
1. Set `COUNTRY_CODE` in `.env` to the new country code
2. Update the data generator with country-specific data
3. Configure the API scraper for the new country's tender service

## 🔧 Configuration

### Environment Variables

- `MAIN_DB_URL`: PostgreSQL connection string
- `OPENAI_API_KEY`: OpenAI API key for LangChain features
- `COUNTRY_CODE`: Country code for tender data (default: UK)

### Scraping Parameters

- **Record Count**: 10-500 records per scraping session
- **Procurement Stage**: planning, tender, award
- **Date Range**: 7-365 days back from current date

## 📦 Dependencies

Core dependencies (see `requirements.txt` for full list):

- `streamlit` - Web application framework
- `pandas` - Data manipulation and analysis
- `psycopg2-binary` - PostgreSQL adapter
- `sqlalchemy` - SQL toolkit and ORM
- `requests` - HTTP library for API calls
- `playwright` - Browser automation (fallback scraping)
- `faker` - Synthetic data generation
- `langchain` - LLM framework
- `langchain-openai` - OpenAI integration for LangChain
- `langgraph` - Graph-based LLM workflows
- `openpyxl` - Excel file operations

## 🚀 Deployment

### Streamlit Cloud

1. Fork this repository
2. Sign up at [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Add secrets in Streamlit Cloud dashboard:
   - `MAIN_DB_URL`
   - `OPENAI_API_KEY`
   - `COUNTRY_CODE`
5. Deploy!

### Heroku

```bash
heroku create uk-tender-scraper
heroku addons:create heroku-postgresql:mini
heroku config:set OPENAI_API_KEY=your_key_here
heroku config:set COUNTRY_CODE=UK
git push heroku main
heroku open
```

### Docker

```bash
docker build -t uk-tender-scraper .
docker run -p 8501:8501 \
  -e MAIN_DB_URL=your_db_url \
  -e OPENAI_API_KEY=your_key \
  -e COUNTRY_CODE=UK \
  uk-tender-scraper
```

## 📝 API Documentation

The application uses the Find a Tender API:
- Base URL: `https://www.find-tender.service.gov.uk/api/1.0/`
- Endpoint: `/ocdsReleasePackages`
- Format: OCDS (Open Contracting Data Standard)
- Authentication: Not required for public data

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
- Powered by [LangChain](https://langchain.com/) and [OpenAI](https://openai.com/)

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Lohusalu Capital Management** | UK Tender Scraper | Data from Find a Tender Service
