"""
Search Tenders Page - Search and filter tender data
"""

import streamlit as st
from utils.database import TenderDatabase
import pandas as pd

st.set_page_config(
    page_title="Search Tenders - UK + EU Tender Data",
    page_icon="🔎",
    layout="wide"
)

# Initialize
@st.cache_resource
def get_database():
    return TenderDatabase()

db = get_database()

# Header
st.title("🔎 Search & Filter Tenders")
st.markdown("Search through UK public tender database with advanced filters")
st.markdown("---")

# Search filters on main page
st.subheader("🎯 Search Filters")

col1, col2, col3, col4 = st.columns([3, 2, 2, 1])

with col1:
    keyword = st.text_input(
        "Keyword Search",
        placeholder="Search in title or description...",
        help="Search for keywords in tender title or description",
        label_visibility="collapsed",
        key="keyword_search"
    )
    st.caption("🔍 Keyword Search")

with col2:
    buyer_filter = st.text_input(
        "Buyer Name",
        placeholder="Filter by buyer organization...",
        help="Filter tenders by buyer organization name",
        label_visibility="collapsed",
        key="buyer_filter"
    )
    st.caption("🏢 Buyer Name")

with col3:
    status_options = ["All", "planned", "active", "complete", "cancelled", "unsuccessful"]
    status_filter = st.selectbox(
        "Status",
        options=status_options,
        help="Filter by tender status",
        label_visibility="collapsed",
        key="status_filter"
    )
    st.caption("📊 Status")

with col4:
    st.write("")
    search_clicked = st.button("🔎 Search", type="primary", use_container_width=True)

st.markdown("---")

# Main content
st.subheader("🔍 Search Results")

# Perform search
if search_clicked or keyword or buyer_filter or status_filter != "All":
    with st.spinner("Searching..."):
        # Prepare filters
        status_param = None if status_filter == "All" else status_filter
        keyword_param = keyword if keyword else None
        buyer_param = buyer_filter if buyer_filter else None
        
        # Search database
        results = db.search_tenders(
            keyword=keyword_param,
            buyer=buyer_param,
            status=status_param
        )
        
        if results:
            st.success(f"Found {len(results)} tender(s)")
            
            # Convert to DataFrame
            df = pd.DataFrame(results)
            
            # Display summary table
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
            
            # Format value
            if 'Value (£)' in df_display.columns:
                df_display['Value (£)'] = df_display['Value (£)'].apply(
                    lambda x: f"£{x:,.2f}" if pd.notna(x) else "N/A"
                )
            
            # Format date
            if 'Published' in df_display.columns:
                df_display['Published'] = pd.to_datetime(df_display['Published']).dt.strftime('%Y-%m-%d')
            
            # Display table with selection
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
            
            st.markdown("---")
            
            # Detailed view
            st.subheader("📄 Tender Details")
            
            selected_notice = st.selectbox(
                "Select a tender to view full details:",
                options=df['notice_id'].tolist(),
                format_func=lambda x: f"{x} - {df[df['notice_id']==x]['title'].values[0][:60]}..."
            )
            
            if selected_notice:
                tender = df[df['notice_id'] == selected_notice].iloc[0]
                
                # Create tabs for different sections
                tab1, tab2, tab3 = st.tabs(["📋 Overview", "💰 Financial", "📞 Buyer Info"])
                
                with tab1:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Identification**")
                        st.text(f"Notice ID: {tender['notice_id']}")
                        st.text(f"OCID: {tender.get('ocid', 'N/A')}")
                        st.text(f"Publication Date: {tender.get('publication_date', 'N/A')[:10]}")
                        
                        st.markdown("**Status**")
                        st.text(f"Status: {tender.get('status', 'N/A')}")
                        st.text(f"Stage: {tender.get('stage', 'N/A')}")
                        st.text(f"Category: {tender.get('main_procurement_category', 'N/A')}")
                    
                    with col2:
                        st.markdown("**Classification**")
                        st.text(f"CPV Code: {tender.get('classification_id', 'N/A')}")
                        if pd.notna(tender.get('classification_description')):
                            st.text_area(
                                "Description",
                                value=tender['classification_description'],
                                height=100,
                                disabled=True,
                                label_visibility="collapsed"
                            )
                        
                        st.markdown("**Legal Basis**")
                        st.text(f"{tender.get('legal_basis', 'N/A')}")
                    
                    st.markdown("**Title**")
                    st.info(tender.get('title', 'N/A'))
                    
                    st.markdown("**Description**")
                    st.text_area(
                        "Full Description",
                        value=tender.get('description', 'N/A'),
                        height=200,
                        disabled=True,
                        label_visibility="collapsed"
                    )
                
                with tab2:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Contract Value**")
                        value = tender.get('value_amount')
                        currency = tender.get('value_currency', 'GBP')
                        
                        if pd.notna(value):
                            st.metric("Total Value", f"{currency} {value:,.2f}")
                        else:
                            st.info("Value not specified")
                    
                    with col2:
                        st.markdown("**Procurement Category**")
                        category = tender.get('main_procurement_category', 'N/A')
                        st.info(f"Category: {category.upper()}")
                
                with tab3:
                    st.markdown("**Buyer Organization**")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.text(f"Name: {tender.get('buyer_name', 'N/A')}")
                        st.text(f"ID: {tender.get('buyer_id', 'N/A')}")
                        st.text(f"Email: {tender.get('buyer_email', 'N/A')}")
                    
                    with col2:
                        if pd.notna(tender.get('buyer_address')):
                            st.markdown("**Address**")
                            st.text_area(
                                "Address",
                                value=tender['buyer_address'],
                                height=100,
                                disabled=True,
                                label_visibility="collapsed"
                            )
        
        else:
            st.warning("No tenders found matching your search criteria.")
            st.info("Try adjusting your filters to find relevant tenders.")

else:
    # Show all tenders by default
    st.info("👆 Use the filters in the sidebar to search for specific tenders, or click Search to view all.")
    
    # Show recent tenders as preview
    st.subheader("📋 Recent Tenders (Preview)")
    
    recent_tenders = db.get_all_tenders(limit=10)
    
    if recent_tenders:
        df = pd.DataFrame(recent_tenders)
        
        display_columns = {
            'notice_id': 'Notice ID',
            'title': 'Title',
            'buyer_name': 'Buyer',
            'status': 'Status',
            'publication_date': 'Published',
        }
        
        df_display = df[list(display_columns.keys())].copy()
        df_display.columns = list(display_columns.values())
        
        if 'Published' in df_display.columns:
            df_display['Published'] = pd.to_datetime(df_display['Published']).dt.strftime('%Y-%m-%d')
        
        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("No tenders in database. Please run the scraper to populate the database.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>Advanced search and filtering for UK tender opportunities</p>
    </div>
    """,
    unsafe_allow_html=True
)
