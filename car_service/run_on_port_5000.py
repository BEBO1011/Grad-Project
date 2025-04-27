import sys
import os

# Import the Flask app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app import app

if __name__ == "__main__":
    # Run the Flask app on port 5000 for testing with Replit's feedback tool
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)