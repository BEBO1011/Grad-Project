import streamlit as st
import pandas as pd
import os
import io
from utils.data_connector import DataConnector
from utils.session_state import initialize_session_state, add_data_source, get_data_source_by_id
from utils.db_utils import DatabaseConnector

# Initialize session state
initialize_session_state()

# Page configuration
st.set_page_config(
    page_title="Data Sources - DataDash",
    page_icon="📁",
    layout="wide"
)

# Main title
st.title("📁 Data Sources")
st.subheader("Connect and manage your data sources")

# Tabs for different operations
tab1, tab2, tab3 = st.tabs(["Connect to Data", "Manage Sources", "Preview Data"])

# Connect to Data tab
with tab1:
    st.header("Connect to a New Data Source")
    
    # Data source type selection
    source_type = st.selectbox(
        "Select data source type",
        ["CSV File", "Excel File", "SQL Database", "PostgreSQL Database"]
    )
    
    source_name = st.text_input("Data Source Name", placeholder="My Data Source")
    
    # Different UI based on source type
    if source_type == "CSV File":
        st.info("Upload a CSV file to import data")
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
        
        col1, col2 = st.columns(2)
        with col1:
            header_option = st.checkbox("First row as header", value=True)
        with col2:
            separator = st.text_input("Separator", value=",", max_chars=1)
        
        if uploaded_file is not None:
            if st.button("Import CSV Data"):
                if not source_name:
                    st.error("Please provide a name for this data source")
                else:
                    # Load the CSV data
                    df, error = DataConnector.load_csv(
                        uploaded_file, 
                        header=0 if header_option else None,
                        sep=separator
                    )
                    
                    if error:
                        st.error(error)
                    else:
                        # Add to session state
                        connection_details = {
                            "file_type": "csv",
                            "has_header": header_option,
                            "separator": separator,
                            "original_filename": uploaded_file.name
                        }
                        
                        source_id = add_data_source(source_name, "csv", connection_details)
                        
                        # Store the DataFrame in session state
                        if 'data_frames' not in st.session_state:
                            st.session_state.data_frames = {}
                        
                        st.session_state.data_frames[source_id] = df
                        
                        st.success(f"Successfully imported CSV data: {df.shape[0]} rows, {df.shape[1]} columns")
                        st.dataframe(df.head(), use_container_width=True)
    
    elif source_type == "Excel File":
        st.info("Upload an Excel file to import data")
        uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx", "xls"])
        
        sheet_name = st.text_input("Sheet Name (leave empty for first sheet)")
        
        if uploaded_file is not None:
            if st.button("Import Excel Data"):
                if not source_name:
                    st.error("Please provide a name for this data source")
                else:
                    # Load the Excel data
                    kwargs = {"sheet_name": sheet_name} if sheet_name else {}
                    df, error = DataConnector.load_excel(uploaded_file, **kwargs)
                    
                    if error:
                        st.error(error)
                    else:
                        # Add to session state
                        connection_details = {
                            "file_type": "excel",
                            "sheet_name": sheet_name,
                            "original_filename": uploaded_file.name
                        }
                        
                        source_id = add_data_source(source_name, "excel", connection_details)
                        
                        # Store the DataFrame in session state
                        if 'data_frames' not in st.session_state:
                            st.session_state.data_frames = {}
                        
                        st.session_state.data_frames[source_id] = df
                        
                        st.success(f"Successfully imported Excel data: {df.shape[0]} rows, {df.shape[1]} columns")
                        st.dataframe(df.head(), use_container_width=True)
    
    elif source_type == "SQL Database":
        st.info("Connect to a SQL database")
        
        conn_string = st.text_input("Connection String", placeholder="dialect+driver://username:password@host:port/database")
        st.caption("Example: postgresql://user:password@localhost:5432/mydatabase")
        
        query = st.text_area("SQL Query", placeholder="SELECT * FROM table LIMIT 100")
        
        if st.button("Test Connection and Import Data"):
            if not source_name or not conn_string or not query:
                st.error("Please fill in all fields")
            else:
                # Validate the query
                is_valid, validation_msg = DatabaseConnector.validate_query(query)
                
                if not is_valid:
                    st.error(validation_msg)
                else:
                    # Validate connection string
                    is_valid, validation_msg = DataConnector.validate_connection_string(conn_string)
                    
                    if not is_valid:
                        st.error(validation_msg)
                    else:
                        # Connect and execute query
                        engine = DatabaseConnector.get_connection("sql", conn_string)
                        
                        if engine:
                            # Load the SQL data
                            df = DatabaseConnector.execute_query(engine, query)
                            
                            if df is None:
                                st.error("Error executing SQL query")
                            else:
                                # Add to session state
                                connection_details = {
                                    "connection_string": conn_string,
                                    "query": query
                                }
                                
                                source_id = add_data_source(source_name, "sql", connection_details)
                                
                                # Store the DataFrame in session state
                                if 'data_frames' not in st.session_state:
                                    st.session_state.data_frames = {}
                                
                                st.session_state.data_frames[source_id] = df
                                
                                st.success(f"Successfully connected to database and executed query: {df.shape[0]} rows, {df.shape[1]} columns")
                                st.dataframe(df.head(), use_container_width=True)
    
    elif source_type == "PostgreSQL Database":
        st.info("Connect to a PostgreSQL database using environment variables")
        
        # Show status of environment variables
        env_vars = {
            "PGUSER": os.getenv("PGUSER", "Not set"),
            "PGHOST": os.getenv("PGHOST", "Not set"),
            "PGDATABASE": os.getenv("PGDATABASE", "Not set"),
            "DATABASE_URL": "******" if os.getenv("DATABASE_URL") else "Not set"
        }
        
        st.write("Environment variables:")
        for var, value in env_vars.items():
            status = "✅" if value != "Not set" else "❌"
            st.write(f"{status} {var}: {value if var != 'DATABASE_URL' or value == 'Not set' else '******'}")
        
        query = st.text_area("SQL Query", placeholder="SELECT * FROM table LIMIT 100", key="pg_query")
        
        if st.button("Test Connection and Import Data"):
            if not source_name or not query:
                st.error("Please fill in all fields")
            else:
                # Validate the query
                is_valid, validation_msg = DatabaseConnector.validate_query(query)
                
                if not is_valid:
                    st.error(validation_msg)
                else:
                    # Connect to PostgreSQL
                    df, error = DataConnector.load_postgres(query)
                    
                    if error:
                        st.error(error)
                    elif df is not None:
                        # Add to session state
                        connection_details = {
                            "query": query,
                            "using_env_vars": True
                        }
                        
                        source_id = add_data_source(source_name, "postgres", connection_details)
                        
                        # Store the DataFrame in session state
                        if 'data_frames' not in st.session_state:
                            st.session_state.data_frames = {}
                        
                        st.session_state.data_frames[source_id] = df
                        
                        st.success(f"Successfully connected to PostgreSQL and executed query: {df.shape[0]} rows, {df.shape[1]} columns")
                        st.dataframe(df.head(), use_container_width=True)

# Manage Sources tab
with tab2:
    st.header("Manage Data Sources")
    
    if not st.session_state.data_sources:
        st.info("No data sources have been added yet. Go to the 'Connect to Data' tab to add a source.")
    else:
        # Display all data sources
        st.write(f"You have {len(st.session_state.data_sources)} data sources")
        
        for source_id, source in st.session_state.data_sources.items():
            with st.expander(f"{source['name']} ({source['type']})"):
                st.write(f"**ID:** {source_id}")
                st.write(f"**Type:** {source['type']}")
                st.write(f"**Created:** {source['created']}")
                st.write(f"**Last Used:** {source['last_used']}")
                
                # Show connection details (except sensitive info)
                st.write("**Connection Details:**")
                safe_details = source['connection_details'].copy()
                
                # Remove sensitive information
                if 'connection_string' in safe_details:
                    safe_details['connection_string'] = "******"
                
                st.json(safe_details)
                
                # Actions
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("Set as Active", key=f"set_active_{source_id}"):
                        st.session_state.active_data_source = source_id
                        
                        # Load the data if needed
                        if source_id in st.session_state.data_frames:
                            st.session_state.active_data = st.session_state.data_frames[source_id]
                            st.success(f"Set {source['name']} as the active data source")
                        else:
                            st.warning("Data not available. Please reconnect to this source.")
                
                with col2:
                    if st.button("Preview Data", key=f"preview_{source_id}"):
                        if source_id in st.session_state.data_frames:
                            # Set active tab to Preview Data
                            st.session_state.active_data_source = source_id
                            st.session_state.active_data = st.session_state.data_frames[source_id]
                            st.rerun()
                        else:
                            st.warning("Data not available. Please reconnect to this source.")
                
                with col3:
                    if st.button("Remove", key=f"remove_{source_id}"):
                        # Remove from session state
                        del st.session_state.data_sources[source_id]
                        
                        if source_id in st.session_state.data_frames:
                            del st.session_state.data_frames[source_id]
                        
                        if st.session_state.active_data_source == source_id:
                            st.session_state.active_data_source = None
                            st.session_state.active_data = None
                        
                        st.success(f"Removed data source: {source['name']}")
                        st.rerun()

# Preview Data tab
with tab3:
    st.header("Preview Data")
    
    if st.session_state.active_data_source and st.session_state.active_data is not None:
        source = get_data_source_by_id(st.session_state.active_data_source)
        
        if source:
            st.write(f"**Active Data Source:** {source['name']} ({source['type']})")
            
            df = st.session_state.active_data
            
            # Display general info
            st.metric("Rows", df.shape[0])
            st.metric("Columns", df.shape[1])
            
            # Data preview
            st.subheader("Data Preview")
            st.dataframe(df.head(10), use_container_width=True)
            
            # Column information
            st.subheader("Column Information")
            col_info = []
            
            for col in df.columns:
                col_info.append({
                    "Column": col,
                    "Type": str(df[col].dtype),
                    "Non-Null Count": df[col].count(),
                    "Null Count": df[col].isna().sum(),
                    "Unique Values": df[col].nunique()
                })
            
            col_df = pd.DataFrame(col_info)
            st.dataframe(col_df, use_container_width=True)
            
            # Sample values for each column
            st.subheader("Sample Values")
            
            for col in df.columns:
                with st.expander(f"{col} ({df[col].dtype})"):
                    unique_vals = df[col].unique()
                    if len(unique_vals) <= 10:
                        st.write("All unique values:")
                        st.write(unique_vals)
                    else:
                        st.write("Sample values:")
                        st.write(df[col].sample(min(10, df.shape[0])).values)
        else:
            st.info("No active data source. Please select a data source from the 'Manage Sources' tab.")
    else:
        st.info("No active data source. Please select a data source from the 'Manage Sources' tab.")
