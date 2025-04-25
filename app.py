import os
import streamlit as st
from flask import Flask, render_template, redirect, url_for
import subprocess
import sys

st.title("Car Service Application")

st.markdown("""
## Car Service and Diagnostic Tool

This application provides a mobile-friendly interface for:
- Diagnosing car problems with AI-powered chatbot
- Finding nearby maintenance centers
- Getting roadside assistance
- Scheduling maintenance appointments

### Instructions:
1. The Flask server is running in the background
2. Access the application directly through the URL below
""")

# Display URL for the Flask application
st.info("Open car service application at: [http://0.0.0.0:5000](http://0.0.0.0:5000)")

# Check if the Flask server is running
flask_process = None

if "flask_running" not in st.session_state:
    st.session_state.flask_running = False

if not st.session_state.flask_running:
    try:
        # Run the Flask application as a background process
        flask_cmd = [sys.executable, "car_service/app.py"]
        flask_process = subprocess.Popen(flask_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        st.session_state.flask_running = True
        st.success("Flask server started successfully!")
    except Exception as e:
        st.error(f"Error starting Flask server: {e}")
else:
    st.success("Flask server is running!")

# Display information about the chatbot feature
st.header("Chatbot Diagnostic Feature")
st.write("""
The chatbot diagnostic feature allows users to:
- Describe their car problem in natural language
- Specify their car's make and model
- Receive expert diagnostic suggestions and solutions
- Get maintenance center recommendations based on the diagnosis
""")

# Button to open the chatbot directly
if st.button("Open Chatbot Directly"):
    js = f"window.open('http://0.0.0.0:5000/chatbot', '_blank');"
    st.markdown(f'<script>{js}</script>', unsafe_allow_html=True)
    st.write("Attempting to open the chatbot in a new tab. If it doesn't open automatically, click here: [Chatbot](http://0.0.0.0:5000/chatbot)")