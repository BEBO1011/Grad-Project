from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_cors import CORS
import os
import json
import re
import secrets
from geopy.distance import geodesic
from datetime import datetime, timedelta
import random
import db_utils
from sqlalchemy import create_engine
from functools import wraps
# Import database modules
from database import init_db

# Correct PostgreSQL connection string format
engine = create_engine("postgresql://username:password@localhost:5432/mydatabase")

# Initialize Flask app
app = Flask(__name__, 
    static_folder='static',
    static_url_path='/static'
)
app.secret_key = secrets.token_hex(16)  # Secure session key
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.config['SESSION_COOKIE_SECURE'] = True  # For HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
CORS(app)

# Initialize database
init_db()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print(session)
        if 'user_id' not in session:
            return jsonify({
                "error": "Please sign in to access this feature",
                "message": "Please sign in to access this feature"
            }), 401
        return f(*args, **kwargs)
    return decorated_function

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

# This will be replaced with database queries
# Legacy user array for backward compatibility until fully migrated
users = [
    {
        "id": 1,
        "email": "user@example.com",
        "name": "Test User",
        "password": "argon2$Password123!",  # This is a dummy hash; we'll use db authentication
        "car_brand": "Toyota",
        "car_model": "Corolla",
        "manufacturing_year": 2020
    }
]

# Admin authentication middleware
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or not session.get('is_admin'):
            return jsonify({
                "error": "Admin access required",
                "message": "Please sign in as an admin to access this feature"
            }), 403
        return f(*args, **kwargs)
    return decorated_function

# ROUTES

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup')
def signup_page():
    return render_template('signup.html')

@app.route('/home')
@login_required
def home():
    return render_template('home_new.html')

@app.route('/map')
@login_required
def map_page():
    return render_template('map_new.html')

@app.route('/maintenance-centers')
@login_required
def maintenance_centers_page():
    return render_template('maintenance-centers.html')

@app.route('/chatbot')
@login_required
def chatbot():
    return render_template('chatbot.html')

@app.route('/settings')
@login_required
def settings():
    return render_template('settings_new.html')

@app.route('/center-details')
@login_required
def center_details():
    return render_template('center-details.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/admin')
@admin_required
def admin_dashboard():
    return render_template('admin_dashboard.html')

# API ENDPOINTS

@app.route('/api/user/vehicles', methods=['GET'])
@login_required
def get_user_vehicles():
    """Get all vehicles for a user from the database."""
    try:
        user_id = session.get('user_id')  # Get user_id from session instead of request
        
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400
            
        # Get vehicles from database
        vehicles = db_utils.get_user_vehicles(user_id)
        
        # Convert to JSON-serializable format
        vehicle_list = [vehicle.to_dict() for vehicle in vehicles]
        
        return jsonify(vehicle_list)
    except Exception as e:
        print(f"Error fetching user vehicles: {str(e)}")
        return jsonify({"error": "Failed to fetch vehicles"}), 500

@app.route('/api/maintenance-centers', methods=['GET'])
@login_required
def get_maintenance_centers():
    try:
        # Get centers from database
        centers = db_utils.get_maintenance_centers()
        
        # Convert to JSON-serializable format
        center_list = [center.to_dict() for center in centers]
        
        return jsonify(center_list)
    except Exception as e:
        print(f"Error fetching maintenance centers: {str(e)}")
        return jsonify({"error": "Failed to fetch maintenance centers"}), 500
        
@app.route('/api/maintenance-center/<int:center_id>', methods=['GET'])
@login_required
def get_maintenance_center(center_id):
    """Get details for a specific maintenance center."""
    try:
        # Get center from database
        center = db_utils.get_center_by_id(center_id)
        
        if not center:
            return jsonify({"error": "Maintenance center not found"}), 404
            
        # Get services for this center
        services = db_utils.get_center_services(center_id)
        
        # Convert to JSON-serializable format
        center_data = center.to_dict()
        service_list = [service.to_dict() for service in services]
        
        # Add services to center data
        center_data['services'] = service_list
        
        return jsonify(center_data)
    except Exception as e:
        print(f"Error fetching maintenance center: {str(e)}")
        return jsonify({"error": "Failed to fetch maintenance center details"}), 500

@app.route('/api/user/profile', methods=['GET'])
@login_required
def get_user_profile():
    """Get user profile information."""
    try:
        user_id = session.get('user_id')  # Get user_id from session instead of request
        
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400
            
        # Get user profile from database
        user = db_utils.get_user_by_id(user_id)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
            
        # Get user's vehicles
        vehicles = db_utils.get_user_vehicles(user_id)
        vehicle_list = [vehicle.to_dict() for vehicle in vehicles]
        
        # Convert to JSON-serializable format and include vehicles
        user_data = user.to_dict()
        user_data['vehicles'] = vehicle_list
        
        return jsonify(user_data)
    except Exception as e:
        print(f"Error fetching user profile: {str(e)}")
        return jsonify({"error": "Failed to fetch user profile"}), 500
        
@app.route('/api/user/profile', methods=['PUT'])
def update_user_profile():
    """Update user profile information."""
    try:
        data = request.json
        user_id = data.get("user_id")
        
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400
            
        # Get updateable fields from request
        name = data.get("name")
        phone = data.get("phone")
        preferred_language = data.get("preferred_language")
        profile_picture = data.get("profile_picture")
        
        # Update user profile in database
        user, error = db_utils.update_user_profile(
            user_id=user_id,
            name=name,
            phone=phone,
            preferred_language=preferred_language,
            profile_picture=profile_picture
        )
        
        if error:
            return jsonify({"error": error}), 400
            
        return jsonify({
            "success": True,
            "message": "Profile updated successfully",
            "user": user.to_dict()
        })
        
    except Exception as e:
        print(f"Error updating user profile: {str(e)}")
        return jsonify({"error": "Failed to update user profile"}), 500

@app.route('/nearest-owner', methods=['GET'])
def get_nearest_owner():
    try:
        user_lat = float(request.args.get("lat"))
        user_lon = float(request.args.get("lon"))

        # Get all users from database
        session = db_utils.get_session()
        try:
            users = session.query(db_utils.User).filter(db_utils.User.is_active == True).all()
            
            if not users:
                return jsonify({"message": "No active users found."}), 404
                
            # Find users with saved locations
            users_with_locations = []
            for user in users:
                # Get user's saved locations
                locations = db_utils.get_user_saved_locations(user.id)
                if locations:
                    # Use the first location (or favorite if available)
                    favorite_location = next((loc for loc in locations if loc.is_favorite), locations[0])
                    users_with_locations.append({
                        "user": user,
                        "location": favorite_location
                    })
            
            if not users_with_locations:
                return jsonify({"message": "No users with saved locations found."}), 404
                
            # Find the nearest user using Haversine formula
            nearest_owner = None
            min_distance = float('inf')
            
            for user_data in users_with_locations:
                user = user_data["user"]
                location = user_data["location"]
                
                owner_location = (location.latitude, location.longitude)
                user_location = (user_lat, user_lon)
                distance = geodesic(user_location, owner_location).km
                
                if distance < min_distance:
                    min_distance = distance
                    nearest_owner = {
                        "user": user,
                        "location": location,
                        "distance": distance
                    }
            
            if nearest_owner:
                return jsonify({
                    "name": nearest_owner["user"].name,
                    "phone": nearest_owner["user"].phone or "Not available",
                    "latitude": nearest_owner["location"].latitude,
                    "longitude": nearest_owner["location"].longitude,
                    "distance_km": round(nearest_owner["distance"], 2)
                })
            else:
                return jsonify({"message": "No nearby owners found."}), 404
                
        finally:
            session.close()
            
    except Exception as e:
        print(f"Error finding nearest owner: {str(e)}")
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
        
        # Create the user in the database
        user, error = db_utils.create_user(name, email, password)
        if error:
            return jsonify({"error": error}), 400
            
        # Add vehicle for the user
        vehicle, error = db_utils.add_vehicle(
            user.id, 
            car_brand, 
            car_model, 
            int(manufacturing_year) if manufacturing_year else 2020
        )
        
        if error:
            return jsonify({"error": f"User created but failed to add vehicle: {error}"}), 400
            
        # Set up session data
        session['user_id'] = user.id
        session['name'] = user.name
        session['email'] = user.email
        
        return jsonify({
            "message": "User registered successfully", 
            "success": True,
            "user_id": user.id,
            "name": user.name
        }), 201

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

        # Authenticate user with database
        user, error = db_utils.authenticate_user(email, password)
        
        if error:
            return jsonify({"error": "Invalid email or password"}), 401

        if user:
            # Set up session data
            session['user_id'] = user["id"]
            session['name'] = user["name"]
            session['email'] = user["email"]
            
            return jsonify({
                "message": "Login successful", 
                "user_id": user["id"], 
                "name": user["name"]
            }), 200
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

@app.route("/api/book-appointment", methods=["POST"])
def book_appointment():
    """Book a maintenance appointment."""
    try:
        data = request.json
        user_id = data.get("user_id")
        vehicle_id = data.get("vehicle_id")
        center_id = data.get("center_id")
        service_id = data.get("service_id")
        appointment_date_str = data.get("appointment_date")
        notes = data.get("notes")
        # Validate required inputs
        if not user_id or not vehicle_id or not center_id or not appointment_date_str:
            return jsonify({"error": "User ID, vehicle ID, center ID and appointment date are required"}), 400
            
        # Parse appointment date
        try:
            appointment_date = datetime.fromisoformat(appointment_date_str.replace('Z', '+00:00'))
        except ValueError:
            return jsonify({"error": "Invalid appointment date format. Please use ISO format (YYYY-MM-DDTHH:MM:SS)"}), 400
            
        # Book appointment in database
        appointment, error = db_utils.book_appointment(
            user_id=user_id,
            vehicle_id=vehicle_id,
            center_id=center_id,
            service_id=service_id,
            appointment_date=appointment_date,
            notes=notes
        )
        if error:
            return jsonify({"error": error}), 400
            
        return jsonify({
            "success": True,
            "message": "Appointment booked successfully",
            "appointment": appointment
        })
        
    except Exception as e:
        print(f"Error booking appointment: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/user/appointments", methods=["GET"])
def get_user_appointments():
    """Get appointments for a user."""
    try:
        user_id = request.args.get("user_id")
        status = request.args.get("status")  # Optional
        
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400
            
        # Get appointments from database
        appointments = db_utils.get_user_appointments(user_id, status)
        
        # Convert to JSON-serializable format
        appointment_list = [appointment.to_dict() for appointment in appointments]
        
        return jsonify(appointment_list)
    except Exception as e:
        print(f"Error fetching user appointments: {str(e)}")
        return jsonify({"error": "Failed to fetch appointments"}), 500

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
        
        # Get additional data if available
        location_name = data.get("name", "My Location")
        address = data.get("address", "")
        is_favorite = data.get("is_favorite", False)
        
        # Save location to database
        location, error = db_utils.save_user_location(
            user_id=user_id,
            name=location_name,
            latitude=latitude,
            longitude=longitude,
            address=address,
            is_favorite=is_favorite
        )
        
        if error:
            return jsonify({"error": error}), 400
            
        return jsonify({
            "success": True,
            "message": "Location saved successfully",
            "location": location
        })
        
    except Exception as e:
        print(f"Error saving location: {str(e)}")
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
        vehicle_id = request.args.get("vehicle_id")
        user_id = request.args.get("user_id")
        
        if not vehicle_id:
            logger.warning("Missing vehicle_id parameter in vehicle health request")
            return jsonify({"error": "Vehicle ID is required"}), 400
        
        # Get vehicle data from database
        try:
            # First try to get vehicle health data from database
            health_data = db_utils.get_vehicle_health_history(vehicle_id, limit=1)
            
            # Then try to get vehicle details
            vehicle = db_utils.get_vehicle_by_id(vehicle_id)
            
            if not vehicle:
                logger.warning(f"Vehicle with ID {vehicle_id} not found")
                return jsonify({"error": "Vehicle not found"}), 404
                
            # Use vehicle data for analysis
            brand = vehicle.brand
            model = vehicle.model
            year = str(vehicle.year)
            
            # If we have health data, use it to enhance the analysis
            condition = ""
            if health_data and len(health_data) > 0:
                latest_data = health_data[0]
                # Build condition string based on health data
                conditions = []
                
                if latest_data.check_engine_light:
                    conditions.append("check engine light on")
                    
                if latest_data.oil_level and latest_data.oil_level < 30:
                    conditions.append("low oil level")
                    
                if latest_data.coolant_level and latest_data.coolant_level < 30:
                    conditions.append("low coolant level")
                    
                if latest_data.engine_temperature and latest_data.engine_temperature > 100:
                    conditions.append("high engine temperature")
                    
                condition = ", ".join(conditions)
            
            # Log the request parameters
            logger.info(f"Vehicle health request - ID: '{vehicle_id}', Brand: '{brand}', Model: '{model}', Year: '{year}'")
            
            # Get complete analysis with better error handling
            analysis = get_complete_vehicle_analysis(vehicle_id, brand, model, year, condition)
            
            # Enhance analysis with actual vehicle data
            if "vehicle_data" in analysis:
                analysis["vehicle_data"]["brand"] = brand
                analysis["vehicle_data"]["model"] = model
                analysis["vehicle_data"]["year"] = year
                analysis["vehicle_data"]["vehicle_id"] = vehicle_id
                
                if health_data and len(health_data) > 0:
                    latest_data = health_data[0]
                    analysis["vehicle_data"]["mileage"] = latest_data.mileage
                    
                    # Add health metrics
                    if "health_metrics" not in analysis:
                        analysis["health_metrics"] = {}
                        
                    analysis["health_metrics"]["engine_status"] = latest_data.engine_status or "Good"
                    analysis["health_metrics"]["oil_level"] = latest_data.oil_level or 85
                    analysis["health_metrics"]["coolant_level"] = latest_data.coolant_level or 92
                    analysis["health_metrics"]["brake_fluid"] = latest_data.brake_fluid_level or 78
                    analysis["health_metrics"]["tire_pressure"] = {
                        "front_left": latest_data.tire_pressure_front_left or 32.5,
                        "front_right": latest_data.tire_pressure_front_right or 32.0,
                        "rear_left": latest_data.tire_pressure_rear_left or 32.8,
                        "rear_right": latest_data.tire_pressure_rear_right or 32.2
                    }
                    analysis["health_metrics"]["battery_health"] = latest_data.battery_health or 90
                    analysis["health_metrics"]["fuel_level"] = latest_data.fuel_level or 65
            
            # Return the enhanced analysis as JSON
            return jsonify(analysis)
            
        except Exception as analysis_error:
            logger.error(f"Error generating vehicle analysis: {str(analysis_error)}")
            return jsonify({
                "error": "Unable to analyze vehicle health at this time",
                "vehicle_data": {
                    "vehicle_id": vehicle_id,
                    "status": "Error"
                }
            }), 500
        
    except Exception as e:
        print(f"Unexpected error in vehicle health API: {str(e)}")
        return jsonify({"error": "An unexpected error occurred while analyzing vehicle health"}), 500

@app.route('/api/admin/stats')
@admin_required
def get_admin_stats():
    try:
        # Get total users
        total_users = db_utils.get_total_users()
        
        # Get active appointments
        active_appointments = db_utils.get_active_appointments()
        
        # Get monthly revenue
        monthly_revenue = db_utils.get_monthly_revenue()
        
        # Get total service centers
        total_centers = db_utils.get_total_centers()
        
        return jsonify({
            "total_users": total_users,
            "active_appointments": active_appointments,
            "monthly_revenue": monthly_revenue,
            "total_centers": total_centers
        })
    except Exception as e:
        print(f"Error fetching admin stats: {str(e)}")
        return jsonify({"error": "Failed to fetch admin statistics"}), 500

@app.route('/api/admin/recent-appointments')
@admin_required
def get_recent_appointments():
    try:
        appointments = db_utils.get_recent_appointments(limit=10)
        return jsonify([appointment.to_dict() for appointment in appointments])
    except Exception as e:
        print(f"Error fetching recent appointments: {str(e)}")
        return jsonify({"error": "Failed to fetch recent appointments"}), 500

@app.route('/api/admin/user-activity')
@admin_required
def get_user_activity():
    try:
        activities = db_utils.get_recent_user_activity(limit=10)
        return jsonify([activity.to_dict() for activity in activities])
    except Exception as e:
        print(f"Error fetching user activity: {str(e)}")
        return jsonify({"error": "Failed to fetch user activity"}), 500

@app.route('/api/admin/monthly-stats')
@admin_required
def get_monthly_stats():
    try:
        stats = db_utils.get_monthly_statistics()
        return jsonify(stats)
    except Exception as e:
        print(f"Error fetching monthly stats: {str(e)}")
        return jsonify({"error": "Failed to fetch monthly statistics"}), 500

if __name__ == "__main__":
    import socket
    from contextlib import closing
    
    def find_free_port(start_port=8082, max_port=9000):
        """Find a free port between start_port and max_port."""
        for port in range(start_port, max_port + 1):
            with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
                try:
                    sock.bind(('0.0.0.0', port))
                    return port
                except OSError:
                    continue
        return None
    
    # Try to find a free port
    port = find_free_port()
    if port is None:
        print("Error: Could not find a free port between 8082 and 9000")
        print("Please close other applications that might be using these ports")
        print("or manually specify a port using the PORT environment variable")
        exit(1)
        
    print(f"Starting server on port {port}")
    try:
        app.run(host="0.0.0.0", port=port, debug=True)
    except OSError as e:
        print(f"Error starting server: {e}")
        print("Please make sure no other application is using the port")
        exit(1)