import streamlit as st
import os

# Configure page
st.set_page_config(
    page_title="Car Service & Analytics Platform",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a luxury look and feel
st.markdown("""
<style>
    /* Gold accent color for luxury feel */
    :root {
        --primary-color: #d4af37;
        --secondary-bg: #f8f9fa;
        --dark-text: #14151a;
    }
    
    /* Title and headers styling */
    h1, h2, h3 {
        color: var(--dark-text);
        font-family: 'Playfair Display', serif;
        font-weight: 600;
    }
    
    /* Gold accents */
    .gold-accent {
        color: var(--primary-color);
        font-weight: 600;
    }
    
    /* Cards for features */
    .feature-card {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    
    /* Button styling */
    .css-1x8cf1d {
        background-color: var(--primary-color);
        color: white;
        font-weight: 600;
    }
    
    /* Sidebar styling */
    .css-1lcbmhc {
        background-color: #14151a;
    }
    
    .css-1lcbmhc .css-10trblm {
        color: white;
    }
    
    .css-1lcbmhc .css-16idsys p {
        color: rgba(255, 255, 255, 0.8);
    }
    
    /* Link styling */
    a {
        color: var(--primary-color);
        text-decoration: none;
        font-weight: 500;
    }
    
    a:hover {
        text-decoration: underline;
    }
    
    /* Custom button styling */
    .custom-button {
        display: inline-block;
        background-color: var(--primary-color);
        color: white;
        padding: 10px 20px;
        text-align: center;
        border-radius: 8px;
        text-decoration: none;
        font-weight: 600;
        margin-top: 10px;
        transition: all 0.3s ease;
    }
    
    .custom-button:hover {
        background-color: #c09c2c;
        text-decoration: none;
    }
    
    /* Two-column container */
    .two-column {
        display: flex;
        gap: 20px;
    }
    
    .column {
        flex: 1;
    }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .two-column {
            flex-direction: column;
        }
    }
</style>
""", unsafe_allow_html=True)

# Create a two-column layout
col1, col2 = st.columns([2, 1])

with col1:
    st.title("Car Service Diagnostic Platform")
    st.markdown("""
    <p style='font-size: 1.2em;'>
    An advanced dual-application platform combining <span class='gold-accent'>AI-powered car diagnostics</span> with 
    <span class='gold-accent'>sophisticated data analytics</span> capabilities.
    </p>
    """, unsafe_allow_html=True)
    
    # Main app description
    st.markdown("""
    ## Dual Platform Structure
    This platform consists of two integrated applications:
    
    ### 1. Car Service Application (Port 8080)
    A mobile-optimized application providing:
    - AI-powered car diagnostics with realistic solutions
    - Maintenance center finder with interactive maps
    - Roadside assistance service
    - Appointment scheduling system
    
    ### 2. Data Analytics Dashboard (Port 5000)
    A Streamlit-powered dashboard for:
    - Custom report generation
    - Data visualization tools
    - Integration with various data sources
    - Advanced analytics capabilities
    """)

# Direct access buttons for both applications
st.markdown("""
<div class='two-column'>
    <div class='column feature-card'>
        <h3>🚗 Car Service App</h3>
        <p>Mobile-optimized car diagnostic app with AI-powered solutions</p>
        <a href='http://0.0.0.0:8080' class='custom-button'>Launch Car Service App</a>
        <br><br>
        <p><strong>Direct access to key features:</strong></p>
        <ul>
            <li><a href='http://0.0.0.0:8080/chatbot'>AI Diagnostic Chatbot</a></li>
            <li><a href='http://0.0.0.0:8080/maintenance-centers'>Maintenance Centers</a></li>
            <li><a href='http://0.0.0.0:8080/map'>Interactive Map</a></li>
        </ul>
    </div>
    
    <div class='column feature-card'>
        <h3>📊 Data Analytics Dashboard</h3>
        <p>Powerful analysis tools for creating custom reports and visualizations</p>
        <a href='http://0.0.0.0:5000' class='custom-button'>Access Analytics Dashboard</a>
        <br><br>
        <p><strong>Analytics features:</strong></p>
        <ul>
            <li><a href='http://0.0.0.0:5000/Data_Sources'>Data Source Management</a></li>
            <li><a href='http://0.0.0.0:5000/Dashboard_Builder'>Dashboard Builder</a></li>
            <li><a href='http://0.0.0.0:5000/Reports'>Report Generation</a></li>
        </ul>
    </div>
</div>
""", unsafe_allow_html=True)

# Key Features Section
st.header("Key Platform Features")

# Create two columns for the features
feature_col1, feature_col2 = st.columns(2)

with feature_col1:
    st.markdown("""
    <div class="feature-card">
        <h3>🤖 AI Diagnostic Chatbot</h3>
        <ul>
            <li><strong>Natural Language Understanding</strong>: Describe problems in everyday language</li>
            <li><strong>Multi-language Support</strong>: Works in both English and Arabic</li>
            <li><strong>41+ Car Brands</strong>: Support for all major vehicle manufacturers</li>
            <li><strong>Model-Specific Solutions</strong>: Tailored to your exact vehicle</li>
            <li><strong>Severity Indicators</strong>: Visual indicators of problem urgency</li>
            <li><strong>Cost Estimates</strong>: Approximate repair costs for budgeting</li>
            <li><strong>DIY vs Professional</strong>: Clear guidance on what you can fix yourself</li>
            <li><strong>Tools & Parts Lists</strong>: What you need for DIY repairs</li>
            <li><strong>Time Estimates</strong>: Expected repair duration</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with feature_col2:
    st.markdown("""
    <div class="feature-card">
        <h3>📊 Data Analytics Tools</h3>
        <ul>
            <li><strong>Multiple Data Sources</strong>: Connect to databases, APIs, CSVs</li>
            <li><strong>Custom Dashboards</strong>: Build interactive visualizations</li>
            <li><strong>Reports</strong>: Generate and schedule exportable reports</li>
            <li><strong>Data Transformation</strong>: Clean and prepare your data</li>
            <li><strong>API Documentation</strong>: Access data programmatically</li>
            <li><strong>Real-time Updates</strong>: Live data refreshing</li>
            <li><strong>User Management</strong>: Control access to dashboards</li>
            <li><strong>Export Functionality</strong>: Download as Excel, CSV, or PDF</li>
            <li><strong>Responsive Design</strong>: Works on all devices</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Example section
st.header("Example Diagnostic Queries")

# Create columns for examples
example_col1, example_col2 = st.columns(2)

with example_col1:
    st.subheader("Luxury Vehicles")
    example_problems_luxury = [
        "BMW 3 Series making grinding noise when braking",
        "Mercedes-Benz E-Class check engine light keeps coming on",
        "Audi A4 air conditioning not cooling properly",
        "Tesla Model 3 battery draining too quickly",
        "Porsche 911 strange noise during acceleration"
    ]
    
    for problem in example_problems_luxury:
        st.markdown(f"- *{problem}*")

with example_col2:
    st.subheader("Common Vehicles")
    example_problems_common = [
        "Toyota Corolla won't start in cold weather",
        "Honda Civic pulling to the left when driving",
        "Ford F-150 rough idle and stalling",
        "Volkswagen Golf transmission slipping when shifting",
        "Hyundai Tucson air bag warning light on dashboard"
    ]
    
    for problem in example_problems_common:
        st.markdown(f"- *{problem}*")

# Mobile optimization
st.header("Mobile-First Design Philosophy")
st.markdown("""
<div class="feature-card">
    <p>Both applications in this platform are fully optimized for mobile devices with:</p>
    <div class="two-column">
        <div class="column">
            <ul>
                <li><strong>Responsive layouts</strong> that adjust to any screen size</li>
                <li><strong>Touch-friendly interface</strong> with appropriately sized elements</li>
                <li><strong>Fast loading times</strong> optimized for mobile connections</li>
                <li><strong>Offline capabilities</strong> for basic functionality</li>
            </ul>
        </div>
        <div class="column">
            <ul>
                <li><strong>Progressive loading</strong> to prioritize critical content</li>
                <li><strong>Dark theme options</strong> for battery conservation</li>
                <li><strong>Reduced data usage</strong> through optimized assets</li>
                <li><strong>Location-aware features</strong> for maintenance centers</li>
            </ul>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Platform Screenshots
st.header("Platform Screenshots")

st.markdown("""
<div class="feature-card">
    <div class="two-column">
        <div class="column">
            <h3>Car Service App</h3>
            <p>The mobile-optimized car service application featuring the AI diagnostic chatbot with enhanced results displaying severity indicators, cost estimates, and DIY badges.</p>
        </div>
        <div class="column">
            <h3>Analytics Dashboard</h3>
            <p>The Streamlit-powered data analytics platform allowing users to create custom visualizations, reports, and dashboards from multiple data sources.</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Placeholder for actual screenshots once they're available
screenshot_col1, screenshot_col2 = st.columns(2)

with screenshot_col1:
    st.image("https://placehold.co/600x400?text=Car+Diagnostic+App", caption="Car Service & Diagnostic App")

with screenshot_col2:
    st.image("https://placehold.co/600x400?text=Analytics+Dashboard", caption="Data Analytics Dashboard")

st.sidebar.title("Navigation")

# Streamlit Data Analytics Navigation
st.sidebar.markdown("### Analytics Platform (Port 5000)")
st.sidebar.markdown("""
- [Analytics Home](/)
- [Data Sources](/Data_Sources)
- [Dashboard Builder](/Dashboard_Builder)
- [Reports](/Reports)
- [Data Transformation](/Data_Transformation)
- [API Documentation](/API_Documentation)
""")

# Car Service App Navigation
st.sidebar.markdown("### Car Service App (Port 8080)")
st.sidebar.markdown("""
- [Car App Home](http://0.0.0.0:8080)
- [Diagnostic Chatbot](http://0.0.0.0:8080/chatbot)
- [Maintenance Centers](http://0.0.0.0:8080/maintenance-centers)
- [Interactive Map](http://0.0.0.0:8080/map)
- [User Settings](http://0.0.0.0:8080/settings)
""")

# About section
st.sidebar.markdown("---")
st.sidebar.header("About the Platform")
st.sidebar.info("""
This dual-platform system combines a powerful data analytics dashboard with a user-friendly mobile car diagnostic application.

The analytics dashboard (port 5000) enables creating custom reports and visualizations, while the car service app (port 8080) provides AI-powered diagnostic solutions and maintenance services.

Both applications operate independently but can share data for integrated operations.
""")