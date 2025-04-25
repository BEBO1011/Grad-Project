import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import uuid
import os
from datetime import datetime
from utils.session_state import initialize_session_state, create_new_dashboard, save_dashboard_config, get_dashboard_by_id
from utils.visualizations import Visualizer

# Initialize session state
initialize_session_state()

# Page configuration
st.set_page_config(
    page_title="Dashboard Builder - DataDash",
    page_icon="📊",
    layout="wide"
)

# Main title
st.title("📊 Dashboard Builder")
st.subheader("Create and manage custom dashboards")

# Function to add component to dashboard
def add_component_to_dashboard(component_type, component_config):
    if not st.session_state.active_dashboard:
        st.error("Please select or create a dashboard first")
        return False
    
    # Add component to dashboard
    component_id = str(uuid.uuid4())
    component = {
        "id": component_id,
        "type": component_type,
        **component_config
    }
    
    st.session_state.dashboard_components.append(component)
    save_dashboard_config()
    return True

# Function to create visualization
def create_visualization(viz_type, data_source_id, config):
    if data_source_id not in st.session_state.data_frames:
        st.error("Data source not found")
        return None
    
    df = st.session_state.data_frames[data_source_id]
    
    if viz_type == "line_chart":
        return Visualizer.create_line_chart(df, config["x_col"], config["y_cols"], config["title"])
    
    elif viz_type == "bar_chart":
        return Visualizer.create_bar_chart(df, config["x_col"], config["y_col"], config["title"], 
                                         config.get("color_col"), config.get("orientation", "v"))
    
    elif viz_type == "scatter_plot":
        return Visualizer.create_scatter_plot(df, config["x_col"], config["y_col"], config["title"],
                                            config.get("color_col"), config.get("size_col"))
    
    elif viz_type == "pie_chart":
        return Visualizer.create_pie_chart(df, config["values_col"], config["names_col"], config["title"])
    
    elif viz_type == "histogram":
        return Visualizer.create_histogram(df, config["x_col"], config.get("nbins", 20), config["title"])
    
    elif viz_type == "heatmap":
        return Visualizer.create_heatmap(df, config["title"])
    
    elif viz_type == "area_chart":
        return Visualizer.create_area_chart(df, config["x_col"], config["y_cols"], config["title"])
    
    elif viz_type == "box_plot":
        return Visualizer.create_box_plot(df, config["x_col"], config["y_col"], config["title"], 
                                        config.get("color_col"))
    
    elif viz_type == "table":
        return df
    
    return None

# Sidebar for dashboard management
with st.sidebar:
    st.header("Dashboard Management")
    
    # Dashboard selection or creation
    st.subheader("Select Dashboard")
    
    dashboard_options = ["Create New Dashboard"] + list(st.session_state.dashboards.items())
    dashboard_format = {
        "Create New Dashboard": "Create New Dashboard",
        **{k: f"{v['name']} ({k[:8]}...)" for k, v in st.session_state.dashboards.items()}
    }
    
    selected_option = st.selectbox(
        "Dashboard",
        options=["Create New Dashboard"] + list(st.session_state.dashboards.keys()),
        format_func=lambda x: "Create New Dashboard" if x == "Create New Dashboard" else f"{st.session_state.dashboards[x]['name']} ({x[:8]}...)"
    )
    
    if selected_option == "Create New Dashboard":
        new_dashboard_name = st.text_input("Dashboard Name")
        if st.button("Create Dashboard") and new_dashboard_name:
            new_id = create_new_dashboard(new_dashboard_name)
            st.session_state.active_dashboard = new_id
            st.session_state.dashboard_components = []
            st.success(f"Created new dashboard: {new_dashboard_name}")
            st.rerun()
    else:
        # Set the selected dashboard as active
        st.session_state.active_dashboard = selected_option
        dashboard = get_dashboard_by_id(selected_option)
        
        if dashboard:
            st.session_state.dashboard_components = dashboard["components"]
            st.write(f"**Selected:** {dashboard['name']}")
            st.write(f"**Created:** {dashboard['created']}")
            st.write(f"**Last Modified:** {dashboard['last_modified']}")
            
            if st.button("Clear Dashboard"):
                st.session_state.dashboard_components = []
                save_dashboard_config()
                st.success("Dashboard cleared")
                st.rerun()
    
    # Data source selection
    st.subheader("Data Source")
    
    if not st.session_state.data_sources:
        st.warning("No data sources available. Please add a data source first.")
        st.page_link("pages/1_Data_Sources.py", label="Go to Data Sources", icon="📁")
    else:
        data_source_id = st.selectbox(
            "Select Data Source",
            options=list(st.session_state.data_sources.keys()),
            format_func=lambda x: f"{st.session_state.data_sources[x]['name']} ({x[:8]}...)"
        )

# Main content area
if not st.session_state.active_dashboard:
    st.info("Please select or create a dashboard from the sidebar to get started.")
else:
    dashboard = get_dashboard_by_id(st.session_state.active_dashboard)
    
    # Display dashboard title and info
    st.header(f"Dashboard: {dashboard['name']}")
    
    # Tabs for different operations
    tab1, tab2 = st.tabs(["Dashboard View", "Add Visualization"])
    
    # Dashboard View tab
    with tab1:
        if not st.session_state.dashboard_components:
            st.info("This dashboard is empty. Add visualizations from the 'Add Visualization' tab.")
        else:
            # Display dashboard components
            st.subheader("Dashboard Components")
            
            # Function to create layout
            def create_dashboard_layout():
                # Group components into rows of 2
                components = st.session_state.dashboard_components
                for i in range(0, len(components), 2):
                    # Create a row
                    cols = st.columns(2)
                    
                    # Add components to this row
                    for j in range(2):
                        if i + j < len(components):
                            component = components[i + j]
                            with cols[j]:
                                try:
                                    # Display component based on type
                                    if component["type"] == "visualization":
                                        st.subheader(component["config"]["title"])
                                        
                                        # Create visualization
                                        viz = create_visualization(
                                            component["viz_type"],
                                            component["data_source_id"],
                                            component["config"]
                                        )
                                        
                                        if viz is not None:
                                            if component["viz_type"] == "table":
                                                st.dataframe(viz, use_container_width=True)
                                            else:
                                                st.plotly_chart(viz, use_container_width=True)
                                        else:
                                            st.error("Error creating visualization")
                                    
                                    # Component actions
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        if st.button("Remove", key=f"remove_{component['id']}"):
                                            st.session_state.dashboard_components.remove(component)
                                            save_dashboard_config()
                                            st.rerun()
                                    
                                    with col2:
                                        if st.button("Edit", key=f"edit_{component['id']}"):
                                            st.session_state.editing_component = component
                                            st.rerun()
                                            
                                except Exception as e:
                                    st.error(f"Error displaying component: {str(e)}")
            
            # Create the dashboard layout
            create_dashboard_layout()
            
            # Export options
            st.subheader("Export Options")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Export Dashboard Configuration"):
                    from utils.report_generator import ReportGenerator
                    config_json = ReportGenerator.export_dashboard_config(
                        st.session_state.active_dashboard,
                        dashboard
                    )
                    
                    st.download_button(
                        "Download Configuration (JSON)",
                        config_json,
                        file_name=f"dashboard_{dashboard['name'].lower().replace(' ', '_')}_config.json",
                        mime="application/json"
                    )
            
            with col2:
                if st.button("Generate Report"):
                    st.page_link("pages/3_Reports.py", label="Go to Reports to generate a report from this dashboard", icon="📄")
    
    # Add Visualization tab
    with tab2:
        if not st.session_state.data_sources:
            st.warning("No data sources available. Please add a data source first.")
            st.page_link("pages/1_Data_Sources.py", label="Go to Data Sources", icon="📁")
        else:
            st.subheader("Add Visualization to Dashboard")
            
            # Form for adding visualization
            with st.form("add_visualization_form"):
                viz_title = st.text_input("Visualization Title", "New Visualization")
                
                # Select visualization type
                viz_type = st.selectbox(
                    "Visualization Type",
                    [
                        "line_chart", "bar_chart", "scatter_plot", "pie_chart",
                        "histogram", "heatmap", "area_chart", "box_plot", "table"
                    ]
                )
                
                # Select data source
                data_source = st.selectbox(
                    "Data Source",
                    options=list(st.session_state.data_sources.keys()),
                    format_func=lambda x: f"{st.session_state.data_sources[x]['name']} ({x[:8]}...)"
                )
                
                # Get DataFrame
                if data_source in st.session_state.data_frames:
                    df = st.session_state.data_frames[data_source]
                    columns = df.columns.tolist()
                    
                    # Dynamic inputs based on visualization type
                    if viz_type in ["line_chart", "area_chart"]:
                        x_col = st.selectbox("X-axis Column", columns)
                        y_cols = st.multiselect("Y-axis Columns", columns)
                        
                    elif viz_type in ["bar_chart", "box_plot"]:
                        x_col = st.selectbox("X-axis Column", columns)
                        y_col = st.selectbox("Y-axis Column", columns, index=min(1, len(columns)-1) if len(columns) > 1 else 0)
                        color_col = st.selectbox("Color Column (optional)", ["None"] + columns)
                        orientation = st.selectbox("Orientation", ["v", "h"], format_func=lambda x: "Vertical" if x == "v" else "Horizontal")
                        
                    elif viz_type == "scatter_plot":
                        x_col = st.selectbox("X-axis Column", columns)
                        y_col = st.selectbox("Y-axis Column", columns, index=min(1, len(columns)-1) if len(columns) > 1 else 0)
                        color_col = st.selectbox("Color Column (optional)", ["None"] + columns)
                        size_col = st.selectbox("Size Column (optional)", ["None"] + columns)
                        
                    elif viz_type == "pie_chart":
                        values_col = st.selectbox("Values Column", columns)
                        names_col = st.selectbox("Names Column", columns, index=min(1, len(columns)-1) if len(columns) > 1 else 0)
                        
                    elif viz_type == "histogram":
                        x_col = st.selectbox("Column", columns)
                        nbins = st.slider("Number of Bins", 5, 100, 20)
                        
                    elif viz_type == "heatmap":
                        st.info("Heatmap will use numerical columns to compute correlation matrix")
                        
                    elif viz_type == "table":
                        max_rows = st.slider("Maximum Rows to Display", 5, 100, 20)
                else:
                    st.error("Data not available for selected source. Please reload the data source.")
                    columns = []
                
                # Submit button
                submitted = st.form_submit_button("Add to Dashboard")
                
                if submitted:
                    if not st.session_state.active_dashboard:
                        st.error("Please select or create a dashboard first")
                    else:
                        try:
                            # Create component configuration based on type
                            component_config = {
                                "data_source_id": data_source,
                                "viz_type": viz_type,
                                "config": {"title": viz_title}
                            }
                            
                            if viz_type in ["line_chart", "area_chart"]:
                                if not y_cols:
                                    st.error("Please select at least one Y-axis column")
                                else:
                                    component_config["config"].update({
                                        "x_col": x_col,
                                        "y_cols": y_cols
                                    })
                                    
                                    success = add_component_to_dashboard("visualization", component_config)
                                    if success:
                                        st.success(f"Added {viz_type} visualization to dashboard")
                                        st.rerun()
                            
                            elif viz_type in ["bar_chart", "box_plot"]:
                                component_config["config"].update({
                                    "x_col": x_col,
                                    "y_col": y_col,
                                    "color_col": None if color_col == "None" else color_col,
                                    "orientation": orientation
                                })
                                
                                success = add_component_to_dashboard("visualization", component_config)
                                if success:
                                    st.success(f"Added {viz_type} visualization to dashboard")
                                    st.rerun()
                            
                            elif viz_type == "scatter_plot":
                                component_config["config"].update({
                                    "x_col": x_col,
                                    "y_col": y_col,
                                    "color_col": None if color_col == "None" else color_col,
                                    "size_col": None if size_col == "None" else size_col
                                })
                                
                                success = add_component_to_dashboard("visualization", component_config)
                                if success:
                                    st.success(f"Added scatter plot visualization to dashboard")
                                    st.rerun()
                            
                            elif viz_type == "pie_chart":
                                component_config["config"].update({
                                    "values_col": values_col,
                                    "names_col": names_col
                                })
                                
                                success = add_component_to_dashboard("visualization", component_config)
                                if success:
                                    st.success(f"Added pie chart visualization to dashboard")
                                    st.rerun()
                            
                            elif viz_type == "histogram":
                                component_config["config"].update({
                                    "x_col": x_col,
                                    "nbins": nbins
                                })
                                
                                success = add_component_to_dashboard("visualization", component_config)
                                if success:
                                    st.success(f"Added histogram visualization to dashboard")
                                    st.rerun()
                            
                            elif viz_type == "heatmap":
                                component_config["config"].update({})
                                
                                success = add_component_to_dashboard("visualization", component_config)
                                if success:
                                    st.success(f"Added heatmap visualization to dashboard")
                                    st.rerun()
                            
                            elif viz_type == "table":
                                component_config["config"].update({
                                    "max_rows": max_rows
                                })
                                
                                success = add_component_to_dashboard("visualization", component_config)
                                if success:
                                    st.success(f"Added table visualization to dashboard")
                                    st.rerun()
                            
                        except Exception as e:
                            st.error(f"Error adding visualization: {str(e)}")
            
            # Preview section
            if viz_type and data_source in st.session_state.data_frames:
                st.subheader("Visualization Preview")
                
                try:
                    # Create preview configuration
                    preview_config = {"title": viz_title}
                    
                    if viz_type in ["line_chart", "area_chart"]:
                        if 'y_cols' in locals() and y_cols:
                            preview_config.update({
                                "x_col": x_col,
                                "y_cols": y_cols
                            })
                            
                            viz = create_visualization(viz_type, data_source, preview_config)
                            if viz is not None:
                                st.plotly_chart(viz, use_container_width=True)
                    
                    elif viz_type in ["bar_chart", "box_plot"]:
                        preview_config.update({
                            "x_col": x_col,
                            "y_col": y_col,
                            "color_col": None if color_col == "None" else color_col,
                            "orientation": orientation
                        })
                        
                        viz = create_visualization(viz_type, data_source, preview_config)
                        if viz is not None:
                            st.plotly_chart(viz, use_container_width=True)
                    
                    elif viz_type == "scatter_plot":
                        preview_config.update({
                            "x_col": x_col,
                            "y_col": y_col,
                            "color_col": None if color_col == "None" else color_col,
                            "size_col": None if size_col == "None" else size_col
                        })
                        
                        viz = create_visualization(viz_type, data_source, preview_config)
                        if viz is not None:
                            st.plotly_chart(viz, use_container_width=True)
                    
                    elif viz_type == "pie_chart":
                        preview_config.update({
                            "values_col": values_col,
                            "names_col": names_col
                        })
                        
                        viz = create_visualization(viz_type, data_source, preview_config)
                        if viz is not None:
                            st.plotly_chart(viz, use_container_width=True)
                    
                    elif viz_type == "histogram":
                        preview_config.update({
                            "x_col": x_col,
                            "nbins": nbins
                        })
                        
                        viz = create_visualization(viz_type, data_source, preview_config)
                        if viz is not None:
                            st.plotly_chart(viz, use_container_width=True)
                    
                    elif viz_type == "heatmap":
                        viz = create_visualization(viz_type, data_source, preview_config)
                        if viz is not None:
                            st.plotly_chart(viz, use_container_width=True)
                    
                    elif viz_type == "table":
                        df = st.session_state.data_frames[data_source]
                        st.dataframe(df.head(max_rows), use_container_width=True)
                
                except Exception as e:
                    st.error(f"Error creating preview: {str(e)}")
