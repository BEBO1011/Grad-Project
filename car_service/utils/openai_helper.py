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
    Generate a comprehensive diagnostic response based on user query about car problems.
    
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
        You are an expert automotive diagnostic AI specializing in luxury vehicles with over 30 years of experience. 
        You have deep knowledge of {brand} {model} vehicles and their common issues, including model-specific problems
        and manufacturer service bulletins.
        
        Provide a {detail_level} diagnostic response to the user's car problem with extreme accuracy and specificity.
        Use real part names, specific error codes, and professionally-oriented technical terminology when appropriate.
        
        Structure your response in valid JSON format with the following structure:
        {{
            "results": [
                {{
                    "problem": "Clear title of the diagnosed problem",
                    "problem_severity": "Critical"|"Warning"|"Minor",
                    "solution": "Detailed solution steps or recommendations",
                    "estimated_cost": "Cost range in $ (e.g., $50-$200)",
                    "diy_possible": true|false,
                    "tools_required": ["Tool 1", "Tool 2", "etc"],
                    "time_estimate": "Expected time to fix (e.g. '30 min', '2-3 hours')",
                    "parts_needed": ["Part 1", "Part 2", "etc"],
                    "additional_info": "Optional additional information or context"
                }},
                // Add 1-2 more potential issues if there could be multiple causes
            ],
            "follow_up_questions": [
                "Question 1?",
                "Question 2?",
                "Question 3?"
            ]
        }}
        
        Make sure to:
        1. Include all relevant specific part names for the {brand} {model}
        2. Provide accurate cost estimates based on genuine parts and professional labor rates
        3. Be specific about which problems can be fixed at home (DIY) vs requiring professional help
        4. Provide detailed diagnostic steps where appropriate
        5. Focus on the most likely issues based on the symptoms described
        6. Include any known Technical Service Bulletins (TSBs) or recalls if relevant
        
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
            temperature=0.4,  # Lower temperature for more consistent, factual responses
            response_format={"type": "json_object"},
            max_tokens=1200   # Allow for longer, more detailed responses
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
        
        system_prompt = f"""
        You are a certified master technician specializing in {brand} vehicles with 25+ years of experience.
        Provide 4-6 specific, actionable maintenance tips for a{year_info} {brand} {model}.
        
        Your tips should:
        1. Include model-specific advice that owners may not know
        2. Reference specific maintenance intervals when applicable
        3. Mention any common issues that preventative maintenance can help avoid
        4. Include specific fluids or parts recommended by the manufacturer
        5. Provide practical tips that a vehicle owner can understand and act upon
        
        Return your response as a JSON object with a "tips" array of detailed maintenance tip strings.
        Format each tip to be concise but informative with specific details.
        """
        
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"What are the most important maintenance tips for a{year_info} {brand} {model} that will keep it running at peak performance and prevent common issues?"}
            ],
            temperature=0.4,
            response_format={"type": "json_object"},
            max_tokens=800
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
        system_prompt = f"""
        You are a diagnostic expert specializing in {brand} vehicles with comprehensive knowledge of their 
        interconnected systems. When a {brand} {model} has a particular issue, you can identify other 
        related problems that may be connected due to:
        
        1. Shared components or systems
        2. Cascading failures where one issue causes another
        3. Common underlying root causes
        4. Typical wear patterns that occur together
        5. Model-specific failure points
        
        For the issue described, provide 2-3 related problems that an owner should check or be aware of.
        Each related issue should:
        - Be specifically related to the primary issue
        - Include early warning signs to watch for
        - Explain why/how it's connected to the primary issue
        - Be relevant specifically to this {brand} {model}
        
        Return the results as a JSON array of objects with 'issue' and 'description' fields in a 'related_issues' object.
        """
        
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"When a {brand} {model} has the following problem: '{primary_issue}', what other related issues should the owner check or be aware of?"}
            ],
            temperature=0.4,
            response_format={"type": "json_object"},
            max_tokens=800
        )
        
        result = json.loads(response.choices[0].message.content)
        return result.get("related_issues", [])
        
    except Exception as e:
        logger.error(f"Error generating related issues: {e}")
        return []