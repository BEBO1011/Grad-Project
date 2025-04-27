import os
import sys

# Import Flask app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app import app

if __name__ == "__main__":
    # Force the app to use port 5000
    app.run(host="0.0.0.0", port=5000, debug=True)