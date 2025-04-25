import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime
import re

class DataTransformer:
    """
    Provides data transformation capabilities for DataFrame manipulation
    """
    
    @staticmethod
    def filter_data(df, column, condition, value):
        """
        Filter DataFrame based on a condition
        
        Args:
            df (pd.DataFrame): Input DataFrame
            column (str): Column to filter on
            condition (str): Condition type ('equals', 'contains', 'greater_than', etc.)
            value: Value to filter by
            
        Returns:
            pd.DataFrame: Filtered DataFrame
        """
        try:
            if condition == 'equals':
                return df[df[column] == value]
            elif condition == 'not_equals':
                return df[df[column] != value]
            elif condition == 'contains':
                return df[df[column].astype(str).str.contains(str(value), na=False)]
            elif condition == 'greater_than':
                return df[df[column] > value]
            elif condition == 'less_than':
                return df[df[column] < value]
            elif condition == 'greater_equals':
                return df[df[column] >= value]
            elif condition == 'less_equals':
                return df[df[column] <= value]
            elif condition == 'is_null':
                return df[df[column].isna()]
            elif condition == 'not_null':
                return df[~df[column].isna()]
            else:
                st.warning(f"Unsupported condition: {condition}")
                return df
        except Exception as e:
            st.error(f"Error filtering data: {str(e)}")
            return df
    
    @staticmethod
    def sort_data(df, column, ascending=True):
        """
        Sort DataFrame by a column
        
        Args:
            df (pd.DataFrame): Input DataFrame
            column (str): Column to sort by
            ascending (bool): Sort order
            
        Returns:
            pd.DataFrame: Sorted DataFrame
        """
        try:
            return df.sort_values(by=column, ascending=ascending)
        except Exception as e:
            st.error(f"Error sorting data: {str(e)}")
            return df
    
    @staticmethod
    def group_data(df, groupby_cols, agg_dict):
        """
        Group DataFrame by columns and apply aggregation functions
        
        Args:
            df (pd.DataFrame): Input DataFrame
            groupby_cols (list): Columns to group by
            agg_dict (dict): Dictionary mapping columns to aggregation functions
            
        Returns:
            pd.DataFrame: Grouped DataFrame
        """
        try:
            return df.groupby(groupby_cols).agg(agg_dict).reset_index()
        except Exception as e:
            st.error(f"Error grouping data: {str(e)}")
            return df
    
    @staticmethod
    def pivot_data(df, index, columns, values, aggfunc='mean'):
        """
        Create a pivot table
        
        Args:
            df (pd.DataFrame): Input DataFrame
            index (str): Column to use as index
            columns (str): Column to use as columns
            values (str): Column to use as values
            aggfunc (str): Aggregation function
            
        Returns:
            pd.DataFrame: Pivot table
        """
        try:
            # Map string function name to actual function
            agg_map = {
                'mean': np.mean,
                'sum': np.sum,
                'count': np.size,
                'min': np.min,
                'max': np.max,
                'std': np.std,
                'median': np.median
            }
            
            func = agg_map.get(aggfunc, np.mean)
            pivot_df = pd.pivot_table(df, index=index, columns=columns, values=values, aggfunc=func)
            return pivot_df.reset_index()
        except Exception as e:
            st.error(f"Error creating pivot table: {str(e)}")
            return df
    
    @staticmethod
    def clean_column_names(df):
        """
        Clean column names (lowercase, replace spaces with underscores)
        
        Args:
            df (pd.DataFrame): Input DataFrame
            
        Returns:
            pd.DataFrame: DataFrame with cleaned column names
        """
        try:
            df.columns = [re.sub(r'[^\w\s]', '', col).lower().replace(' ', '_') for col in df.columns]
            return df
        except Exception as e:
            st.error(f"Error cleaning column names: {str(e)}")
            return df
    
    @staticmethod
    def handle_missing_values(df, method, columns=None, value=None):
        """
        Handle missing values in DataFrame
        
        Args:
            df (pd.DataFrame): Input DataFrame
            method (str): Method to handle missing values ('drop', 'fill_value', 'fill_mean', etc.)
            columns (list): Columns to apply method to (if None, apply to all)
            value: Value to fill with (for 'fill_value' method)
            
        Returns:
            pd.DataFrame: DataFrame with handled missing values
        """
        try:
            result_df = df.copy()
            cols_to_use = columns if columns else df.columns
            
            if method == 'drop':
                if columns:
                    return result_df.dropna(subset=columns)
                else:
                    return result_df.dropna()
            
            elif method == 'fill_value':
                if columns:
                    for col in columns:
                        result_df[col] = result_df[col].fillna(value)
                else:
                    result_df = result_df.fillna(value)
            
            elif method == 'fill_mean':
                for col in cols_to_use:
                    if pd.api.types.is_numeric_dtype(result_df[col]):
                        result_df[col] = result_df[col].fillna(result_df[col].mean())
            
            elif method == 'fill_median':
                for col in cols_to_use:
                    if pd.api.types.is_numeric_dtype(result_df[col]):
                        result_df[col] = result_df[col].fillna(result_df[col].median())
            
            elif method == 'fill_mode':
                for col in cols_to_use:
                    result_df[col] = result_df[col].fillna(result_df[col].mode()[0])
            
            elif method == 'interpolate':
                for col in cols_to_use:
                    if pd.api.types.is_numeric_dtype(result_df[col]):
                        result_df[col] = result_df[col].interpolate()
            
            return result_df
        
        except Exception as e:
            st.error(f"Error handling missing values: {str(e)}")
            return df
    
    @staticmethod
    def convert_types(df, column, new_type):
        """
        Convert column data type
        
        Args:
            df (pd.DataFrame): Input DataFrame
            column (str): Column to convert
            new_type (str): New data type ('int', 'float', 'str', 'datetime', 'categorical')
            
        Returns:
            pd.DataFrame: DataFrame with converted column
        """
        try:
            result_df = df.copy()
            
            if new_type == 'int':
                result_df[column] = pd.to_numeric(result_df[column], errors='coerce').fillna(0).astype(int)
            elif new_type == 'float':
                result_df[column] = pd.to_numeric(result_df[column], errors='coerce')
            elif new_type == 'str':
                result_df[column] = result_df[column].astype(str)
            elif new_type == 'datetime':
                result_df[column] = pd.to_datetime(result_df[column], errors='coerce')
            elif new_type == 'categorical':
                result_df[column] = result_df[column].astype('category')
            else:
                st.warning(f"Unsupported type: {new_type}")
            
            return result_df
        except Exception as e:
            st.error(f"Error converting data type: {str(e)}")
            return df
    
    @staticmethod
    def add_calculated_column(df, new_column_name, expression):
        """
        Add calculated column based on an expression
        
        Args:
            df (pd.DataFrame): Input DataFrame
            new_column_name (str): Name for the new column
            expression (str): Python expression using column names
            
        Returns:
            pd.DataFrame: DataFrame with new column
        """
        try:
            result_df = df.copy()
            
            # Create a safe namespace with just the DataFrame columns
            namespace = {col: result_df[col] for col in result_df.columns}
            namespace['np'] = np
            namespace['pd'] = pd
            
            # Evaluate the expression
            result = eval(expression, {"__builtins__": {}}, namespace)
            result_df[new_column_name] = result
            
            return result_df
        except Exception as e:
            st.error(f"Error calculating column: {str(e)}")
            return df
    
    @staticmethod
    def normalize_column(df, column):
        """
        Normalize a numeric column (scale to 0-1 range)
        
        Args:
            df (pd.DataFrame): Input DataFrame
            column (str): Column to normalize
            
        Returns:
            pd.DataFrame: DataFrame with normalized column
        """
        try:
            result_df = df.copy()
            if pd.api.types.is_numeric_dtype(result_df[column]):
                min_val = result_df[column].min()
                max_val = result_df[column].max()
                if max_val > min_val:
                    result_df[column] = (result_df[column] - min_val) / (max_val - min_val)
            else:
                st.warning(f"Column {column} is not numeric and cannot be normalized.")
            
            return result_df
        except Exception as e:
            st.error(f"Error normalizing column: {str(e)}")
            return df
