from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import os
import json
import re
import spacy
from deep_translator import GoogleTranslator
from argon2 import PasswordHasher

# Initialize Flask app
app = Flask(__name__, 
            static_url_path='/static', 
            static_folder='static',
            template_folder='templates')
CORS(app)
    
# Initialize the security Hasher
ph = PasswordHasher()

# Load English NLP model
try:
    nlp = spacy.load("en_core_web_sm")
except:
    print("Please install the spaCy model with: python -m spacy download en_core_web_sm")
    nlp = None

# Placeholder for database (for demo purposes)
car_issues_db = [
    {
        "brand": "Toyota", 
        "model": "Corolla",
        "problem_en": "Engine not starting",
        "solution_en": "Check battery connections. If the battery is good, the issue could be the starter motor or ignition switch.",
        "keywords": "engine, start, battery, power, ignition"
    },
    {
        "brand": "Toyota", 
        "model": "Corolla",
        "problem_en": "Brakes squeaking",
        "solution_en": "Likely worn brake pads. Have them inspected and replaced if needed. Could also be moisture or dust build-up.",
        "keywords": "brakes, squeaking, noise, stopping, brake pads"
    },
    {
        "brand": "Toyota", 
        "model": "Camry",
        "problem_en": "AC not cooling properly",
        "solution_en": "Check refrigerant levels. Could also be a clogged filter or a malfunctioning compressor.",
        "keywords": "ac, cooling, air conditioning, hot, temperature"
    },
    {
        "brand": "Mercedes", 
        "model": "C-Class",
        "problem_en": "Check engine light on",
        "solution_en": "Use an OBD scanner to read error codes. Common issues include oxygen sensor, loose gas cap, or catalytic converter problems.",
        "keywords": "check engine, light, warning, dashboard, OBD"
    },
    {
        "brand": "Fiat", 
        "model": "500",
        "problem_en": "Car stalling while driving",
        "solution_en": "Could be a fuel pump issue, clogged fuel filter, or faulty ignition coil. Have the vehicle diagnosed by a specialist.",
        "keywords": "stalling, stops, dies, running, fuel"
    },
    {
        "brand": "Audi", 
        "model": "A4",
        "problem_en": "Strange vibration at high speeds",
        "solution_en": "Likely wheel balance issue or worn suspension components. Could also be damaged tires or alignment problems.",
        "keywords": "vibration, shake, steering, wheel, balance"
    }
]

# Placeholder for maintenance centers
maintenance_centers = [
    {"id": 1, "name": "AutoFix Garage", "latitude": 30.0444, "longitude": 31.2357, "rating": 4.8},
    {"id": 2, "name": "Elite Motors", "latitude": 30.0258, "longitude": 31.2123, "rating": 4.6},
    {"id": 3, "name": "Speedy Repairs", "latitude": 30.0495, "longitude": 31.2415, "rating": 4.5}
]

# User database (placeholder)
users = []

# General car issues and questions
general_issues = {
    "car not starting": "Is the issue related to the battery, starter motor, or ignition?",
    "strange noise": "Where is the noise coming from? Engine, brakes, or tires?",
    "brakes issue": "Are the brakes making a noise, feeling weak, or completely failing?",
    "engine problem": "Is the engine misfiring, overheating, or consuming too much oil?",
    "AC problem": "Is the AC blowing hot air, making noise, or not turning on?",
    "السيارة لا تعمل": "هل المشكلة متعلقة بالبطارية، أو محرك التشغيل، أو الإشعال؟",
    "صوت غريب": "من اين الصوت بالتحديد ؟ المحرك , الفرامل ام الاطارات ؟",
    "مشكلة في الفرامل": "هل الفرامل تصدر صوتًا، أو تشعر بالضعف، أو تتعطل تمامًا؟",
    "مشكلة في المحرك": "هل المحرك لا يعمل بشكل صحيح، أو يسخن بشكل زائد، أو يستهلك كمية كبيرة من الزيت؟",
    "مشكله في مكيف الهواء": "هل ينفث مكيف الهواء هواءً ساخنًا، أو يصدر ضوضاء، أو لا يعمل؟"
}

# Translation function
def translate_text(text, target_lang="en"):
    """Translate text to the target language, detecting Arabic input automatically."""
    try:
        if isinstance(text, bytes):
            text = text.decode("utf-8")

        source_lang = "ar" if any("\u0600" <= char <= "\u06FF" for char in text) else "auto"
        return GoogleTranslator(source=source_lang, target=target_lang).translate(text)
    except Exception as e:
        print(f"Translation Error: {e}")
        return text  # Return original text if translation fails

# Extract keywords from text
def extract_keywords(text):
    if not nlp:
        return text.split()
    
    doc = nlp(text)
    keywords = [token.text.lower() for token in doc if token.pos_ in ["NOUN", "VERB", "ADJ"]]
    return keywords if keywords else text.split()

# Password strength check
def is_strong_password(password):
    """Check if the password meets strength requirements."""
    if len(password) < 8:
        return "Password must be at least 8 characters long."
    if not re.search(r"\d", password):  # Check for a number
        return "Password must contain at least one number."
    if not re.search(r"[!@#$%^&*]", password):  # Check for a special character
        return "Password must contain at least one special character (!@#$%^&*)."
    return None  # Password is valid

# Routes for serving HTML pages
@app.route('/')
def index():
    return send_from_directory('templates', 'index.html')

@app.route('/home')
def home():
    return send_from_directory('templates', 'home.html')

@app.route('/map')
def map_page():
    return send_from_directory('templates', 'map.html')

@app.route('/maintenance-centers')
def maintenance_centers_page():
    return send_from_directory('templates', 'maintenance-centers.html')

@app.route('/chatbot')
def chatbot_page():
    return send_from_directory('templates', 'chatbot.html')

@app.route('/settings')
def settings_page():
    return send_from_directory('templates', 'settings.html')

@app.route('/signup')
def signup_page():
    return send_from_directory('templates', 'signup.html')

@app.route('/center-details')
def center_details_page():
    return send_from_directory('templates', 'center-details.html')

# API Endpoints
@app.route("/api/maintenance-centers", methods=["GET"])
def get_maintenance_centers_api():
    return jsonify(maintenance_centers)

@app.route("/nearest-owner", methods=["GET"])
def get_nearest_owner():
    try:
        user_lat = float(request.args.get("lat"))
        user_lon = float(request.args.get("lon"))

        # Placeholder response
        owner = {
            "name": "Ahmed's Towing Service",
            "phone": "+201112218026",
            "latitude": user_lat + 0.01,  # Just offset a bit from user location
            "longitude": user_lon - 0.01,
            "distance_km": 2.5
        }

        return jsonify(owner)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/nearest-maintenance-center", methods=["GET"])
def get_nearest_center():
    try:
        user_lat = float(request.args.get("lat"))
        user_lon = float(request.args.get("lon"))

        # Just return the first center for demo purposes
        center = maintenance_centers[0]
        center["distance_km"] = 3.2  # Demo distance
        
        return jsonify(center)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/signup", methods=["POST"])
def signup():
    try:
        data = request.json
        email = data.get("email")
        name = data.get("name")
        password = data.get("password")
        car_brand = data.get("car_brand")
        car_model = data.get("car_model")
        manufacturing_year = data.get("manufacturing_year")

        if not email or not name or not password or not car_brand or not car_model or not manufacturing_year:
            return jsonify({"error": "All fields are required"}), 400
        
        # Check password strength
        password_error = is_strong_password(password)
        if password_error:
            return jsonify({"error": password_error}), 400
        
        # Hash the password with Argon2
        hashed_password = ph.hash(password)

        # Create a new user (in a real app, would save to database)
        new_user = {
            "id": len(users) + 1,
            "email": email,
            "name": name,
            "password": hashed_password,
            "car_brand": car_brand,
            "car_model": car_model,
            "manufacturing_year": manufacturing_year
        }
        users.append(new_user)

        return jsonify({"message": "User registered successfully", "success": True}), 201

    except Exception as e:
        print(f"Error in signup: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/signin", methods=["POST"])
def signin():
    try:
        data = request.json
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        # Find user by email
        user = next((u for u in users if u["email"] == email), None)

        if user:
            try:
                # Verify the password using Argon2
                ph.verify(user["password"], password)
                return jsonify({
                    "message": "Login successful", 
                    "user_id": user["id"], 
                    "name": user["name"]
                }), 200
            except:
                return jsonify({"error": "Invalid email or password"}), 401
        else:
            # For demo, allow any login with correct format
            if "@" in email and len(password) >= 8:
                return jsonify({
                    "message": "Login successful", 
                    "user_id": 999, 
                    "name": "Demo User"
                }), 200
            else:
                return jsonify({"error": "Invalid email or password"}), 401
        
    except Exception as e:
        print("Error in /signin:", str(e))
        return jsonify({"error": str(e)}), 500

@app.route("/search", methods=["POST"])
def search():
    try:
        data = request.json
        query_text = data.get("query", "")
        brand_filter = data.get("brand", "").lower()
        model_filter = data.get("model", "").lower()

        if not query_text:
            return jsonify({"error": "Query is required"}), 400

        # Check for general issues first
        for key, question in general_issues.items():
            if key in query_text.lower():
                response = {
                    "message": "I need more details to provide a solution, احتاج المزيد من التفاصيل لمساعدك.",
                    "follow_up_question": question
                }
                return jsonify(response)

        # Translate if query is in Arabic
        translated_query = translate_text(query_text, "en")
        query_language = "ar" if query_text != translated_query else "en"

        # Extract keywords from translated query
        extracted_keywords = extract_keywords(translated_query)
        refined_query = " ".join(extracted_keywords)

        # Search for car issues
        search_results = []
        for issue in car_issues_db:
            if brand_filter and brand_filter != issue["brand"].lower():
                continue
            if model_filter and model_filter != issue["model"].lower():
                continue
                
            # Check keyword matches
            issue_keywords = issue["keywords"].lower().split(", ")
            matches = [kw for kw in extracted_keywords if kw in issue_keywords or any(kw in ik for ik in issue_keywords)]
            
            if matches:
                problem = issue["problem_en"]
                solution = issue["solution_en"]
                
                # Translate if query was in Arabic
                if query_language == "ar":
                    if problem:
                        problem = translate_text(problem, "ar")
                    if solution:
                        solution = translate_text(solution, "ar")
                
                search_results.append({
                    "brand": issue["brand"],
                    "model": issue["model"],
                    "problem": problem,
                    "solution": solution
                })
        
        if not search_results:
            return jsonify({
                "message": "No relevant issues found. Try rephrasing your query or providing more details."
            }), 200

        return jsonify({"results": search_results})
    
    except Exception as e:
        print("Error in /search:", str(e))
        return jsonify({"error": str(e)}), 500

# Run the Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)