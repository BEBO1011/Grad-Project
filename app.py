import streamlit as st

st.title("Car Service Diagnostic App")

st.markdown("""
## Car Service and Diagnostic Tool

This application provides a mobile-friendly interface for:
- Diagnosing car problems with AI-powered chatbot
- Finding nearby maintenance centers
- Getting roadside assistance
- Scheduling maintenance appointments

### Instructions:
1. Open the application in your mobile browser
2. Use the chatbot to diagnose car problems
3. Get personalized solutions based on your car's make and model
""")

# Display URLs for the Car Service app and chatbot
st.info("### App URL: [http://0.0.0.0:8080](http://0.0.0.0:8080)")
st.success("### Chatbot URL: [http://0.0.0.0:8080/chatbot](http://0.0.0.0:8080/chatbot)")

# Display chatbot features
st.header("Chatbot Features")
st.markdown("""
- **Natural Language Understanding**: Describe your car problem in everyday language
- **Multi-language Support**: Works in both English and Arabic
- **Make/Model Specific**: Get solutions tailored to your specific vehicle
- **Follow-up Questions**: The chatbot will ask for additional details when needed
""")

# Car problem examples
st.header("Example Problems to Ask:")
example_problems = [
    "My Toyota Corolla won't start in the morning",
    "The brakes on my Mercedes are making a squeaking noise",
    "My Audi A4 air conditioning is not cooling properly",
    "Check engine light is on in my Fiat 500",
    "My car is pulling to one side when driving"
]

for problem in example_problems:
    st.markdown(f"- *{problem}*")

# Mobile optimization information
st.header("Mobile Optimization")
st.markdown("""
This application is fully optimized for mobile devices:
- Responsive layout that adjusts to screen size
- Touch-friendly interface elements
- Fast loading times for mobile data connections
- Works on iOS and Android browsers
""")

# Display screenshots
st.header("Screenshots")
st.image("https://placehold.co/600x400?text=Car+Service+App+Screenshot", caption="Car Service App on Mobile")

st.sidebar.title("Navigation")
st.sidebar.markdown("""
- [Home](/)
- [Chatbot](http://0.0.0.0:8080/chatbot)
- [Maintenance Centers](http://0.0.0.0:8080/maintenance-centers)
- [Map](http://0.0.0.0:8080/map)
- [Settings](http://0.0.0.0:8080/settings)
""")

st.sidebar.header("About")
st.sidebar.info("""
This application helps diagnose car problems and provides solutions. It's designed to work well on mobile devices for on-the-go troubleshooting.
""")