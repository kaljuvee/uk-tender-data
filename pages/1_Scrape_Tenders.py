"""
Scrape Tenders Page - Fetch data from Find a Tender API
"""

import streamlit as st
from utils.database import TenderDatabase
from utils.api_scraper import TenderAPIScraper
from utils.data_generator import TenderDataGenerator
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="Scrape Tenders",
    page_icon="🔍",
    layout="wide"
)

# Initialize
@st.cache_resource
def get_database():
    return TenderDatabase()

db = get_database()

# Header
st.title("🔍 Scrape UK Tenders")
st.markdown("Fetch tender data from the Find a Tender API or generate synthetic data")
st.markdown("---")

# Sidebar controls
st.sidebar.header("⚙️ Scraping Parameters")

# Data source selection
data_source = st.sidebar.radio(
    "Data Source",
    options=["API (Real Data)", "Synthetic (Test Data)"],
    help="Choose between real API data or synthetic test data"
)

# Number of records
num_records = st.sidebar.slider(
    "Number of Records",
    min_value=10,
    max_value=500,
    value=100,
    step=10,
    help="Number of tender records to fetch (max 500)"
)

if data_source == "API (Real Data)":
    # API-specific parameters
    st.sidebar.markdown("### API Filters")
    
    stage_filter = st.sidebar.multiselect(
        "Procurement Stage",
        options=["planning", "tender", "award"],
        default=None,
        help="Filter by procurement stage"
    )
    
    days_back = st.sidebar.slider(
        "Days to Look Back",
        min_value=7,
        max_value=365,
        value=30,
        step=7,
        help="How many days back to search for tenders"
    )

st.sidebar.markdown("---")

# Generate synthetic data button (always available)
if st.sidebar.button("🎲 Generate Synthetic Data", use_container_width=True):
    with st.spinner("Generating synthetic tender data..."):
        generator = TenderDataGenerator()
        synthetic_tenders = generator.generate_tenders(count=50)
        
        inserted = 0
        duplicates = 0
        
        for tender in synthetic_tenders:
            result = db.insert_tender(tender)
            if result:
                inserted += 1
            else:
                duplicates += 1
        
        db.log_scraping_run(
            records_fetched=len(synthetic_tenders),
            records_inserted=inserted,
            records_duplicates=duplicates,
            source="synthetic_generator"
        )
        
        st.sidebar.success(f"✅ Generated {inserted} tenders")
        st.rerun()

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📊 Scraping Configuration")
    
    if data_source == "API (Real Data)":
        st.info("""
        **API Data Source**: Find a Tender OCDS API
        
        This will fetch real tender data from the UK government's Find a Tender service.
        The API provides data in Open Contracting Data Standard (OCDS) format.
        """)
        
        st.markdown("**Current Settings:**")
        st.write(f"- Records to fetch: **{num_records}**")
        st.write(f"- Stage filter: **{', '.join(stage_filter) if stage_filter else 'All stages'}**")
        st.write(f"- Date range: **Last {days_back} days**")
        
    else:
        st.info("""
        **Synthetic Data Source**: Faker-based Generator
        
        This will generate realistic but fake tender data for testing purposes.
        Useful for development and demonstration without hitting the API.
        """)
        
        st.markdown("**Current Settings:**")
        st.write(f"- Records to generate: **{num_records}**")

with col2:
    st.subheader("📈 Quick Stats")
    stats = db.get_statistics()
    st.metric("Current Total", stats.get('total_tenders', 0))
    st.metric("Recent (7d)", stats.get('recent_tenders', 0))

st.markdown("---")

# Scrape button
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    if st.button("🚀 Start Scraping", type="primary", use_container_width=True):
        
        if data_source == "API (Real Data)":
            # API scraping
            with st.spinner("🔄 Fetching data from Find a Tender API..."):
                try:
                    scraper = TenderAPIScraper()
                    
                    # Prepare stage filter
                    stages_param = ','.join(stage_filter) if stage_filter else None
                    
                    # Fetch and parse
                    parsed_tenders = scraper.scrape_and_parse(
                        total_records=num_records,
                        stages=stages_param,
                        days_back=days_back
                    )
                    
                    # Insert into database
                    inserted = 0
                    duplicates = 0
                    errors = 0
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    for idx, tender in enumerate(parsed_tenders):
                        try:
                            result = db.insert_tender(tender)
                            if result:
                                inserted += 1
                            else:
                                duplicates += 1
                        except Exception as e:
                            errors += 1
                            st.warning(f"Error inserting tender {tender.get('notice_id')}: {str(e)}")
                        
                        # Update progress
                        progress = (idx + 1) / len(parsed_tenders)
                        progress_bar.progress(progress)
                        status_text.text(f"Processing: {idx + 1}/{len(parsed_tenders)}")
                    
                    # Log the scraping run
                    db.log_scraping_run(
                        records_fetched=len(parsed_tenders),
                        records_inserted=inserted,
                        records_duplicates=duplicates,
                        source="api_scraper"
                    )
                    
                    progress_bar.empty()
                    status_text.empty()
                    
                    # Show results
                    st.success("✅ Scraping completed!")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Fetched", len(parsed_tenders))
                    with col2:
                        st.metric("Inserted", inserted)
                    with col3:
                        st.metric("Duplicates", duplicates)
                    with col4:
                        st.metric("Errors", errors)
                    
                except Exception as e:
                    st.error(f"❌ Scraping failed: {str(e)}")
                    db.log_scraping_run(
                        records_fetched=0,
                        records_inserted=0,
                        records_duplicates=0,
                        source="api_scraper",
                        status="error",
                        error_message=str(e)
                    )
        
        else:
            # Synthetic data generation
            with st.spinner("🎲 Generating synthetic tender data..."):
                try:
                    generator = TenderDataGenerator()
                    synthetic_tenders = generator.generate_tenders(count=num_records)
                    
                    inserted = 0
                    duplicates = 0
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    for idx, tender in enumerate(synthetic_tenders):
                        result = db.insert_tender(tender)
                        if result:
                            inserted += 1
                        else:
                            duplicates += 1
                        
                        # Update progress
                        progress = (idx + 1) / len(synthetic_tenders)
                        progress_bar.progress(progress)
                        status_text.text(f"Processing: {idx + 1}/{len(synthetic_tenders)}")
                    
                    db.log_scraping_run(
                        records_fetched=len(synthetic_tenders),
                        records_inserted=inserted,
                        records_duplicates=duplicates,
                        source="synthetic_generator"
                    )
                    
                    progress_bar.empty()
                    status_text.empty()
                    
                    st.success("✅ Data generation completed!")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Generated", len(synthetic_tenders))
                    with col2:
                        st.metric("Inserted", inserted)
                    with col3:
                        st.metric("Duplicates", duplicates)
                    
                except Exception as e:
                    st.error(f"❌ Generation failed: {str(e)}")

st.markdown("---")

# Scraping history
st.subheader("📜 Scraping History")

logs = db.get_scraping_logs(limit=10)

if logs:
    df_logs = pd.DataFrame(logs)
    
    # Format the dataframe
    display_columns = {
        'scrape_date': 'Date/Time',
        'source': 'Source',
        'records_fetched': 'Fetched',
        'records_inserted': 'Inserted',
        'records_duplicates': 'Duplicates',
        'status': 'Status',
    }
    
    df_display = df_logs[list(display_columns.keys())].copy()
    df_display.columns = list(display_columns.values())
    
    # Format date
    df_display['Date/Time'] = pd.to_datetime(df_display['Date/Time']).dt.strftime('%Y-%m-%d %H:%M:%S')
    
    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("No scraping history yet. Start scraping to see logs here.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>Data Source: Find a Tender Service (https://www.find-tender.service.gov.uk/)</p>
    </div>
    """,
    unsafe_allow_html=True
)
