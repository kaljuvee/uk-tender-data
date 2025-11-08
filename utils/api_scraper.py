"""API scraper for UK Find a Tender service."""

import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta


class TenderAPIScraper:
    """Scraper for UK Find a Tender OCDS API."""
    
    BASE_URL = "https://www.find-tender.service.gov.uk/api/1.0/ocdsReleasePackages"
    
    def __init__(self):
        """Initialize the API scraper."""
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'User-Agent': 'UK-Tender-Scraper/1.0'
        })
    
    def fetch_tenders(self, limit: int = 100, stages: str = None, 
                     updated_from: str = None, updated_to: str = None,
                     cursor: str = None) -> Dict[str, Any]:
        """
        Fetch tenders from the OCDS API.
        
        Args:
            limit: Number of records to fetch (max 100)
            stages: Filter by stage (planning, tender, award)
            updated_from: Earliest update date (YYYY-MM-DDTHH:MM:SS)
            updated_to: Latest update date (YYYY-MM-DDTHH:MM:SS)
            cursor: Pagination cursor
        
        Returns:
            API response as dictionary
        """
        params = {'limit': min(limit, 100)}
        
        if stages:
            params['stages'] = stages
        if updated_from:
            params['updatedFrom'] = updated_from
        if updated_to:
            params['updatedTo'] = updated_to
        if cursor:
            params['cursor'] = cursor
        
        try:
            response = self.session.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
    
    def fetch_multiple_pages(self, total_records: int = 100, 
                            stages: str = None,
                            days_back: int = 30) -> List[Dict[str, Any]]:
        """
        Fetch multiple pages of tender data.
        
        Args:
            total_records: Total number of records to fetch
            stages: Filter by stage
            days_back: Number of days to look back
        
        Returns:
            List of all releases
        """
        all_releases = []
        cursor = None
        
        # Calculate date range
        updated_to = datetime.now().isoformat(timespec='seconds')
        updated_from = (datetime.now() - timedelta(days=days_back)).isoformat(timespec='seconds')
        
        while len(all_releases) < total_records:
            remaining = total_records - len(all_releases)
            limit = min(remaining, 100)
            
            response = self.fetch_tenders(
                limit=limit,
                stages=stages,
                updated_from=updated_from,
                updated_to=updated_to,
                cursor=cursor
            )
            
            # Extract releases
            releases = response.get('releases', [])
            if not releases:
                break
            
            all_releases.extend(releases)
            
            # Check for next page cursor
            # Note: The API might include a cursor in the response
            # This is a placeholder - adjust based on actual API response
            cursor = response.get('cursor')
            if not cursor:
                break
        
        return all_releases[:total_records]
    
    def parse_release(self, release: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse an OCDS release into our database format.
        
        Args:
            release: OCDS release object
        
        Returns:
            Parsed tender data
        """
        tender_data = {
            'notice_id': release.get('id'),
            'ocid': release.get('ocid'),
            'stage': ','.join(release.get('tag', [])),
            'publication_date': release.get('date'),
        }
        
        # Extract tender information
        tender = release.get('tender', {})
        if tender:
            tender_data.update({
                'title': tender.get('title'),
                'description': tender.get('description'),
                'status': tender.get('status'),
                'main_procurement_category': tender.get('mainProcurementCategory'),
            })
            
            # Extract value
            value = tender.get('value', {})
            if value:
                tender_data['value_amount'] = value.get('amount')
                tender_data['value_currency'] = value.get('currency')
            
            # Extract classification
            classification = tender.get('classification', {})
            if classification:
                tender_data['classification_id'] = classification.get('id')
                tender_data['classification_description'] = classification.get('description')
            
            # Extract legal basis
            legal_basis = tender.get('legalBasis', {})
            if legal_basis:
                tender_data['legal_basis'] = legal_basis.get('id')
            
            # Extract lots
            lots = tender.get('lots', [])
            if lots:
                tender_data['lots'] = []
                for lot in lots:
                    lot_data = {
                        'lot_id': lot.get('id'),
                        'description': lot.get('description'),
                        'status': lot.get('status'),
                        'has_renewal': lot.get('hasRenewal'),
                        'has_options': lot.get('hasOptions'),
                    }
                    
                    # Lot value
                    lot_value = lot.get('value', {})
                    if lot_value:
                        lot_data['value_amount'] = lot_value.get('amount')
                        lot_data['value_currency'] = lot_value.get('currency')
                    
                    # Contract period
                    contract_period = lot.get('contractPeriod', {})
                    if contract_period:
                        lot_data['duration_days'] = contract_period.get('durationInDays')
                    
                    # Renewal
                    renewal = lot.get('renewal', {})
                    if renewal:
                        lot_data['renewal_description'] = renewal.get('description')
                    
                    # Options
                    options = lot.get('options', {})
                    if options:
                        lot_data['options_description'] = options.get('description')
                    
                    tender_data['lots'].append(lot_data)
        
        # Extract buyer information
        buyer = release.get('buyer', {})
        if buyer:
            tender_data['buyer_name'] = buyer.get('name')
            tender_data['buyer_id'] = buyer.get('id')
        
        # Extract party details (for more buyer info)
        parties = release.get('parties', [])
        for party in parties:
            if 'buyer' in party.get('roles', []):
                contact = party.get('contactPoint', {})
                if contact:
                    tender_data['buyer_email'] = contact.get('email')
                
                address = party.get('address', {})
                if address:
                    address_parts = [
                        address.get('streetAddress'),
                        address.get('locality'),
                        address.get('postalCode'),
                        address.get('countryName')
                    ]
                    tender_data['buyer_address'] = ', '.join(
                        filter(None, address_parts)
                    )
                break
        
        # Extract planning documents
        planning = release.get('planning', {})
        if planning:
            documents = planning.get('documents', [])
            if documents:
                tender_data['documents'] = []
                for doc in documents:
                    doc_data = {
                        'document_id': doc.get('id'),
                        'document_type': doc.get('documentType'),
                        'notice_type': doc.get('noticeType'),
                        'description': doc.get('description'),
                        'url': doc.get('url'),
                        'date_published': doc.get('datePublished'),
                        'format': doc.get('format'),
                    }
                    tender_data['documents'].append(doc_data)
        
        # Also check tender documents
        if tender:
            tender_docs = tender.get('documents', [])
            if tender_docs:
                if 'documents' not in tender_data:
                    tender_data['documents'] = []
                for doc in tender_docs:
                    doc_data = {
                        'document_id': doc.get('id'),
                        'document_type': doc.get('documentType'),
                        'description': doc.get('description'),
                        'url': doc.get('url'),
                        'date_published': doc.get('datePublished'),
                        'format': doc.get('format'),
                    }
                    tender_data['documents'].append(doc_data)
        
        return tender_data
    
    def scrape_and_parse(self, total_records: int = 100, 
                        stages: str = None,
                        days_back: int = 30) -> List[Dict[str, Any]]:
        """
        Scrape and parse tender data.
        
        Args:
            total_records: Total number of records to fetch
            stages: Filter by stage
            days_back: Number of days to look back
        
        Returns:
            List of parsed tender data
        """
        releases = self.fetch_multiple_pages(
            total_records=total_records,
            stages=stages,
            days_back=days_back
        )
        
        parsed_tenders = []
        for release in releases:
            try:
                parsed = self.parse_release(release)
                parsed_tenders.append(parsed)
            except Exception as e:
                print(f"Error parsing release {release.get('id')}: {str(e)}")
                continue
        
        return parsed_tenders
