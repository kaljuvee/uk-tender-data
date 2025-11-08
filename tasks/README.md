# Tasks Directory

This directory contains command-line scripts for data collection and processing tasks.

## Available Tasks

### scrape_tenders.py

Command-line script to scrape UK tender data from the Find a Tender API.

**Usage:**
```bash
python tasks/scrape_tenders.py [OPTIONS]
```

**Options:**
- `--limit N`: Number of records to fetch (default: 100, max: 100)
- `--stage STAGE`: Filter by procurement stage (planning, tender, award)
- `--days-back N`: Number of days to look back (default: 7)
- `--country CODE`: Country code (default: from .env)

**Examples:**
```bash
# Fetch 100 tenders from the last 7 days
python tasks/scrape_tenders.py

# Fetch 50 tenders from the last 30 days
python tasks/scrape_tenders.py --limit 50 --days-back 30

# Fetch only tenders in "tender" stage
python tasks/scrape_tenders.py --stage tender

# Fetch tenders for a specific country
python tasks/scrape_tenders.py --country UK
```

**Output:**
- Inserts tender data into PostgreSQL database
- Logs scraping run to database (`tendly.scraping_log`)
- Writes JSON log file to `logs/scrape_YYYYMMDD_HHMMSS.json`
- Prints progress to console

**Exit Codes:**
- `0`: Success
- `1`: Error occurred

## Scheduling with Cron

### Setup Hourly Scraping

Run the setup script to configure hourly scraping:

```bash
bash tasks/setup_cron.sh
```

This will create a cron job that runs every hour at minute 0.

### Manual Cron Setup

Alternatively, set up cron manually:

```bash
# Edit crontab
crontab -e

# Add this line (adjust paths as needed):
0 * * * * cd /path/to/uk-tender-scraper && /path/to/venv/bin/python tasks/scrape_tenders.py --limit 100 --days-back 1 >> logs/cron.log 2>&1
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
# Delete the line containing 'scrape_tenders.py'
```

## Logging

All scraping tasks write logs to the `logs/` directory:

### JSON Logs
- **Location**: `logs/scrape_YYYYMMDD_HHMMSS.json`
- **Format**: Structured JSON with scraping metadata
- **Retention**: Kept indefinitely (implement rotation as needed)

### Cron Logs
- **Location**: `logs/cron.log`
- **Format**: Plain text output from cron execution
- **Content**: Console output and errors

### Log Structure

```json
{
  "task": "scrape_tenders",
  "start_time": "2025-11-08T16:00:00",
  "end_time": "2025-11-08T16:05:23",
  "duration_seconds": 323.45,
  "country_code": "UK",
  "parameters": {
    "limit": 100,
    "stage": null,
    "days_back": 7
  },
  "status": "success",
  "records_fetched": 100,
  "records_inserted": 85,
  "records_duplicates": 15,
  "errors": []
}
```

## Monitoring

### Check Latest Scraping Status

```bash
# View latest log
ls -t logs/scrape_*.json | head -1 | xargs cat | jq .

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
# Total records inserted today
jq -s 'map(.records_inserted) | add' logs/scrape_$(date +%Y%m%d)*.json

# Count scraping runs today
ls logs/scrape_$(date +%Y%m%d)*.json | wc -l
```

## Database Logging

In addition to JSON logs, scraping runs are logged to the database:

```sql
-- View recent scraping runs
SELECT * FROM tendly.scraping_log 
WHERE country_code = 'UK' 
ORDER BY timestamp DESC 
LIMIT 10;

-- Count successful runs today
SELECT COUNT(*) FROM tendly.scraping_log 
WHERE country_code = 'UK' 
  AND DATE(timestamp) = CURRENT_DATE 
  AND status = 'success';

-- Total records inserted today
SELECT SUM(records_inserted) FROM tendly.scraping_log 
WHERE country_code = 'UK' 
  AND DATE(timestamp) = CURRENT_DATE;
```

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

1. Test API manually:
   ```bash
   curl "https://www.find-tender.service.gov.uk/api/1.0/ocdsReleasePackages?limit=1"
   ```

2. Check API scraper:
   ```bash
   python -c "from utils.api_scraper import TenderAPIScraper; s = TenderAPIScraper(); print(s.fetch_tenders(limit=1))"
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
   crontab -l | grep scrape_tenders
   ```

## Best Practices

1. **Start Small**: Test with `--limit 5` before running large scrapes
2. **Monitor Logs**: Regularly check logs for errors
3. **Avoid Duplicates**: The scraper automatically skips duplicate tenders
4. **Rate Limiting**: Don't scrape more frequently than hourly to respect API limits
5. **Log Rotation**: Implement log rotation to manage disk space
6. **Backup Database**: Regular backups of PostgreSQL database
7. **Error Alerts**: Set up monitoring to alert on failed scraping runs

## Adding New Tasks

To add a new task:

1. Create a new Python script in `tasks/`
2. Follow the same structure as `scrape_tenders.py`
3. Include JSON logging
4. Add command-line argument parsing
5. Document in this README
6. Add to cron if needed

Example template:

```python
#!/usr/bin/env python3
"""
Task Name - Brief Description
"""

import sys
import os
import json
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

load_dotenv()

def main():
    # Task logic here
    pass

if __name__ == "__main__":
    main()
```

## Support

For issues or questions:
- Check logs in `logs/` directory
- Review database logs in `tendly.scraping_log`
- Open an issue on GitHub
