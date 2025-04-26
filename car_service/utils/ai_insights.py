"""
AI-powered insights and anomaly detection for vehicle diagnostics.
This module analyzes vehicle data to provide intelligent insights and detect anomalies.
"""
import os
import json
import logging
import random
import datetime
from typing import Dict, List, Any, Optional, Tuple, Union

# Import OpenAI helper
from utils.openai_helper import generate_diagnostic_response

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants for anomaly thresholds
THRESHOLDS = {
    'oil_pressure': {'min': 10, 'max': 80, 'unit': 'psi'},
    'coolant_temp': {'min': 75, 'max': 105, 'unit': '°C'},
    'battery_voltage': {'min': 11.5, 'max': 14.5, 'unit': 'V'},
    'fuel_pressure': {'min': 35, 'max': 65, 'unit': 'psi'},
    'engine_rpm': {'min': 600, 'max': 7000, 'unit': 'RPM'},
    'tire_pressure': {'min': 28, 'max': 36, 'unit': 'psi'},
    'brake_pad_thickness': {'min': 3, 'max': 12, 'unit': 'mm'},
    'transmission_temp': {'min': 70, 'max': 95, 'unit': '°C'},
    'fuel_level': {'min': 10, 'max': 100, 'unit': '%'},
    'oxygen_sensor': {'min': 0.1, 'max': 0.9, 'unit': 'V'}
}

# Vehicle data patterns for different vehicle conditions
VEHICLE_PATTERNS = {
    'normal': {
        'oil_pressure': {'base': 45, 'variance': 5},
        'coolant_temp': {'base': 88, 'variance': 5},
        'battery_voltage': {'base': 13.8, 'variance': 0.3},
        'fuel_pressure': {'base': 50, 'variance': 5},
        'engine_rpm': {'base': 800, 'variance': 100},
        'tire_pressure': {'base': 32, 'variance': 1},
        'brake_pad_thickness': {'base': 8, 'variance': 1},
        'transmission_temp': {'base': 80, 'variance': 5},
        'fuel_level': {'base': 65, 'variance': 15},
        'oxygen_sensor': {'base': 0.5, 'variance': 0.2}
    },
    'oil_issue': {
        'oil_pressure': {'base': 15, 'variance': 5},
        'coolant_temp': {'base': 90, 'variance': 5},
        'engine_rpm': {'base': 850, 'variance': 150}
    },
    'battery_issue': {
        'battery_voltage': {'base': 10.8, 'variance': 0.5},
        'engine_rpm': {'base': 750, 'variance': 200}
    },
    'cooling_issue': {
        'coolant_temp': {'base': 110, 'variance': 8},
        'engine_rpm': {'base': 850, 'variance': 100}
    },
    'brake_issue': {
        'brake_pad_thickness': {'base': 2.5, 'variance': 0.5}
    },
    'tire_issue': {
        'tire_pressure': {'base': 24, 'variance': 3}
    },
    'fuel_issue': {
        'fuel_pressure': {'base': 30, 'variance': 5},
        'engine_rpm': {'base': 780, 'variance': 150},
        'oxygen_sensor': {'base': 0.3, 'variance': 0.1}
    },
    'transmission_issue': {
        'transmission_temp': {'base': 105, 'variance': 8},
        'engine_rpm': {'base': 850, 'variance': 200}
    }
}

def get_sensor_data(vehicle_id: str, condition: str = 'normal') -> Dict[str, Any]:
    """
    Generate realistic sensor data for a vehicle based on its condition.
    
    Args:
        vehicle_id: The unique identifier for the vehicle
        condition: The vehicle's condition ('normal' or a specific issue)
    
    Returns:
        A dictionary containing sensor readings and metadata
    """
    # Use a pattern based on condition, defaulting to normal
    pattern = VEHICLE_PATTERNS.get(condition, VEHICLE_PATTERNS['normal'])
    
    # Start with normal data for all sensors
    normal_pattern = VEHICLE_PATTERNS['normal']
    data = {}
    
    # Add timestamp
    now = datetime.datetime.now()
    data['timestamp'] = now.isoformat()
    data['vehicle_id'] = vehicle_id
    data['readings'] = {}
    
    # Generate readings for all sensors with normal pattern
    for sensor, params in normal_pattern.items():
        # If this sensor is affected by the condition, use that pattern instead
        if sensor in pattern:
            base = pattern[sensor]['base']
            variance = pattern[sensor]['variance']
        else:
            base = params['base']
            variance = params['variance']
        
        # Generate value with some randomness
        value = base + (random.random() * 2 - 1) * variance
        
        # Add unit information
        data['readings'][sensor] = {
            'value': round(value, 2),
            'unit': THRESHOLDS[sensor]['unit']
        }
    
    return data

def detect_anomalies(sensor_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Analyze sensor data to detect anomalies based on predefined thresholds.
    
    Args:
        sensor_data: Dictionary of sensor readings with metadata
    
    Returns:
        List of detected anomalies with severity and recommendations
    """
    anomalies = []
    readings = sensor_data.get('readings', {})
    
    for sensor, reading in readings.items():
        if sensor in THRESHOLDS:
            value = reading['value']
            thresholds = THRESHOLDS[sensor]
            
            # Check if value is outside thresholds
            if value < thresholds['min'] or value > thresholds['max']:
                severity = "critical" if (value < thresholds['min'] * 0.8 or value > thresholds['max'] * 1.2) else "warning"
                
                anomaly = {
                    'sensor': sensor,
                    'current_value': value,
                    'unit': thresholds['unit'],
                    'expected_range': f"{thresholds['min']} - {thresholds['max']} {thresholds['unit']}",
                    'severity': severity,
                    'timestamp': sensor_data.get('timestamp')
                }
                
                # Generate recommendations based on the sensor
                if sensor == 'oil_pressure':
                    if value < thresholds['min']:
                        anomaly['recommendation'] = "Check oil level and refill if necessary. If problem persists, inspect for oil leaks or engine damage."
                    else:
                        anomaly['recommendation'] = "High oil pressure detected. Check oil viscosity and possible blockage in the oil system."
                
                elif sensor == 'coolant_temp':
                    if value > thresholds['max']:
                        anomaly['recommendation'] = "Engine overheating. Check coolant level, radiator function, and water pump. Stop driving if temperature continues to rise."
                    else:
                        anomaly['recommendation'] = "Engine temperature too low. Check thermostat function."
                
                elif sensor == 'battery_voltage':
                    if value < thresholds['min']:
                        anomaly['recommendation'] = "Low battery voltage. Check charging system, alternator, and battery condition."
                    else:
                        anomaly['recommendation'] = "High battery voltage. Check voltage regulator and charging system."
                
                elif sensor == 'tire_pressure':
                    if value < thresholds['min']:
                        anomaly['recommendation'] = "Low tire pressure. Inflate tires to recommended PSI and check for leaks."
                    else:
                        anomaly['recommendation'] = "High tire pressure. Reduce to manufacturer recommended PSI."
                
                elif sensor == 'brake_pad_thickness':
                    if value < thresholds['min']:
                        anomaly['recommendation'] = "Brake pads critically worn. Replace immediately for safety."
                    
                elif sensor == 'fuel_pressure':
                    if value < thresholds['min']:
                        anomaly['recommendation'] = "Low fuel pressure. Check fuel pump, filter, and pressure regulator."
                    else:
                        anomaly['recommendation'] = "High fuel pressure. Inspect pressure regulator and fuel system."
                
                elif sensor == 'transmission_temp':
                    if value > thresholds['max']:
                        anomaly['recommendation'] = "Transmission overheating. Check fluid level and condition. Avoid towing or heavy loads until resolved."
                
                elif sensor == 'oxygen_sensor':
                    anomaly['recommendation'] = "Oxygen sensor readings out of range. Check for exhaust leaks, fuel mixture issues, or sensor failure."
                
                else:
                    anomaly['recommendation'] = f"Abnormal {sensor} reading. Schedule inspection with a qualified technician."
                
                anomalies.append(anomaly)
    
    return anomalies

def get_ai_analysis(vehicle_data: Dict[str, Any], anomalies: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate AI-powered analysis of vehicle data and anomalies.
    
    Args:
        vehicle_data: Dictionary containing vehicle information
        anomalies: List of detected anomalies
    
    Returns:
        AI insights and recommendations
    """
    try:
        # Extract relevant information
        brand = vehicle_data.get('brand', '')
        model = vehicle_data.get('model', '')
        
        # Construct a detailed prompt for the AI
        issue_description = ""
        
        # Add information about each anomaly
        for anomaly in anomalies:
            issue_description += f"{anomaly['sensor'].replace('_', ' ').title()}: {anomaly['current_value']} {anomaly['unit']} "
            issue_description += f"(Expected: {anomaly['expected_range']}). "
        
        # If we have anomalies, get AI analysis
        if issue_description:
            # Call OpenAI helper with the constructed prompt
            ai_response = generate_diagnostic_response(issue_description, brand, model, detailed=True)
            return ai_response
        else:
            # No anomalies detected
            return {
                "results": [
                    {
                        "problem": "No anomalies detected",
                        "problem_severity": "Minor",
                        "solution": "Your vehicle is operating within normal parameters. Continue with regular maintenance schedule.",
                        "estimated_cost": "$0",
                        "diy_possible": True
                    }
                ],
                "follow_up_questions": [
                    "When was your last scheduled maintenance?",
                    "Have you noticed any unusual behavior while driving?"
                ],
                "maintenance_tips": [
                    "Regular oil changes every 5,000-7,500 miles",
                    "Rotate tires every 6,000-8,000 miles",
                    "Replace air filter annually",
                    "Check fluid levels monthly"
                ]
            }
            
    except Exception as e:
        logger.error(f"Error generating AI analysis: {e}")
        # Return basic analysis in case of error
        return {
            "results": [
                {
                    "problem": "Diagnostic data analysis",
                    "problem_severity": "Warning" if anomalies else "Minor",
                    "solution": "Based on sensor readings, recommend professional inspection" if anomalies else "No immediate issues detected",
                    "estimated_cost": "Varies" if anomalies else "$0",
                    "diy_possible": False if anomalies else True
                }
            ],
            "follow_up_questions": [
                "When was your last scheduled maintenance?",
                "Have you noticed any unusual behavior while driving?"
            ],
            "maintenance_tips": [
                "Regular oil changes every 5,000-7,500 miles",
                "Rotate tires every 6,000-8,000 miles",
                "Replace air filter annually",
                "Check fluid levels monthly"
            ]
        }

def track_vehicle_patterns(vehicle_id: str, sensor_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Track patterns in vehicle data over time to detect subtle issues.
    
    Args:
        vehicle_id: The unique identifier for the vehicle
        sensor_data: Current sensor readings
    
    Returns:
        Insights based on historical pattern analysis
    """
    # In a production environment, this would retrieve historical data from a database
    # Here we'll simulate a simple pattern detection
    
    # Return simulated insights
    current_hour = datetime.datetime.now().hour
    
    insights = {
        "pattern_insights": [
            {
                "type": "consumption",
                "description": "Fuel consumption increases by 15% during cold morning starts" if current_hour < 10 else "Fuel efficiency optimal during current driving conditions",
                "recommendation": "Allow engine to warm up for 1-2 minutes before driving in cold weather" if current_hour < 10 else "Continue current driving habits"
            },
            {
                "type": "battery",
                "description": "Battery voltage shows optimal charging pattern",
                "recommendation": "No action required"
            },
            {
                "type": "maintenance",
                "description": "Based on mileage and time patterns, maintenance will be due in approximately 2 weeks",
                "recommendation": "Schedule your next service appointment"
            }
        ]
    }
    
    return insights

def get_vehicle_health_score(vehicle_data: Dict[str, Any], anomalies: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate an overall health score for the vehicle based on sensor data and anomalies.
    
    Args:
        vehicle_data: Dictionary containing vehicle information
        anomalies: List of detected anomalies
    
    Returns:
        Health score and component-specific scores
    """
    base_score = 100
    component_scores = {
        "engine": 100,
        "battery": 100,
        "brakes": 100,
        "transmission": 100,
        "tires": 100,
        "fuel_system": 100,
        "cooling_system": 100
    }
    
    # Reduce scores based on anomalies
    for anomaly in anomalies:
        severity_factor = 30 if anomaly['severity'] == 'critical' else 15
        
        # Map sensors to components
        if anomaly['sensor'] == 'oil_pressure' or anomaly['sensor'] == 'engine_rpm':
            component_scores["engine"] -= severity_factor
        elif anomaly['sensor'] == 'battery_voltage':
            component_scores["battery"] -= severity_factor
        elif anomaly['sensor'] == 'brake_pad_thickness':
            component_scores["brakes"] -= severity_factor
        elif anomaly['sensor'] == 'transmission_temp':
            component_scores["transmission"] -= severity_factor
        elif anomaly['sensor'] == 'tire_pressure':
            component_scores["tires"] -= severity_factor
        elif anomaly['sensor'] == 'fuel_pressure' or anomaly['sensor'] == 'oxygen_sensor':
            component_scores["fuel_system"] -= severity_factor
        elif anomaly['sensor'] == 'coolant_temp':
            component_scores["cooling_system"] -= severity_factor
    
    # Ensure no score goes below zero
    for component in component_scores:
        component_scores[component] = max(0, component_scores[component])
    
    # Calculate overall score as an average
    overall_score = sum(component_scores.values()) / len(component_scores)
    
    # Add descriptions based on scores
    score_descriptions = {}
    for component, score in component_scores.items():
        if score >= 90:
            score_descriptions[component] = "Excellent"
        elif score >= 70:
            score_descriptions[component] = "Good"
        elif score >= 50:
            score_descriptions[component] = "Fair"
        elif score >= 30:
            score_descriptions[component] = "Poor"
        else:
            score_descriptions[component] = "Critical"
    
    return {
        "overall_score": round(overall_score, 1),
        "overall_status": get_status_from_score(overall_score),
        "component_scores": component_scores,
        "component_statuses": score_descriptions
    }

def get_status_from_score(score: float) -> str:
    """Helper function to convert numerical score to status text"""
    if score >= 90:
        return "Excellent"
    elif score >= 70:
        return "Good"
    elif score >= 50:
        return "Fair"
    elif score >= 30:
        return "Poor"
    else:
        return "Critical"

def get_complete_vehicle_analysis(vehicle_id: str, brand: str, model: str, year: str, condition: Optional[str] = "") -> Dict[str, Any]:
    """
    Provide a complete analysis of vehicle health including AI insights and anomaly detection.
    
    Args:
        vehicle_id: The unique identifier for the vehicle
        brand: The vehicle brand/manufacturer
        model: The vehicle model
        year: The vehicle year
        condition: Optional specific condition to simulate
    
    Returns:
        Complete vehicle analysis with health score, anomalies, and AI insights
    """
    # Set vehicle metadata
    vehicle_data = {
        'vehicle_id': vehicle_id,
        'brand': brand,
        'model': model,
        'year': year
    }
    
    # Get sensor data based on condition (or random condition)
    if not condition:
        # Randomly decide if we'll return normal data or data with an issue
        conditions = list(VEHICLE_PATTERNS.keys())
        # Higher chance of normal condition
        weights = [0.7] + [(0.3/(len(conditions)-1)) for _ in range(len(conditions)-1)]
        condition = random.choices(conditions, weights=weights, k=1)[0]
    
    sensor_data = get_sensor_data(vehicle_id, condition)
    vehicle_data.update(sensor_data)
    
    # Detect anomalies in the sensor data
    anomalies = detect_anomalies(sensor_data)
    
    # Get AI analysis if anomalies are detected
    ai_analysis = get_ai_analysis(vehicle_data, anomalies)
    
    # Get pattern-based insights
    pattern_insights = track_vehicle_patterns(vehicle_id, sensor_data)
    
    # Calculate health score
    health_score = get_vehicle_health_score(vehicle_data, anomalies)
    
    # Combine all insights into a single response
    return {
        "vehicle_data": vehicle_data,
        "health_scores": health_score,
        "anomalies": anomalies,
        "pattern_insights": pattern_insights.get("pattern_insights", []),
        "ai_diagnostics": ai_analysis
    }