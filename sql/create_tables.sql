-- UK Tender Database Schema

-- Main tenders table
CREATE TABLE IF NOT EXISTS tenders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    notice_id TEXT UNIQUE NOT NULL,
    ocid TEXT,
    title TEXT,
    description TEXT,
    status TEXT,
    stage TEXT,
    publication_date TEXT,
    value_amount REAL,
    value_currency TEXT,
    buyer_name TEXT,
    buyer_id TEXT,
    buyer_email TEXT,
    buyer_address TEXT,
    classification_id TEXT,
    classification_description TEXT,
    main_procurement_category TEXT,
    legal_basis TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for faster lookups
CREATE INDEX IF NOT EXISTS idx_notice_id ON tenders(notice_id);
CREATE INDEX IF NOT EXISTS idx_ocid ON tenders(ocid);
CREATE INDEX IF NOT EXISTS idx_publication_date ON tenders(publication_date);
CREATE INDEX IF NOT EXISTS idx_buyer_name ON tenders(buyer_name);
CREATE INDEX IF NOT EXISTS idx_status ON tenders(status);

-- Lots table (one-to-many with tenders)
CREATE TABLE IF NOT EXISTS lots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tender_id INTEGER NOT NULL,
    lot_id TEXT,
    description TEXT,
    value_amount REAL,
    value_currency TEXT,
    status TEXT,
    duration_days INTEGER,
    has_renewal BOOLEAN,
    renewal_description TEXT,
    has_options BOOLEAN,
    options_description TEXT,
    FOREIGN KEY (tender_id) REFERENCES tenders(id) ON DELETE CASCADE
);

-- Documents table (one-to-many with tenders)
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tender_id INTEGER NOT NULL,
    document_id TEXT,
    document_type TEXT,
    notice_type TEXT,
    description TEXT,
    url TEXT,
    date_published TEXT,
    format TEXT,
    FOREIGN KEY (tender_id) REFERENCES tenders(id) ON DELETE CASCADE
);

-- Scraping log table
CREATE TABLE IF NOT EXISTS scraping_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scrape_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    records_fetched INTEGER,
    records_inserted INTEGER,
    records_duplicates INTEGER,
    source TEXT,
    status TEXT,
    error_message TEXT
);
