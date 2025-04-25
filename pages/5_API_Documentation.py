import streamlit as st
import json
import os
import pandas as pd
from utils.session_state import initialize_session_state
from utils.api_service import initialize_api

# Initialize session state and API
initialize_session_state()
initialize_api()

# Page configuration
st.set_page_config(
    page_title="API Documentation - DataDash",
    page_icon="🔌",
    layout="wide"
)

# Main title
st.title("🔌 API Documentation")
st.subheader("Documentation and configuration for DataDash API")

# Get API key (for display purposes)
default_api_key = st.session_state.get('default_api_key', 'API key not found')

# Tabs for different sections
tab1, tab2, tab3 = st.tabs(["API Overview", "Endpoints", "Configuration"])

# API Overview tab
with tab1:
    st.header("DataDash API Overview")
    
    st.markdown("""
    ## Introduction

    The DataDash API allows technical teams to integrate with the dashboards and data sources created in DataDash.
    Use this API to programmatically access your data, create dashboards, and generate reports.
    
    ## Authentication
    
    All API requests must include an API key in the header:
    ```
    X-API-Key: your_api_key_here
    ```
    
    ## Base URL
    
    The base URL for all API requests is:
    ```
    http://localhost:8000/api
    ```
    
    ## Response Format
    
    All responses are in JSON format.
    
    ## Rate Limits
    
    The API is rate-limited to 100 requests per minute per API key.
    """)
    
    # Display default API key
    st.subheader("Your API Key")
    
    st.code(default_api_key, language="text")
    st.warning("Keep this API key secure. Do not share it publicly.")
    
    # Example request section
    st.subheader("Example Request")
    
    st.code("""
    import requests
    
    api_key = "your_api_key_here"
    base_url = "http://localhost:8000/api"
    
    # Example request to get all dashboards
    response = requests.get(
        f"{base_url}/dashboards",
        headers={"X-API-Key": api_key}
    )
    
    if response.status_code == 200:
        dashboards = response.json()
        print(dashboards)
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
    """, language="python")
    
    # Error Codes section
    st.subheader("Error Codes")
    
    error_codes = [
        {"Code": 400, "Description": "Bad Request - The request was malformed"},
        {"Code": 401, "Description": "Unauthorized - API key is missing or invalid"},
        {"Code": 403, "Description": "Forbidden - API key does not have permission for this operation"},
        {"Code": 404, "Description": "Not Found - The requested resource was not found"},
        {"Code": 429, "Description": "Too Many Requests - Rate limit exceeded"},
        {"Code": 500, "Description": "Internal Server Error - Something went wrong on the server"}
    ]
    
    st.table(pd.DataFrame(error_codes))

# Endpoints tab
with tab2:
    st.header("API Endpoints")
    
    # Data Sources endpoints
    with st.expander("Data Sources Endpoints"):
        st.subheader("GET /api/data-sources")
        st.markdown("Get a list of all data sources.")
        
        st.markdown("**Response:**")
        st.code("""
        [
            {
                "id": "data_source_id",
                "name": "My CSV Data",
                "type": "csv",
                "connection_details": {
                    "file_type": "csv",
                    "has_header": true,
                    "separator": ",",
                    "original_filename": "data.csv"
                },
                "created": "2023-06-01 10:15:23",
                "last_used": "2023-06-01 15:30:45"
            },
            ...
        ]
        """, language="json")
        
        st.subheader("POST /api/data-sources")
        st.markdown("Create a new data source.")
        
        st.markdown("**Request:**")
        st.code("""
        {
            "name": "My SQL Database",
            "type": "sql",
            "connection_details": {
                "connection_string": "postgresql://user:password@host:port/database",
                "query": "SELECT * FROM table LIMIT 100"
            }
        }
        """, language="json")
        
        st.markdown("**Response:**")
        st.code("""
        {
            "id": "new_data_source_id",
            "name": "My SQL Database",
            "type": "sql",
            "connection_details": {
                "connection_string": "postgresql://user:password@host:port/database",
                "query": "SELECT * FROM table LIMIT 100"
            },
            "created": "2023-06-02 09:12:34",
            "last_used": "2023-06-02 09:12:34"
        }
        """, language="json")
        
        st.subheader("GET /api/data-sources/{source_id}")
        st.markdown("Get details for a specific data source.")
        
        st.markdown("**Response:**")
        st.code("""
        {
            "id": "data_source_id",
            "name": "My CSV Data",
            "type": "csv",
            "connection_details": {
                "file_type": "csv",
                "has_header": true,
                "separator": ",",
                "original_filename": "data.csv"
            },
            "created": "2023-06-01 10:15:23",
            "last_used": "2023-06-01 15:30:45"
        }
        """, language="json")
    
    # Dashboards endpoints
    with st.expander("Dashboards Endpoints"):
        st.subheader("GET /api/dashboards")
        st.markdown("Get a list of all dashboards.")
        
        st.markdown("**Response:**")
        st.code("""
        [
            {
                "id": "dashboard_id",
                "name": "Sales Dashboard",
                "created": "2023-06-01 10:15:23",
                "last_modified": "2023-06-01 15:30:45",
                "components": [
                    {
                        "id": "component_id",
                        "title": "Monthly Sales",
                        "chart_type": "bar_chart",
                        "data_source_id": "data_source_id",
                        "config": {
                            "x_col": "month",
                            "y_col": "sales"
                        },
                        "created": "2023-06-01 10:20:15"
                    },
                    ...
                ]
            },
            ...
        ]
        """, language="json")
        
        st.subheader("POST /api/dashboards")
        st.markdown("Create a new dashboard.")
        
        st.markdown("**Request:**")
        st.code("""
        {
            "name": "Revenue Analysis"
        }
        """, language="json")
        
        st.markdown("**Response:**")
        st.code("""
        {
            "id": "new_dashboard_id",
            "name": "Revenue Analysis",
            "created": "2023-06-02 09:12:34",
            "last_modified": "2023-06-02 09:12:34",
            "components": []
        }
        """, language="json")
        
        st.subheader("POST /api/dashboards/{dashboard_id}/components")
        st.markdown("Add a component to a dashboard.")
        
        st.markdown("**Request:**")
        st.code("""
        {
            "title": "Revenue by Region",
            "chart_type": "pie_chart",
            "data_source_id": "data_source_id",
            "config": {
                "values_col": "revenue",
                "names_col": "region"
            }
        }
        """, language="json")
        
        st.markdown("**Response:**")
        st.code("""
        {
            "id": "new_component_id",
            "title": "Revenue by Region",
            "chart_type": "pie_chart",
            "data_source_id": "data_source_id",
            "config": {
                "values_col": "revenue",
                "names_col": "region"
            },
            "created": "2023-06-02 09:15:22"
        }
        """, language="json")
    
    # Query endpoint
    with st.expander("Query Endpoint"):
        st.subheader("POST /api/query")
        st.markdown("Execute a query on a data source.")
        
        st.markdown("**Request:**")
        st.code("""
        {
            "data_source_id": "data_source_id",
            "query": "SELECT * FROM table WHERE column = 'value'"
        }
        """, language="json")
        
        st.markdown("**Response:**")
        st.code("""
        {
            "success": true,
            "message": "Query executed on sql data source",
            "query": "SELECT * FROM table WHERE column = 'value'",
            "source": "My SQL Database",
            "timestamp": "2023-06-02 09:20:15"
        }
        """, language="json")
    
    # API Keys endpoint
    with st.expander("API Keys Endpoint"):
        st.subheader("POST /api/api-keys")
        st.markdown("Create a new API key.")
        
        st.markdown("**Request:**")
        st.code("""
        {
            "name": "Development Key",
            "expires_in_days": 30
        }
        """, language="json")
        
        st.markdown("**Response:**")
        st.code("""
        {
            "id": "api_key_id",
            "name": "Development Key",
            "key": "new_api_key_value",
            "created": "2023-06-02 09:25:30",
            "expires": "2023-07-02 09:25:30"
        }
        """, language="json")

# Configuration tab
with tab3:
    st.header("API Configuration")
    
    # API Keys management
    st.subheader("API Keys Management")
    
    # Create new API key form
    with st.form("create_api_key_form"):
        api_key_name = st.text_input("API Key Name", placeholder="My API Key")
        expires_in_days = st.number_input("Expires In (Days)", min_value=1, max_value=365, value=30)
        
        submitted = st.form_submit_button("Create API Key")
        
        if submitted and api_key_name:
            try:
                from utils.api_service import api_app
                import uuid
                from datetime import datetime, timedelta
                
                # Create a new API key
                key_id = str(uuid.uuid4())
                new_key = str(uuid.uuid4())
                now = datetime.now()
                
                # Calculate expiry date
                expires = now + timedelta(days=expires_in_days)
                
                key_info = {
                    "name": api_key_name,
                    "key": new_key,
                    "created": now.strftime("%Y-%m-%d %H:%M:%S"),
                    "expires": expires.strftime("%Y-%m-%d %H:%M:%S")
                }
                
                if 'api_keys' not in st.session_state:
                    st.session_state.api_keys = {}
                
                st.session_state.api_keys[key_id] = key_info
                
                st.success(f"API key '{api_key_name}' created successfully!")
                st.code(new_key, language="text")
                st.warning("Save this key now. You won't be able to see it again.")
                
            except Exception as e:
                st.error(f"Error creating API key: {str(e)}")
    
    # Display existing API keys
    st.subheader("Existing API Keys")
    
    if 'api_keys' in st.session_state and st.session_state.api_keys:
        api_keys = st.session_state.api_keys
        
        api_key_data = []
        for key_id, key_info in api_keys.items():
            api_key_data.append({
                "ID": key_id,
                "Name": key_info["name"],
                "Created": key_info["created"],
                "Expires": key_info["expires"]
            })
        
        api_key_df = pd.DataFrame(api_key_data)
        st.dataframe(api_key_df, use_container_width=True)
        
        # Option to revoke a key
        key_to_revoke = st.selectbox(
            "Select API Key to Revoke",
            options=[key_id for key_id in api_keys.keys()],
            format_func=lambda x: f"{api_keys[x]['name']} ({x[:8]}...)"
        )
        
        if st.button("Revoke Selected API Key"):
            if key_to_revoke in st.session_state.api_keys:
                del st.session_state.api_keys[key_to_revoke]
                st.success("API key revoked successfully")
                st.rerun()
    else:
        st.info("No API keys created yet.")
    
    # API Settings
    st.subheader("API Settings")
    
    with st.form("api_settings_form"):
        rate_limit = st.number_input("Rate Limit (requests per minute)", min_value=10, max_value=1000, value=100)
        enable_cors = st.checkbox("Enable CORS", value=True)
        allowed_origins = st.text_input("Allowed Origins (comma-separated)", value="*")
        
        submitted = st.form_submit_button("Update API Settings")
        
        if submitted:
            st.success("API settings updated successfully")
            
            # In a real implementation, this would update the API configuration
            if 'api_settings' not in st.session_state:
                st.session_state.api_settings = {}
            
            st.session_state.api_settings = {
                "rate_limit": rate_limit,
                "enable_cors": enable_cors,
                "allowed_origins": allowed_origins.split(",")
            }
    
    # API Status
    st.subheader("API Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Status", "Active")
    
    with col2:
        st.metric("Uptime", "3 days, 5 hours")
    
    with col3:
        st.metric("Total Requests", "1,245")
    
    # API Usage Chart (mock)
    st.subheader("API Usage")
    
    import plotly.express as px
    import numpy as np
    
    # Create mock usage data
    dates = pd.date_range(start='2023-06-01', periods=14)
    requests = np.random.randint(50, 200, size=len(dates))
    
    usage_df = pd.DataFrame({
        'Date': dates,
        'Requests': requests
    })
    
    fig = px.bar(usage_df, x='Date', y='Requests', title='API Requests per Day')
    st.plotly_chart(fig, use_container_width=True)
    
    # API Documentation Resources
    st.subheader("Additional Resources")
    
    st.markdown("""
    - [API Documentation (Swagger UI)](#) - Interactive API documentation
    - [Postman Collection](#) - Ready-to-use Postman collection for DataDash API
    - [Client Libraries](#) - SDKs for various languages
    """)
