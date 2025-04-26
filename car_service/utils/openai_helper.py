import os
import json
import logging
from openai import OpenAI

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
MODEL = "gpt-4o"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
try:
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    logger.info("OpenAI client initialized successfully")
except Exception as e:
    logger.error(f"Error initializing OpenAI client: {e}")
    client = None


def generate_diagnostic_response(query, brand, model, detailed=False):
    """
    Generate a diagnostic response based on user query about car problems.
    
    Args:
        query (str): User's description of the car problem
        brand (str): Car brand (e.g., "Mercedes", "BMW")
        model (str): Car model (e.g., "S-Class", "3 Series")
        detailed (bool): Whether to provide a detailed response
        
    Returns:
        dict: JSON response with diagnostic information
    """
    if not client:
        # Fallback response if OpenAI client is not available
        return {
            "results": [
                {
                    "problem": f"Issue with {brand} {model}",
                    "solution": f"Unable to generate AI diagnostic response. Please contact support for assistance with your {brand} {model} issue."
                }
            ]
        }
    
    try:
        detail_level = "detailed and comprehensive" if detailed else "concise but informative"
        
        system_prompt = f"""
        You are an expert automotive diagnostic AI specializing in luxury vehicles. 
        You have deep knowledge of {brand} {model} vehicles and their common issues.
        
        Provide a {detail_level} diagnostic response to the user's car problem.
        Structure your response in valid JSON format with the following structure:
        {{
            "results": [
                {{
                    "problem": "Clear title of the diagnosed problem",
                    "problem_severity": "Critical"|"Warning"|"Minor",
                    "solution": "Detailed solution steps or recommendations",
                    "estimated_cost": "Cost range in $ (e.g., $50-$200)",
                    "diy_possible": true|false,
                    "additional_info": "Optional additional information or context"
                }},
                // Add more potential issues if applicable
            ],
            "follow_up_questions": [
                "Question 1?",
                "Question 2?"
            ]
        }}
        
        Base your diagnostic response on the best available information for this specific
        brand and model. Be accurate, professional, and helpful.
        """
        
        user_prompt = f"I have a problem with my {brand} {model}: {query}"
        
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.5,
            response_format={"type": "json_object"}
        )
        
        # Parse JSON response
        result = json.loads(response.choices[0].message.content)
        return result
        
    except Exception as e:
        logger.error(f"Error generating diagnostic response: {e}")
        return {
            "results": [
                {
                    "problem": "Diagnostic Service Error",
                    "problem_severity": "Warning",
                    "solution": f"We encountered an error analyzing your {brand} {model} issue. Please try again or contact our service center directly.",
                    "estimated_cost": "Unknown",
                    "diy_possible": False,
                    "additional_info": "Our technical team has been notified of this issue."
                }
            ],
            "follow_up_questions": [
                "Would you like to speak with a human technician?",
                "Would you like to schedule an appointment for an in-person diagnosis?"
            ]
        }


def generate_maintenance_tips(brand, model, year=None):
    """
    Generate proactive maintenance tips for a specific vehicle
    
    Args:
        brand (str): Car brand
        model (str): Car model
        year (str, optional): Car year
        
    Returns:
        list: List of maintenance tips
    """
    if not client:
        return ["Regular maintenance recommended", "Check with your service center for details"]
    
    try:
        year_info = f" {year}" if year else ""
        
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are an automotive maintenance expert. Provide 3-5 specific maintenance tips as a JSON array of strings."},
                {"role": "user", "content": f"Give me specific maintenance tips for a{year_info} {brand} {model}."}
            ],
            temperature=0.5,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        return result.get("tips", ["Regular service is recommended", "Keep fluids topped off", "Check tire pressure monthly"])
        
    except Exception as e:
        logger.error(f"Error generating maintenance tips: {e}")
        return ["Regular service is recommended", "Keep fluids topped off", "Check tire pressure monthly"]


def generate_related_issues(brand, model, primary_issue):
    """
    Generate related issues that might be connected to the primary issue
    
    Args:
        brand (str): Car brand
        model (str): Car model
        primary_issue (str): The main issue reported
        
    Returns:
        list: List of related issues
    """
    if not client:
        return []
    
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are an automotive diagnostic expert. Return 2-3 related issues that might be connected to the primary issue as a JSON array of objects with 'issue' and 'description' fields."},
                {"role": "user", "content": f"What issues are commonly related to '{primary_issue}' on a {brand} {model}?"}
            ],
            temperature=0.5,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        return result.get("related_issues", [])
        
    except Exception as e:
        logger.error(f"Error generating related issues: {e}")
        return []