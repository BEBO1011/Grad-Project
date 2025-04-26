from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_cors import CORS
import os
import json
import re
import secrets
from argon2 import PasswordHasher
import geopy.distance
from datetime import datetime, timedelta

# Initialize Flask app
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Secure session key
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
CORS(app)

# Initialize security hasher
ph = PasswordHasher()

# Sample car issue data for the chatbot
car_issues = [
    {
        "brand": "Toyota",
        "model": "Corolla",
        "problem_en": "Car not starting",
        "solution_en": "Check the battery connections. If corroded, clean them. If battery is old (3+ years), consider replacing it. Also check the starter motor for proper function.",
        "keywords": "start, starting, battery, dead, crank, ignition, won't start"
    },
    {
        "brand": "Toyota",
        "model": "Camry",
        "problem_en": "Engine overheating",
        "solution_en": "Check coolant level and fill if low. Inspect for leaks in the cooling system. Ensure the radiator fan is working properly. Consider flushing the cooling system if it hasn't been done recently.",
        "keywords": "hot, overheat, temperature, cooling, radiator, steam"
    },
    {
        "brand": "Mercedes",
        "model": "C-Class",
        "problem_en": "Warning lights on dashboard",
        "solution_en": "Use an OBD-II scanner to read the error codes. Most common issues include oxygen sensor failures, loose gas cap, or catalytic converter problems.",
        "keywords": "warning, light, dashboard, check engine, indicator, diagnostic"
    },
    {
        "brand": "Fiat",
        "model": "500",
        "problem_en": "Grinding noise when braking",
        "solution_en": "Brake pads likely worn out and need replacement. Have the rotors inspected as well, as they might need resurfacing or replacement.",
        "keywords": "brakes, brake, grinding, noise, stopping, squealing, squeaking"
    },
    {
        "brand": "Audi",
        "model": "A4",
        "problem_en": "Air conditioning not cooling",
        "solution_en": "Check refrigerant levels, may need recharging. Inspect for leaks in the AC system. The condenser or evaporator might be dirty or damaged.",
        "keywords": "ac, air conditioning, cooling, cold, hot air, refrigerant"
    }
]

# Sample maintenance center data
maintenance_centers = [
    {"id": 1, "name": "AutoFix Center", "latitude": 30.0444, "longitude": 31.2357},
    {"id": 2, "name": "Pro Mechanics", "latitude": 30.0500, "longitude": 31.2300},
    {"id": 3, "name": "Expert Car Services", "latitude": 30.0550, "longitude": 31.2400}
]

# Sample car owner data (for towing service)
car_owners = [
    {"id": 1, "name": "Ahmed", "personal_number": "01112218026", "latitude": 30.0480, "longitude": 31.2370},
    {"id": 2, "name": "Mohamed", "personal_number": "01012345678", "latitude": 30.0520, "longitude": 31.2410}
]

# Sample registered users
users = [
    {
        "id": 1,
        "email": "user@example.com",
        "name": "Test User",
        "password": ph.hash("Password123!"),
        "car_brand": "Toyota",
        "car_model": "Corolla",
        "manufacturing_year": 2020
    }
]

# ROUTES

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup')
def signup_page():
    return render_template('signup.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/map')
def map_page():
    return render_template('new_map.html')

@app.route('/maintenance-centers')
def maintenance_centers_page():
    return render_template('maintenance-centers.html')

@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/center-details')
def center_details():
    return render_template('center-details.html')

# API ENDPOINTS

@app.route('/api/maintenance-centers', methods=['GET'])
def get_maintenance_centers():
    return jsonify(maintenance_centers)

@app.route('/nearest-owner', methods=['GET'])
def get_nearest_owner():
    try:
        user_lat = float(request.args.get("lat"))
        user_lon = float(request.args.get("lon"))

        # Find the nearest car owner using Haversine formula
        nearest_owner = None
        min_distance = float('inf')
        
        for owner in car_owners:
            owner_location = (owner["latitude"], owner["longitude"])
            user_location = (user_lat, user_lon)
            distance = geopy.distance.geodesic(user_location, owner_location).km
            
            if distance < min_distance:
                min_distance = distance
                nearest_owner = owner
        
        if nearest_owner:
            return jsonify({
                "name": nearest_owner["name"],
                "phone": nearest_owner["personal_number"],
                "latitude": nearest_owner["latitude"],
                "longitude": nearest_owner["longitude"],
                "distance_km": round(min_distance, 2)
            })
        else:
            return jsonify({"message": "No car owners found."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Strong password validation
def is_strong_password(password):
    """Check if the password meets strength requirements."""
    if len(password) < 8:
        return "Password must be at least 8 characters long."
    if not re.search(r"\d", password):  # Check for a number
        return "Password must contain at least one number."
    if not re.search(r"[!@#$%^&*]", password):  # Check for a special character
        return "Password must contain at least one special character (!@#$%^&*)."
    return None  # Password is valid

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
        
        # Check if strong password or not 
        password_error = is_strong_password(password)
        if password_error:
            return jsonify({"error": password_error}), 400
        
        # Hash the password with Argon2
        hashed_password = ph.hash(password)

        # Check if email already exists
        for user in users:
            if user["email"] == email:
                return jsonify({"error": "Email already exists"}), 400

        # Create new user
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
            return jsonify({"error": "Invalid email or password"}), 401
        
    except Exception as e:
        print("Error in /signin:", str(e))
        return jsonify({"error": str(e)}), 500

# General car issue suggestions
general_issues = {
    "car not starting": "Is the issue related to the battery, starter motor, or ignition?",
    "strange noise": "Where is the noise coming from? Engine, brakes, or tires?",
    "brakes issue": "Are the brakes making a noise, feeling weak, or completely failing?",
    "engine problem": "Is the engine misfiring, overheating, or consuming too much oil?",
    "ac problem": "Is the AC blowing hot air, making noise, or not turning on?",
    "السيارة لا تعمل": "هل المشكلة متعلقة بالبطارية، أو محرك التشغيل، أو الإشعال؟",
    "صوت غريب": "من اين الصوت بالتحديد ؟ المحرك, الفرامل ام الاطارات ؟",
    "مشكلة في الفرامل": "هل الفرامل تصدر صوتًا، أو تشعر بالضعف، أو تتعطل تمامًا؟",
    "مشكلة في المحرك": "هل المحرك لا يعمل بشكل صحيح، أو يسخن بشكل زائد، أو يستهلك كمية كبيرة من الزيت؟",
    "مشكلة في مكيف الهواء": "هل ينفث مكيف الهواء هواءً ساخنًا، أو يصدر ضوضاء، أو لا يعمل؟"
}

# Simplified keyword extraction without requiring spaCy
def extract_keywords(text):
    """Extract potential keywords from text using simple splitting and filtering."""
    # Convert to lowercase and split by whitespace
    words = text.lower().split()
    
    # Filter out very short words (likely prepositions, articles, etc.)
    keywords = [word for word in words if len(word) > 2]
    
    # If no keywords found, fall back to original text split
    return keywords if keywords else text.lower().split()

# Language detection and translation simulation
def detect_language(text):
    """Detect if text is Arabic or English."""
    # Check if text contains Arabic characters (Unicode range U+0600 to U+06FF)
    is_arabic = any("\u0600" <= char <= "\u06FF" for char in text)
    return "ar" if is_arabic else "en"

def simulate_translation(text, target_lang="en"):
    """Simulate translation by checking if text appears to be in Arabic."""
    source_lang = detect_language(text)
    
    # No need to translate if already in target language
    if source_lang == target_lang:
        return text
        
    if source_lang == "ar" and target_lang == "en":
        # Placeholder for Arabic to English translation
        return f"[AR→EN: {text}]"
    elif source_lang == "en" and target_lang == "ar":
        # Placeholder for English to Arabic translation
        return f"[EN→AR: {text}]"
    else:
        # No translation needed or unsupported language pair
        return text

@app.route("/search", methods=["POST"])
def search():
    try:
        import logging
        from utils.gemini_helper import generate_diagnostic_response, generate_maintenance_tips, generate_related_issues
        
        # Set up logging for diagnostics
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        logger.info("Starting diagnostic search")
        
        # Parse request data
        data = request.json
        if not data:
            logger.error("No JSON data received in request")
            return jsonify({"error": "Invalid request format. Please provide JSON data."}), 400
            
        query_text = data.get("query", "").strip()
        brand = data.get("brand", "").strip()
        model = data.get("model", "").strip()
        
        # Log the request parameters
        logger.info(f"Search request - Query: '{query_text}', Brand: '{brand}', Model: '{model}'")
        
        # Create case-insensitive filters
        brand_filter = brand.lower() if brand else None
        model_filter = model.lower() if model else None
        
        if not query_text:
            logger.warning("Empty query received")
            return jsonify({"error": "Please provide a description of your car problem."}), 400
            
        # Check for follow-up questions that might be needed for vague queries
        for key, question in general_issues.items():
            if key.lower() in query_text.lower() and len(query_text.split()) < 5:
                response = {
                    "message": "I need more details to provide a solution, احتاج المزيد من التفاصيل لمساعدك.",
                    "follow_up_question": question
                }
                return jsonify(response)

        # Language detection for Arabic
        is_arabic = any("\u0600" <= char <= "\u06FF" for char in query_text)
        
        # For Arabic queries, perform simple translation
        if is_arabic:
            # Inform that we detected Arabic
            print("Arabic query detected: translation would be applied")
            # In a production system, we would use a proper translation API here
        
        # Use OpenAI to generate a diagnostic response
        try:
            print(f"Generating diagnostic for {brand} {model}: {query_text}")
            
            # Call OpenAI for detailed diagnostics
            ai_response = generate_diagnostic_response(query_text, brand, model)
            
            # If we have results from the AI
            if 'results' in ai_response and ai_response['results']:
                # Process the results
                results = ai_response['results']
                
                # Add related issues for the first problem
                if len(results) > 0 and 'problem' in results[0]:
                    related = generate_related_issues(brand, model, results[0]['problem'])
                    if related:
                        ai_response['related_issues'] = related
                
                # Generate maintenance tips
                maintenance_tips = generate_maintenance_tips(brand, model)
                if maintenance_tips:
                    ai_response['maintenance_tips'] = maintenance_tips
                
                # Return enhanced AI response
                return jsonify(ai_response)
            
            # Fallback to traditional search if AI response has no results
            print("No AI results, falling back to traditional search")
        except Exception as ai_error:
            # Log the AI error but continue with traditional search
            print(f"Error with AI diagnostic: {str(ai_error)}")
        
        # Traditional keyword-based search (fallback method)
        # Extract keywords from query
        extracted_keywords = extract_keywords(query_text)
        refined_query = " ".join(extracted_keywords)

        # Search for relevant problems
        results = []
        for issue in car_issues:
            # Apply brand & model filtering
            if brand_filter and brand_filter != issue["brand"].lower():
                continue
            if model_filter and model_filter != issue["model"].lower():
                continue
                
            # Check for keyword matches
            issue_keywords = set(issue["keywords"].lower().split(", "))
            query_keywords = set(refined_query.lower().split())
            
            match_score = len(query_keywords.intersection(issue_keywords))
            
            if match_score > 0:
                problem = issue["problem_en"]
                solution = issue["solution_en"]
                
                # Simulate translating response back to Arabic if needed
                if is_arabic:
                    problem = simulate_translation(problem, "ar")
                    solution = simulate_translation(solution, "ar")
                
                results.append({
                    "problem": problem,
                    "solution": solution,
                    "score": match_score,
                    "problem_severity": "Warning",  # Default severity for backward compatibility
                    "estimated_cost": "$100-300",   # Default cost estimate
                    "diy_possible": True,          # Default DIY possibility
                })
        
        # Sort results by relevance
        results.sort(key=lambda x: x.get("score", 0), reverse=True)
        
        if not results:
            # Try to generate a response even when we don't have exact matches
            try:
                ai_response = generate_diagnostic_response(query_text, brand, model)
                if 'results' in ai_response and ai_response['results']:
                    return jsonify(ai_response)
            except Exception:
                pass
                
            # Truly no results found
            return jsonify({
                "message": "No diagnostic information found. Please provide more details about your vehicle issue.",
                "follow_up_questions": [
                    "When did you first notice the problem?",
                    "Does the issue happen all the time or only under certain conditions?",
                    "Are there any warning lights on your dashboard?"
                ]
            }), 200
            
        return jsonify({"results": results})
        
    except Exception as e:
        print("Error in /search:", str(e))
        return jsonify({"error": "An unexpected error occurred. Our technical team has been notified. Please try again."}), 500

@app.route("/get-directions", methods=["GET"])
def get_directions():
    """Simulate getting directions between two points."""
    start = request.args.get("start")  # Example: "30.0444,31.2357"
    end = request.args.get("end")      # Example: "30.0500,31.2333"

    if not start or not end:
        return jsonify({"error": "Start and end locations are required"}), 400

    # Simulate a response from a mapping service
    directions = {
        "routes": [
            {
                "distance": 5.2,  # in kilometers
                "duration": 15,   # in minutes
                "steps": [
                    {
                        "instruction": "Head north on Main St.",
                        "distance": 1.2
                    },
                    {
                        "instruction": "Turn right onto Central Ave.",
                        "distance": 2.5
                    },
                    {
                        "instruction": "Turn left onto Destination Rd.",
                        "distance": 1.5
                    }
                ]
            }
        ]
    }

    return jsonify(directions)

@app.route("/save-location", methods=["POST"])
def save_location():
    """Save user's location."""
    try:
        data = request.json
        user_id = data.get("user_id")
        latitude = data.get("latitude")
        longitude = data.get("longitude")
        
        if not user_id or latitude is None or longitude is None:
            return jsonify({"error": "User ID, latitude, and longitude are required"}), 400
            
        # In a real application, this would update a database
        # For now, just return success
        return jsonify({"message": "Location saved successfully"})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/vehicle-health")
def vehicle_health_page():
    """Display the vehicle health monitoring page."""
    return render_template("vehicle_health.html")

@app.route("/api/vehicle-health")
def vehicle_health_api():
    """API endpoint to get vehicle health data."""
    try:
        import logging
        from utils.ai_insights import get_complete_vehicle_analysis
        
        # Set up logging for diagnostics
        logger = logging.getLogger(__name__)
        logger.info("Vehicle health API request received")
        
        # Get parameters from request
        vehicle_id = request.args.get("vehicle_id", "default-vehicle")
        brand = request.args.get("brand", "Unknown").strip()
        model = request.args.get("model", "Unknown").strip()
        year = request.args.get("year", "2025")
        condition = request.args.get("condition", "")
        
        # Log the request parameters
        logger.info(f"Vehicle health request - ID: '{vehicle_id}', Brand: '{brand}', Model: '{model}', Year: '{year}'")
        
        # Validate inputs
        if not brand or brand == "Unknown":
            logger.warning("Missing brand parameter in vehicle health request")
            # We'll still process the request but log the warning
        
        if not model or model == "Unknown":
            logger.warning("Missing model parameter in vehicle health request")
            # We'll still process the request but log the warning
        
        # Get complete analysis with better error handling
        try:
            analysis = get_complete_vehicle_analysis(vehicle_id, brand, model, year, condition)
            
            # Ensure the vehicle data section contains the provided brand and model
            if "vehicle_data" in analysis:
                analysis["vehicle_data"]["brand"] = brand
                analysis["vehicle_data"]["model"] = model
                analysis["vehicle_data"]["year"] = year
            
            # Return the analysis as JSON
            return jsonify(analysis)
            
        except Exception as analysis_error:
            logger.error(f"Error generating vehicle analysis: {str(analysis_error)}")
            return jsonify({
                "error": "Unable to analyze vehicle health at this time",
                "vehicle_data": {
                    "vehicle_id": vehicle_id,
                    "brand": brand, 
                    "model": model,
                    "year": year,
                    "status": "Error"
                }
            }), 500
        
    except Exception as e:
        logger.error(f"Unexpected error in vehicle health API: {str(e)}")
        return jsonify({"error": "An unexpected error occurred while analyzing vehicle health"}), 500

if __name__ == "__main__":
    # Use a different port (8080) since port 5000 is used by Streamlit
    app.run(host="0.0.0.0", port=8080, debug=True)