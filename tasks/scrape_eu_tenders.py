#!/usr/bin/env python3
"""
EU Tender Scraper - Command Line Task
Scrapes tender data from TED (Tenders Electronic Daily) API and stores in PostgreSQL.
Can be run hourly via cron job.
"""

import sys
import os
import json
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from utils.database import TenderDatabase
from utils.ted_api_scraper import TEDAPIScraper

# Load environment variables
load_dotenv()


def log_to_json(log_data: dict, log_dir: str = "logs"):
    """Write log data to JSON file."""
    os.makedirs(log_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"scrape_eu_{timestamp}.json")
    
    with open(log_file, 'w') as f:
        json.dump(log_data, f, indent=2, default=str)
    
    return log_file


def scrape_eu_tenders(
    limit: int = 100,
    days_back: int = 7,
    country_code: str = 'EU'
):
    """
    Scrape EU tenders from TED API.
    
    Args:
        limit: Number of records to fetch (max 100 per request)
        days_back: Number of days to look back
        country_code: Country code for data (default: EU)
    
    Returns:
        dict: Log data with scraping results
    """
    start_time = datetime.now()
    
    log_data = {
        "task": "scrape_eu_tenders",
        "start_time": start_time.isoformat(),
        "country_code": country_code,
        "parameters": {
            "limit": limit,
            "days_back": days_back
        },
        "status": "started",
        "records_fetched": 0,
        "records_inserted": 0,
        "records_duplicates": 0,
        "errors": []
    }
    
    try:
        # Initialize database and scraper
        db = TenderDatabase(country_code=country_code)
        scraper = TEDAPIScraper()
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting EU tender scraping...")
        print(f"  Country: {country_code}")
        print(f"  Limit: {limit}")
        print(f"  Days back: {days_back}")
        
        # Fetch tenders from TED API
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Fetching tenders from TED API...")
        
        all_notices = scraper.fetch_multiple_pages(
            total_records=limit,
            days_back=days_back
        )
        
        log_data["records_fetched"] = len(all_notices)
        print(f"  Fetched: {len(all_notices)} notices")
        
        # Parse and insert tenders into database
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Parsing and inserting tenders...")
        inserted = 0
        duplicates = 0
        parse_errors = 0
        
        for notice in all_notices:
            try:
                # Parse notice into tender format
                tender = scraper.parse_notice(notice)
                
                # Add country code to tender data
                tender['country_code'] = country_code
                
                # Insert into database
                tender_id = db.insert_tender(tender)
                if tender_id:
                    inserted += 1
                    if inserted % 10 == 0:
                        print(f"  Inserted: {inserted} tenders...")
                else:
                    duplicates += 1
            except Exception as e:
                parse_errors += 1
                error_msg = f"Error parsing notice {notice.get('ND', 'unknown')}: {str(e)}"
                print(f"  Warning: {error_msg}")
                log_data["errors"].append({
                    "timestamp": datetime.now().isoformat(),
                    "error": error_msg,
                    "type": "parse_error",
                    "notice_id": notice.get('ND', 'unknown')
                })
        
        log_data["records_inserted"] = inserted
        log_data["records_duplicates"] = duplicates
        log_data["parse_errors"] = parse_errors
        
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Scraping completed:")
        print(f"  Fetched: {len(all_notices)}")
        print(f"  Inserted: {inserted}")
        print(f"  Duplicates: {duplicates}")
        print(f"  Parse errors: {parse_errors}")
        
        # Log to database
        db.log_scraping_run(
            records_fetched=len(all_notices),
            records_inserted=inserted,
            records_duplicates=duplicates,
            source="ted_api",
            parameters=json.dumps(log_data["parameters"])
        )
        
        log_data["status"] = "success"
        
    except Exception as e:
        error_msg = f"Error during scraping: {str(e)}"
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ERROR: {error_msg}")
        
        log_data["status"] = "error"
        log_data["errors"].append({
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "type": type(e).__name__
        })
        
        # Log error to database
        try:
            db.log_scraping_run(
                records_fetched=log_data["records_fetched"],
                records_inserted=log_data["records_inserted"],
                records_duplicates=log_data["records_duplicates"],
                source="ted_api",
                parameters=json.dumps(log_data["parameters"]),
                status="error",
                error_message=str(e)
            )
        except:
            pass
    
    finally:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        log_data["end_time"] = end_time.isoformat()
        log_data["duration_seconds"] = duration
        
        # Write log to JSON file
        log_file = log_to_json(log_data)
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Log written to: {log_file}")
    
    return log_data


def main():
    """Main entry point for command-line execution."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Scrape EU tender data from TED (Tenders Electronic Daily) API"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=100,
        help="Number of records to fetch (default: 100, max: 100)"
    )
    parser.add_argument(
        "--days-back",
        type=int,
        default=7,
        help="Number of days to look back (default: 7)"
    )
    parser.add_argument(
        "--country",
        type=str,
        default='EU',
        help="Country code (default: EU)"
    )
    
    args = parser.parse_args()
    
    # Run scraper
    result = scrape_eu_tenders(
        limit=args.limit,
        days_back=args.days_back,
        country_code=args.country
    )
    
    # Exit with appropriate code
    if result["status"] == "success":
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
