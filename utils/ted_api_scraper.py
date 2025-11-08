"""
EU TED API Scraper - Fetch tenders from Tenders Electronic Daily
"""

import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json


class TEDAPIScraper:
    """Scraper for EU Tenders Electronic Daily (TED) API."""
    
    BASE_URL = "https://api.ted.europa.eu"
    SEARCH_ENDPOINT = "/v3/notices/search"
    
    def __init__(self):
        """Initialize the TED API scraper."""
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'User-Agent': 'UK-Tender-Scraper/1.0-EU'
        })
    
    def search_notices(
        self,
        query: str = "*",
        fields: List[str] = None
    ) -> Dict[str, Any]:
        """
        Search for notices using TED Search API.
        
        Args:
            query: Expert query string (default: "*" for all)
            fields: List of fields to return (required by API)
        
        Returns:
            API response as dictionary
        """
        url = f"{self.BASE_URL}{self.SEARCH_ENDPOINT}"
        
        # Default fields if not specified
        if fields is None:
            fields = [
                "ND",  # Notice Document ID
                "PD",  # Publication Date
                "DD",  # Dispatch Date
                "TI",  # Title
                "CY",  # Country
                "TD",  # Document Type
                "NC",  # Nature of Contract
                "DT",  # Deadline
                "total-value",  # Total contract value
                "result-value-cur-lot",  # Result value with currency
                "framework-value-notice",  # Framework value
                "BT-27-Lot"  # Estimated value
            ]
        
        payload = {
            "query": query,
            "fields": fields
        }
        
        try:
            response = self.session.post(url, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            # Try to get error details from response
            error_detail = ""
            try:
                if response.text:
                    error_detail = f" - {response.text}"
            except:
                pass
            raise Exception(f"TED API request failed: {str(e)}{error_detail}")
    
    def search_by_date_range(
        self,
        days_back: int = 7
    ) -> Dict[str, Any]:
        """
        Search for notices published within a date range.
        
        Args:
            days_back: Number of days to look back
        
        Returns:
            API response as dictionary
        """
        # Search for recent dates (yesterday to account for timezone differences)
        # TED API expert query syntax is complex, so we'll use a simple date query
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
        
        # Build expert query for publication date
        # PD = Publication Date field in TED
        query = f"PD={yesterday}"
        
        return self.search_notices(query=query)
    
    def fetch_multiple_pages(
        self,
        total_records: int = 100,
        days_back: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Fetch tender data from TED API.
        
        Args:
            total_records: Total number of records to fetch (limit)
            days_back: Number of days to look back
        
        Returns:
            List of all notices
        """
        # TED API returns results based on query, not pagination
        # We'll fetch once and limit the results
        response = self.search_by_date_range(days_back=days_back)
        
        # Extract notices from response
        notices = response.get('notices', [])
        
        # Return up to total_records
        return notices[:total_records]
    
    def parse_notice(self, notice: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse a TED notice into our database format.
        
        Args:
            notice: TED notice object
        
        Returns:
            Parsed tender data
        """
        # Helper to extract value from field (could be string or dict)
        def get_value(field_data, lang='eng'):
            if isinstance(field_data, dict):
                # Try English first, then any available language
                return field_data.get(lang, field_data.get(list(field_data.keys())[0] if field_data else '', ''))
            return field_data or ''
        
        # Helper to get first item from list or the value itself
        def get_first(value):
            if isinstance(value, list):
                return value[0] if value else ''
            return value or ''
        
        # Extract basic information
        tender_data = {
            'notice_id': notice.get('ND', ''),  # Notice Document ID
            'ocid': notice.get('PD', ''),  # Publication Document ID
            'publication_date': self._parse_date(notice.get('DD')),  # Dispatch Date
        }
        
        # Extract title (can be multilingual dict)
        title_data = notice.get('TI', '')
        tender_data['title'] = get_value(title_data)
        
        # Description - use title if no separate description
        tender_data['description'] = tender_data['title']
        
        # Extract buyer information (country)
        cy_data = notice.get('CY', '')
        country = get_first(cy_data)
        tender_data['buyer_name'] = f"{country} Contracting Authority"
        tender_data['buyer_id'] = country
        
        # Extract status and stage
        td_data = notice.get('TD', '')
        tender_data['status'] = self._map_status(get_first(td_data))
        
        # Extract procurement category
        nc_data = notice.get('NC', '')
        tender_data['stage'] = get_first(nc_data)
        tender_data['main_procurement_category'] = self._map_category(get_first(nc_data))
        
        # Extract value information from various TED fields
        value_amount = None
        value_currency = 'EUR'
        
        # Try total-value first
        total_value = notice.get('total-value')
        if total_value:
            value_amount = self._extract_value_amount(total_value)
            value_currency = self._extract_currency(total_value) or 'EUR'
        
        # Try result-value-cur-lot if no total value
        if not value_amount:
            result_value = notice.get('result-value-cur-lot')
            if result_value:
                value_amount = self._extract_value_amount(result_value)
                value_currency = self._extract_currency(result_value) or 'EUR'
        
        # Try framework-value-notice
        if not value_amount:
            framework_value = notice.get('framework-value-notice')
            if framework_value:
                value_amount = self._extract_value_amount(framework_value)
                value_currency = self._extract_currency(framework_value) or 'EUR'
        
        # Try BT-27-Lot (estimated value)
        if not value_amount:
            estimated_value = notice.get('BT-27-Lot')
            if estimated_value:
                value_amount = self._extract_value_amount(estimated_value)
                value_currency = self._extract_currency(estimated_value) or 'EUR'
        
        tender_data['value_amount'] = value_amount
        tender_data['value_currency'] = value_currency
        
        # Classification
        tender_data['classification_id'] = None
        
        # Extract deadline
        deadline = notice.get('DT', '')
        if deadline:
            tender_data['tender_period_end_date'] = self._parse_date(get_first(deadline))
        else:
            tender_data['tender_period_end_date'] = None
        
        return tender_data
    
    def _parse_date(self, date_str: str) -> Optional[str]:
        """
        Parse TED date string to ISO format.
        
        Args:
            date_str: Date string in various TED formats
        
        Returns:
            ISO formatted date string or None
        """
        if not date_str:
            return None
        
        try:
            # TED dates are typically in YYYYMMDD format
            if len(date_str) == 8 and date_str.isdigit():
                dt = datetime.strptime(date_str, "%Y%m%d")
                return dt.isoformat()
            
            # Try ISO format
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.isoformat()
        except:
            return None
    
    def _map_status(self, doc_type: str) -> str:
        """
        Map TED document type to our status field.
        
        Args:
            doc_type: TED document type code
        
        Returns:
            Mapped status string
        """
        # TED document types
        type_mapping = {
            '1': 'planned',      # Prior information notice
            '2': 'active',       # Contract notice
            '3': 'active',       # Contract award notice
            '4': 'complete',     # Periodic indicative notice
            '5': 'active',       # Qualification system
            '6': 'complete',     # Contract award
            '7': 'active',       # Corrigendum
            '8': 'active',       # Voluntary ex ante transparency notice
            '9': 'active',       # Concession notice
        }
        
        return type_mapping.get(doc_type, 'active')
    
    def _extract_value_amount(self, value_data: Any) -> Optional[float]:
        """
        Extract numeric value amount from TED value field.
        
        Args:
            value_data: Value data (could be string, number, list, or dict)
        
        Returns:
            Numeric value or None
        """
        if not value_data:
            return None
        
        try:
            # If it's already a number
            if isinstance(value_data, (int, float)):
                return float(value_data)
            
            # If it's a list, take first item
            if isinstance(value_data, list):
                if value_data:
                    return self._extract_value_amount(value_data[0])
                return None
            
            # If it's a dict, look for common value keys
            if isinstance(value_data, dict):
                for key in ['value', 'amount', 'val']:
                    if key in value_data:
                        return self._extract_value_amount(value_data[key])
                # If dict has numeric values, try first one
                for v in value_data.values():
                    result = self._extract_value_amount(v)
                    if result:
                        return result
                return None
            
            # If it's a string, try to parse as number
            if isinstance(value_data, str):
                # Remove common currency symbols and whitespace
                cleaned = value_data.replace(',', '').replace(' ', '').strip()
                for symbol in ['€', '$', '£', 'EUR', 'USD', 'GBP']:
                    cleaned = cleaned.replace(symbol, '')
                if cleaned:
                    return float(cleaned)
            
        except (ValueError, TypeError):
            pass
        
        return None
    
    def _extract_currency(self, value_data: Any) -> Optional[str]:
        """
        Extract currency code from TED value field.
        
        Args:
            value_data: Value data (could be string, number, list, or dict)
        
        Returns:
            Currency code or None
        """
        if not value_data:
            return None
        
        try:
            # If it's a list, take first item
            if isinstance(value_data, list):
                if value_data:
                    return self._extract_currency(value_data[0])
                return None
            
            # If it's a dict, look for currency key
            if isinstance(value_data, dict):
                for key in ['currency', 'cur', 'curr']:
                    if key in value_data:
                        return str(value_data[key]).upper()
                return None
            
            # If it's a string, look for currency codes
            if isinstance(value_data, str):
                value_upper = value_data.upper()
                for currency in ['EUR', 'USD', 'GBP', 'PLN', 'CZK', 'HUF', 'RON', 'BGN', 'HRK', 'DKK', 'SEK']:
                    if currency in value_upper:
                        return currency
        except:
            pass
        
        return None
    
    def _map_category(self, nature_code: str) -> str:
        """
        Map TED nature of contract to procurement category.
        
        Args:
            nature_code: TED nature of contract code
        
        Returns:
            Procurement category
        """
        # TED nature of contract codes
        category_mapping = {
            '1': 'works',
            '2': 'supplies',
            '3': 'services',
            '4': 'services',  # Services category A
            '5': 'services',  # Services category B
            '6': 'works',     # Works concession
            '7': 'services',  # Services concession
            '8': 'supplies',  # Mixed
        }
        
        return category_mapping.get(nature_code, 'services')


def test_ted_api():
    """Test function to verify TED API connectivity."""
    scraper = TEDAPIScraper()
    
    print("Testing TED API connection...")
    try:
        # Fetch recent notices
        response = scraper.search_by_date_range(days_back=30)
        
        print(f"✓ API connection successful")
        print(f"  Total notices available: {response.get('total', 0)}")
        print(f"  Notices returned: {len(response.get('notices', []))}")
        
        # Parse first notice
        notices = response.get('notices', [])
        if notices:
            print("\nFirst notice (raw):")
            print(json.dumps(notices[0], indent=2))
            print("\nFirst notice (parsed):")
            parsed = scraper.parse_notice(notices[0])
            print(json.dumps(parsed, indent=2))
        
        return True
    except Exception as e:
        print(f"✗ API test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_ted_api()
