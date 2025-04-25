from flask import Flask, request, jsonify
from flask_cors import CORS
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
from deep_translator import GoogleTranslator
import re
import requests
import mysql.connector
import json
import geopy.distance
import spacy
import nltk
from argon2 import PasswordHasher
from pydantic import BaseModel
from mysql.connector import pooling

class LocationModel(BaseModel):
    user_id: int
    latitude: float
    longitude: float


# Initialize Flask app
app = Flask(__name__)
CORS(app)
    
# Intialize the security Hasher
ph = PasswordHasher()

# Load English NLP model
nlp = spacy.load("en_core_web_sm")

# Database Connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="123456789",
    database="car_maintenance" ,
)
cursor = db.cursor(dictionary=True)  # ✅ Returns results as dictionaries
cnxpool = pooling.MySQLConnectionPool(pool_name="mypool",
                                      pool_size=5)

# Later when you need a connection
conn = cnxpool.get_connection()

# to save the query into database   
def log_query(query, response):
    """Logs user queries and responses into MySQL database."""
    try:
        conn = mysql.connector.connect(**db)
        cursor = conn.cursor()
        sql = "INSERT INTO user_queries (query, response) VALUES (%s, %s)"
        cursor.execute(sql, (query, response))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error logging query: {e}")

#Nearest maintanace center
def get_nearest_center(user_lat, user_lon):
    conn = mysql.connector.connect(**db)
    cursor = conn.cursor(dictionary=True)

    # Fetch all maintenance centers from the database
    cursor.execute("SELECT id, name, latitude, longitude FROM maintenance_centers")
    centers = cursor.fetchall()
    cursor.close()
    conn.close()

    # Calculate distance for each center
    for center in centers:
        center_location = (center["latitude"], center["longitude"])
        user_location = (user_lat, user_lon)
        center["distance_km"] = geopy.distance.geodesic(user_location, center_location).km  # Calculate distance

    # Sort centers by distance
    centers.sort(key=lambda c: c["distance_km"])

    return centers[:5]  # Return the 5 closest centers

@app.route("/api/maintenance-centers", methods=["GET"])
def get_maintenance_centers():
    conn = mysql.connector.connect(**db)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name, latitude, longitude FROM maintenance_centers")  # Ensure lat/lon fields exist
    centers = cursor.fetchall()
    conn.close()
    return jsonify(centers)


# Nearest tow car 
@app.route("/nearest-owner", methods=["GET"])
def get_nearest_owner():
    try:
        user_lat = float(request.args.get("lat"))
        user_lon = float(request.args.get("lon"))

        conn = mysql.connector.connect(**db)
        cursor = conn.cursor(dictionary=True)

        # Haversine formula to calculate distance
        query = """
        SELECT id, name, personal_number, latitude, longitude,
            (6371 * ACOS(COS(RADIANS(%s)) * COS(RADIANS(latitude)) 
            * COS(RADIANS(longitude) - RADIANS(%s)) 
            + SIN(RADIANS(%s)) * SIN(RADIANS(latitude)))) AS distance
        FROM car_owners
        ORDER BY distance ASC
        LIMIT 1;
        """
        cursor.execute(query, (user_lat, user_lon, user_lat))
        owner = cursor.fetchone()

        cursor.close()
        conn.close()

        if owner:
            return jsonify({
                "name": owner["name"],
                "phone": owner["personal_number"],  # Include contact number
                "latitude": owner["latitude"],
                "longitude": owner["longitude"],
                "distance_km": round(owner["distance"], 2)
            })
        else:
            return jsonify({"message": "No car owners found."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Saving call history between customer and car owner     
@app.route("/log-call", methods=["POST"])
def log_call():
    try:
        data = request.json
        caller_number = data.get("caller_number")
        owner_id = data.get("owner_id")

        if not caller_number or not owner_id:
            return jsonify({"error": "Caller number and owner ID are required"}), 400

        conn = mysql.connector.connect(**db)
        cursor = conn.cursor()

        query = "INSERT INTO call_history (caller_number, owner_id) VALUES (%s, %s)"
        cursor.execute(query, (caller_number, owner_id))
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({"message": "Call logged successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Mapbox API Key (Replace with your actual key)
MAPBOX_API_KEY = "pk.eyJ1IjoicmFvb3V1ZiIsImEiOiJjbThhczR3dHQwaXNrMmlyNDFiNWNlbXJuIn0.aG1MNazYf9MdCc9w3bT27A"

# Directions with Mapbox
@app.route('/get-directions', methods=['GET'])
def get_directions():
    start = request.args.get("start")  # Example: "30.0444,31.2357"
    end = request.args.get("end")      # Example: "30.0500,31.2333"

    if not start or not end:
        return jsonify({"error": "Start and end locations are required"}), 400

    url = f"https://api.mapbox.com/directions/v5/mapbox/driving/{start};{end}?access_token={MAPBOX_API_KEY}&geometries=geojson&steps=true"

    response = requests.get(url)
    if response.status_code != 200:
        return jsonify({"error": "Failed to get directions"}), 500

    return jsonify(response.json())


# STRONG PASSWORD special charactar and number (1 at least)
def is_strong_password(password):
    """Check if the password meets strength requirements."""
    if len(password) < 8:
        return "Password must be at least 8 characters long."
    if not re.search(r"\d", password):  # Check for a number
        return "Password must contain at least one number."
    if not re.search(r"[!@#$%^&*]", password):  # Check for a special character
        return "Password must contain at least one special character (!@#$%^&*)."
    return None  # Password is valid

# SIGN UP
@app.route("/signup", methods=["POST"])  # Allow POST & OPTIONS
def signup():
    if request.method == "OPTIONS":  # Handle preflight request
        return jsonify({"message": "CORS preflight passed"}), 200

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
        
        # check if strong password  or not 
        password_error = is_strong_password(password)
        if password_error:
            return jsonify({"error": password_error}), 400
        
        # Hash the password with Argon2
        hashed_password = ph.hash(password)

        conn = mysql.connector.connect(**db)
        cursor = conn.cursor()

        query = "INSERT INTO users (email, name, password, car_brand, car_model, manufacturing_year) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (email, name, hashed_password, car_brand, car_model, manufacturing_year))
        conn.commit()

        cursor.close()
        conn.close()
        data = request.json
        return jsonify({"message": "User registered successfully"}), 201

    except mysql.connector.IntegrityError:
        return jsonify({"error": "Email already exists"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.before_request 
def log_request():
    print(f"Received {request.method} request for {request.path}")

# SIGN IN
@app.route("/signin", methods=["POST"])  # ✅ Allow OPTIONS requests
def signin():
    try:
        data = request.json
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        conn = mysql.connector.connect(**db)
        cursor = conn.cursor(dictionary=True)

        query = "SELECT id, name, password FROM users WHERE email = %s"
        cursor.execute(query, (email,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user:
            try:
                # Verify the password using Argon2
                ph.verify(user["password"], password)

                return jsonify({"message": "Login successful", "user_id": user["id"], "name": user["name"]}), 200
            except:
                return jsonify({"error": "Invalid email or password"}), 401
        else:
            return jsonify({"error": "Invalid email or password"}), 401
        
    except Exception as e:
        print("Error in /signin:", str(e))  # ✅ Print error in terminal
        return jsonify({"error": str(e)}), 500

# LOCATION SAVED
@app.route("/save-location", methods=["POST"])
def save_location(location: LocationModel):
    try:
        conn = cnxpool.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET latitude=%s, longitude=%s WHERE id=%s",
            (location.latitude, location.longitude, location.user_id)
        )
        conn.commit()
        return {"message": "Location saved successfully"}
    except Exception as e:
        print("Error saving location:", e)
        return {"error": str(e)}
    finally:
        cursor.close()
        conn.close()


# Load Sentence Transformer model بيحاول يماتش الكلام المكتوب بالداتا بيز
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")  # Ensure it matches the index dimension

#translation work
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

# General issue suggestions on customers 
general_issues = {
    "car not starting": "Is the issue related to the battery, starter motor, or ignition?",
    "strange noise": "Where is the noise coming from? Engine, brakes, or tires?",
    "brakes issue": "Are the brakes making a noise, feeling weak, or completely failing?",
    "engine problem": "Is the engine misfiring, overheating, or consuming too much oil?",
    "AC problem ": "Is the AC blowing hot air, making noise, or not turning on?",
    "السيارة لا تعمل" : "هل المشكلة متعلقة بالبطارية، أو محرك التشغيل، أو الإشعال؟",
    "صوت غريب" : "من اين الصوت بالتحديد ؟ المحرك , الفرامل ام الاطارات ؟",
    "مشكلة في الفرامل" : "هل الفرامل تصدر صوتًا، أو تشعر بالضعف، أو تتعطل تمامًا؟",
    "مشكلة في المحرك" : "هل المحرك لا يعمل بشكل صحيح، أو يسخن بشكل زائد، أو يستهلك كمية كبيرة من الزيت؟" ,
    "مشكله في مكيف الهواء" : "هل ينفث مكيف الهواء هواءً ساخنًا، أو يصدر ضوضاء، أو لا يعمل؟"
}

#Getting the common words
def extract_keywords(text):
    doc = nlp(text)
    keywords = [token.text.lower() for token in doc if token.pos_ in ["NOUN", "VERB", "ADJ"]]
    return keywords if keywords else text.split()  # Fallback to simple split if no keywords

def fetch_issues_from_db(brand, model, query_text):
    """
    Fetch car issues using NLP to match similar queries.
    """
    relevant_issues = []

    # ✅ Extract Keywords from Query using NLP
    query_doc = nlp(query_text)
    query_keywords = {token.lemma_.lower() for token in query_doc if token.is_alpha and not token.is_stop}

    with db.cursor(dictionary=True) as cursor:
        query = """
            SELECT problem_en, solution_en, keywords
            FROM car_issues
            WHERE brand = %s AND model = %s
        """
        cursor.execute(query, (brand, model))
        issues = cursor.fetchall()

        for issue in issues:
            issue_keywords = {word.lower() for word in issue["keywords"].split(", ")}  # ✅ Convert keywords to lowercase
            
            # ✅ Calculate similarity score based on keyword overlap
            match_score = len(query_keywords & issue_keywords) / max(len(query_keywords), 1)  # Avoid division by zero
            
            # ✅ Store relevant issues with a score
            if match_score > 0.3:  # ✅ Only include results with a score above 0.3
                relevant_issues.append({
                    "problem": issue["problem_en"],
                    "solution": issue["solution_en"],
                    "score": match_score  # Store score for ranking
                })

    # ✅ Sort results by relevance (highest score first)
    relevant_issues.sort(key=lambda x: x["score"], reverse=True)

    return relevant_issues


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
            if key in query_text:
                response = {
                    "message": "I need more details to provide a solution, احتاج المزيد من التفاصيل لمساعدك.",
                    "follow_up_question": question
                }
                log_query(query_text, response["follow_up_question"])
                return jsonify(response)

        translated_query = translate_text(query_text, "en")
        query_language = "ar" if query_text != translated_query else "en"

        # Extract keywords from translated query
        extracted_keywords = extract_keywords(translated_query)
        refined_query = " ".join(extracted_keywords)

        # **Search MySQL for relevant problems**
        with db.cursor(dictionary=True) as cursor:
            sql_query = """
         SELECT brand, model, problem_en, solution_en
            FROM car_issues
            WHERE brand = %s AND model = %s
            AND keywords LIKE %s
            LIMIT 3;
            """
            cursor.execute(sql_query, (brand_filter, model_filter, f"%{refined_query}%",))
            search_results = cursor.fetchall()

        results = []

        for row in search_results:
            problem = row["problem_en"]
            solution = row["solution_en"]

            # Apply brand & model filtering
            if brand_filter and brand_filter != row["brand"].lower():
                continue
            if model_filter and model_filter != row["model"].lower():
                continue

            # Translate response back to Arabic if needed
            if query_language == "ar":
                if problem:
                    problem = translate_text(problem, "ar")
                if solution:
                    solution = translate_text(solution, "ar")

            results.append({
                "brand": row["brand"],
                "model": row["model"],
                "problem": problem,
                "solution": solution
            })
        
        if not search_results:
            return jsonify({
                "message": "No relevant issues found. Try rephrasing your query or providing more details."
            }), 200

        log_query(query_text, str(results))
        
        return jsonify({"results": results})
    
    except Exception as e:
        print("Error in /search:", str(e))
        return jsonify({"error": str(e)}), 500

# Run the Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)