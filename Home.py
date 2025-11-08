"""
UK Public Tender Data
Lohusalu Capital Management
"""

import streamlit as st
import pandas as pd
from utils.database import TenderDatabase
import os

# Page configuration
st.set_page_config(
    page_title="UK Public Tender Data",
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
st.sidebar.title("🇬🇧 UK Public Tender Data")
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
st.title("🇬🇧 UK Public Tender Data")
st.markdown("**Find and analyze UK government tender opportunities**")
st.markdown("---")

# Overview cards
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="📋 Total Tenders",
        value=stats.get('total_tenders', 0)
    )

with col2:
    st.metric(
        label="🆕 Recent Tenders",
        value=stats.get('recent_tenders', 0)
    )

with col3:
    active_count = stats.get('by_status', {}).get('active', 0)
    st.metric(
        label="✅ Active",
        value=active_count
    )

with col4:
    planned_count = stats.get('by_status', {}).get('planned', 0)
    st.metric(
        label="📅 Planned",
        value=planned_count
    )

st.markdown("---")

# Recent tenders table
st.subheader("📋 Recent Tenders")

tenders = db.get_all_tenders(limit=10)

if tenders:
    # Convert to DataFrame
    df = pd.DataFrame(tenders)
    
    # Select and rename columns for display
    display_columns = ['notice_id', 'title', 'buyer_name', 'status', 'value_amount', 'publication_date']
    available_columns = [col for col in display_columns if col in df.columns]
    
    if available_columns:
        df_display = df[available_columns].copy()
        
        # Rename columns
        column_names = {
            'notice_id': 'Notice ID',
            'title': 'Title',
            'buyer_name': 'Buyer',
            'status': 'Status',
            'value_amount': 'Value (£)',
            'publication_date': 'Published'
        }
        df_display.rename(columns=column_names, inplace=True)
        
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
            hide_index=True
        )
    else:
        st.info("No tender data available.")
else:
    st.info("No tenders found in database. Run the scraper task to fetch data.")

st.markdown("---")

# Tender details viewer
st.subheader("🔍 Tender Details")

if tenders:
    # Create selectbox with tender titles
    tender_options = [f"{t['notice_id']} - {t['title'][:50]}..." for t in tenders]
    selected_option = st.selectbox(
        "Select a tender to view details:",
        options=tender_options,
        key="tender_selector"
    )
    
    # Get selected tender index
    selected_index = tender_options.index(selected_option)
    selected_tender = tenders[selected_index]
    
    # Display tender details in columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Basic Information")
        st.text(f"Notice ID: {selected_tender.get('notice_id', 'N/A')}")
        st.text(f"OCID: {selected_tender.get('ocid', 'N/A')}")
        st.text(f"Status: {selected_tender.get('status', 'N/A')}")
        st.text(f"Stage: {selected_tender.get('stage', 'N/A')}")
        st.text(f"Category: {selected_tender.get('main_procurement_category', 'N/A')}")
    
    with col2:
        st.markdown("#### Buyer Information")
        st.text(f"Name: {selected_tender.get('buyer_name', 'N/A')}")
        st.text(f"ID: {selected_tender.get('buyer_id', 'N/A')}")
        st.text(f"Email: {selected_tender.get('buyer_email', 'N/A')}")
    
    st.markdown("#### Value")
    value = selected_tender.get('value_amount', 0)
    currency = selected_tender.get('value_currency', 'GBP')
    st.text(f"{currency} {value:,.2f}" if value else "N/A")
    
    st.markdown("#### Classification")
    st.text(f"CPV: {selected_tender.get('classification_id', 'N/A')}")
    
    st.markdown("#### Description")
    st.text_area(
        label="",
        value=selected_tender.get('description', 'No description available'),
        height=150,
        disabled=True,
        label_visibility="collapsed"
    )
else:
    st.info("No tenders available to display.")

# Footer
st.markdown("---")
st.caption("UK Public Tender Data | Lohusalu Capital Management | Data from Find a Tender Service")
