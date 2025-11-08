"""
Analytics & Export Page - Analyze and export tender data
"""

import streamlit as st
from utils.database import TenderDatabase
from utils.data_generator import TenderDataGenerator
import pandas as pd
import json
from datetime import datetime

st.set_page_config(
    page_title="Analytics & Export",
    page_icon="📊",
    layout="wide"
)

# Initialize
@st.cache_resource
def get_database():
    return TenderDatabase()

db = get_database()

# Header
st.title("📊 Analytics & Export")
st.markdown("Analyze tender data and export results")
st.markdown("---")

# Sidebar
st.sidebar.header("⚙️ Options")

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
        
        st.sidebar.success(f"✅ Generated {inserted} tenders")
        st.rerun()

st.sidebar.markdown("---")

# Export options
st.sidebar.subheader("📥 Export Options")
export_format = st.sidebar.selectbox(
    "Export Format",
    options=["CSV", "JSON", "Excel"],
    help="Choose export file format"
)

export_limit = st.sidebar.number_input(
    "Max Records to Export",
    min_value=10,
    max_value=10000,
    value=1000,
    step=100,
    help="Maximum number of records to export"
)

# Main content - Analytics
st.subheader("📈 Tender Analytics")

# Get all tenders for analysis
all_tenders = db.get_all_tenders()

if all_tenders:
    df = pd.DataFrame(all_tenders)
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Tenders", len(df))
    
    with col2:
        total_value = df['value_amount'].sum()
        st.metric("Total Value", f"£{total_value:,.0f}")
    
    with col3:
        avg_value = df['value_amount'].mean()
        st.metric("Avg Value", f"£{avg_value:,.0f}")
    
    with col4:
        unique_buyers = df['buyer_name'].nunique()
        st.metric("Unique Buyers", unique_buyers)
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Tenders by Status")
        
        status_counts = df['status'].value_counts()
        
        if not status_counts.empty:
            st.bar_chart(status_counts)
            
            # Show table
            status_df = pd.DataFrame({
                'Status': status_counts.index,
                'Count': status_counts.values
            })
            st.dataframe(status_df, use_container_width=True, hide_index=True)
    
    with col2:
        st.subheader("📊 Tenders by Category")
        
        category_counts = df['main_procurement_category'].value_counts()
        
        if not category_counts.empty:
            st.bar_chart(category_counts)
            
            # Show table
            category_df = pd.DataFrame({
                'Category': category_counts.index,
                'Count': category_counts.values
            })
            st.dataframe(category_df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Top buyers
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏢 Top 10 Buyers by Tender Count")
        
        buyer_counts = df['buyer_name'].value_counts().head(10)
        
        buyer_df = pd.DataFrame({
            'Buyer': buyer_counts.index,
            'Tenders': buyer_counts.values
        })
        
        st.dataframe(buyer_df, use_container_width=True, hide_index=True)
    
    with col2:
        st.subheader("💰 Top 10 Buyers by Total Value")
        
        buyer_values = df.groupby('buyer_name')['value_amount'].sum().sort_values(ascending=False).head(10)
        
        buyer_value_df = pd.DataFrame({
            'Buyer': buyer_values.index,
            'Total Value (£)': buyer_values.values
        })
        
        buyer_value_df['Total Value (£)'] = buyer_value_df['Total Value (£)'].apply(
            lambda x: f"£{x:,.2f}" if pd.notna(x) else "N/A"
        )
        
        st.dataframe(buyer_value_df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Value distribution
    st.subheader("💵 Value Distribution")
    
    # Filter out null values
    df_with_values = df[df['value_amount'].notna()]
    
    if not df_with_values.empty:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            min_value = df_with_values['value_amount'].min()
            st.metric("Min Value", f"£{min_value:,.2f}")
        
        with col2:
            median_value = df_with_values['value_amount'].median()
            st.metric("Median Value", f"£{median_value:,.2f}")
        
        with col3:
            max_value = df_with_values['value_amount'].max()
            st.metric("Max Value", f"£{max_value:,.2f}")
        
        # Histogram
        st.bar_chart(df_with_values['value_amount'])
    
    st.markdown("---")
    
    # Export section
    st.subheader("📥 Export Data")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("📥 Export Tenders", type="primary", use_container_width=True):
            
            # Limit records
            export_df = df.head(export_limit)
            
            # Prepare export
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if export_format == "CSV":
                csv_data = export_df.to_csv(index=False)
                st.download_button(
                    label="⬇️ Download CSV",
                    data=csv_data,
                    file_name=f"uk_tenders_{timestamp}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            elif export_format == "JSON":
                json_data = export_df.to_json(orient='records', indent=2)
                st.download_button(
                    label="⬇️ Download JSON",
                    data=json_data,
                    file_name=f"uk_tenders_{timestamp}.json",
                    mime="application/json",
                    use_container_width=True
                )
            
            elif export_format == "Excel":
                # For Excel, we need to use a buffer
                from io import BytesIO
                
                buffer = BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    export_df.to_excel(writer, index=False, sheet_name='Tenders')
                
                excel_data = buffer.getvalue()
                
                st.download_button(
                    label="⬇️ Download Excel",
                    data=excel_data,
                    file_name=f"uk_tenders_{timestamp}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            
            st.success(f"✅ Prepared {len(export_df)} records for export in {export_format} format")
    
    # Preview export data
    st.markdown("---")
    st.subheader("👀 Export Preview")
    
    preview_df = df.head(10)
    
    # Select columns for preview
    preview_columns = [
        'notice_id', 'title', 'buyer_name', 'status', 
        'value_amount', 'publication_date'
    ]
    
    preview_display = preview_df[preview_columns].copy()
    
    st.dataframe(
        preview_display,
        use_container_width=True,
        hide_index=True
    )
    
    st.info(f"Showing first 10 of {len(df)} total records. Export will include up to {export_limit} records.")

else:
    st.warning("📭 No tender data available for analysis.")
    st.info("Generate synthetic data or scrape from the API to populate the database.")
    
    # Show generate button
    if st.button("🎲 Generate Sample Data", type="primary"):
        with st.spinner("Generating synthetic tender data..."):
            generator = TenderDataGenerator()
            synthetic_tenders = generator.generate_tenders(count=100)
            
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
            
            st.success(f"✅ Generated {inserted} tenders")
            st.rerun()

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>Analytics and export functionality for UK tender data</p>
    </div>
    """,
    unsafe_allow_html=True
)
