import streamlit as st
import pandas as pd
import plotly.express as px
import io
import base64
from datetime import datetime, timedelta
import json
from utils.session_state import initialize_session_state, get_dashboard_by_id
from utils.report_generator import ReportGenerator
from utils.visualizations import Visualizer

# Initialize session state
initialize_session_state()

# Page configuration
st.set_page_config(
    page_title="Reports - DataDash",
    page_icon="📄",
    layout="wide"
)

# Main title
st.title("📄 Reports")
st.subheader("Generate and manage reports")

# Tabs for different operations
tab1, tab2, tab3 = st.tabs(["Generate Reports", "Scheduled Reports", "Report Templates"])

# Generate Reports tab
with tab1:
    st.header("Generate Reports")
    
    # Dashboard selection
    if not st.session_state.dashboards:
        st.warning("No dashboards available. Please create a dashboard first.")
        st.page_link("pages/2_Dashboard_Builder.py", label="Go to Dashboard Builder", icon="📊")
    else:
        dashboard_id = st.selectbox(
            "Select Dashboard",
            options=list(st.session_state.dashboards.keys()),
            format_func=lambda x: f"{st.session_state.dashboards[x]['name']} ({x[:8]}...)"
        )
        
        # Get selected dashboard
        dashboard = get_dashboard_by_id(dashboard_id)
        
        if dashboard:
            st.write(f"**Selected:** {dashboard['name']}")
            st.write(f"**Created:** {dashboard['created']}")
            st.write(f"**Last Modified:** {dashboard['last_modified']}")
            st.write(f"**Components:** {len(dashboard['components'])}")
            
            # Report format selection
            report_format = st.selectbox(
                "Report Format",
                ["Excel", "CSV", "PDF", "HTML"]
            )
            
            # Report options
            include_charts = st.checkbox("Include Charts", value=True)
            include_data_tables = st.checkbox("Include Data Tables", value=True)
            include_summary = st.checkbox("Include Summary Statistics", value=True)
            
            # Generate report button
            if st.button("Generate Report"):
                if dashboard["components"]:
                    try:
                        # Prepare data frames for report
                        df_dict = {}
                        for component in dashboard["components"]:
                            if component["type"] == "visualization":
                                data_source_id = component["data_source_id"]
                                if data_source_id in st.session_state.data_frames:
                                    df_dict[data_source_id] = st.session_state.data_frames[data_source_id]
                        
                        # Generate report based on format
                        if report_format == "Excel":
                            # Create a dict of dataframes to export
                            excel_dict = {}
                            
                            if include_data_tables:
                                # Add data tables
                                for i, component in enumerate(dashboard["components"]):
                                    if component["type"] == "visualization":
                                        data_source_id = component["data_source_id"]
                                        if data_source_id in st.session_state.data_frames:
                                            df = st.session_state.data_frames[data_source_id]
                                            sheet_name = f"{component['config']['title'][:28]}"
                                            excel_dict[sheet_name] = df
                            
                            if include_summary:
                                # Add summary statistics
                                summary_data = []
                                for i, component in enumerate(dashboard["components"]):
                                    if component["type"] == "visualization":
                                        data_source_id = component["data_source_id"]
                                        if data_source_id in st.session_state.data_frames:
                                            viz_type = component["viz_type"]
                                            summary_data.append({
                                                "Component": component["config"]["title"],
                                                "Visualization Type": viz_type,
                                                "Data Source": st.session_state.data_sources[data_source_id]["name"],
                                                "Rows": st.session_state.data_frames[data_source_id].shape[0],
                                                "Columns": st.session_state.data_frames[data_source_id].shape[1]
                                            })
                                
                                if summary_data:
                                    excel_dict["Summary"] = pd.DataFrame(summary_data)
                            
                            # Generate Excel report
                            excel_data = ReportGenerator.generate_excel_report(
                                excel_dict,
                                f"{dashboard['name']}_report.xlsx"
                            )
                            
                            if excel_data:
                                # Provide download link
                                b64 = base64.b64encode(excel_data).decode()
                                href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{dashboard["name"]}_report.xlsx">Download Excel Report</a>'
                                st.markdown(href, unsafe_allow_html=True)
                                st.success("Excel report generated successfully!")
                        
                        elif report_format == "CSV":
                            # For CSV, we'll export the first data source or a combined one
                            if dashboard["components"] and include_data_tables:
                                first_component = dashboard["components"][0]
                                if first_component["type"] == "visualization":
                                    data_source_id = first_component["data_source_id"]
                                    if data_source_id in st.session_state.data_frames:
                                        df = st.session_state.data_frames[data_source_id]
                                        
                                        # Generate CSV
                                        csv_data = ReportGenerator.generate_csv_report(
                                            df,
                                            f"{dashboard['name']}_report.csv"
                                        )
                                        
                                        if csv_data:
                                            # Provide download link
                                            st.download_button(
                                                "Download CSV Report",
                                                csv_data,
                                                file_name=f"{dashboard['name']}_report.csv",
                                                mime="text/csv"
                                            )
                                            st.success("CSV report generated successfully!")
                            else:
                                st.error("No data available for CSV export")
                        
                        elif report_format == "HTML" or report_format == "PDF":
                            # Create HTML summary report
                            html_report = ReportGenerator.create_report_summary(
                                dashboard["components"],
                                df_dict
                            )
                            
                            # For HTML, provide direct download
                            if report_format == "HTML":
                                st.download_button(
                                    "Download HTML Report",
                                    html_report,
                                    file_name=f"{dashboard['name']}_report.html",
                                    mime="text/html"
                                )
                                st.success("HTML report generated successfully!")
                                
                                # Display preview
                                with st.expander("HTML Report Preview"):
                                    st.components.v1.html(html_report, height=500, scrolling=True)
                            
                            # For PDF, we would need to convert HTML to PDF
                            # This typically requires additional libraries like weasyprint or a service
                            # For this example, we'll provide a message
                            else:
                                st.warning("PDF generation would require additional configuration. Please use HTML format instead.")
                    
                    except Exception as e:
                        st.error(f"Error generating report: {str(e)}")
                else:
                    st.error("This dashboard has no components. Add visualizations to the dashboard first.")
            
            # Schedule report option
            st.subheader("Schedule This Report")
            
            with st.expander("Schedule Options"):
                schedule_name = st.text_input("Schedule Name", f"{dashboard['name']} Report")
                
                schedule_frequency = st.selectbox(
                    "Frequency",
                    ["Daily", "Weekly", "Monthly", "Custom"]
                )
                
                if schedule_frequency == "Daily":
                    schedule_time = st.time_input("Time of day", datetime.now().time())
                elif schedule_frequency == "Weekly":
                    schedule_day = st.selectbox(
                        "Day of week",
                        ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                    )
                    schedule_time = st.time_input("Time of day", datetime.now().time())
                elif schedule_frequency == "Monthly":
                    schedule_day = st.selectbox(
                        "Day of month",
                        list(range(1, 32))
                    )
                    schedule_time = st.time_input("Time of day", datetime.now().time())
                else:  # Custom
                    schedule_datetime = st.date_input("Custom date", datetime.now() + timedelta(days=1))
                    schedule_time = st.time_input("Time", datetime.now().time())
                
                delivery_method = st.selectbox(
                    "Delivery Method",
                    ["Email", "Save to File"]
                )
                
                if delivery_method == "Email":
                    recipients = st.text_input("Recipients (comma separated emails)")
                    email_subject = st.text_input("Email Subject", f"{dashboard['name']} Report")
                
                report_format_scheduled = st.selectbox(
                    "Report Format for Scheduled Report",
                    ["Excel", "CSV", "HTML"],
                    key="schedule_format"
                )
                
                if st.button("Schedule Report"):
                    # Create schedule configuration
                    schedule_config = {
                        "name": schedule_name,
                        "dashboard_id": dashboard_id,
                        "frequency": schedule_frequency,
                        "format": report_format_scheduled,
                        "delivery": delivery_method,
                        "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    # Add frequency-specific details
                    if schedule_frequency == "Daily":
                        schedule_config["time"] = schedule_time.strftime("%H:%M")
                    elif schedule_frequency == "Weekly":
                        schedule_config["day"] = schedule_day
                        schedule_config["time"] = schedule_time.strftime("%H:%M")
                    elif schedule_frequency == "Monthly":
                        schedule_config["day"] = schedule_day
                        schedule_config["time"] = schedule_time.strftime("%H:%M")
                    else:  # Custom
                        schedule_config["datetime"] = f"{schedule_datetime.strftime('%Y-%m-%d')} {schedule_time.strftime('%H:%M')}"
                    
                    # Add delivery details
                    if delivery_method == "Email":
                        schedule_config["recipients"] = recipients.split(",")
                        schedule_config["subject"] = email_subject
                    
                    # Schedule the report (mock implementation)
                    schedule_id = ReportGenerator.schedule_report(
                        schedule_config,
                        schedule_config.get("datetime", "daily"),
                        schedule_config.get("recipients", [])
                    )
                    
                    if schedule_id:
                        st.success(f"Report scheduled successfully with ID: {schedule_id}")
                        st.rerun()

# Scheduled Reports tab
with tab2:
    st.header("Scheduled Reports")
    
    if 'scheduled_reports' not in st.session_state or not st.session_state.scheduled_reports:
        st.info("No scheduled reports. You can schedule reports from the 'Generate Reports' tab.")
    else:
        # Display all scheduled reports
        scheduled_reports = st.session_state.scheduled_reports
        st.write(f"You have {len(scheduled_reports)} scheduled reports")
        
        for report_id, report in scheduled_reports.items():
            with st.expander(f"{report['config']['name']} ({report_id[:8]}...)"):
                st.write(f"**Dashboard:** {st.session_state.dashboards[report['config']['dashboard_id']]['name']}")
                st.write(f"**Frequency:** {report['config']['frequency']}")
                st.write(f"**Format:** {report['config']['format']}")
                st.write(f"**Delivery:** {report['config']['delivery']}")
                st.write(f"**Created:** {report['created_at']}")
                st.write(f"**Status:** {report['status']}")
                
                if report['config']['delivery'] == "Email":
                    st.write(f"**Recipients:** {', '.join(report['recipients'])}")
                
                # Actions
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("Run Now", key=f"run_{report_id}"):
                        st.info("Report execution would be triggered in a production environment.")
                        st.warning("This is a demonstration - actual scheduling requires additional server configuration.")
                
                with col2:
                    if st.button("Delete", key=f"delete_{report_id}"):
                        del st.session_state.scheduled_reports[report_id]
                        st.success("Scheduled report deleted")
                        st.rerun()

# Report Templates tab
with tab3:
    st.header("Report Templates")
    
    # Create new template section
    with st.expander("Create New Template"):
        template_name = st.text_input("Template Name")
        template_description = st.text_area("Description")
        
        # Template sections
        sections = st.multiselect(
            "Sections to Include",
            ["Summary Statistics", "Data Tables", "Charts and Visualizations", "Custom Text"]
        )
        
        # Template format
        template_format = st.selectbox(
            "Default Format",
            ["Excel", "CSV", "HTML", "PDF"]
        )
        
        if st.button("Save Template"):
            if template_name:
                # Create template
                template_id = f"template_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                
                if 'report_templates' not in st.session_state:
                    st.session_state.report_templates = {}
                
                st.session_state.report_templates[template_id] = {
                    "name": template_name,
                    "description": template_description,
                    "sections": sections,
                    "format": template_format,
                    "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                st.success(f"Template '{template_name}' created successfully!")
                st.rerun()
            else:
                st.error("Please provide a template name")
    
    # Display existing templates
    if 'report_templates' not in st.session_state or not st.session_state.report_templates:
        st.info("No report templates created yet. Use the form above to create a template.")
    else:
        # Display all templates
        templates = st.session_state.report_templates
        st.write(f"You have {len(templates)} report templates")
        
        for template_id, template in templates.items():
            with st.expander(f"{template['name']} ({template_id[:8]}...)"):
                st.write(f"**Description:** {template['description']}")
                st.write(f"**Sections:** {', '.join(template['sections'])}")
                st.write(f"**Default Format:** {template['format']}")
                st.write(f"**Created:** {template['created']}")
                
                # Actions
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("Use Template", key=f"use_{template_id}"):
                        # This would redirect to the report generation with pre-filled options
                        st.session_state.active_template = template_id
                        st.rerun()
                
                with col2:
                    if st.button("Delete Template", key=f"delete_template_{template_id}"):
                        del st.session_state.report_templates[template_id]
                        st.success("Template deleted")
                        st.rerun()
