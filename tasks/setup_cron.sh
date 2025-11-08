#!/bin/bash
# Setup cron job for hourly tender scraping

# Get the absolute path to the project directory
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
PYTHON_PATH="$PROJECT_DIR/venv/bin/python"
SCRIPT_PATH="$PROJECT_DIR/tasks/scrape_tenders.py"

# Create cron job entry
CRON_JOB="0 * * * * cd $PROJECT_DIR && $PYTHON_PATH $SCRIPT_PATH --limit 100 --days-back 1 >> $PROJECT_DIR/logs/cron.log 2>&1"

echo "Setting up cron job for hourly tender scraping..."
echo ""
echo "Cron job command:"
echo "$CRON_JOB"
echo ""

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "scrape_tenders.py"; then
    echo "Cron job already exists. Removing old entry..."
    crontab -l 2>/dev/null | grep -v "scrape_tenders.py" | crontab -
fi

# Add new cron job
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo "Cron job added successfully!"
echo ""
echo "The scraper will run every hour at minute 0."
echo "Logs will be written to:"
echo "  - JSON logs: $PROJECT_DIR/logs/scrape_*.json"
echo "  - Cron logs: $PROJECT_DIR/logs/cron.log"
echo ""
echo "To view current cron jobs:"
echo "  crontab -l"
echo ""
echo "To remove the cron job:"
echo "  crontab -e"
echo "  (then delete the line containing 'scrape_tenders.py')"
