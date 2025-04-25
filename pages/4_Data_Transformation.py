import streamlit as st
import pandas as pd
import numpy as np
import uuid
from utils.session_state import initialize_session_state, add_data_source, get_data_source_by_id
from utils.data_transformer import DataTransformer

# Initialize session state
initialize_session_state()

# Page configuration
st.set_page_config(
    page_title="Data Transformation - DataDash",
    page_icon="🔄",
    layout="wide"
)

# Main title
st.title("🔄 Data Transformation")
st.subheader("Transform and prepare your data for analysis")

# Check if we have data sources available
if not st.session_state.data_sources:
    st.warning("No data sources available. Please add a data source first.")
    st.page_link("pages/1_Data_Sources.py", label="Go to Data Sources", icon="📁")
else:
    # Tabs for different operations
    tab1, tab2, tab3 = st.tabs(["Basic Transformations", "Advanced Operations", "Transformation History"])
    
    # Basic Transformations tab
    with tab1:
        st.header("Basic Data Transformations")
        
        # Data source selection
        data_source_id = st.selectbox(
            "Select Data Source",
            options=list(st.session_state.data_sources.keys()),
            format_func=lambda x: f"{st.session_state.data_sources[x]['name']} ({x[:8]}...)"
        )
        
        if data_source_id in st.session_state.data_frames:
            # Get the DataFrame
            original_df = st.session_state.data_frames[data_source_id]
            
            # Check if there's a transformed version in session state
            if 'transformed_data' not in st.session_state:
                st.session_state.transformed_data = {}
            
            if data_source_id not in st.session_state.transformed_data:
                st.session_state.transformed_data[data_source_id] = original_df.copy()
            
            # Current working copy
            df = st.session_state.transformed_data[data_source_id]
            
            # Display data info
            st.subheader("Data Preview")
            st.dataframe(df.head(5), use_container_width=True)
            
            # Transformation options
            st.subheader("Transformation Options")
            
            # Filter Data
            with st.expander("Filter Data"):
                # Get columns
                columns = df.columns.tolist()
                
                # Filter options
                filter_col = st.selectbox("Select Column to Filter", columns, key="filter_col")
                
                # Different filter options based on data type
                col_dtype = str(df[filter_col].dtype)
                
                if pd.api.types.is_numeric_dtype(df[filter_col]):
                    # Numeric columns
                    filter_condition = st.selectbox(
                        "Filter Condition",
                        ["greater_than", "less_than", "equals", "not_equals", 
                         "greater_equals", "less_equals", "is_null", "not_null"],
                        key="num_filter_condition"
                    )
                    
                    if filter_condition not in ["is_null", "not_null"]:
                        filter_value = st.number_input("Filter Value", value=0.0, key="num_filter_value")
                else:
                    # Non-numeric columns
                    filter_condition = st.selectbox(
                        "Filter Condition",
                        ["equals", "not_equals", "contains", "is_null", "not_null"],
                        key="str_filter_condition"
                    )
                    
                    if filter_condition not in ["is_null", "not_null"]:
                        filter_value = st.text_input("Filter Value", key="str_filter_value")
                
                # Apply filter button
                if st.button("Apply Filter"):
                    try:
                        # Get filter value if applicable
                        if filter_condition not in ["is_null", "not_null"]:
                            value = filter_value
                        else:
                            value = None
                        
                        # Apply the filter
                        filtered_df = DataTransformer.filter_data(df, filter_col, filter_condition, value)
                        
                        # Update the transformed data
                        st.session_state.transformed_data[data_source_id] = filtered_df
                        st.success(f"Filter applied: {df.shape[0] - filtered_df.shape[0]} rows removed")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error applying filter: {str(e)}")
            
            # Sort Data
            with st.expander("Sort Data"):
                # Get columns
                columns = df.columns.tolist()
                
                # Sort options
                sort_col = st.selectbox("Select Column to Sort By", columns, key="sort_col")
                sort_order = st.radio("Sort Order", ["Ascending", "Descending"], key="sort_order")
                
                # Apply sort button
                if st.button("Apply Sort"):
                    try:
                        # Apply the sort
                        is_ascending = (sort_order == "Ascending")
                        sorted_df = DataTransformer.sort_data(df, sort_col, is_ascending)
                        
                        # Update the transformed data
                        st.session_state.transformed_data[data_source_id] = sorted_df
                        st.success(f"Data sorted by {sort_col} in {sort_order.lower()} order")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error sorting data: {str(e)}")
            
            # Handle Missing Values
            with st.expander("Handle Missing Values"):
                # Get columns
                columns = df.columns.tolist()
                col_selection = st.multiselect("Select Columns (leave empty for all columns)", columns, key="missing_cols")
                
                # Method selection
                method = st.selectbox(
                    "Method to Handle Missing Values",
                    ["drop", "fill_value", "fill_mean", "fill_median", "fill_mode", "interpolate"],
                    key="missing_method"
                )
                
                # Value for fill_value method
                if method == "fill_value":
                    fill_value = st.text_input("Value to Fill With", "0", key="fill_value")
                else:
                    fill_value = None
                
                # Apply button
                if st.button("Handle Missing Values"):
                    try:
                        # Apply the method
                        if method == "fill_value":
                            # Try to convert to numeric if appropriate
                            try:
                                fill_value = float(fill_value)
                            except:
                                # Keep as string if not numeric
                                pass
                                
                        result_df = DataTransformer.handle_missing_values(df, method, col_selection, fill_value)
                        
                        # Update the transformed data
                        st.session_state.transformed_data[data_source_id] = result_df
                        st.success(f"Missing values handled using '{method}' method")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error handling missing values: {str(e)}")
            
            # Convert Data Types
            with st.expander("Convert Data Types"):
                # Get columns
                columns = df.columns.tolist()
                
                # Column selection
                convert_col = st.selectbox("Select Column to Convert", columns, key="convert_col")
                
                # Target data type
                target_type = st.selectbox(
                    "Target Data Type",
                    ["int", "float", "str", "datetime", "categorical"],
                    key="target_type"
                )
                
                # Apply conversion button
                if st.button("Convert Data Type"):
                    try:
                        # Apply the conversion
                        result_df = DataTransformer.convert_types(df, convert_col, target_type)
                        
                        # Update the transformed data
                        st.session_state.transformed_data[data_source_id] = result_df
                        st.success(f"Converted {convert_col} to {target_type} type")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error converting data type: {str(e)}")
            
            # Clean Column Names
            with st.expander("Clean Column Names"):
                if st.button("Clean All Column Names"):
                    try:
                        # Apply the cleaning
                        result_df = DataTransformer.clean_column_names(df)
                        
                        # Update the transformed data
                        st.session_state.transformed_data[data_source_id] = result_df
                        st.success("Column names cleaned (lowercase, spaces replaced with underscores)")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error cleaning column names: {str(e)}")
            
            # Save Transformed Data
            st.subheader("Save Transformed Data")
            new_source_name = st.text_input("New Data Source Name", f"{st.session_state.data_sources[data_source_id]['name']} (Transformed)")
            
            if st.button("Save as New Data Source"):
                try:
                    # Create new data source
                    connection_details = {
                        "original_source_id": data_source_id,
                        "transformations_applied": "Custom transformations",
                        "transformed_at": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    new_source_id = add_data_source(new_source_name, "transformed", connection_details)
                    
                    # Store the transformed DataFrame
                    st.session_state.data_frames[new_source_id] = st.session_state.transformed_data[data_source_id].copy()
                    
                    st.success(f"Transformed data saved as new data source: {new_source_name}")
                    st.page_link("pages/1_Data_Sources.py", label="Go to Data Sources", icon="📁")
                except Exception as e:
                    st.error(f"Error saving transformed data: {str(e)}")
            
            # Reset Transformations button
            if st.button("Reset Transformations"):
                # Reset to original data
                st.session_state.transformed_data[data_source_id] = original_df.copy()
                st.success("Transformations reset to original data")
                st.rerun()
        
        else:
            st.error("Data not available for selected source. Please reload the data source.")
    
    # Advanced Operations tab
    with tab2:
        st.header("Advanced Data Operations")
        
        # Data source selection
        adv_data_source_id = st.selectbox(
            "Select Data Source",
            options=list(st.session_state.data_sources.keys()),
            format_func=lambda x: f"{st.session_state.data_sources[x]['name']} ({x[:8]}...)",
            key="adv_data_source"
        )
        
        if adv_data_source_id in st.session_state.data_frames:
            # Get the DataFrame
            if 'transformed_data' not in st.session_state:
                st.session_state.transformed_data = {}
            
            if adv_data_source_id not in st.session_state.transformed_data:
                st.session_state.transformed_data[adv_data_source_id] = st.session_state.data_frames[adv_data_source_id].copy()
            
            # Current working copy
            df = st.session_state.transformed_data[adv_data_source_id]
            
            # Display data info
            st.subheader("Data Preview")
            st.dataframe(df.head(5), use_container_width=True)
            
            # Advanced transformation options
            st.subheader("Advanced Operations")
            
            # Group By operation
            with st.expander("Group By Operation"):
                # Get columns
                columns = df.columns.tolist()
                
                # Select groupby columns
                groupby_cols = st.multiselect("Select Columns to Group By", columns, key="groupby_cols")
                
                if groupby_cols:
                    # Select columns to aggregate and corresponding functions
                    agg_options = {}
                    
                    st.write("Select Aggregation Functions for Each Column:")
                    
                    for col in columns:
                        if col not in groupby_cols:
                            col_dtype = str(df[col].dtype)
                            
                            if pd.api.types.is_numeric_dtype(df[col]):
                                # Numeric columns have more aggregation options
                                agg_funcs = st.multiselect(
                                    f"Aggregation for {col}",
                                    ["sum", "mean", "min", "max", "count", "std", "median"],
                                    key=f"agg_{col}"
                                )
                                
                                if agg_funcs:
                                    agg_options[col] = agg_funcs
                            else:
                                # Non-numeric columns have fewer options
                                agg_funcs = st.multiselect(
                                    f"Aggregation for {col}",
                                    ["count", "first", "last"],
                                    key=f"agg_{col}"
                                )
                                
                                if agg_funcs:
                                    agg_options[col] = agg_funcs
                    
                    # Apply button
                    if st.button("Apply Group By") and agg_options:
                        try:
                            # Create the aggregation dictionary
                            agg_dict = {}
                            for col, funcs in agg_options.items():
                                agg_dict[col] = funcs
                            
                            # Apply the group by
                            result_df = DataTransformer.group_data(df, groupby_cols, agg_dict)
                            
                            # Update the transformed data
                            st.session_state.transformed_data[adv_data_source_id] = result_df
                            st.success(f"Group by operation applied: {result_df.shape[0]} rows in result")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error applying group by: {str(e)}")
            
            # Pivot Table
            with st.expander("Create Pivot Table"):
                # Get columns
                columns = df.columns.tolist()
                
                # Select pivot options
                pivot_index = st.selectbox("Select Index Column", columns, key="pivot_index")
                pivot_columns = st.selectbox("Select Columns", columns, key="pivot_columns")
                pivot_values = st.selectbox("Select Values Column", columns, key="pivot_values")
                
                # Aggregation function
                pivot_aggfunc = st.selectbox(
                    "Aggregation Function",
                    ["mean", "sum", "count", "min", "max", "std", "median"],
                    key="pivot_aggfunc"
                )
                
                # Apply button
                if st.button("Create Pivot Table"):
                    try:
                        # Apply the pivot
                        result_df = DataTransformer.pivot_data(
                            df, pivot_index, pivot_columns, pivot_values, pivot_aggfunc
                        )
                        
                        # Update the transformed data
                        st.session_state.transformed_data[adv_data_source_id] = result_df
                        st.success(f"Pivot table created")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error creating pivot table: {str(e)}")
            
            # Add Calculated Column
            with st.expander("Add Calculated Column"):
                # Get columns
                columns = df.columns.tolist()
                
                # New column name
                new_col_name = st.text_input("New Column Name", key="new_col_name")
                
                # Expression help
                st.info("""
                Enter a Python expression using column names. Examples:
                - `df['column1'] + df['column2']`
                - `np.log(df['numeric_column'])`
                - `df['column'].str.upper()`
                
                Available columns: """ + ", ".join([f"`{col}`" for col in columns]))
                
                # Expression input
                expression = st.text_area("Expression", key="calc_expression")
                
                # Apply button
                if st.button("Add Calculated Column") and new_col_name and expression:
                    try:
                        # Apply the calculation
                        # Replace df['colname'] with the actual column for eval
                        for col in columns:
                            expression = expression.replace(f"df['{col}']", f"df['{col}']")
                            expression = expression.replace(f'df["{col}"]', f"df['{col}']")
                        
                        result_df = DataTransformer.add_calculated_column(df, new_col_name, expression)
                        
                        # Update the transformed data
                        st.session_state.transformed_data[adv_data_source_id] = result_df
                        st.success(f"Added calculated column: {new_col_name}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error adding calculated column: {str(e)}")
            
            # Normalize Columns
            with st.expander("Normalize Columns"):
                # Get columns
                columns = df.columns.tolist()
                
                # Select numeric columns
                numeric_cols = [col for col in columns if pd.api.types.is_numeric_dtype(df[col])]
                cols_to_normalize = st.multiselect("Select Columns to Normalize", numeric_cols, key="normalize_cols")
                
                # Apply button
                if st.button("Normalize Columns") and cols_to_normalize:
                    try:
                        result_df = df.copy()
                        
                        for col in cols_to_normalize:
                            result_df = DataTransformer.normalize_column(result_df, col)
                        
                        # Update the transformed data
                        st.session_state.transformed_data[adv_data_source_id] = result_df
                        st.success(f"Normalized {len(cols_to_normalize)} column(s)")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error normalizing columns: {str(e)}")
        
        else:
            st.error("Data not available for selected source. Please reload the data source.")
    
    # Transformation History tab
    with tab3:
        st.header("Transformation History")
        
        # This would typically show a log of all transformations applied
        # For this demo, we'll just show a message
        st.info("Transformation history tracking would be implemented in a production environment.")
        
        # Here we would typically save transformation steps in session state
        if 'transformation_history' not in st.session_state:
            st.session_state.transformation_history = {}
        
        # Display mock history for demonstration purposes
        st.subheader("Examples of Tracked Operations")
        
        example_history = [
            {"timestamp": "2023-06-01 10:15:23", "operation": "Filter Data", "details": "Filtered column 'age' where values > 30"},
            {"timestamp": "2023-06-01 10:17:45", "operation": "Sort Data", "details": "Sorted by 'revenue' in descending order"},
            {"timestamp": "2023-06-01 10:25:12", "operation": "Handle Missing Values", "details": "Filled missing values in 'category' with mode"},
            {"timestamp": "2023-06-01 11:05:33", "operation": "Group By", "details": "Grouped by 'region', 'product' with sum aggregation on 'sales'"}
        ]
        
        for entry in example_history:
            st.write(f"**{entry['timestamp']}**: {entry['operation']} - {entry['details']}")
        
        st.write("---")
        st.write("In a complete implementation, all transformation operations would be tracked with options to:")
        st.write("- Export transformation steps as a script")
        st.write("- Reapply transformation workflow to new data")
        st.write("- Schedule recurring transformations")
