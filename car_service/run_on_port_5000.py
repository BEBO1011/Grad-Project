import sys
import os

# Import the Flask app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app import app

if __name__ == "__main__":
    # Run the Flask app on port 3000 for testing with Replit's feedback tool
    app.run(host="0.0.0.0", port=3000, debug=True)