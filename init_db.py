"""Initialize PostgreSQL database with tendly schema."""

import psycopg2
import os
from dotenv import load_dotenv
from urllib.parse import urlparse

# Load environment variables
load_dotenv()

db_url = os.getenv('MAIN_DB_URL')
print(f'Connecting to database...')

# Parse URL
parsed = urlparse(db_url)

conn = psycopg2.connect(
    host=parsed.hostname,
    port=parsed.port or 5432,
    database=parsed.path[1:],
    user=parsed.username,
    password=parsed.password
)

print('Connected successfully!')

# Read and execute schema
with open('sql/create_tables.sql', 'r') as f:
    schema_sql = f.read()

cursor = conn.cursor()
cursor.execute(schema_sql)
conn.commit()

print('Schema created successfully in tendly namespace!')

# Verify tables
cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'tendly'
    ORDER BY table_name
""")

tables = cursor.fetchall()
print(f'\nTables created in tendly schema:')
for table in tables:
    print(f'  - {table[0]}')

cursor.close()
conn.close()

print('\nDatabase initialization complete!')
