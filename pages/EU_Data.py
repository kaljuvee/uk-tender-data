"""
EU Data Page - View and download EU tender data from TED
"""

import streamlit as st
from utils.database import TenderDatabase
import pandas as pd
import json
from datetime import datetime

st.set_page_config(
    page_title="EU Data - UK + EU Tender Data",
    page_icon="🇪🇺",
    layout="wide"
)

# Initialize
@st.cache_resource
def get_database():
    return TenderDatabase()

db = get_database()

# Header
st.title("🇪🇺 EU Tender Data (TED)")
st.markdown("View and analyze EU tender data from Tenders Electronic Daily (TED)")
st.markdown("---")

# Get EU-specific statistics
try:
    # Get EU tenders only
    all_tenders = db.get_all_tenders(limit=10000, country_code=None)  # Get all countries
    eu_tenders = [t for t in all_tenders if t.get('country_code') == 'EU']
    
    # Calculate statistics
    total_eu = len(eu_tenders)
    
    # Get unique countries from buyer_id
    countries = set()
    for tender in eu_tenders:
        buyer_id = tender.get('buyer_id', '')
        if buyer_id:
            countries.add(buyer_id)
    
    # Count by status
    status_counts = {}
    for tender in eu_tenders:
        status = tender.get('status', 'unknown')
        status_counts[status] = status_counts.get(status, 0) + 1
    
except Exception as e:
    st.error(f"Error loading EU tender data: {str(e)}")
    total_eu = 0
    countries = set()
    status_counts = {}

# Overview cards
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="🇪🇺 Total EU Tenders",
        value=total_eu
    )

with col2:
    st.metric(
        label="🌍 EU Countries",
        value=len(countries)
    )

with col3:
    active_count = status_counts.get('active', 0)
    st.metric(
        label="✅ Active",
        value=active_count
    )

with col4:
    planned_count = status_counts.get('planned', 0)
    st.metric(
        label="📅 Planned",
        value=planned_count
    )

st.markdown("---")

# Sidebar - Download options
st.sidebar.header("📥 Download EU Data")

download_format = st.sidebar.selectbox(
    "Format",
    options=["CSV", "Excel", "JSON"],
    help="Select export format for EU tender data"
)

download_limit = st.sidebar.number_input(
    "Max Records",
    min_value=10,
    max_value=10000,
    value=1000,
    step=10,
    help="Maximum number of records to download"
)

if st.sidebar.button("📥 Download EU Tenders", type="primary", use_container_width=True):
    if total_eu > 0:
        df = pd.DataFrame(eu_tenders)
        
        # Limit records
        df_export = df.head(download_limit)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if download_format == "CSV":
            csv = df_export.to_csv(index=False)
            st.sidebar.download_button(
                label="💾 Download CSV",
                data=csv,
                file_name=f"eu_tenders_{timestamp}.csv",
                mime="text/csv",
                use_container_width=True
            )
        elif download_format == "Excel":
            # Create Excel file in memory
            from io import BytesIO
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_export.to_excel(writer, index=False, sheet_name='EU Tenders')
            excel_data = output.getvalue()
            
            st.sidebar.download_button(
                label="💾 Download Excel",
                data=excel_data,
                file_name=f"eu_tenders_{timestamp}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        else:  # JSON
            json_data = df_export.to_json(orient='records', date_format='iso')
            st.sidebar.download_button(
                label="💾 Download JSON",
                data=json_data,
                file_name=f"eu_tenders_{timestamp}.json",
                mime="application/json",
                use_container_width=True
            )
    else:
        st.sidebar.warning("No EU tender data to download")

st.sidebar.markdown("---")

# Show country breakdown
if countries:
    st.sidebar.subheader("🌍 Countries")
    # Count tenders by country
    country_counts = {}
    for tender in eu_tenders:
        country = tender.get('buyer_id', 'Unknown')
        country_counts[country] = country_counts.get(country, 0) + 1
    
    # Sort by count
    sorted_countries = sorted(country_counts.items(), key=lambda x: x[1], reverse=True)
    
    for country, count in sorted_countries[:10]:  # Top 10
        st.sidebar.text(f"• {country}: {count}")

# Main content
if total_eu > 0:
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["📋 All EU Tenders", "🌍 By Country", "📊 Statistics"])
    
    with tab1:
        st.subheader("📋 EU Tender List")
        
        # Convert to DataFrame
        df = pd.DataFrame(eu_tenders)
        
        # Display columns
        display_columns = {
            'notice_id': 'Notice ID',
            'title': 'Title',
            'buyer_name': 'Buyer',
            'buyer_id': 'Country',
            'status': 'Status',
            'publication_date': 'Published',
        }
        
        available_cols = [col for col in display_columns.keys() if col in df.columns]
        df_display = df[available_cols].copy()
        df_display.columns = [display_columns[col] for col in available_cols]
        
        # Format date
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
                "Country": st.column_config.TextColumn(width="small"),
                "Status": st.column_config.TextColumn(width="small"),
                "Published": st.column_config.TextColumn(width="small"),
            }
        )
        
        st.markdown("---")
        
        # Detailed view
        st.subheader("🔍 Tender Details")
        
        selected_notice = st.selectbox(
            "Select a tender to view full details:",
            options=df['notice_id'].tolist(),
            format_func=lambda x: f"{x} - {df[df['notice_id']==x]['title'].values[0][:60]}..."
        )
        
        if selected_notice:
            tender = df[df['notice_id'] == selected_notice].iloc[0]
            
            # Display details
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Identification**")
                st.text(f"Notice ID: {tender['notice_id']}")
                st.text(f"OCID: {tender.get('ocid', 'N/A')}")
                st.text(f"Country: {tender.get('buyer_id', 'N/A')}")
                pub_date = tender.get('publication_date', 'N/A')
                st.text(f"Publication Date: {pub_date[:10] if pub_date and pub_date != 'N/A' else 'N/A'}")
                
                st.markdown("**Status**")
                st.text(f"Status: {tender.get('status', 'N/A')}")
                st.text(f"Stage: {tender.get('stage', 'N/A')}")
                st.text(f"Category: {tender.get('main_procurement_category', 'N/A')}")
            
            with col2:
                st.markdown("**Buyer Organization**")
                st.text(f"Name: {tender.get('buyer_name', 'N/A')}")
                st.text(f"Country Code: {tender.get('buyer_id', 'N/A')}")
                
                st.markdown("**Value**")
                value = tender.get('value_amount')
                currency = tender.get('value_currency', 'EUR')
                if pd.notna(value):
                    st.text(f"Amount: {currency} {value:,.2f}")
                else:
                    st.text("Amount: Not specified")
            
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
        st.subheader("🌍 Tenders by Country")
        
        # Group by country
        country_data = []
        for country, count in sorted_countries:
            # Get tenders for this country
            country_tenders = [t for t in eu_tenders if t.get('buyer_id') == country]
            
            # Calculate stats
            active = len([t for t in country_tenders if t.get('status') == 'active'])
            planned = len([t for t in country_tenders if t.get('status') == 'planned'])
            
            country_data.append({
                'Country': country,
                'Total Tenders': count,
                'Active': active,
                'Planned': planned
            })
        
        df_countries = pd.DataFrame(country_data)
        
        st.dataframe(
            df_countries,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Country": st.column_config.TextColumn(width="medium"),
                "Total Tenders": st.column_config.NumberColumn(width="small"),
                "Active": st.column_config.NumberColumn(width="small"),
                "Planned": st.column_config.NumberColumn(width="small"),
            }
        )
        
        # Bar chart
        st.markdown("---")
        st.subheader("📊 Tender Count by Country")
        
        import plotly.express as px
        
        fig = px.bar(
            df_countries,
            x='Country',
            y='Total Tenders',
            title='EU Tenders by Country',
            labels={'Total Tenders': 'Number of Tenders'},
            color='Total Tenders',
            color_continuous_scale='Blues'
        )
        
        fig.update_layout(
            xaxis_title="Country",
            yaxis_title="Number of Tenders",
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("📊 EU Tender Statistics")
        
        # Status distribution
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Status Distribution**")
            
            status_df = pd.DataFrame(list(status_counts.items()), columns=['Status', 'Count'])
            
            fig = px.pie(
                status_df,
                values='Count',
                names='Status',
                title='Tenders by Status',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("**Category Distribution**")
            
            # Count by category
            category_counts = {}
            for tender in eu_tenders:
                category = tender.get('main_procurement_category', 'unknown')
                category_counts[category] = category_counts.get(category, 0) + 1
            
            category_df = pd.DataFrame(list(category_counts.items()), columns=['Category', 'Count'])
            
            fig = px.pie(
                category_df,
                values='Count',
                names='Category',
                title='Tenders by Category',
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Summary statistics
        st.subheader("📈 Summary Statistics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total EU Tenders", total_eu)
            st.metric("EU Member Countries", len(countries))
        
        with col2:
            st.metric("Active Tenders", status_counts.get('active', 0))
            st.metric("Planned Tenders", status_counts.get('planned', 0))
        
        with col3:
            st.metric("Complete Tenders", status_counts.get('complete', 0))
            st.metric("Cancelled Tenders", status_counts.get('cancelled', 0))

else:
    st.warning("📭 No EU tender data available.")
    st.info("Run the EU scraper to populate the database with TED data:")
    
    st.code("""
# Run EU scraper
python tasks/scrape_eu_tenders.py --limit 100

# Setup automated hourly scraping
bash tasks/setup_cron.sh
    """, language="bash")
    
    st.markdown("---")
    
    st.markdown("**About TED (Tenders Electronic Daily)**")
    st.markdown("""
    TED is the online version of the 'Supplement to the Official Journal' of the EU, 
    dedicated to European public procurement. It provides:
    
    - 📋 Procurement notices from EU member states
    - 🌍 Coverage of all 27 EU countries
    - 📊 Standardized eForms format
    - 🔄 Daily updates with new tenders
    
    **Data Source**: https://ted.europa.eu/
    """)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>EU tender data from Tenders Electronic Daily (TED) | 
        <a href="https://ted.europa.eu/" target="_blank">Visit TED Website</a></p>
    </div>
    """,
    unsafe_allow_html=True
)
