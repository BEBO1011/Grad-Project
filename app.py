import streamlit as st
import os
from utils.session_state import initialize_session_state

# Set page configuration
st.set_page_config(
    page_title="DataDash - Analytics Dashboard Builder",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
initialize_session_state()

# Main page content
st.title("📊 DataDash")
st.subheader("Build custom dashboards and reports with ease")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### What you can do with DataDash:
    - 📁 Connect to various data sources (CSV, Excel, SQL databases)
    - 📊 Create interactive visualizations
    - 📋 Build custom dashboards with drag-and-drop interface
    - 🔄 Transform your data with simple operations
    - 📩 Generate and export reports
    - 🔌 Technical API for integrations
    """)
    
    st.info("""
    **Getting Started:**
    1. Navigate to 'Data Sources' to connect your data
    2. Use 'Dashboard Builder' to create visualizations
    3. Generate reports or schedule automated ones
    """)

with col2:
    st.markdown("""
    ### Features Overview:
    """)
    
    feature_tabs = st.tabs(["Data Sources", "Visualizations", "Reports", "API"])
    
    with feature_tabs[0]:
        st.markdown("""
        - CSV file upload
        - Excel file support
        - SQL database connections
        - PostgreSQL integration
        """)
    
    with feature_tabs[1]:
        st.markdown("""
        - Line charts, Bar charts, Scatter plots
        - Pie charts and Area charts
        - Interactive tables with filtering
        - Heatmaps and Correlation matrices
        """)
    
    with feature_tabs[2]:
        st.markdown("""
        - On-demand report generation
        - Export to PDF, Excel, CSV
        - Scheduled reports
        - Email delivery
        """)
    
    with feature_tabs[3]:
        st.markdown("""
        - RESTful API endpoints
        - Data integration capabilities
        - Authentication and access control
        - Custom endpoint configuration
        """)

# Quick Start Section
st.header("Quick Start Guide")
    
quick_start_option = st.selectbox(
    "What would you like to do?",
    [
        "Connect to a data source",
        "Create a visualization",
        "Build a dashboard",
        "Generate a report",
        "Learn about API integration"
    ]
)

if quick_start_option == "Connect to a data source":
    st.page_link("pages/1_Data_Sources.py", label="Go to Data Sources", icon="📁")
    st.markdown("Connect to CSV, Excel, or SQL databases to import your data.")
    
elif quick_start_option == "Create a visualization":
    st.page_link("pages/2_Dashboard_Builder.py", label="Go to Dashboard Builder", icon="📊")
    st.markdown("Create interactive charts, graphs, and tables from your data sources.")
    
elif quick_start_option == "Build a dashboard":
    st.page_link("pages/2_Dashboard_Builder.py", label="Go to Dashboard Builder", icon="📊")
    st.markdown("Combine multiple visualizations into a custom dashboard.")
    
elif quick_start_option == "Generate a report":
    st.page_link("pages/3_Reports.py", label="Go to Reports", icon="📩")
    st.markdown("Create and export reports based on your dashboards and visualizations.")
    
else:
    st.page_link("pages/5_API_Documentation.py", label="Go to API Documentation", icon="🔌")
    st.markdown("Learn how to integrate DataDash with your technical systems.")

# Footer
st.divider()
st.caption("DataDash - A Streamlit-based data analytics tool")
