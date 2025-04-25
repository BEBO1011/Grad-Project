import os
import sqlalchemy
from sqlalchemy import create_engine, text, Table, Column, MetaData
import streamlit as st
import pandas as pd

class DatabaseConnector:
    """
    Utility class for database connections and operations
    """
    
    @staticmethod
    def get_postgres_connection():
        """
        Get a PostgreSQL connection using environment variables
        
        Returns:
            sqlalchemy.engine.Engine: Database connection engine
        """
        try:
            # Check for direct connection parameters
            user = os.getenv("PGUSER", "")
            password = os.getenv("PGPASSWORD", "")
            host = os.getenv("PGHOST", "")
            port = os.getenv("PGPORT", "5432")
            database = os.getenv("PGDATABASE", "")
            
            # Use either direct connection params or DATABASE_URL
            if user and password and host and database:
                conn_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"
            else:
                conn_string = os.getenv("DATABASE_URL", "")
                
            if not conn_string:
                st.error("PostgreSQL connection details not found in environment variables")
                return None
                
            engine = create_engine(conn_string)
            return engine
        except Exception as e:
            st.error(f"Error connecting to PostgreSQL: {str(e)}")
            return None
    
    @staticmethod
    def get_connection(conn_type, conn_string=None):
        """
        Get a database connection based on type
        
        Args:
            conn_type (str): Database type ('postgres', 'mysql', 'sqlite', etc.)
            conn_string (str): Connection string if needed
        
        Returns:
            sqlalchemy.engine.Engine: Database connection engine
        """
        try:
            if conn_type.lower() == 'postgres':
                return DatabaseConnector.get_postgres_connection()
            elif conn_string:
                engine = create_engine(conn_string)
                return engine
            else:
                st.error("Connection string required for non-PostgreSQL databases")
                return None
        except Exception as e:
            st.error(f"Error creating database connection: {str(e)}")
            return None
    
    @staticmethod
    def execute_query(engine, query):
        """
        Execute a SQL query
        
        Args:
            engine (sqlalchemy.engine.Engine): Database connection engine
            query (str): SQL query to execute
        
        Returns:
            pd.DataFrame: Query results as DataFrame
        """
        try:
            with engine.connect() as connection:
                result = connection.execute(text(query))
                rows = result.fetchall()
                if rows:
                    columns = result.keys()
                    return pd.DataFrame(rows, columns=columns)
                return pd.DataFrame()
        except Exception as e:
            st.error(f"Error executing query: {str(e)}")
            return None
    
    @staticmethod
    def get_table_list(engine):
        """
        Get list of tables in database
        
        Args:
            engine (sqlalchemy.engine.Engine): Database connection engine
        
        Returns:
            list: List of table names
        """
        try:
            metadata = MetaData()
            metadata.reflect(bind=engine)
            return list(metadata.tables.keys())
        except Exception as e:
            st.error(f"Error getting table list: {str(e)}")
            return []
    
    @staticmethod
    def get_table_schema(engine, table_name):
        """
        Get schema information for a table
        
        Args:
            engine (sqlalchemy.engine.Engine): Database connection engine
            table_name (str): Name of the table
        
        Returns:
            list: List of column information dictionaries
        """
        try:
            metadata = MetaData()
            metadata.reflect(bind=engine, only=[table_name])
            
            if table_name in metadata.tables:
                table = metadata.tables[table_name]
                return [
                    {
                        'name': column.name,
                        'type': str(column.type),
                        'nullable': column.nullable,
                        'primary_key': column.primary_key
                    }
                    for column in table.columns
                ]
            return []
        except Exception as e:
            st.error(f"Error getting table schema: {str(e)}")
            return []
    
    @staticmethod
    def validate_query(query):
        """
        Basic validation of SQL query to prevent harmful queries
        
        Args:
            query (str): SQL query to validate
        
        Returns:
            bool: True if query is valid, False otherwise
        """
        # Check for dangerous statements
        dangerous_keywords = [
            "DROP TABLE", "DROP DATABASE", "TRUNCATE TABLE",
            "DELETE FROM", "UPDATE", "INSERT INTO",
            "CREATE TABLE", "ALTER TABLE", "GRANT",
            "REVOKE", ";", "--"
        ]
        
        query_upper = query.upper()
        for keyword in dangerous_keywords:
            if keyword in query_upper:
                return False, f"Query contains potentially harmful operations: {keyword}"
        
        # Ensure it starts with SELECT
        if not query_upper.strip().startswith("SELECT"):
            return False, "Only SELECT queries are allowed"
        
        return True, None
