import os
import streamlit as st
import threading
import time
import subprocess
import sys

def start_flask_app():
    """Start the Flask car service app in a separate process"""
    try:
        flask_cmd = [sys.executable, "car_service/app.py"]
        flask_process = subprocess.Popen(flask_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Flask server started with PID:", flask_process.pid)
        return flask_process
    except Exception as e:
        print(f"Error starting Flask server: {e}")
        return None

# Main Streamlit UI
st.title("Car Service Dashboard")

st.markdown("""
## Car Service and Diagnostic Tool

This application provides a mobile-friendly interface for:
- Diagnosing car problems with an AI-powered chatbot
- Finding nearby maintenance centers
- Getting roadside assistance
- Scheduling maintenance appointments
""")

# Display URL for the Flask application
st.info("Open the car service app at: [http://0.0.0.0:8080](http://0.0.0.0:8080)")
st.info("Access the chatbot directly at: [http://0.0.0.0:8080/chatbot](http://0.0.0.0:8080/chatbot)")

# Start the Flask app on page load
if "flask_started" not in st.session_state:
    st.session_state.flask_started = False
    st.session_state.flask_process = None

if not st.session_state.flask_started:
    flask_process = start_flask_app()
    if flask_process:
        st.session_state.flask_process = flask_process
        st.session_state.flask_started = True
        st.success("✅ Flask server for car service started successfully")
    else:
        st.error("❌ Failed to start Flask server")
else:
    st.success("✅ Flask server is already running")

# Information about the chatbot
st.header("Chatbot Diagnostic Feature")
st.write("""
The car diagnostic chatbot can help you:
- Identify car problems based on symptoms
- Get solutions for common car issues
- Find the nearest maintenance center
- Schedule repairs
""")

# Explanation of mobile access
st.header("Mobile Access")
st.write("""
This application is fully responsive and works on mobile devices:
1. Open the app URL on your phone's browser
2. Browse maintenance centers or use the chatbot 
3. Get instant solutions for car problems
""")

# Add some sample car issue information
st.header("Common Car Issues")
with st.expander("Engine Problems"):
    st.write("""
    - **Car not starting**: Often related to battery, starter motor, or ignition switch issues
    - **Check engine light**: Can indicate sensor problems, emissions issues, or engine misfires
    - **Engine overheating**: Usually caused by coolant leaks, radiator problems, or thermostat failure
    """)

with st.expander("Brake Issues"):
    st.write("""
    - **Squeaking brakes**: Typically worn brake pads that need replacement
    - **Soft brake pedal**: Could indicate air in the brake lines or fluid leaks
    - **Vibration when braking**: Often caused by warped rotors or caliper problems
    """)

with st.expander("Electrical Issues"):
    st.write("""
    - **Battery draining**: Can be caused by alternator problems or parasitic draws
    - **Flickering lights**: Often related to alternator or voltage regulator issues
    - **Power window failure**: Usually due to faulty switches or motors
    """)

if __name__ == "__main__":
    # This will be run by the Streamlit server
    print("Car Service App started!")