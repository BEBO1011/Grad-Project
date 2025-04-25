import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import altair as alt
import numpy as np
from datetime import datetime

class Visualizer:
    """
    Creates various visualizations from pandas DataFrames
    """
    
    @staticmethod
    def create_line_chart(df, x_col, y_cols, title="Line Chart", color_discrete_map=None):
        """
        Create a line chart using Plotly
        
        Args:
            df (pd.DataFrame): Data source
            x_col (str): Column to use for x-axis
            y_cols (list): List of columns to plot as lines
            title (str): Chart title
            color_discrete_map (dict): Mapping of columns to colors
        
        Returns:
            plotly.graph_objects.Figure: The line chart figure
        """
        try:
            # Create the figure
            fig = go.Figure()
            
            # Add each y column as a separate line
            for y_col in y_cols:
                fig.add_trace(go.Scatter(
                    x=df[x_col],
                    y=df[y_col],
                    mode='lines+markers',
                    name=y_col
                ))
            
            # Set chart title and labels
            fig.update_layout(
                title=title,
                xaxis_title=x_col,
                yaxis_title=', '.join(y_cols),
                legend_title="Variables",
                height=400
            )
            
            return fig
        except Exception as e:
            st.error(f"Error creating line chart: {str(e)}")
            return None
    
    @staticmethod
    def create_bar_chart(df, x_col, y_col, title="Bar Chart", color_col=None, orientation="v"):
        """
        Create a bar chart using Plotly
        
        Args:
            df (pd.DataFrame): Data source
            x_col (str): Column to use for x-axis
            y_col (str): Column to use for y-axis
            title (str): Chart title
            color_col (str): Column to use for coloring bars
            orientation (str): 'v' for vertical bars, 'h' for horizontal bars
        
        Returns:
            plotly.graph_objects.Figure: The bar chart figure
        """
        try:
            if orientation == "v":
                fig = px.bar(df, x=x_col, y=y_col, color=color_col, title=title)
            else:
                fig = px.bar(df, y=x_col, x=y_col, color=color_col, title=title, orientation='h')
            
            fig.update_layout(height=400)
            return fig
        except Exception as e:
            st.error(f"Error creating bar chart: {str(e)}")
            return None
    
    @staticmethod
    def create_scatter_plot(df, x_col, y_col, title="Scatter Plot", color_col=None, size_col=None):
        """
        Create a scatter plot using Plotly
        
        Args:
            df (pd.DataFrame): Data source
            x_col (str): Column to use for x-axis
            y_col (str): Column to use for y-axis
            title (str): Chart title
            color_col (str): Column to use for point colors
            size_col (str): Column to use for point sizes
        
        Returns:
            plotly.graph_objects.Figure: The scatter plot figure
        """
        try:
            fig = px.scatter(df, x=x_col, y=y_col, color=color_col, size=size_col, title=title)
            fig.update_layout(height=400)
            return fig
        except Exception as e:
            st.error(f"Error creating scatter plot: {str(e)}")
            return None
    
    @staticmethod
    def create_pie_chart(df, values_col, names_col, title="Pie Chart"):
        """
        Create a pie chart using Plotly
        
        Args:
            df (pd.DataFrame): Data source
            values_col (str): Column containing values
            names_col (str): Column containing category names
            title (str): Chart title
        
        Returns:
            plotly.graph_objects.Figure: The pie chart figure
        """
        try:
            fig = px.pie(df, values=values_col, names=names_col, title=title)
            fig.update_layout(height=400)
            return fig
        except Exception as e:
            st.error(f"Error creating pie chart: {str(e)}")
            return None
    
    @staticmethod
    def create_histogram(df, x_col, nbins=20, title="Histogram"):
        """
        Create a histogram using Plotly
        
        Args:
            df (pd.DataFrame): Data source
            x_col (str): Column to plot
            nbins (int): Number of bins
            title (str): Chart title
        
        Returns:
            plotly.graph_objects.Figure: The histogram figure
        """
        try:
            fig = px.histogram(df, x=x_col, nbins=nbins, title=title)
            fig.update_layout(height=400)
            return fig
        except Exception as e:
            st.error(f"Error creating histogram: {str(e)}")
            return None
    
    @staticmethod
    def create_heatmap(df, title="Correlation Heatmap"):
        """
        Create a correlation heatmap using Plotly
        
        Args:
            df (pd.DataFrame): Data source with numerical columns
            title (str): Chart title
        
        Returns:
            plotly.graph_objects.Figure: The heatmap figure
        """
        try:
            # Calculate correlation matrix
            corr = df.select_dtypes(include=['number']).corr()
            
            # Create heatmap
            fig = px.imshow(
                corr,
                text_auto=True,
                aspect="auto",
                color_continuous_scale="RdBu_r",
                title=title
            )
            
            fig.update_layout(height=600)
            return fig
        except Exception as e:
            st.error(f"Error creating heatmap: {str(e)}")
            return None
    
    @staticmethod
    def create_area_chart(df, x_col, y_cols, title="Area Chart"):
        """
        Create an area chart using Plotly
        
        Args:
            df (pd.DataFrame): Data source
            x_col (str): Column to use for x-axis
            y_cols (list): List of columns to plot as areas
            title (str): Chart title
        
        Returns:
            plotly.graph_objects.Figure: The area chart figure
        """
        try:
            fig = go.Figure()
            
            for y_col in y_cols:
                fig.add_trace(go.Scatter(
                    x=df[x_col],
                    y=df[y_col],
                    mode='lines',
                    name=y_col,
                    fill='tozeroy'
                ))
            
            fig.update_layout(
                title=title,
                xaxis_title=x_col,
                yaxis_title=', '.join(y_cols),
                legend_title="Variables",
                height=400
            )
            
            return fig
        except Exception as e:
            st.error(f"Error creating area chart: {str(e)}")
            return None
    
    @staticmethod
    def create_box_plot(df, x_col, y_col, title="Box Plot", color_col=None):
        """
        Create a box plot using Plotly
        
        Args:
            df (pd.DataFrame): Data source
            x_col (str): Column to use for x-axis categories
            y_col (str): Column to use for y-axis values
            title (str): Chart title
            color_col (str): Column to use for box colors
        
        Returns:
            plotly.graph_objects.Figure: The box plot figure
        """
        try:
            fig = px.box(df, x=x_col, y=y_col, color=color_col, title=title)
            fig.update_layout(height=400)
            return fig
        except Exception as e:
            st.error(f"Error creating box plot: {str(e)}")
            return None
    
    @staticmethod
    def create_altair_chart(df, chart_type, x_col, y_col, color_col=None, title="Altair Chart"):
        """
        Create a chart using Altair
        
        Args:
            df (pd.DataFrame): Data source
            chart_type (str): Type of chart ('bar', 'line', 'point', 'area', etc.)
            x_col (str): Column to use for x-axis
            y_col (str): Column to use for y-axis
            color_col (str): Column to use for colors
            title (str): Chart title
        
        Returns:
            altair.Chart: The Altair chart object
        """
        try:
            # Base chart
            base = alt.Chart(df).encode(
                x=alt.X(x_col),
                y=alt.Y(y_col),
                color=alt.Color(color_col) if color_col else alt.value('steelblue')
            ).properties(
                title=title,
                width='container',
                height=400
            )
            
            # Apply chart type
            if chart_type == 'bar':
                chart = base.mark_bar()
            elif chart_type == 'line':
                chart = base.mark_line()
            elif chart_type == 'point':
                chart = base.mark_point()
            elif chart_type == 'area':
                chart = base.mark_area()
            elif chart_type == 'circle':
                chart = base.mark_circle()
            elif chart_type == 'tick':
                chart = base.mark_tick()
            else:
                chart = base.mark_line()  # Default to line
                
            return chart
        except Exception as e:
            st.error(f"Error creating Altair chart: {str(e)}")
            return None
    
    @staticmethod
    def create_table(df, title="Data Table"):
        """
        Create an interactive table using Streamlit
        
        Args:
            df (pd.DataFrame): Data source
            title (str): Table title
        
        Returns:
            None (directly renders in Streamlit)
        """
        try:
            st.subheader(title)
            st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"Error creating table: {str(e)}")
