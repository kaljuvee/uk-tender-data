"""
UK Tender Scraper - Main Application
Lohusalu Capital Management
"""

import streamlit as st
import pandas as pd
from utils.database import TenderDatabase
from utils.data_generator import TenderDataGenerator
import os

# Page configuration
st.set_page_config(
    page_title="UK Tender Scraper",
    page_icon="🇬🇧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
@st.cache_resource
def get_database():
    """Get database instance."""
    return TenderDatabase()

db = get_database()

# Sidebar
st.sidebar.title("🇬🇧 UK Tender Scraper")
st.sidebar.markdown("---")

# Generate synthetic data button
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
        
        st.sidebar.success(f"✅ Generated {inserted} tenders ({duplicates} duplicates skipped)")
        st.rerun()

st.sidebar.markdown("---")

# Statistics
st.sidebar.subheader("📊 Database Statistics")
stats = db.get_statistics()

col1, col2 = st.sidebar.columns(2)
with col1:
    st.metric("Total Tenders", stats.get('total_tenders', 0))
with col2:
    st.metric("Recent (7d)", stats.get('recent_tenders', 0))

if stats.get('by_status'):
    st.sidebar.markdown("**By Status:**")
    for status, count in stats['by_status'].items():
        st.sidebar.text(f"• {status}: {count}")

# Main content
st.title("🇬🇧 UK Tender Scraper")
st.markdown("**Find and analyze UK government tender opportunities**")
st.markdown("---")

# Overview cards
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="📋 Total Tenders",
        value=stats.get('total_tenders', 0),
        delta=None
    )

with col2:
    st.metric(
        label="🆕 Recent Tenders",
        value=stats.get('recent_tenders', 0),
        delta=None
    )

with col3:
    active_count = stats.get('by_status', {}).get('active', 0)
    st.metric(
        label="✅ Active",
        value=active_count,
        delta=None
    )

with col4:
    planned_count = stats.get('by_status', {}).get('planned', 0)
    st.metric(
        label="📅 Planned",
        value=planned_count,
        delta=None
    )

st.markdown("---")

# Recent tenders
st.subheader("📋 Recent Tenders")

# Fetch recent tenders
tenders = db.get_all_tenders(limit=20)

if tenders:
    # Convert to DataFrame
    df = pd.DataFrame(tenders)
    
    # Select and rename columns for display
    display_columns = {
        'notice_id': 'Notice ID',
        'title': 'Title',
        'buyer_name': 'Buyer',
        'status': 'Status',
        'value_amount': 'Value (£)',
        'publication_date': 'Published',
    }
    
    df_display = df[list(display_columns.keys())].copy()
    df_display.columns = list(display_columns.values())
    
    # Format value column
    if 'Value (£)' in df_display.columns:
        df_display['Value (£)'] = df_display['Value (£)'].apply(
            lambda x: f"£{x:,.2f}" if pd.notna(x) else "N/A"
        )
    
    # Format date column
    if 'Published' in df_display.columns:
        df_display['Published'] = pd.to_datetime(df_display['Published']).dt.strftime('%Y-%m-%d')
    
    # Display table
    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Notice ID": st.column_config.TextColumn(width="small"),
            "Title": st.column_config.TextColumn(width="large"),
            "Buyer": st.column_config.TextColumn(width="medium"),
            "Status": st.column_config.TextColumn(width="small"),
            "Value (£)": st.column_config.TextColumn(width="small"),
            "Published": st.column_config.TextColumn(width="small"),
        }
    )
    
    # Tender details expander
    st.markdown("---")
    st.subheader("🔍 Tender Details")
    
    selected_notice = st.selectbox(
        "Select a tender to view details:",
        options=df['notice_id'].tolist(),
        format_func=lambda x: f"{x} - {df[df['notice_id']==x]['title'].values[0][:60]}..."
    )
    
    if selected_notice:
        tender_detail = df[df['notice_id'] == selected_notice].iloc[0]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Basic Information**")
            st.text(f"Notice ID: {tender_detail['notice_id']}")
            st.text(f"OCID: {tender_detail.get('ocid', 'N/A')}")
            st.text(f"Status: {tender_detail.get('status', 'N/A')}")
            st.text(f"Stage: {tender_detail.get('stage', 'N/A')}")
            st.text(f"Category: {tender_detail.get('main_procurement_category', 'N/A')}")
            
            st.markdown("**Value**")
            value = tender_detail.get('value_amount')
            currency = tender_detail.get('value_currency', 'GBP')
            if pd.notna(value):
                st.text(f"{currency} {value:,.2f}")
            else:
                st.text("N/A")
        
        with col2:
            st.markdown("**Buyer Information**")
            st.text(f"Name: {tender_detail.get('buyer_name', 'N/A')}")
            st.text(f"ID: {tender_detail.get('buyer_id', 'N/A')}")
            st.text(f"Email: {tender_detail.get('buyer_email', 'N/A')}")
            
            st.markdown("**Classification**")
            st.text(f"CPV: {tender_detail.get('classification_id', 'N/A')}")
            if pd.notna(tender_detail.get('classification_description')):
                st.text(f"{tender_detail['classification_description'][:60]}...")
        
        st.markdown("**Description**")
        st.text_area(
            "Tender Description",
            value=tender_detail.get('description', 'N/A'),
            height=150,
            disabled=True,
            label_visibility="collapsed"
        )

else:
    st.info("📭 No tenders in database. Use the sidebar to generate synthetic data or scrape from the API.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>UK Tender Scraper | Lohusalu Capital Management | Data from Find a Tender Service</p>
    </div>
    """,
    unsafe_allow_html=True
)
