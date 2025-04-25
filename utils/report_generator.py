import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import io
import os
import base64
from datetime import datetime
import json

class ReportGenerator:
    """
    Generates reports from dashboards and visualizations
    """
    
    @staticmethod
    def generate_excel_report(data_dict, filename="report.xlsx"):
        """
        Generate Excel report from multiple DataFrames
        
        Args:
            data_dict (dict): Dictionary mapping sheet names to DataFrames
            filename (str): Name of the Excel file
            
        Returns:
            bytes: Excel file as bytes
        """
        try:
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                for sheet_name, df in data_dict.items():
                    if isinstance(df, pd.DataFrame):
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
                    
                    # Add some formatting
                    workbook = writer.book
                    worksheet = writer.sheets[sheet_name]
                    
                    # Add a header format
                    header_format = workbook.add_format({
                        'bold': True,
                        'text_wrap': True,
                        'valign': 'top',
                        'fg_color': '#D7E4BC',
                        'border': 1
                    })
                    
                    # Write the column headers with the defined format
                    for col_num, value in enumerate(df.columns.values):
                        worksheet.write(0, col_num, value, header_format)
            
            output.seek(0)
            return output.getvalue()
        except Exception as e:
            st.error(f"Error generating Excel report: {str(e)}")
            return None
    
    @staticmethod
    def generate_csv_report(df, filename="report.csv"):
        """
        Generate CSV report from DataFrame
        
        Args:
            df (pd.DataFrame): Data to export
            filename (str): Name of the CSV file
            
        Returns:
            bytes: CSV file as bytes
        """
        try:
            output = io.StringIO()
            df.to_csv(output, index=False)
            return output.getvalue()
        except Exception as e:
            st.error(f"Error generating CSV report: {str(e)}")
            return None
    
    @staticmethod
    def create_report_summary(dashboard_components, df_dict):
        """
        Create a summary report of dashboard components
        
        Args:
            dashboard_components (list): List of dashboard component configurations
            df_dict (dict): Dictionary mapping data source IDs to DataFrames
            
        Returns:
            str: HTML summary report
        """
        try:
            html_output = f"""
            <html>
            <head>
                <title>Dashboard Report</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    h1 {{ color: #2C3E50; }}
                    h2 {{ color: #3498DB; margin-top: 30px; }}
                    table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; }}
                    th {{ background-color: #f2f2f2; text-align: left; }}
                    .summary {{ background-color: #f9f9f9; padding: 15px; border-radius: 5px; }}
                </style>
            </head>
            <body>
                <h1>Dashboard Report</h1>
                <div class="summary">
                    <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p>Number of components: {len(dashboard_components)}</p>
                </div>
            """
            
            # Add component details
            for i, component in enumerate(dashboard_components):
                html_output += f"""
                <h2>Component {i+1}: {component.get('title', 'Untitled')}</h2>
                <table>
                    <tr>
                        <th>Type</th>
                        <td>{component.get('chart_type', 'Unknown')}</td>
                    </tr>
                    <tr>
                        <th>Data Source</th>
                        <td>{component.get('data_source_id', 'Unknown')}</td>
                    </tr>
                """
                
                # Add component-specific config
                for key, value in component.items():
                    if key not in ['title', 'chart_type', 'data_source_id']:
                        html_output += f"""
                        <tr>
                            <th>{key}</th>
                            <td>{value}</td>
                        </tr>
                        """
                
                html_output += "</table>"
                
                # If this is a tabular component, add data preview
                if component.get('chart_type') == 'table' and component.get('data_source_id') in df_dict:
                    df = df_dict[component.get('data_source_id')]
                    html_output += f"""
                    <h3>Data Preview (top 5 rows)</h3>
                    {df.head(5).to_html(index=False)}
                    """
            
            html_output += """
            </body>
            </html>
            """
            
            return html_output
        except Exception as e:
            st.error(f"Error creating report summary: {str(e)}")
            return "<html><body><h1>Error generating report</h1></body></html>"
    
    @staticmethod
    def get_download_link(data, filename, text="Download File"):
        """
        Generate a download link for a file
        
        Args:
            data: File data (bytes or string)
            filename (str): Name of the file
            text (str): Link text
            
        Returns:
            str: HTML link
        """
        try:
            if isinstance(data, str):
                data = data.encode()
                
            b64 = base64.b64encode(data).decode()
            href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
            return href
        except Exception as e:
            st.error(f"Error creating download link: {str(e)}")
            return ""
    
    @staticmethod
    def schedule_report(report_config, schedule_time, recipient_emails=None):
        """
        Schedule a report for generation (mock implementation)
        
        Args:
            report_config (dict): Report configuration
            schedule_time (str): When to generate the report
            recipient_emails (list): List of email recipients
            
        Returns:
            str: Schedule ID
        """
        try:
            schedule_id = f"schedule_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # In a real implementation, this would add the schedule to a database
            # and set up a task scheduler. For this demo, we'll just store it in session state.
            schedule = {
                'id': schedule_id,
                'config': report_config,
                'schedule_time': schedule_time,
                'recipients': recipient_emails,
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'status': 'scheduled'
            }
            
            if 'scheduled_reports' not in st.session_state:
                st.session_state.scheduled_reports = {}
                
            st.session_state.scheduled_reports[schedule_id] = schedule
            
            return schedule_id
        except Exception as e:
            st.error(f"Error scheduling report: {str(e)}")
            return None
    
    @staticmethod
    def export_dashboard_config(dashboard_id, dashboard_data):
        """
        Export dashboard configuration to JSON
        
        Args:
            dashboard_id (str): Dashboard ID
            dashboard_data (dict): Dashboard configuration
            
        Returns:
            str: JSON string
        """
        try:
            config = {
                'id': dashboard_id,
                'config': dashboard_data,
                'exported_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            return json.dumps(config, indent=2)
        except Exception as e:
            st.error(f"Error exporting dashboard configuration: {str(e)}")
            return "{}"
