-- UK Tender Scraper - PostgreSQL Database Schema
-- Schema: tendly
-- All tables include country_code for multi-country support

-- Create tendly schema
CREATE SCHEMA IF NOT EXISTS tendly;

-- Set search path to tendly schema
SET search_path TO tendly;

-- Drop tables if they exist (for clean recreation)
DROP TABLE IF EXISTS tendly.documents CASCADE;
DROP TABLE IF EXISTS tendly.lots CASCADE;
DROP TABLE IF EXISTS tendly.scraping_log CASCADE;
DROP TABLE IF EXISTS tendly.tenders CASCADE;

-- Main tenders table
CREATE TABLE tendly.tenders (
    id SERIAL PRIMARY KEY,
    country_code VARCHAR(2) NOT NULL DEFAULT 'UK',
    notice_id VARCHAR(255) NOT NULL,
    ocid VARCHAR(255),
    title TEXT NOT NULL,
    description TEXT,
    status VARCHAR(50),
    publication_date TIMESTAMP,
    
    -- Buyer information
    buyer_name VARCHAR(500),
    buyer_id VARCHAR(255),
    buyer_address TEXT,
    buyer_contact_point TEXT,
    
    -- Tender details
    main_procurement_category VARCHAR(50),
    tender_status VARCHAR(50),
    procurement_method VARCHAR(100),
    procurement_method_details TEXT,
    
    -- Value information
    value_amount DECIMAL(15, 2),
    value_currency VARCHAR(3) DEFAULT 'GBP',
    
    -- Dates
    tender_period_start TIMESTAMP,
    tender_period_end TIMESTAMP,
    contract_period_start TIMESTAMP,
    contract_period_end TIMESTAMP,
    
    -- Additional fields
    cpv_codes TEXT,
    lots_info TEXT,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT unique_notice_country UNIQUE (notice_id, country_code)
);

-- Create indexes for tenders table
CREATE INDEX idx_tenders_country_code ON tendly.tenders(country_code);
CREATE INDEX idx_tenders_notice_id ON tendly.tenders(notice_id);
CREATE INDEX idx_tenders_ocid ON tendly.tenders(ocid);
CREATE INDEX idx_tenders_status ON tendly.tenders(status);
CREATE INDEX idx_tenders_buyer_name ON tendly.tenders(buyer_name);
CREATE INDEX idx_tenders_publication_date ON tendly.tenders(publication_date);
CREATE INDEX idx_tenders_created_at ON tendly.tenders(created_at);

-- Lots table (one-to-many with tenders)
CREATE TABLE tendly.lots (
    id SERIAL PRIMARY KEY,
    country_code VARCHAR(2) NOT NULL DEFAULT 'UK',
    tender_id INTEGER NOT NULL REFERENCES tendly.tenders(id) ON DELETE CASCADE,
    lot_id VARCHAR(255),
    title TEXT,
    description TEXT,
    status VARCHAR(50),
    value_amount DECIMAL(15, 2),
    value_currency VARCHAR(3) DEFAULT 'GBP',
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT unique_lot_tender UNIQUE (lot_id, tender_id, country_code)
);

-- Create indexes for lots table
CREATE INDEX idx_lots_country_code ON tendly.lots(country_code);
CREATE INDEX idx_lots_tender_id ON tendly.lots(tender_id);
CREATE INDEX idx_lots_lot_id ON tendly.lots(lot_id);

-- Documents table (one-to-many with tenders)
CREATE TABLE tendly.documents (
    id SERIAL PRIMARY KEY,
    country_code VARCHAR(2) NOT NULL DEFAULT 'UK',
    tender_id INTEGER NOT NULL REFERENCES tendly.tenders(id) ON DELETE CASCADE,
    document_id VARCHAR(255),
    title TEXT,
    description TEXT,
    document_type VARCHAR(100),
    url TEXT,
    format VARCHAR(50),
    language VARCHAR(10),
    date_published TIMESTAMP,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT unique_document_tender UNIQUE (document_id, tender_id, country_code)
);

-- Create indexes for documents table
CREATE INDEX idx_documents_country_code ON tendly.documents(country_code);
CREATE INDEX idx_documents_tender_id ON tendly.documents(tender_id);
CREATE INDEX idx_documents_document_id ON tendly.documents(document_id);

-- Scraping log table (audit trail)
CREATE TABLE tendly.scraping_log (
    id SERIAL PRIMARY KEY,
    country_code VARCHAR(2) NOT NULL DEFAULT 'UK',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR(100),
    records_fetched INTEGER DEFAULT 0,
    records_inserted INTEGER DEFAULT 0,
    records_duplicates INTEGER DEFAULT 0,
    records_errors INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'success',
    error_message TEXT,
    
    -- Additional metadata
    parameters JSONB,
    duration_seconds DECIMAL(10, 2)
);

-- Create indexes for scraping_log table
CREATE INDEX idx_scraping_log_country_code ON tendly.scraping_log(country_code);
CREATE INDEX idx_scraping_log_timestamp ON tendly.scraping_log(timestamp);
CREATE INDEX idx_scraping_log_source ON tendly.scraping_log(source);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION tendly.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for tenders table
CREATE TRIGGER update_tenders_updated_at
    BEFORE UPDATE ON tendly.tenders
    FOR EACH ROW
    EXECUTE FUNCTION tendly.update_updated_at_column();

-- Grant permissions (adjust as needed)
-- GRANT USAGE ON SCHEMA tendly TO indurent_db_user;
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA tendly TO indurent_db_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA tendly TO indurent_db_user;

-- Comments for documentation
COMMENT ON SCHEMA tendly IS 'Tender data schema for multi-country tender scraping';
COMMENT ON TABLE tendly.tenders IS 'Main table storing tender/contract opportunities';
COMMENT ON TABLE tendly.lots IS 'Individual lots associated with tenders';
COMMENT ON TABLE tendly.documents IS 'Documents and attachments related to tenders';
COMMENT ON TABLE tendly.scraping_log IS 'Audit log of scraping operations';

COMMENT ON COLUMN tendly.tenders.country_code IS 'ISO 3166-1 alpha-2 country code (e.g., UK, US, DE)';
COMMENT ON COLUMN tendly.lots.country_code IS 'ISO 3166-1 alpha-2 country code';
COMMENT ON COLUMN tendly.documents.country_code IS 'ISO 3166-1 alpha-2 country code';
COMMENT ON COLUMN tendly.scraping_log.country_code IS 'ISO 3166-1 alpha-2 country code';
