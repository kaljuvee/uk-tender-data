"""Test database functionality."""

import sys
import os
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database import TenderDatabase
from utils.data_generator import TenderDataGenerator


def test_database_operations():
    """Test basic database operations."""
    
    results = {
        "test_name": "Database Operations Test",
        "timestamp": datetime.now().isoformat(),
        "tests": []
    }
    
    # Use a test database
    db = TenderDatabase(db_path="sql/test_tenders.db")
    
    # Test 1: Database initialization
    try:
        stats = db.get_statistics()
        results["tests"].append({
            "name": "Database Initialization",
            "status": "PASS",
            "message": f"Database initialized successfully. Total tenders: {stats.get('total_tenders', 0)}"
        })
    except Exception as e:
        results["tests"].append({
            "name": "Database Initialization",
            "status": "FAIL",
            "message": str(e)
        })
    
    # Test 2: Insert tender
    try:
        generator = TenderDataGenerator()
        test_tender = generator.generate_tender(notice_number=99999)
        
        tender_id = db.insert_tender(test_tender)
        
        if tender_id:
            results["tests"].append({
                "name": "Insert Tender",
                "status": "PASS",
                "message": f"Tender inserted successfully with ID: {tender_id}"
            })
        else:
            results["tests"].append({
                "name": "Insert Tender",
                "status": "FAIL",
                "message": "Failed to insert tender (returned None)"
            })
    except Exception as e:
        results["tests"].append({
            "name": "Insert Tender",
            "status": "FAIL",
            "message": str(e)
        })
    
    # Test 3: Duplicate detection
    try:
        # Try to insert the same tender again
        duplicate_id = db.insert_tender(test_tender)
        
        if duplicate_id is None:
            results["tests"].append({
                "name": "Duplicate Detection",
                "status": "PASS",
                "message": "Duplicate tender correctly rejected"
            })
        else:
            results["tests"].append({
                "name": "Duplicate Detection",
                "status": "FAIL",
                "message": "Duplicate tender was inserted (should have been rejected)"
            })
    except Exception as e:
        results["tests"].append({
            "name": "Duplicate Detection",
            "status": "FAIL",
            "message": str(e)
        })
    
    # Test 4: Get all tenders
    try:
        tenders = db.get_all_tenders(limit=10)
        
        if isinstance(tenders, list):
            results["tests"].append({
                "name": "Get All Tenders",
                "status": "PASS",
                "message": f"Retrieved {len(tenders)} tenders"
            })
        else:
            results["tests"].append({
                "name": "Get All Tenders",
                "status": "FAIL",
                "message": "Expected list, got something else"
            })
    except Exception as e:
        results["tests"].append({
            "name": "Get All Tenders",
            "status": "FAIL",
            "message": str(e)
        })
    
    # Test 5: Search tenders
    try:
        search_results = db.search_tenders(keyword="test")
        
        if isinstance(search_results, list):
            results["tests"].append({
                "name": "Search Tenders",
                "status": "PASS",
                "message": f"Search completed, found {len(search_results)} results"
            })
        else:
            results["tests"].append({
                "name": "Search Tenders",
                "status": "FAIL",
                "message": "Expected list, got something else"
            })
    except Exception as e:
        results["tests"].append({
            "name": "Search Tenders",
            "status": "FAIL",
            "message": str(e)
        })
    
    # Test 6: Logging
    try:
        db.log_scraping_run(
            records_fetched=10,
            records_inserted=8,
            records_duplicates=2,
            source="test"
        )
        
        logs = db.get_scraping_logs(limit=1)
        
        if logs and len(logs) > 0:
            results["tests"].append({
                "name": "Scraping Log",
                "status": "PASS",
                "message": "Scraping run logged successfully"
            })
        else:
            results["tests"].append({
                "name": "Scraping Log",
                "status": "FAIL",
                "message": "No logs found after logging"
            })
    except Exception as e:
        results["tests"].append({
            "name": "Scraping Log",
            "status": "FAIL",
            "message": str(e)
        })
    
    # Test 7: Statistics
    try:
        stats = db.get_statistics()
        
        if 'total_tenders' in stats:
            results["tests"].append({
                "name": "Statistics",
                "status": "PASS",
                "message": f"Statistics retrieved: {stats}"
            })
        else:
            results["tests"].append({
                "name": "Statistics",
                "status": "FAIL",
                "message": "Statistics missing expected fields"
            })
    except Exception as e:
        results["tests"].append({
            "name": "Statistics",
            "status": "FAIL",
            "message": str(e)
        })
    
    # Summary
    total_tests = len(results["tests"])
    passed_tests = sum(1 for t in results["tests"] if t["status"] == "PASS")
    failed_tests = total_tests - passed_tests
    
    results["summary"] = {
        "total": total_tests,
        "passed": passed_tests,
        "failed": failed_tests,
        "success_rate": f"{(passed_tests/total_tests)*100:.1f}%"
    }
    
    return results


if __name__ == "__main__":
    print("Running Database Tests...")
    print("=" * 60)
    
    results = test_database_operations()
    
    # Print results
    for test in results["tests"]:
        status_symbol = "✓" if test["status"] == "PASS" else "✗"
        print(f"{status_symbol} {test['name']}: {test['message']}")
    
    print("=" * 60)
    print(f"Summary: {results['summary']['passed']}/{results['summary']['total']} tests passed ({results['summary']['success_rate']})")
    
    # Save to JSON
    os.makedirs("test-results", exist_ok=True)
    output_file = "test-results/database_test.json"
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")
