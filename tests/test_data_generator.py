"""Test synthetic data generator."""

import sys
import os
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_generator import TenderDataGenerator


def test_data_generator():
    """Test synthetic data generation."""
    
    results = {
        "test_name": "Data Generator Test",
        "timestamp": datetime.now().isoformat(),
        "tests": []
    }
    
    generator = TenderDataGenerator()
    
    # Test 1: Generate single tender
    try:
        tender = generator.generate_tender()
        
        required_fields = [
            'notice_id', 'ocid', 'title', 'description', 
            'status', 'buyer_name', 'value_amount'
        ]
        
        missing_fields = [f for f in required_fields if f not in tender]
        
        if not missing_fields:
            results["tests"].append({
                "name": "Generate Single Tender",
                "status": "PASS",
                "message": f"Generated tender with notice_id: {tender['notice_id']}"
            })
        else:
            results["tests"].append({
                "name": "Generate Single Tender",
                "status": "FAIL",
                "message": f"Missing required fields: {missing_fields}"
            })
    except Exception as e:
        results["tests"].append({
            "name": "Generate Single Tender",
            "status": "FAIL",
            "message": str(e)
        })
    
    # Test 2: Generate multiple tenders
    try:
        tenders = generator.generate_tenders(count=10)
        
        if isinstance(tenders, list) and len(tenders) == 10:
            results["tests"].append({
                "name": "Generate Multiple Tenders",
                "status": "PASS",
                "message": f"Generated {len(tenders)} tenders successfully"
            })
        else:
            results["tests"].append({
                "name": "Generate Multiple Tenders",
                "status": "FAIL",
                "message": f"Expected 10 tenders, got {len(tenders) if isinstance(tenders, list) else 'not a list'}"
            })
    except Exception as e:
        results["tests"].append({
            "name": "Generate Multiple Tenders",
            "status": "FAIL",
            "message": str(e)
        })
    
    # Test 3: Unique notice IDs
    try:
        tenders = generator.generate_tenders(count=20)
        notice_ids = [t['notice_id'] for t in tenders]
        unique_ids = set(notice_ids)
        
        if len(unique_ids) == len(notice_ids):
            results["tests"].append({
                "name": "Unique Notice IDs",
                "status": "PASS",
                "message": "All generated notice IDs are unique"
            })
        else:
            results["tests"].append({
                "name": "Unique Notice IDs",
                "status": "FAIL",
                "message": f"Found {len(notice_ids) - len(unique_ids)} duplicate notice IDs"
            })
    except Exception as e:
        results["tests"].append({
            "name": "Unique Notice IDs",
            "status": "FAIL",
            "message": str(e)
        })
    
    # Test 4: Data types
    try:
        tender = generator.generate_tender()
        
        type_checks = [
            (tender['notice_id'], str, 'notice_id'),
            (tender['title'], str, 'title'),
            (tender['value_amount'], (int, float), 'value_amount'),
            (tender['buyer_name'], str, 'buyer_name'),
        ]
        
        type_errors = []
        for value, expected_type, field_name in type_checks:
            if not isinstance(value, expected_type):
                type_errors.append(f"{field_name} is {type(value)}, expected {expected_type}")
        
        if not type_errors:
            results["tests"].append({
                "name": "Data Types",
                "status": "PASS",
                "message": "All fields have correct data types"
            })
        else:
            results["tests"].append({
                "name": "Data Types",
                "status": "FAIL",
                "message": "; ".join(type_errors)
            })
    except Exception as e:
        results["tests"].append({
            "name": "Data Types",
            "status": "FAIL",
            "message": str(e)
        })
    
    # Test 5: Lots generation
    try:
        # Generate multiple tenders and check if some have lots
        tenders = generator.generate_tenders(count=20)
        tenders_with_lots = [t for t in tenders if 'lots' in t and t['lots']]
        
        if len(tenders_with_lots) > 0:
            results["tests"].append({
                "name": "Lots Generation",
                "status": "PASS",
                "message": f"{len(tenders_with_lots)} out of 20 tenders have lots"
            })
        else:
            results["tests"].append({
                "name": "Lots Generation",
                "status": "WARN",
                "message": "No tenders generated with lots (random, may be OK)"
            })
    except Exception as e:
        results["tests"].append({
            "name": "Lots Generation",
            "status": "FAIL",
            "message": str(e)
        })
    
    # Test 6: Value ranges
    try:
        tenders = generator.generate_tenders(count=50)
        values = [t['value_amount'] for t in tenders]
        
        min_val = min(values)
        max_val = max(values)
        
        # Check if values are in reasonable range (10k to 10M)
        if min_val >= 10000 and max_val <= 10000000:
            results["tests"].append({
                "name": "Value Ranges",
                "status": "PASS",
                "message": f"Values range from £{min_val:,.2f} to £{max_val:,.2f}"
            })
        else:
            results["tests"].append({
                "name": "Value Ranges",
                "status": "FAIL",
                "message": f"Values outside expected range: £{min_val:,.2f} to £{max_val:,.2f}"
            })
    except Exception as e:
        results["tests"].append({
            "name": "Value Ranges",
            "status": "FAIL",
            "message": str(e)
        })
    
    # Summary
    total_tests = len(results["tests"])
    passed_tests = sum(1 for t in results["tests"] if t["status"] == "PASS")
    warned_tests = sum(1 for t in results["tests"] if t["status"] == "WARN")
    failed_tests = total_tests - passed_tests - warned_tests
    
    results["summary"] = {
        "total": total_tests,
        "passed": passed_tests,
        "failed": failed_tests,
        "warnings": warned_tests,
        "success_rate": f"{(passed_tests/total_tests)*100:.1f}%"
    }
    
    return results


if __name__ == "__main__":
    print("Running Data Generator Tests...")
    print("=" * 60)
    
    results = test_data_generator()
    
    # Print results
    for test in results["tests"]:
        if test["status"] == "PASS":
            status_symbol = "✓"
        elif test["status"] == "WARN":
            status_symbol = "⚠"
        else:
            status_symbol = "✗"
        
        print(f"{status_symbol} {test['name']}: {test['message']}")
    
    print("=" * 60)
    print(f"Summary: {results['summary']['passed']}/{results['summary']['total']} tests passed ({results['summary']['success_rate']})")
    
    # Save to JSON
    os.makedirs("test-results", exist_ok=True)
    output_file = "test-results/data_generator_test.json"
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")
