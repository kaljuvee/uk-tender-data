"""Database utilities for UK Tender Scraper."""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Any, Optional


class TenderDatabase:
    """SQLite database manager for tender data."""
    
    def __init__(self, db_path: str = "sql/tenders.db"):
        """Initialize database connection."""
        self.db_path = db_path
        self._ensure_db_directory()
        self._initialize_database()
    
    def _ensure_db_directory(self):
        """Ensure the database directory exists."""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
    
    def _initialize_database(self):
        """Create tables if they don't exist."""
        schema_path = "sql/create_tables.sql"
        if os.path.exists(schema_path):
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
            
            conn = self.get_connection()
            try:
                conn.executescript(schema_sql)
                conn.commit()
            finally:
                conn.close()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get a database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def insert_tender(self, tender_data: Dict[str, Any]) -> Optional[int]:
        """
        Insert a tender into the database.
        Returns the tender ID if successful, None if duplicate.
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Check for duplicate
            cursor.execute(
                "SELECT id FROM tenders WHERE notice_id = ?",
                (tender_data.get('notice_id'),)
            )
            if cursor.fetchone():
                return None  # Duplicate
            
            # Insert tender
            cursor.execute("""
                INSERT INTO tenders (
                    notice_id, ocid, title, description, status, stage,
                    publication_date, value_amount, value_currency,
                    buyer_name, buyer_id, buyer_email, buyer_address,
                    classification_id, classification_description,
                    main_procurement_category, legal_basis
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                tender_data.get('notice_id'),
                tender_data.get('ocid'),
                tender_data.get('title'),
                tender_data.get('description'),
                tender_data.get('status'),
                tender_data.get('stage'),
                tender_data.get('publication_date'),
                tender_data.get('value_amount'),
                tender_data.get('value_currency'),
                tender_data.get('buyer_name'),
                tender_data.get('buyer_id'),
                tender_data.get('buyer_email'),
                tender_data.get('buyer_address'),
                tender_data.get('classification_id'),
                tender_data.get('classification_description'),
                tender_data.get('main_procurement_category'),
                tender_data.get('legal_basis')
            ))
            
            tender_id = cursor.lastrowid
            
            # Insert lots if present
            if 'lots' in tender_data and tender_data['lots']:
                for lot in tender_data['lots']:
                    self._insert_lot(cursor, tender_id, lot)
            
            # Insert documents if present
            if 'documents' in tender_data and tender_data['documents']:
                for doc in tender_data['documents']:
                    self._insert_document(cursor, tender_id, doc)
            
            conn.commit()
            return tender_id
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _insert_lot(self, cursor, tender_id: int, lot_data: Dict[str, Any]):
        """Insert a lot associated with a tender."""
        cursor.execute("""
            INSERT INTO lots (
                tender_id, lot_id, description, value_amount, value_currency,
                status, duration_days, has_renewal, renewal_description,
                has_options, options_description
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            tender_id,
            lot_data.get('lot_id'),
            lot_data.get('description'),
            lot_data.get('value_amount'),
            lot_data.get('value_currency'),
            lot_data.get('status'),
            lot_data.get('duration_days'),
            lot_data.get('has_renewal'),
            lot_data.get('renewal_description'),
            lot_data.get('has_options'),
            lot_data.get('options_description')
        ))
    
    def _insert_document(self, cursor, tender_id: int, doc_data: Dict[str, Any]):
        """Insert a document associated with a tender."""
        cursor.execute("""
            INSERT INTO documents (
                tender_id, document_id, document_type, notice_type,
                description, url, date_published, format
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            tender_id,
            doc_data.get('document_id'),
            doc_data.get('document_type'),
            doc_data.get('notice_type'),
            doc_data.get('description'),
            doc_data.get('url'),
            doc_data.get('date_published'),
            doc_data.get('format')
        ))
    
    def log_scraping_run(self, records_fetched: int, records_inserted: int, 
                        records_duplicates: int, source: str, 
                        status: str = "success", error_message: str = None):
        """Log a scraping run."""
        conn = self.get_connection()
        try:
            conn.execute("""
                INSERT INTO scraping_log (
                    records_fetched, records_inserted, records_duplicates,
                    source, status, error_message
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (records_fetched, records_inserted, records_duplicates, 
                  source, status, error_message))
            conn.commit()
        finally:
            conn.close()
    
    def get_all_tenders(self, limit: int = None) -> List[Dict[str, Any]]:
        """Get all tenders from the database."""
        conn = self.get_connection()
        try:
            query = "SELECT * FROM tenders ORDER BY publication_date DESC"
            if limit:
                query += f" LIMIT {limit}"
            
            cursor = conn.execute(query)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()
    
    def search_tenders(self, keyword: str = None, buyer: str = None, 
                      status: str = None) -> List[Dict[str, Any]]:
        """Search tenders with filters."""
        conn = self.get_connection()
        try:
            query = "SELECT * FROM tenders WHERE 1=1"
            params = []
            
            if keyword:
                query += " AND (title LIKE ? OR description LIKE ?)"
                params.extend([f"%{keyword}%", f"%{keyword}%"])
            
            if buyer:
                query += " AND buyer_name LIKE ?"
                params.append(f"%{buyer}%")
            
            if status:
                query += " AND status = ?"
                params.append(status)
            
            query += " ORDER BY publication_date DESC"
            
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()
    
    def get_scraping_logs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent scraping logs."""
        conn = self.get_connection()
        try:
            cursor = conn.execute(
                "SELECT * FROM scraping_log ORDER BY scrape_date DESC LIMIT ?",
                (limit,)
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics."""
        conn = self.get_connection()
        try:
            stats = {}
            
            # Total tenders
            cursor = conn.execute("SELECT COUNT(*) as count FROM tenders")
            stats['total_tenders'] = cursor.fetchone()['count']
            
            # Tenders by status
            cursor = conn.execute("""
                SELECT status, COUNT(*) as count 
                FROM tenders 
                GROUP BY status
            """)
            stats['by_status'] = {row['status']: row['count'] for row in cursor.fetchall()}
            
            # Recent tenders (last 7 days)
            cursor = conn.execute("""
                SELECT COUNT(*) as count 
                FROM tenders 
                WHERE publication_date >= date('now', '-7 days')
            """)
            stats['recent_tenders'] = cursor.fetchone()['count']
            
            return stats
        finally:
            conn.close()
