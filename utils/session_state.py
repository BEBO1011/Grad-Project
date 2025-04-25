import streamlit as st
import pandas as pd
import os
import uuid
import json
from datetime import datetime

def initialize_session_state():
    """Initialize session state variables if they don't exist"""
    
    # Data source management
    if 'data_sources' not in st.session_state:
        st.session_state.data_sources = {}
    
    if 'active_data_source' not in st.session_state:
        st.session_state.active_data_source = None
    
    if 'active_data' not in st.session_state:
        st.session_state.active_data = None
    
    # Dashboard management
    if 'dashboards' not in st.session_state:
        st.session_state.dashboards = {}
    
    if 'active_dashboard' not in st.session_state:
        st.session_state.active_dashboard = None
    
    if 'dashboard_components' not in st.session_state:
        st.session_state.dashboard_components = []
        
    # Visualization settings
    if 'visualizations' not in st.session_state:
        st.session_state.visualizations = {}
    
    # Report management
    if 'reports' not in st.session_state:
        st.session_state.reports = {}
        
    if 'scheduled_reports' not in st.session_state:
        st.session_state.scheduled_reports = {}
    
    # API settings
    if 'api_keys' not in st.session_state:
        st.session_state.api_keys = {}
    
    if 'api_endpoints' not in st.session_state:
        st.session_state.api_endpoints = {}

def save_dashboard_config():
    """Save the current dashboard configuration"""
    if st.session_state.active_dashboard:
        dashboard_id = st.session_state.active_dashboard
        st.session_state.dashboards[dashboard_id]['components'] = st.session_state.dashboard_components
        st.session_state.dashboards[dashboard_id]['last_modified'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def create_new_dashboard(name):
    """Create a new dashboard with the given name"""
    dashboard_id = str(uuid.uuid4())
    st.session_state.dashboards[dashboard_id] = {
        'name': name,
        'created': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'last_modified': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'components': []
    }
    return dashboard_id

def add_data_source(name, source_type, connection_details):
    """Add a new data source to session state"""
    source_id = str(uuid.uuid4())
    st.session_state.data_sources[source_id] = {
        'name': name,
        'type': source_type,
        'connection_details': connection_details,
        'created': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'last_used': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    return source_id

def get_dashboard_by_id(dashboard_id):
    """Get dashboard configuration by ID"""
    if dashboard_id in st.session_state.dashboards:
        return st.session_state.dashboards[dashboard_id]
    return None

def get_data_source_by_id(source_id):
    """Get data source configuration by ID"""
    if source_id in st.session_state.data_sources:
        return st.session_state.data_sources[source_id]
    return None

def export_configuration():
    """Export the current configuration as JSON"""
    config = {
        'data_sources': st.session_state.data_sources,
        'dashboards': st.session_state.dashboards,
        'visualizations': st.session_state.visualizations,
        'reports': st.session_state.reports,
        'scheduled_reports': st.session_state.scheduled_reports,
        'api_endpoints': st.session_state.api_endpoints
    }
    return json.dumps(config, indent=2)

def import_configuration(config_json):
    """Import configuration from JSON"""
    try:
        config = json.loads(config_json)
        st.session_state.data_sources = config.get('data_sources', {})
        st.session_state.dashboards = config.get('dashboards', {})
        st.session_state.visualizations = config.get('visualizations', {})
        st.session_state.reports = config.get('reports', {})
        st.session_state.scheduled_reports = config.get('scheduled_reports', {})
        st.session_state.api_endpoints = config.get('api_endpoints', {})
        return True
    except Exception as e:
        st.error(f"Failed to import configuration: {str(e)}")
        return False
