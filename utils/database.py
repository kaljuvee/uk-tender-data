"""PostgreSQL database manager for tender data using psycopg2."""

import psycopg2
import psycopg2.extras
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse


class TenderDatabase:
    """PostgreSQL database manager for tender data."""
    
    def __init__(self, db_url: str = None, country_code: str = 'UK'):
        """
        Initialize database connection.
        
        Args:
            db_url: PostgreSQL connection URL (defaults to MAIN_DB_URL env var)
            country_code: Country code for this instance (default: 'UK')
        """
        self.db_url = db_url or os.getenv('MAIN_DB_URL')
        self.country_code = country_code
        
        if not self.db_url:
            raise ValueError("Database URL not provided. Set MAIN_DB_URL environment variable.")
        
        # Parse connection URL
        self.conn_params = self._parse_db_url(self.db_url)
        
        # Test connection
        self._test_connection()
    
    def _parse_db_url(self, url: str) -> Dict[str, str]:
        """Parse PostgreSQL URL into connection parameters."""
        parsed = urlparse(url)
        
        return {
            'host': parsed.hostname,
            'port': parsed.port or 5432,
            'database': parsed.path[1:],  # Remove leading slash
            'user': parsed.username,
            'password': parsed.password
        }
    
    def _test_connection(self):
        """Test database connection."""
        try:
            conn = self.get_connection()
            conn.close()
        except Exception as e:
            raise ConnectionError(f"Failed to connect to database: {e}")
    
    def get_connection(self):
        """Get a database connection with RealDictCursor."""
        conn = psycopg2.connect(**self.conn_params)
        return conn
    
    def insert_tender(self, tender_data: Dict[str, Any]) -> Optional[int]:
        """
        Insert a tender into the database.
        Returns the tender ID if successful, None if duplicate.
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            # Check for duplicate
            cursor.execute(
                "SELECT id FROM tendly.tenders WHERE notice_id = %s AND country_code = %s",
                (tender_data.get('notice_id'), self.country_code)
            )
            if cursor.fetchone():
                return None  # Duplicate
            
            # Insert tender
            cursor.execute("""
                INSERT INTO tendly.tenders (
                    country_code, notice_id, ocid, title, description, status,
                    publication_date, value_amount, value_currency,
                    buyer_name, buyer_id, buyer_address,
                    main_procurement_category, cpv_codes, lots_info
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                self.country_code,
                tender_data.get('notice_id'),
                tender_data.get('ocid'),
                tender_data.get('title'),
                tender_data.get('description'),
                tender_data.get('status'),
                tender_data.get('publication_date'),
                tender_data.get('value_amount'),
                tender_data.get('value_currency', 'GBP'),
                tender_data.get('buyer_name'),
                tender_data.get('buyer_id'),
                tender_data.get('buyer_address'),
                tender_data.get('main_procurement_category'),
                tender_data.get('cpv_codes'),
                tender_data.get('lots_info')
            ))
            
            result = cursor.fetchone()
            tender_id = result['id'] if result else None
            
            # Insert lots if present
            if tender_id and 'lots' in tender_data and tender_data['lots']:
                for lot in tender_data['lots']:
                    self._insert_lot(cursor, tender_id, lot)
            
            # Insert documents if present
            if tender_id and 'documents' in tender_data and tender_data['documents']:
                for doc in tender_data['documents']:
                    self._insert_document(cursor, tender_id, doc)
            
            conn.commit()
            return tender_id
            
        except Exception as e:
            conn.rollback()
            print(f"Error inserting tender: {e}")
            return None
        finally:
            cursor.close()
            conn.close()
    
    def _insert_lot(self, cursor, tender_id: int, lot_data: Dict[str, Any]):
        """Insert a lot associated with a tender."""
        cursor.execute("""
            INSERT INTO tendly.lots (
                country_code, tender_id, lot_id, title, description,
                status, value_amount, value_currency
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (lot_id, tender_id, country_code) DO NOTHING
        """, (
            self.country_code,
            tender_id,
            lot_data.get('id'),
            lot_data.get('title'),
            lot_data.get('description'),
            lot_data.get('status'),
            lot_data.get('value', {}).get('amount'),
            lot_data.get('value', {}).get('currency', 'GBP')
        ))
    
    def _insert_document(self, cursor, tender_id: int, doc_data: Dict[str, Any]):
        """Insert a document associated with a tender."""
        cursor.execute("""
            INSERT INTO tendly.documents (
                country_code, tender_id, document_id, title, description,
                document_type, url, format, language, date_published
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (document_id, tender_id, country_code) DO NOTHING
        """, (
            self.country_code,
            tender_id,
            doc_data.get('id'),
            doc_data.get('title'),
            doc_data.get('description'),
            doc_data.get('documentType'),
            doc_data.get('url'),
            doc_data.get('format'),
            doc_data.get('language'),
            doc_data.get('datePublished')
        ))
    
    def get_all_tenders(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all tenders for the current country."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            cursor.execute("""
                SELECT * FROM tendly.tenders
                WHERE country_code = %s
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """, (self.country_code, limit, offset))
            
            tenders = cursor.fetchall()
            return [dict(row) for row in tenders]
            
        finally:
            cursor.close()
            conn.close()
    
    def search_tenders(
        self,
        keyword: str = None,
        buyer: str = None,
        status: str = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Search tenders with filters."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            query = "SELECT * FROM tendly.tenders WHERE country_code = %s"
            params = [self.country_code]
            
            if keyword:
                query += " AND (title ILIKE %s OR description ILIKE %s)"
                params.extend([f"%{keyword}%", f"%{keyword}%"])
            
            if buyer:
                query += " AND buyer_name ILIKE %s"
                params.append(f"%{buyer}%")
            
            if status:
                query += " AND status = %s"
                params.append(status)
            
            query += " ORDER BY created_at DESC LIMIT %s"
            params.append(limit)
            
            cursor.execute(query, params)
            tenders = cursor.fetchall()
            return [dict(row) for row in tenders]
            
        finally:
            cursor.close()
            conn.close()
    
    def get_tender_by_id(self, tender_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific tender by ID."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            cursor.execute(
                "SELECT * FROM tendly.tenders WHERE id = %s AND country_code = %s",
                (tender_id, self.country_code)
            )
            
            tender = cursor.fetchone()
            return dict(tender) if tender else None
            
        finally:
            cursor.close()
            conn.close()
    
    def log_scraping_run(
        self,
        records_fetched: int,
        records_inserted: int,
        records_duplicates: int,
        source: str,
        records_errors: int = 0,
        error_message: str = None,
        parameters: Dict[str, Any] = None,
        duration_seconds: float = None
    ):
        """Log a scraping run."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            import json
            
            cursor.execute("""
                INSERT INTO tendly.scraping_log (
                    country_code, source, records_fetched, records_inserted,
                    records_duplicates, records_errors, status, error_message,
                    parameters, duration_seconds
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                self.country_code,
                source,
                records_fetched,
                records_inserted,
                records_duplicates,
                records_errors,
                'error' if error_message else 'success',
                error_message,
                json.dumps(parameters) if parameters else None,
                duration_seconds
            ))
            
            conn.commit()
            
        finally:
            cursor.close()
            conn.close()
    
    def get_scraping_logs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent scraping logs."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            cursor.execute("""
                SELECT * FROM tendly.scraping_log
                WHERE country_code = %s
                ORDER BY timestamp DESC
                LIMIT %s
            """, (self.country_code, limit))
            
            logs = cursor.fetchall()
            return [dict(row) for row in logs]
            
        finally:
            cursor.close()
            conn.close()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            # Total tenders
            cursor.execute(
                "SELECT COUNT(*) as count FROM tendly.tenders WHERE country_code = %s",
                (self.country_code,)
            )
            total_tenders = cursor.fetchone()['count']
            
            # By status
            cursor.execute("""
                SELECT status, COUNT(*) as count
                FROM tendly.tenders
                WHERE country_code = %s
                GROUP BY status
            """, (self.country_code,))
            
            by_status = {row['status']: row['count'] for row in cursor.fetchall()}
            
            # Recent tenders (last 7 days)
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM tendly.tenders
                WHERE country_code = %s
                AND created_at >= NOW() - INTERVAL '7 days'
            """, (self.country_code,))
            
            recent_tenders = cursor.fetchone()['count']
            
            return {
                'total_tenders': total_tenders,
                'by_status': by_status,
                'recent_tenders': recent_tenders
            }
            
        finally:
            cursor.close()
            conn.close()
