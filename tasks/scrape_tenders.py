#!/usr/bin/env python3
"""
UK Tender Scraper - Command Line Task
Scrapes tender data from Find a Tender API and stores in PostgreSQL.
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
from utils.api_scraper import TenderAPIScraper

# Load environment variables
load_dotenv()


def log_to_json(log_data: dict, log_dir: str = "logs"):
    """Write log data to JSON file."""
    os.makedirs(log_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"scrape_{timestamp}.json")
    
    with open(log_file, 'w') as f:
        json.dump(log_data, f, indent=2, default=str)
    
    return log_file


def scrape_tenders(
    limit: int = 100,
    stage: str = None,
    days_back: int = 7,
    country_code: str = None
):
    """
    Scrape tenders from Find a Tender API.
    
    Args:
        limit: Number of records to fetch (max 100 per request)
        stage: Procurement stage filter (planning, tender, award)
        days_back: Number of days to look back
        country_code: Country code for data (default from env)
    
    Returns:
        dict: Log data with scraping results
    """
    start_time = datetime.now()
    
    # Get country code from env if not provided
    if country_code is None:
        country_code = os.getenv('COUNTRY_CODE', 'UK')
    
    log_data = {
        "task": "scrape_tenders",
        "start_time": start_time.isoformat(),
        "country_code": country_code,
        "parameters": {
            "limit": limit,
            "stage": stage,
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
        scraper = TenderAPIScraper()
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting tender scraping...")
        print(f"  Country: {country_code}")
        print(f"  Limit: {limit}")
        print(f"  Stage: {stage or 'all'}")
        print(f"  Days back: {days_back}")
        
        # Calculate date range
        updated_to = datetime.now()
        updated_from = updated_to - timedelta(days=days_back)
        
        # Fetch tenders from API
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Fetching tenders from API...")
        
        # Use fetch_multiple_pages which handles pagination
        all_releases = scraper.fetch_multiple_pages(
            total_records=limit,
            stages=stage,
            days_back=days_back
        )
        
        # Parse releases into tender format
        tenders = [scraper.parse_release(release) for release in all_releases]
        
        log_data["records_fetched"] = len(tenders)
        print(f"  Fetched: {len(tenders)} tenders")
        
        # Insert tenders into database
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Inserting tenders into database...")
        inserted = 0
        duplicates = 0
        
        for tender in tenders:
            # Add country code to tender data
            tender['country_code'] = country_code
            
            tender_id = db.insert_tender(tender)
            if tender_id:
                inserted += 1
                if inserted % 10 == 0:
                    print(f"  Inserted: {inserted} tenders...")
            else:
                duplicates += 1
        
        log_data["records_inserted"] = inserted
        log_data["records_duplicates"] = duplicates
        
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Scraping completed:")
        print(f"  Fetched: {len(tenders)}")
        print(f"  Inserted: {inserted}")
        print(f"  Duplicates: {duplicates}")
        
        # Log to database
        db.log_scraping_run(
            records_fetched=len(tenders),
            records_inserted=inserted,
            records_duplicates=duplicates,
            source="api",
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
                source="api",
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
        description="Scrape UK tender data from Find a Tender API"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=100,
        help="Number of records to fetch (default: 100, max: 100)"
    )
    parser.add_argument(
        "--stage",
        type=str,
        choices=["planning", "tender", "award"],
        help="Filter by procurement stage"
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
        default=None,
        help="Country code (default: from .env)"
    )
    
    args = parser.parse_args()
    
    # Run scraper
    result = scrape_tenders(
        limit=args.limit,
        stage=args.stage,
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
