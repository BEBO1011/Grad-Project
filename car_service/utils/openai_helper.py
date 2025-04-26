"""
OpenAI integration for AI-powered car diagnostics
"""
import os
import json
import logging
import random
import time
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check if OpenAI API Key is available
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
has_openai_access = OPENAI_API_KEY is not None

# Variables for keeping track of OpenAI availability
OPENAI_AVAILABLE = False
client = None

# Try to import and set up OpenAI
try:
    import openai
    from openai import OpenAI
    OPENAI_AVAILABLE = True
    logger.info("OpenAI module imported successfully!")
    
    # Initialize client if we have an API key
    if has_openai_access:
        try:
            client = OpenAI(api_key=OPENAI_API_KEY)
            logger.info("OpenAI client initialized successfully!")
        except Exception as e:
            logger.error(f"Error initializing OpenAI client: {e}")
    else:
        logger.warning("OpenAI API key not found in environment variables")
except ImportError:
    logger.warning("OpenAI module import failed. Using fallback diagnostics.")

# Sample diagnostic data for common car problems
SAMPLE_DIAGNOSTICS = {
    "engine": {
        "oil_pressure": {
            "problem": "Low Engine Oil Pressure",
            "problem_severity": "Critical",
            "solution": "Your engine is experiencing dangerously low oil pressure which can cause severe engine damage if not addressed immediately. Check your oil level and refill if necessary. If the problem persists, visit a mechanic as soon as possible to inspect for oil leaks, worn oil pump, or damaged engine bearings.",
            "estimated_cost": "$150-$1,500",
            "diy_possible": False
        },
        "coolant_temp": {
            "problem": "Engine Overheating",
            "problem_severity": "Critical",
            "solution": "Your engine is overheating, which can lead to severe engine damage. Check coolant levels and inspect for leaks. Ensure the radiator fan is working properly. If these initial checks don't resolve the issue, have your cooling system professionally inspected.",
            "estimated_cost": "$100-$1,200",
            "diy_possible": False
        },
        "rpm": {
            "problem": "Irregular Engine RPM",
            "problem_severity": "Warning",
            "solution": "Your engine is showing irregular RPM patterns, which could indicate issues with the fuel delivery system, spark plugs, or idle control valve. A diagnostic scan is recommended to pinpoint the exact cause.",
            "estimated_cost": "$80-$350",
            "diy_possible": True
        }
    },
    "battery": {
        "voltage": {
            "problem": "Low Battery Voltage",
            "problem_severity": "Warning",
            "solution": "Your battery is showing lower than normal voltage. This could indicate a failing battery or issues with the charging system. Check battery terminals for corrosion and test the alternator output.",
            "estimated_cost": "$150-$400",
            "diy_possible": True
        }
    },
    "transmission": {
        "temp": {
            "problem": "Transmission Overheating",
            "problem_severity": "Critical",
            "solution": "Your transmission is operating at dangerously high temperatures. This can lead to premature transmission failure. Check transmission fluid levels and condition. Avoid towing or heavy loads until resolved.",
            "estimated_cost": "$200-$2,500",
            "diy_possible": False
        }
    },
    "brakes": {
        "pad_thickness": {
            "problem": "Critically Worn Brake Pads",
            "problem_severity": "Critical",
            "solution": "Your brake pads are critically worn and need immediate replacement. Continuing to drive with worn brake pads can damage the rotors and compromise braking performance.",
            "estimated_cost": "$150-$400",
            "diy_possible": True
        }
    },
    "tires": {
        "pressure": {
            "problem": "Low Tire Pressure",
            "problem_severity": "Warning",
            "solution": "One or more of your tires is operating below the recommended pressure. This affects fuel efficiency, handling, and tire lifespan. Inflate to the manufacturer's recommended PSI.",
            "estimated_cost": "$0-$5",
            "diy_possible": True
        }
    },
    "fuel": {
        "pressure": {
            "problem": "Low Fuel Pressure",
            "problem_severity": "Warning",
            "solution": "Your fuel system is operating below the optimal pressure range. This can lead to poor engine performance, misfires, and reduced power. Check the fuel pump, filter, and pressure regulator.",
            "estimated_cost": "$100-$800",
            "diy_possible": False
        },
        "oxygen_sensor": {
            "problem": "Faulty Oxygen Sensor",
            "problem_severity": "Warning",
            "solution": "Your oxygen sensor readings indicate it may be failing. This affects fuel efficiency and emissions. A diagnostic scan can confirm which sensor needs replacement.",
            "estimated_cost": "$150-$500",
            "diy_possible": True
        }
    }
}

# Common follow-up questions based on problem type
FOLLOW_UP_QUESTIONS = {
    "engine": [
        "When was your last oil change?",
        "Have you noticed any unusual engine noises?",
        "Has the check engine light come on recently?",
        "Have you noticed any fluid leaks under your vehicle?"
    ],
    "battery": [
        "How old is your current battery?",
        "Do you have difficulty starting the vehicle?",
        "Have you noticed dimming headlights or other electrical issues?"
    ],
    "transmission": [
        "Have you noticed any hesitation or jerking during gear shifts?",
        "When was the transmission fluid last changed?",
        "Do you often tow heavy loads with your vehicle?"
    ],
    "brakes": [
        "Have you heard any squealing or grinding from the brakes?",
        "Do you feel any vibration when braking?",
        "Does the vehicle pull to one side when braking?"
    ],
    "tires": [
        "When was the last time you rotated your tires?",
        "Have you noticed uneven tire wear?",
        "Have you recently hit any potholes or curbs?"
    ],
    "fuel": [
        "Have you noticed decreased fuel efficiency?",
        "Does the engine hesitate during acceleration?",
        "What grade of fuel do you typically use?"
    ]
}

# Common maintenance tips
MAINTENANCE_TIPS = [
    "Regular oil changes every 5,000-7,500 miles",
    "Rotate tires every 6,000-8,000 miles",
    "Replace air filter annually",
    "Check fluid levels monthly",
    "Keep tires properly inflated",
    "Clean battery terminals periodically",
    "Replace wiper blades twice a year",
    "Follow your vehicle's maintenance schedule",
    "Address warning lights promptly",
    "Use the recommended grade of fuel and oil"
]

def generate_diagnostic_response(issue_description: str, brand: str = "", model: str = "", detailed: bool = False) -> Dict[str, Any]:
    """
    Generate an AI-powered diagnostic response based on issue description
    
    Args:
        issue_description: Description of the car issue
        brand: Car brand/manufacturer
        model: Car model
        detailed: Whether to return a detailed response
    
    Returns:
        Dictionary containing diagnostic information
    """
    try:
        # If OpenAI API is available, use it
        if has_openai_access:
            try:
                return generate_openai_diagnostic(issue_description, brand, model, detailed)
            except Exception as e:
                logger.error(f"Error using OpenAI API: {e}")
                # Fall back to rule-based diagnostics if OpenAI fails
                logger.info("Falling back to rule-based diagnostics")
        
        # Use rule-based diagnostics
        return generate_rule_based_diagnostic(issue_description, brand, model, detailed)
        
    except Exception as e:
        logger.error(f"Error generating diagnostic response: {e}")
        # Return basic fallback response in case of errors
        return {
            "results": [
                {
                    "problem": "Car Issue Analysis",
                    "problem_severity": "Unknown",
                    "solution": "Based on the description provided, we recommend consulting a certified technician for a proper diagnosis.",
                    "estimated_cost": "Varies",
                    "diy_possible": False
                }
            ],
            "follow_up_questions": [
                "When did you first notice this issue?",
                "Has a mechanic looked at this problem before?"
            ],
            "maintenance_tips": random.sample(MAINTENANCE_TIPS, 3)
        }

def generate_openai_diagnostic(issue_description: str, brand: str, model: str, detailed: bool) -> Dict[str, Any]:
    """
    Generate diagnostic response using OpenAI API
    
    Args:
        issue_description: Description of the car issue
        brand: Car brand/manufacturer
        model: Car model
        detailed: Whether to return a detailed response
    
    Returns:
        Dictionary containing AI-generated diagnostic information
    """
    try:
        # Use the global client that was initialized earlier
        global client
        if client is None:
            logger.error("OpenAI client not initialized")
            raise Exception("OpenAI client not initialized")
            
        # Check if API key is valid and has quota remaining
        if not OPENAI_API_KEY or OPENAI_API_KEY.startswith("sk-dummy"):
            logger.warning("Using dummy or invalid OpenAI API key")
            raise Exception("Invalid OpenAI API key configuration")
        
        # Construct system prompt
        system_prompt = """
        You are an expert automotive diagnostic assistant specializing in identifying car problems and providing solutions.
        
        Analyze the vehicle issue description and provide a detailed assessment with the following information in JSON format:
        
        1. results: array of potential issues, each containing:
           - problem: clear name of the identified problem
           - problem_severity: severity level ("Critical", "Warning", or "Minor")
           - solution: detailed explanation and repair instructions
           - estimated_cost: cost range for repairs
           - diy_possible: boolean indicating if it's a DIY repair
           - time_estimate: optional time required for repairs
        
        2. follow_up_questions: array of 2-3 relevant questions to further diagnose the issue
        
        3. maintenance_tips: array of 3-5 maintenance recommendations related to this issue
        
        Format your response as valid JSON.
        """
        
        # Construct user prompt
        user_prompt = f"Vehicle: {brand} {model}\nIssue: {issue_description}"
        
        # Make the API call
        response = client.chat.completions.create(
            model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.5,
            max_tokens=1500
        )
        
        # Parse the response
        result = json.loads(response.choices[0].message.content)
        
        # Ensure the response has the expected structure
        if "results" not in result:
            result["results"] = []
        if "follow_up_questions" not in result:
            result["follow_up_questions"] = []
        if "maintenance_tips" not in result:
            result["maintenance_tips"] = []
        
        return result
        
    except Exception as e:
        error_str = str(e)
        logger.error(f"Error generating OpenAI diagnostic: {e}")
        
        # Handle specific error types with better messaging
        if "quota" in error_str.lower() or "insufficient_quota" in error_str:
            logger.error("OpenAI API quota exceeded. Using fallback diagnostics.")
            # For quota issues, raise a specific exception type
            raise Exception("OpenAI API quota exceeded. Please check your API key and usage limits.")
        elif "invalid" in error_str.lower() and "api key" in error_str.lower():
            logger.error("Invalid API key configuration")
            raise Exception("Invalid OpenAI API key. Please check your API key configuration.")
        else:
            # For other errors, just pass through the original exception
            raise e

def generate_rule_based_diagnostic(issue_description: str, brand: str, model: str, detailed: bool) -> Dict[str, Any]:
    """
    Generate diagnostic response using rule-based approach
    
    Args:
        issue_description: Description of the car issue
        brand: Car brand/manufacturer
        model: Car model
        detailed: Whether to return a detailed response
    
    Returns:
        Dictionary containing diagnostic information based on rules
    """
    issue_description = issue_description.lower()
    results = []
    problem_types = []
    
    # Check for engine-related keywords
    if any(keyword in issue_description for keyword in ['oil', 'pressure', 'engine', 'overheat', 'temperature', 'coolant', 'rpm', 'idle']):
        problem_types.append('engine')
        
        if 'oil' in issue_description or 'pressure' in issue_description:
            results.append(SAMPLE_DIAGNOSTICS['engine']['oil_pressure'])
        
        if 'overheat' in issue_description or 'temperature' in issue_description or 'coolant' in issue_description:
            results.append(SAMPLE_DIAGNOSTICS['engine']['coolant_temp'])
        
        if 'rpm' in issue_description or 'idle' in issue_description:
            results.append(SAMPLE_DIAGNOSTICS['engine']['rpm'])
    
    # Check for battery-related keywords
    if any(keyword in issue_description for keyword in ['battery', 'volt', 'electrical', 'start', 'charge']):
        problem_types.append('battery')
        results.append(SAMPLE_DIAGNOSTICS['battery']['voltage'])
    
    # Check for transmission-related keywords
    if any(keyword in issue_description for keyword in ['transmission', 'gear', 'shift']):
        problem_types.append('transmission')
        results.append(SAMPLE_DIAGNOSTICS['transmission']['temp'])
    
    # Check for brake-related keywords
    if any(keyword in issue_description for keyword in ['brake', 'stop', 'pedal']):
        problem_types.append('brakes')
        results.append(SAMPLE_DIAGNOSTICS['brakes']['pad_thickness'])
    
    # Check for tire-related keywords
    if any(keyword in issue_description for keyword in ['tire', 'wheel', 'pressure', 'flat']):
        problem_types.append('tires')
        results.append(SAMPLE_DIAGNOSTICS['tires']['pressure'])
    
    # Check for fuel-related keywords
    if any(keyword in issue_description for keyword in ['fuel', 'gas', 'injection', 'misfire', 'oxygen']):
        problem_types.append('fuel')
        
        if 'pressure' in issue_description:
            results.append(SAMPLE_DIAGNOSTICS['fuel']['pressure'])
        
        if 'oxygen' in issue_description or 'sensor' in issue_description:
            results.append(SAMPLE_DIAGNOSTICS['fuel']['oxygen_sensor'])
    
    # If no specific problems were found, return a generic response
    if not results:
        results.append({
            "problem": "General Vehicle Issue",
            "problem_severity": "Unknown",
            "solution": f"Based on the description provided for your {brand} {model}, we recommend a comprehensive diagnostic scan. The information provided isn't specific enough to pinpoint the exact issue. Consider visiting a certified technician for proper diagnosis.",
            "estimated_cost": "Varies",
            "diy_possible": False
        })
        problem_types = ["general"]
    
    # Gather follow-up questions
    follow_up_questions = []
    for problem_type in problem_types:
        if problem_type in FOLLOW_UP_QUESTIONS:
            follow_up_questions.extend(random.sample(FOLLOW_UP_QUESTIONS[problem_type], min(2, len(FOLLOW_UP_QUESTIONS[problem_type]))))
    
    # If we have fewer than 3 questions, add some general ones
    general_questions = [
        "When did you first notice this issue?",
        "Does the issue occur under specific conditions?",
        "Has a mechanic examined this before?"
    ]
    
    if len(follow_up_questions) < 3:
        additional_needed = 3 - len(follow_up_questions)
        follow_up_questions.extend(random.sample(general_questions, min(additional_needed, len(general_questions))))
    
    # Get maintenance tips
    maintenance_tips = random.sample(MAINTENANCE_TIPS, 5)
    
    # Add specific maintenance tips based on problem types
    if 'engine' in problem_types:
        maintenance_tips.insert(0, "Check oil level and condition regularly")
    if 'transmission' in problem_types:
        maintenance_tips.insert(0, "Have transmission fluid changed every 30,000-60,000 miles")
    if 'brakes' in problem_types:
        maintenance_tips.insert(0, "Inspect brake pads and rotors every 10,000 miles")
    if 'tires' in problem_types:
        maintenance_tips.insert(0, "Check tire pressure monthly and before long trips")
    
    # Assemble the response
    return {
        "results": results,
        "follow_up_questions": follow_up_questions[:3],  # Limit to 3 questions
        "maintenance_tips": maintenance_tips[:5]  # Limit to 5 tips
    }

def generate_maintenance_tips(brand: str, model: str) -> List[str]:
    """
    Generate maintenance tips based on car brand and model
    
    Args:
        brand: Car brand/manufacturer
        model: Car model
        
    Returns:
        List of maintenance tips
    """
    # Generic maintenance tips
    generic_tips = [
        "Regular oil changes every 5,000-7,500 miles",
        "Rotate tires every 6,000-8,000 miles",
        "Replace air filter annually",
        "Check fluid levels monthly",
        "Keep tires properly inflated",
        "Clean battery terminals periodically",
        "Replace wiper blades twice a year",
        "Follow your vehicle's maintenance schedule",
        "Address warning lights promptly",
        "Use the recommended grade of fuel and oil"
    ]
    
    # Brand-specific tips
    brand_tips = {
        "Mercedes": [
            "Use only synthetic oil specifically recommended for Mercedes engines",
            "Check AdBlue levels regularly if your model has a diesel engine",
            "Monitor air suspension system for proper operation"
        ],
        "BMW": [
            "Check for coolant leaks around the expansion tank",
            "Monitor valve cover gasket for oil leaks",
            "Have the VANOS system inspected regularly"
        ],
        "Audi": [
            "Inspect timing chain tensioners regularly on older models",
            "Check DSG transmission fluid at recommended intervals",
            "Monitor PCV system for potential issues"
        ],
        "Toyota": [
            "Inspect water pump and timing belt on older models",
            "Check hybrid battery health if applicable",
            "Monitor transmission fluid condition"
        ],
        "Fiat": [
            "Check for oil consumption between services",
            "Monitor clutch wear if manual transmission",
            "Inspect suspension components regularly"
        ]
    }
    
    # Select tips
    selected_tips = random.sample(generic_tips, 3)
    
    # Add brand-specific tips if available
    if brand in brand_tips:
        selected_tips.extend(random.sample(brand_tips[brand], min(2, len(brand_tips[brand]))))
    
    return selected_tips

def generate_related_issues(brand: str, model: str, problem: str) -> List[Dict[str, str]]:
    """
    Generate related issues based on the current problem
    
    Args:
        brand: Car brand/manufacturer
        model: Car model
        problem: Current problem description
        
    Returns:
        List of related issues
    """
    # Common related issues by system
    related_issues_by_system = {
        "engine": [
            {
                "issue": "Oil Leaks",
                "description": "Oil leaks from the valve cover gasket, oil pan, or timing cover can lead to low oil pressure and engine damage."
            },
            {
                "issue": "Coolant Leaks",
                "description": "Coolant leaks from hoses, the radiator, or water pump can cause engine overheating."
            },
            {
                "issue": "Timing Belt/Chain Failure",
                "description": "A worn timing belt/chain can lead to engine misfires, poor performance, or catastrophic engine damage."
            }
        ],
        "battery": [
            {
                "issue": "Alternator Problems",
                "description": "A failing alternator can lead to battery drainage and electrical system issues."
            },
            {
                "issue": "Corroded Battery Terminals",
                "description": "Corrosion on battery terminals can prevent proper charging and cause starting issues."
            },
            {
                "issue": "Parasitic Drain",
                "description": "Electrical components drawing power when the car is off can drain the battery."
            }
        ],
        "transmission": [
            {
                "issue": "Fluid Leaks",
                "description": "Transmission fluid leaks can lead to overheating and gear slippage."
            },
            {
                "issue": "Torque Converter Issues",
                "description": "A failing torque converter can cause shuddering, slipping, or overheating."
            },
            {
                "issue": "Solenoid Problems",
                "description": "Faulty transmission solenoids can cause irregular shifting or transmission failure."
            }
        ],
        "brakes": [
            {
                "issue": "Warped Rotors",
                "description": "Warped brake rotors can cause vibration when braking and reduced braking efficiency."
            },
            {
                "issue": "Brake Fluid Leaks",
                "description": "Brake fluid leaks can lead to spongy brake pedal feel and brake failure."
            },
            {
                "issue": "Caliper Sticking",
                "description": "Stuck brake calipers can cause uneven pad wear and pull to one side when braking."
            }
        ],
        "tires": [
            {
                "issue": "Alignment Problems",
                "description": "Poor wheel alignment can cause uneven tire wear and pulling to one side."
            },
            {
                "issue": "Suspension Wear",
                "description": "Worn suspension components can lead to uneven tire wear and poor handling."
            },
            {
                "issue": "Valve Stem Leaks",
                "description": "Leaking valve stems can cause gradual tire pressure loss."
            }
        ],
        "fuel": [
            {
                "issue": "Clogged Fuel Injectors",
                "description": "Clogged injectors can cause rough idling, misfires, and reduced fuel efficiency."
            },
            {
                "issue": "Failing Fuel Pump",
                "description": "A failing fuel pump can cause engine sputtering, stalling, or failure to start."
            },
            {
                "issue": "Dirty Fuel Filter",
                "description": "A clogged fuel filter can restrict fuel flow and cause performance issues."
            }
        ]
    }
    
    # Determine which system the problem relates to
    problem_lower = problem.lower()
    detected_system = None
    
    if any(keyword in problem_lower for keyword in ["oil", "engine", "overheat", "coolant", "temperature"]):
        detected_system = "engine"
    elif any(keyword in problem_lower for keyword in ["battery", "electrical", "volt", "charge"]):
        detected_system = "battery"
    elif any(keyword in problem_lower for keyword in ["transmission", "gear", "shift"]):
        detected_system = "transmission"
    elif any(keyword in problem_lower for keyword in ["brake", "stop", "pedal"]):
        detected_system = "brakes"
    elif any(keyword in problem_lower for keyword in ["tire", "wheel", "pressure"]):
        detected_system = "tires"
    elif any(keyword in problem_lower for keyword in ["fuel", "gas", "injection"]):
        detected_system = "fuel"
    
    # If no system detected, return a random selection of issues
    if not detected_system:
        all_issues = []
        for system_issues in related_issues_by_system.values():
            all_issues.extend(system_issues)
        return random.sample(all_issues, min(3, len(all_issues)))
    
    # Return related issues for the detected system
    return related_issues_by_system[detected_system]