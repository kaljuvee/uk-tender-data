"""Test API scraper functionality."""

import sys
import os
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.api_scraper import TenderAPIScraper


def test_api_scraper():
    """Test API scraper operations."""
    
    results = {
        "test_name": "API Scraper Test",
        "timestamp": datetime.now().isoformat(),
        "tests": []
    }
    
    scraper = TenderAPIScraper()
    
    # Test 1: Fetch tenders from API
    try:
        response = scraper.fetch_tenders(limit=5)
        
        if 'releases' in response:
            results["tests"].append({
                "name": "Fetch Tenders",
                "status": "PASS",
                "message": f"Successfully fetched {len(response['releases'])} releases from API"
            })
        else:
            results["tests"].append({
                "name": "Fetch Tenders",
                "status": "FAIL",
                "message": "Response missing 'releases' field"
            })
    except Exception as e:
        results["tests"].append({
            "name": "Fetch Tenders",
            "status": "FAIL",
            "message": str(e)
        })
    
    # Test 2: Parse release
    try:
        # Fetch a sample release
        response = scraper.fetch_tenders(limit=1)
        
        if response.get('releases'):
            release = response['releases'][0]
            parsed = scraper.parse_release(release)
            
            required_fields = ['notice_id', 'ocid', 'title']
            missing_fields = [f for f in required_fields if f not in parsed or not parsed[f]]
            
            if not missing_fields:
                results["tests"].append({
                    "name": "Parse Release",
                    "status": "PASS",
                    "message": f"Successfully parsed release with notice_id: {parsed.get('notice_id')}"
                })
            else:
                results["tests"].append({
                    "name": "Parse Release",
                    "status": "FAIL",
                    "message": f"Missing required fields: {missing_fields}"
                })
        else:
            results["tests"].append({
                "name": "Parse Release",
                "status": "SKIP",
                "message": "No releases available to parse"
            })
    except Exception as e:
        results["tests"].append({
            "name": "Parse Release",
            "status": "FAIL",
            "message": str(e)
        })
    
    # Test 3: Scrape and parse multiple
    try:
        parsed_tenders = scraper.scrape_and_parse(total_records=3, days_back=30)
        
        if isinstance(parsed_tenders, list) and len(parsed_tenders) > 0:
            results["tests"].append({
                "name": "Scrape and Parse Multiple",
                "status": "PASS",
                "message": f"Successfully scraped and parsed {len(parsed_tenders)} tenders"
            })
        else:
            results["tests"].append({
                "name": "Scrape and Parse Multiple",
                "status": "FAIL",
                "message": "Expected non-empty list of parsed tenders"
            })
    except Exception as e:
        results["tests"].append({
            "name": "Scrape and Parse Multiple",
            "status": "FAIL",
            "message": str(e)
        })
    
    # Test 4: Stage filtering
    try:
        response = scraper.fetch_tenders(limit=3, stages="tender")
        
        if 'releases' in response:
            results["tests"].append({
                "name": "Stage Filtering",
                "status": "PASS",
                "message": f"Successfully filtered by stage, got {len(response['releases'])} releases"
            })
        else:
            results["tests"].append({
                "name": "Stage Filtering",
                "status": "FAIL",
                "message": "Stage filtering failed"
            })
    except Exception as e:
        results["tests"].append({
            "name": "Stage Filtering",
            "status": "FAIL",
            "message": str(e)
        })
    
    # Summary
    total_tests = len(results["tests"])
    passed_tests = sum(1 for t in results["tests"] if t["status"] == "PASS")
    skipped_tests = sum(1 for t in results["tests"] if t["status"] == "SKIP")
    failed_tests = total_tests - passed_tests - skipped_tests
    
    results["summary"] = {
        "total": total_tests,
        "passed": passed_tests,
        "failed": failed_tests,
        "skipped": skipped_tests,
        "success_rate": f"{(passed_tests/total_tests)*100:.1f}%"
    }
    
    return results


if __name__ == "__main__":
    print("Running API Scraper Tests...")
    print("=" * 60)
    
    results = test_api_scraper()
    
    # Print results
    for test in results["tests"]:
        if test["status"] == "PASS":
            status_symbol = "✓"
        elif test["status"] == "SKIP":
            status_symbol = "○"
        else:
            status_symbol = "✗"
        
        print(f"{status_symbol} {test['name']}: {test['message']}")
    
    print("=" * 60)
    print(f"Summary: {results['summary']['passed']}/{results['summary']['total']} tests passed ({results['summary']['success_rate']})")
    
    # Save to JSON
    os.makedirs("test-results", exist_ok=True)
    output_file = "test-results/api_scraper_test.json"
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")
