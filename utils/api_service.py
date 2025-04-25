import streamlit as st
from fastapi import FastAPI, Depends, HTTPException, status, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import pandas as pd
import json
import uuid
import os
import time
from datetime import datetime
from typing import List, Dict, Any, Optional

# Create FastAPI app - will be mounted within Streamlit
api_app = FastAPI(title="DataDash API", 
                  description="API for DataDash analytics platform",
                  version="1.0.0")

# Add CORS middleware
api_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define API models
class DataSourceBase(BaseModel):
    name: str
    type: str
    connection_details: Dict[str, Any]

class DataSourceCreate(DataSourceBase):
    pass

class DataSource(DataSourceBase):
    id: str
    created: str
    last_used: str

class DashboardBase(BaseModel):
    name: str
    
class DashboardCreate(DashboardBase):
    pass

class DashboardComponent(BaseModel):
    title: str
    chart_type: str
    data_source_id: str
    config: Dict[str, Any]

class Dashboard(DashboardBase):
    id: str
    created: str
    last_modified: str
    components: List[Dict[str, Any]] = []

class QueryRequest(BaseModel):
    data_source_id: str
    query: str

class APIKeyCreate(BaseModel):
    name: str
    expires_in_days: Optional[int] = 30

class APIKey(BaseModel):
    id: str
    name: str
    key: str
    created: str
    expires: str

# Authentication middleware
async def verify_api_key(api_key: str = Depends(lambda: None)):
    """Verify API key from header"""
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is missing",
        )
    
    # Check if key exists in our stored API keys
    api_keys = st.session_state.get('api_keys', {})
    
    valid_key = False
    for key_info in api_keys.values():
        if key_info.get('key') == api_key:
            # Check if key is expired
            expires = datetime.strptime(key_info.get('expires'), "%Y-%m-%d %H:%M:%S")
            if expires > datetime.now():
                valid_key = True
                break
    
    if not valid_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired API key",
        )
    
    return api_key

# API Routes
@api_app.get("/health")
async def health_check():
    """Check API health"""
    return {"status": "healthy", "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

@api_app.get("/data-sources", response_model=List[DataSource])
async def get_data_sources(api_key: str = Depends(verify_api_key)):
    """Get all data sources"""
    data_sources = st.session_state.get('data_sources', {})
    return [
        {
            "id": id,
            "name": source.get('name'),
            "type": source.get('type'),
            "connection_details": source.get('connection_details'),
            "created": source.get('created'),
            "last_used": source.get('last_used')
        }
        for id, source in data_sources.items()
    ]

@api_app.post("/data-sources", response_model=DataSource)
async def create_data_source(
    data_source: DataSourceCreate,
    api_key: str = Depends(verify_api_key)
):
    """Create a new data source"""
    source_id = str(uuid.uuid4())
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    new_source = {
        "name": data_source.name,
        "type": data_source.type,
        "connection_details": data_source.connection_details,
        "created": now,
        "last_used": now
    }
    
    if 'data_sources' not in st.session_state:
        st.session_state.data_sources = {}
    
    st.session_state.data_sources[source_id] = new_source
    
    return {
        "id": source_id,
        **new_source
    }

@api_app.get("/data-sources/{source_id}", response_model=DataSource)
async def get_data_source(
    source_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Get a specific data source"""
    data_sources = st.session_state.get('data_sources', {})
    
    if source_id not in data_sources:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Data source with ID {source_id} not found"
        )
    
    source = data_sources[source_id]
    return {
        "id": source_id,
        **source
    }

@api_app.get("/dashboards", response_model=List[Dashboard])
async def get_dashboards(api_key: str = Depends(verify_api_key)):
    """Get all dashboards"""
    dashboards = st.session_state.get('dashboards', {})
    return [
        {
            "id": id,
            "name": dash.get('name'),
            "created": dash.get('created'),
            "last_modified": dash.get('last_modified'),
            "components": dash.get('components', [])
        }
        for id, dash in dashboards.items()
    ]

@api_app.post("/dashboards", response_model=Dashboard)
async def create_dashboard(
    dashboard: DashboardCreate,
    api_key: str = Depends(verify_api_key)
):
    """Create a new dashboard"""
    dashboard_id = str(uuid.uuid4())
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    new_dashboard = {
        "name": dashboard.name,
        "created": now,
        "last_modified": now,
        "components": []
    }
    
    if 'dashboards' not in st.session_state:
        st.session_state.dashboards = {}
    
    st.session_state.dashboards[dashboard_id] = new_dashboard
    
    return {
        "id": dashboard_id,
        **new_dashboard
    }

@api_app.post("/dashboards/{dashboard_id}/components")
async def add_dashboard_component(
    dashboard_id: str,
    component: DashboardComponent,
    api_key: str = Depends(verify_api_key)
):
    """Add a component to a dashboard"""
    dashboards = st.session_state.get('dashboards', {})
    
    if dashboard_id not in dashboards:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dashboard with ID {dashboard_id} not found"
        )
    
    # Create component
    new_component = {
        "id": str(uuid.uuid4()),
        "title": component.title,
        "chart_type": component.chart_type,
        "data_source_id": component.data_source_id,
        "config": component.config,
        "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Add to dashboard
    dashboards[dashboard_id]['components'].append(new_component)
    dashboards[dashboard_id]['last_modified'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return new_component

@api_app.post("/query")
async def execute_query(
    query_request: QueryRequest,
    api_key: str = Depends(verify_api_key)
):
    """Execute a query on a data source"""
    data_sources = st.session_state.get('data_sources', {})
    
    if query_request.data_source_id not in data_sources:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Data source with ID {query_request.data_source_id} not found"
        )
    
    source = data_sources[query_request.data_source_id]
    source_type = source.get('type')
    
    try:
        # Update last used timestamp
        data_sources[query_request.data_source_id]['last_used'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # This would call the appropriate data connector based on source type
        # For demo purposes, we'll return a simple response
        return {
            "success": True,
            "message": f"Query executed on {source_type} data source",
            "query": query_request.query,
            "source": source.get('name'),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing query: {str(e)}"
        )

@api_app.post("/api-keys", response_model=APIKey)
async def create_api_key(
    api_key_create: APIKeyCreate,
    api_key: str = Depends(verify_api_key)
):
    """Create a new API key"""
    key_id = str(uuid.uuid4())
    new_key = str(uuid.uuid4())
    now = datetime.now()
    
    # Calculate expiry date
    expires_days = api_key_create.expires_in_days or 30
    expires = now.replace(day=now.day + expires_days)
    
    key_info = {
        "name": api_key_create.name,
        "key": new_key,
        "created": now.strftime("%Y-%m-%d %H:%M:%S"),
        "expires": expires.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    if 'api_keys' not in st.session_state:
        st.session_state.api_keys = {}
    
    st.session_state.api_keys[key_id] = key_info
    
    return {
        "id": key_id,
        **key_info
    }

# Streamlit functions to integrate with the API
def initialize_api():
    """Initialize API and API keys if needed"""
    if 'api_initialized' not in st.session_state:
        if 'api_keys' not in st.session_state:
            st.session_state.api_keys = {}
            
            # Create a default API key
            key_id = str(uuid.uuid4())
            default_key = str(uuid.uuid4())
            now = datetime.now()
            
            # Default key expires in 365 days
            expires = now.replace(year=now.year + 1)
            
            st.session_state.api_keys[key_id] = {
                "name": "Default API Key",
                "key": default_key,
                "created": now.strftime("%Y-%m-%d %H:%M:%S"),
                "expires": expires.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            st.session_state.default_api_key = default_key
        
        st.session_state.api_initialized = True

def get_api_documentation():
    """Return API documentation as a string"""
    docs = """
    # DataDash API Documentation
    
    ## Authentication
    All API requests must include an API key in the header:
    ```
    X-API-Key: your_api_key_here
    ```
    
    ## Endpoints
    
    ### Data Sources
    - `GET /data-sources` - List all data sources
    - `POST /data-sources` - Create a new data source
    - `GET /data-sources/{source_id}` - Get a specific data source
    
    ### Dashboards
    - `GET /dashboards` - List all dashboards
    - `POST /dashboards` - Create a new dashboard
    - `POST /dashboards/{dashboard_id}/components` - Add a component to a dashboard
    
    ### Queries
    - `POST /query` - Execute a query on a data source
    
    ### API Keys
    - `POST /api-keys` - Create a new API key
    
    ## Example Requests
    
    ### Create a data source
    ```
    POST /data-sources
    
    {
        "name": "My CSV Data",
        "type": "csv",
        "connection_details": {
            "path": "/path/to/file.csv"
        }
    }
    ```
    
    ### Create a dashboard
    ```
    POST /dashboards
    
    {
        "name": "Sales Dashboard"
    }
    