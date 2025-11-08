# Tasks Directory

This directory contains command-line scripts for data collection and processing tasks.

## Available Tasks

### 1. scrape_tenders.py - UK Tender Scraper

Command-line script to scrape UK tender data from the Find a Tender API.

**Usage:**
```bash
python tasks/scrape_tenders.py [OPTIONS]
```

**Options:**
- `--limit N`: Number of records to fetch (default: 100, max: 100)
- `--stage STAGE`: Filter by procurement stage (planning, tender, award)
- `--days-back N`: Number of days to look back (default: 7)
- `--country CODE`: Country code (default: UK)

**Examples:**
```bash
# Fetch 100 UK tenders from the last 7 days
python tasks/scrape_tenders.py

# Fetch 50 tenders from the last 30 days
python tasks/scrape_tenders.py --limit 50 --days-back 30

# Fetch only tenders in "tender" stage
python tasks/scrape_tenders.py --stage tender
```

**Data Source:** https://www.find-tender.service.gov.uk/api/1.0/ocdsReleasePackages

---

### 2. scrape_eu_tenders.py - EU Tender Scraper

Command-line script to scrape EU tender data from the TED (Tenders Electronic Daily) API.

**Usage:**
```bash
python tasks/scrape_eu_tenders.py [OPTIONS]
```

**Options:**
- `--limit N`: Number of records to fetch (default: 100)
- `--days-back N`: Number of days to look back (default: 7)
- `--country CODE`: Country code (default: EU)

**Examples:**
```bash
# Fetch 100 EU tenders
python tasks/scrape_eu_tenders.py

# Fetch 50 tenders
python tasks/scrape_eu_tenders.py --limit 50

# Fetch with custom parameters
python tasks/scrape_eu_tenders.py --limit 100 --country EU
```

**Data Source:** https://api.ted.europa.eu/v3/notices/search

**Note:** TED API searches for notices published yesterday (due to publication delays). The API returns notices from all EU member states.

---

## Output

Both scrapers:
- Insert tender data into PostgreSQL database (`tendly.tenders`)
- Log scraping run to database (`tendly.scraping_log`)
- Write JSON log file to `logs/scrape_*.json` or `logs/scrape_eu_*.json`
- Print progress to console

**Exit Codes:**
- `0`: Success
- `1`: Error occurred

---

## Scheduling with Cron

### Setup Hourly Scraping

Run the setup script to configure hourly scraping for both UK and EU:

```bash
bash tasks/setup_cron.sh
```

This will create cron jobs:
- **UK Scraper**: Every hour at minute 0
- **EU Scraper**: Every hour at minute 30

### Manual Cron Setup

Alternatively, set up cron manually:

```bash
# Edit crontab
crontab -e

# Add these lines (adjust paths as needed):
# UK tenders every hour
0 * * * * cd /path/to/uk-tender-scraper && source venv/bin/activate && python tasks/scrape_tenders.py --limit 100 >> logs/cron.log 2>&1

# EU tenders every hour (offset by 30 minutes)
30 * * * * cd /path/to/uk-tender-scraper && source venv/bin/activate && python tasks/scrape_eu_tenders.py --limit 100 >> logs/cron.log 2>&1
```

### Cron Schedule Examples

```bash
# Every hour at minute 0
0 * * * * /path/to/script

# Every 2 hours
0 */2 * * * /path/to/script

# Every day at 2 AM
0 2 * * * /path/to/script

# Every Monday at 9 AM
0 9 * * 1 /path/to/script
```

### View Current Cron Jobs

```bash
crontab -l
```

### Remove Cron Job

```bash
crontab -e
# Delete the lines containing scraper scripts
```

---

## Logging

All scraping tasks write logs to the `logs/` directory:

### JSON Logs
- **UK Scraper**: `logs/scrape_YYYYMMDD_HHMMSS.json`
- **EU Scraper**: `logs/scrape_eu_YYYYMMDD_HHMMSS.json`
- **Format**: Structured JSON with scraping metadata
- **Retention**: Kept indefinitely (implement rotation as needed)

### Cron Logs
- **Location**: `logs/cron.log`
- **Format**: Plain text output from cron execution
- **Content**: Console output and errors

### Log Structure

```json
{
  "task": "scrape_eu_tenders",
  "start_time": "2025-11-08T17:07:49.079015",
  "end_time": "2025-11-08T17:08:15.807396",
  "duration_seconds": 26.73,
  "country_code": "EU",
  "parameters": {
    "limit": 100,
    "days_back": 7
  },
  "status": "success",
  "records_fetched": 100,
  "records_inserted": 95,
  "records_duplicates": 5,
  "parse_errors": 0,
  "errors": []
}
```

---

## Monitoring

### Check Latest Scraping Status

```bash
# View latest UK log
ls -t logs/scrape_*.json | grep -v scrape_eu | head -1 | xargs cat | jq .

# View latest EU log
ls -t logs/scrape_eu_*.json | head -1 | xargs cat | jq .

# Check status
ls -t logs/scrape_*.json | head -1 | xargs jq -r '.status'

# Check records inserted
ls -t logs/scrape_*.json | head -1 | xargs jq -r '.records_inserted'
```

### Check for Errors

```bash
# Find failed scraping runs
grep -l '"status": "error"' logs/scrape_*.json

# View error details
jq -r 'select(.status == "error") | .errors' logs/scrape_*.json
```

### Daily Summary

```bash
# Total records inserted today (UK)
jq -s 'map(.records_inserted) | add' logs/scrape_$(date +%Y%m%d)*.json 2>/dev/null

# Total records inserted today (EU)
jq -s 'map(.records_inserted) | add' logs/scrape_eu_$(date +%Y%m%d)*.json 2>/dev/null

# Count scraping runs today
ls logs/scrape_$(date +%Y%m%d)*.json 2>/dev/null | wc -l
```

### Database Status

```bash
# Check tender counts by country
python -c "
import psycopg2, os
from dotenv import load_dotenv
load_dotenv()
conn = psycopg2.connect(os.getenv('MAIN_DB_URL'))
cur = conn.cursor()
cur.execute('SELECT country_code, COUNT(*) FROM tendly.tenders GROUP BY country_code')
print('Tenders by country:')
for row in cur.fetchall():
    print(f'  {row[0]}: {row[1]}')
cur.close()
conn.close()
"
```

---

## Database Logging

In addition to JSON logs, scraping runs are logged to the database:

```sql
-- View recent scraping runs (all countries)
SELECT * FROM tendly.scraping_log 
ORDER BY timestamp DESC 
LIMIT 10;

-- View UK scraping runs
SELECT * FROM tendly.scraping_log 
WHERE country_code = 'UK' 
ORDER BY timestamp DESC 
LIMIT 10;

-- View EU scraping runs
SELECT * FROM tendly.scraping_log 
WHERE country_code = 'EU' 
ORDER BY timestamp DESC 
LIMIT 10;

-- Count successful runs today
SELECT country_code, COUNT(*) 
FROM tendly.scraping_log 
WHERE DATE(timestamp) = CURRENT_DATE 
  AND status = 'success'
GROUP BY country_code;

-- Total records inserted today by country
SELECT country_code, SUM(records_inserted) 
FROM tendly.scraping_log 
WHERE DATE(timestamp) = CURRENT_DATE
GROUP BY country_code;
```

---

## Troubleshooting

### Script Fails to Run

1. Check Python environment:
   ```bash
   which python
   python --version
   ```

2. Check dependencies:
   ```bash
   pip list | grep -E "(requests|psycopg2|python-dotenv)"
   ```

3. Check environment variables:
   ```bash
   cat .env
   ```

### Database Connection Errors

1. Verify PostgreSQL connection:
   ```bash
   python -c "from utils.database import TenderDatabase; db = TenderDatabase(); print('Connected!')"
   ```

2. Check database URL in `.env`:
   ```bash
   grep MAIN_DB_URL .env
   ```

### API Errors

**UK Scraper:**
```bash
# Test API manually
curl "https://www.find-tender.service.gov.uk/api/1.0/ocdsReleasePackages?limit=1"

# Check API scraper
python -c "from utils.api_scraper import TenderAPIScraper; s = TenderAPIScraper(); print(s.fetch_tenders(limit=1))"
```

**EU Scraper:**
```bash
# Test TED API manually
curl -X POST "https://api.ted.europa.eu/v3/notices/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "PD=20241108", "fields": ["ND", "TI"]}'

# Check TED API scraper
python -c "from utils.ted_api_scraper import TEDAPIScraper; s = TEDAPIScraper(); print(s.search_by_date_range())"
```

### Cron Not Running

1. Check cron service:
   ```bash
   sudo service cron status
   ```

2. Check cron logs:
   ```bash
   tail -f logs/cron.log
   ```

3. Verify cron job:
   ```bash
   crontab -l | grep scrape
   ```

---

## Best Practices

1. **Start Small**: Test with `--limit 5` before running large scrapes
2. **Monitor Logs**: Regularly check logs for errors
3. **Avoid Duplicates**: Scrapers automatically skip duplicate tenders
4. **Rate Limiting**: Don't scrape more frequently than hourly to respect API limits
5. **Log Rotation**: Implement log rotation to manage disk space
6. **Backup Database**: Regular backups of PostgreSQL database
7. **Error Alerts**: Set up monitoring to alert on failed scraping runs
8. **Offset Timing**: Run different scrapers at different times (e.g., :00 and :30)

---

## Adding New Country Scrapers

To add a new country scraper:

1. **Create API Scraper Utility** (`utils/new_country_api_scraper.py`):
   ```python
   class NewCountryAPIScraper:
       def fetch_tenders(self, limit=100):
           # API logic here
           pass
       
       def parse_tender(self, raw_data):
           # Parsing logic here
           return {
               'notice_id': '...',
               'title': '...',
               'country_code': 'XX',  # New country code
               # ... other fields
           }
   ```

2. **Create Command-Line Script** (`tasks/scrape_new_country_tenders.py`):
   ```python
   from utils.database import TenderDatabase
   from utils.new_country_api_scraper import NewCountryAPIScraper
   
   def scrape_new_country_tenders(limit=100, country_code='XX'):
       db = TenderDatabase(country_code=country_code)
       scraper = NewCountryAPIScraper()
       # ... scraping logic
   ```

3. **Update Cron** (offset by different minute):
   ```bash
   15 * * * * cd /path/to/uk-tender-scraper && source venv/bin/activate && python tasks/scrape_new_country_tenders.py --limit 100 >> logs/cron.log 2>&1
   ```

4. **Update Documentation** in this README

All data will be stored in the same `tendly.tenders` table, filtered by `country_code`.

---

## Support

For issues or questions:
- Check logs in `logs/` directory
- Review database logs in `tendly.scraping_log`
- Test API connections manually
- Open an issue on GitHub

