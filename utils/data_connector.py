import pandas as pd
import streamlit as st
import io
import os
import sqlalchemy
from sqlalchemy import create_engine, text
import pyarrow as pa
import pyarrow.parquet as pq

class DataConnector:
    """
    Handles connections to various data sources and returns data as pandas DataFrames
    """
    
    @staticmethod
    def load_csv(file_buffer, **kwargs):
        """Load data from a CSV file"""
        try:
            df = pd.read_csv(file_buffer, **kwargs)
            return df, None
        except Exception as e:
            return None, f"Error loading CSV: {str(e)}"

    @staticmethod
    def load_excel(file_buffer, **kwargs):
        """Load data from an Excel file"""
        try:
            df = pd.read_excel(file_buffer, **kwargs)
            return df, None
        except Exception as e:
            return None, f"Error loading Excel: {str(e)}"

    @staticmethod
    def load_sql(connection_string, query, **kwargs):
        """Load data from an SQL database"""
        try:
            # Safely connect to the database
            engine = create_engine(connection_string)
            df = pd.read_sql_query(text(query), engine.connect(), **kwargs)
            return df, None
        except Exception as e:
            return None, f"Error executing SQL query: {str(e)}"

    @staticmethod
    def load_postgres(query, **kwargs):
        """Load data from PostgreSQL using environment variables"""
        try:
            # Get PostgreSQL connection details from environment variables
            user = os.getenv("PGUSER", "")
            password = os.getenv("PGPASSWORD", "")
            host = os.getenv("PGHOST", "")
            port = os.getenv("PGPORT", "5432")
            database = os.getenv("PGDATABASE", "")
            
            # Check if either direct connection params or DATABASE_URL is available
            if user and password and host and database:
                conn_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"
            else:
                conn_string = os.getenv("DATABASE_URL", "")
                
            if not conn_string:
                return None, "PostgreSQL connection details not found in environment variables"
                
            # Create the connection
            engine = create_engine(conn_string)
            df = pd.read_sql_query(text(query), engine.connect(), **kwargs)
            return df, None
        except Exception as e:
            return None, f"Error connecting to PostgreSQL database: {str(e)}"

    @staticmethod
    def preview_data(df, rows=5):
        """Return a preview of the DataFrame with specified number of rows"""
        if df is not None and not df.empty:
            return df.head(rows)
        return pd.DataFrame()

    @staticmethod
    def get_column_info(df):
        """Get information about DataFrame columns"""
        if df is not None and not df.empty:
            info = []
            for col in df.columns:
                dtype = str(df[col].dtype)
                missing = df[col].isna().sum()
                unique = df[col].nunique()
                
                info.append({
                    'column': col,
                    'dtype': dtype,
                    'missing': missing,
                    'unique_values': unique,
                    'sample': df[col].iloc[0] if not df[col].empty else None
                })
            return info
        return []

    @staticmethod
    def save_to_parquet(df, path):
        """Save DataFrame to Parquet format for efficient storage"""
        try:
            table = pa.Table.from_pandas(df)
            pq.write_table(table, path)
            return True, None
        except Exception as e:
            return False, f"Error saving to Parquet: {str(e)}"

    @staticmethod
    def validate_connection_string(conn_string, db_type="sql"):
        """Validate a database connection string"""
        try:
            if db_type.lower() == "postgres":
                # For PostgreSQL, check environment variables
                if os.getenv("PGUSER") or os.getenv("DATABASE_URL"):
                    return True, None
                return False, "PostgreSQL credentials not found in environment variables"
            
            # For other SQL databases, validate connection string
            if not conn_string:
                return False, "Connection string is empty"
                
            engine = create_engine(conn_string)
            connection = engine.connect()
            connection.close()
            return True, None
        except Exception as e:
            return False, f"Connection validation failed: {str(e)}"
