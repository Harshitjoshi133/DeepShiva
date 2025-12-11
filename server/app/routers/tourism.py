from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from typing import List, Optional
import random
import time
from datetime import datetime, timedelta

from ..logging_config import get_logger, ErrorTracker, PerformanceLogger

router = APIRouter()
logger = get_logger("tourism")
error_tracker = ErrorTracker(logger)
performance_logger = PerformanceLogger(logger)

class CrowdStatus(BaseModel):
    shrine: str
    crowd_level: int
    status: str
    last_updated: str
    weather: str
    temperature: int
    accessibility: str

class CarbonRequest(BaseModel):
    distance: float = Field(..., gt=0, description="Distance in kilometers")
    vehicle_type: str = Field(..., description="Type of vehicle")
    passengers: Optional[int] = Field(1, ge=1, le=8, description="Number of passengers")

class CarbonResponse(BaseModel):
    co2_kg: float
    saved_vs_suv: float
    vehicle_type: str
    distance: float
    passengers: int
    co2_per_person: float
    trees_to_offset: int
    cost_savings: float
    recommendations: List[str]

class WeatherInfo(BaseModel):
    shrine: str
    temperature: int
    condition: str
    humidity: int
    visibility: str
    best_visit_time: str

@router.get("/crowd-status", response_model=List[CrowdStatus])
async def get_crowd_status(http_request: Request):
    """
    Returns live crowd status at major shrines with weather and accessibility info.
    
    TODO: Integrate with real-time crowd monitoring system.
    TODO: Add historical data and prediction models.
    TODO: Connect to weather API for real data.
    """
    start_time = time.time()
    request_id = getattr(http_request.state, 'request_id', 'unknown')
    
    logger.info("Crowd status request received", extra={
        "request_id": request_id,
        "endpoint": "/crowd-status"
    })
    
    # Simulate realistic crowd data based on time of day and season
    current_hour = datetime.now().hour
    is_peak_season = datetime.now().month in [4, 5, 6, 9, 10]  # Peak pilgrimage months
    
    # Base crowd levels with time-based variations
    base_crowds = {
        "Kedarnath": 70 if is_peak_season else 40,
        "Badrinath": 60 if is_peak_season else 35,
        "Gangotri": 45 if is_peak_season else 25,
        "Yamunotri": 50 if is_peak_season else 30
    }
    
    # Time-based modifiers (higher crowds during day time)
    time_modifier = 1.0
    if 6 <= current_hour <= 18:  # Day time
        time_modifier = 1.3
    elif 19 <= current_hour <= 21:  # Evening
        time_modifier = 1.1
    else:  # Night/early morning
        time_modifier = 0.7
    
    mock_data = []
    weather_conditions = ["Clear", "Cloudy", "Light Snow", "Sunny"]
    
    for shrine, base_level in base_crowds.items():
        # Add some randomness and time modifier
        crowd_level = min(100, int(base_level * time_modifier + random.randint(-10, 15)))
        
        # Determine status
        if crowd_level < 30:
            status = "Light"
        elif crowd_level < 70:
            status = "Moderate"
        else:
            status = "Heavy"
        
        # Generate realistic weather data
        temp = random.randint(-5, 15) if shrine in ["Kedarnath", "Badrinath"] else random.randint(5, 25)
        weather = random.choice(weather_conditions)
        
        # Accessibility based on weather and crowd
        if weather == "Light Snow" and crowd_level > 80:
            accessibility = "Limited"
        elif crowd_level > 90:
            accessibility = "Restricted"
        else:
            accessibility = "Open"
        
        mock_data.append({
            "shrine": shrine,
            "crowd_level": crowd_level,
            "status": status,
            "last_updated": datetime.now().strftime("%H:%M"),
            "weather": weather,
            "temperature": temp,
            "accessibility": accessibility
        })
    
    # Calculate processing time
    processing_time = (time.time() - start_time) * 1000
    
    # Log successful response
    logger.info("Crowd status data generated", extra={
        "request_id": request_id,
        "shrines_count": len(mock_data),
        "processing_time_ms": round(processing_time, 2),
        "peak_season": is_peak_season
    })
    
    return [CrowdStatus(**item) for item in mock_data]

@router.post("/calculate-carbon", response_model=CarbonResponse)
async def calculate_carbon(request: CarbonRequest, http_request: Request):
    """
    Enhanced carbon footprint calculator with detailed analysis and recommendations.
    
    Emission factors (kg CO2 per km per vehicle):
    - Car: 0.21, Bike: 0.10, Bus: 0.08, EV: 0.05, SUV: 0.30
    """
    start_time = time.time()
    request_id = getattr(http_request.state, 'request_id', 'unknown')
    
    logger.info("Carbon calculation request received", extra={
        "request_id": request_id,
        "distance": request.distance,
        "vehicle_type": request.vehicle_type,
        "passengers": request.passengers
    })
    
    if request.distance <= 0:
        logger.warning("Invalid distance provided", extra={
            "request_id": request_id,
            "distance": request.distance
        })
        raise HTTPException(status_code=400, detail="Distance must be greater than 0")
    
    emission_factors = {
        "car": 0.21,
        "bike": 0.10, 
        "bus": 0.08,
        "ev": 0.05,
        "suv": 0.30,
        "motorcycle": 0.12,
        "train": 0.04,
        "flight": 0.25  # For comparison
    }
    
    vehicle_type_lower = request.vehicle_type.lower()
    if vehicle_type_lower not in emission_factors:
        raise HTTPException(status_code=400, detail=f"Unsupported vehicle type: {request.vehicle_type}")
    
    # Calculate total emissions
    factor = emission_factors[vehicle_type_lower]
    total_co2_kg = request.distance * factor
    
    # Calculate per person emissions
    co2_per_person = total_co2_kg / request.passengers
    
    # Calculate savings vs SUV
    suv_emissions = request.distance * emission_factors["suv"]
    saved_vs_suv = suv_emissions - total_co2_kg
    
    # Calculate trees needed to offset (1 tree absorbs ~22kg CO2/year)
    trees_to_offset = max(1, int(total_co2_kg / 22))
    
    # Calculate cost savings (assuming ₹80/liter fuel, different efficiency)
    fuel_efficiency = {
        "car": 15,      # km/liter
        "bike": 45,     # km/liter
        "bus": 4,       # km/liter (but shared)
        "ev": 100,      # equivalent km/liter
        "suv": 10,      # km/liter
        "motorcycle": 40,
        "train": 200,   # equivalent
        "flight": 3     # equivalent
    }
    
    fuel_cost_per_km = 80 / fuel_efficiency.get(vehicle_type_lower, 15)
    suv_cost_per_km = 80 / fuel_efficiency["suv"]
    cost_savings = (suv_cost_per_km - fuel_cost_per_km) * request.distance
    
    # Generate personalized recommendations
    recommendations = []
    
    if vehicle_type_lower == "car" and request.passengers == 1:
        recommendations.append("Consider carpooling to reduce per-person emissions by up to 75%")
    
    if vehicle_type_lower in ["car", "suv"]:
        recommendations.append("Switch to an EV to reduce emissions by 75%")
        recommendations.append("Use public transport (bus/train) to cut emissions by 60-80%")
    
    if request.distance > 100:
        recommendations.append("For long distances, consider train travel - it's 80% cleaner than driving")
    
    if total_co2_kg > 50:
        recommendations.append(f"Plant {trees_to_offset} trees to offset your carbon footprint")
    
    recommendations.append("Choose eco-friendly accommodations with renewable energy")
    recommendations.append("Support local businesses to reduce transportation of goods")
    
    # Calculate processing time
    processing_time = (time.time() - start_time) * 1000
    
    # Log successful calculation
    logger.info("Carbon calculation completed", extra={
        "request_id": request_id,
        "total_co2_kg": round(total_co2_kg, 2),
        "co2_per_person": round(co2_per_person, 2),
        "trees_to_offset": trees_to_offset,
        "processing_time_ms": round(processing_time, 2)
    })
    
    return CarbonResponse(
        co2_kg=round(total_co2_kg, 2),
        saved_vs_suv=round(saved_vs_suv, 2),
        vehicle_type=request.vehicle_type,
        distance=request.distance,
        passengers=request.passengers,
        co2_per_person=round(co2_per_person, 2),
        trees_to_offset=trees_to_offset,
        cost_savings=round(cost_savings, 2),
        recommendations=recommendations[:3]  # Limit to top 3 recommendations
    )

@router.get("/weather/{shrine}", response_model=WeatherInfo)
async def get_shrine_weather(shrine: str):
    """
    Get detailed weather information for a specific shrine.
    
    TODO: Integrate with real weather API (OpenWeatherMap, etc.)
    """
    
    valid_shrines = ["kedarnath", "badrinath", "gangotri", "yamunotri"]
    shrine_lower = shrine.lower()
    
    if shrine_lower not in valid_shrines:
        raise HTTPException(status_code=404, detail=f"Weather data not available for {shrine}")
    
    # Mock weather data based on shrine location and season
    current_month = datetime.now().month
    
    # Different weather patterns for different shrines
    weather_patterns = {
        "kedarnath": {
            "base_temp": -2 if current_month in [11, 12, 1, 2, 3] else 8,
            "conditions": ["Clear", "Cloudy", "Light Snow", "Heavy Snow"],
            "altitude": "3583m"
        },
        "badrinath": {
            "base_temp": 0 if current_month in [11, 12, 1, 2, 3] else 10,
            "conditions": ["Sunny", "Cloudy", "Light Rain", "Snow"],
            "altitude": "3133m"
        },
        "gangotri": {
            "base_temp": 2 if current_month in [11, 12, 1, 2, 3] else 12,
            "conditions": ["Clear", "Partly Cloudy", "Light Rain"],
            "altitude": "3100m"
        },
        "yamunotri": {
            "base_temp": 1 if current_month in [11, 12, 1, 2, 3] else 11,
            "conditions": ["Sunny", "Cloudy", "Light Snow"],
            "altitude": "3293m"
        }
    }
    
    pattern = weather_patterns[shrine_lower]
    temp = pattern["base_temp"] + random.randint(-5, 8)
    condition = random.choice(pattern["conditions"])
    humidity = random.randint(40, 80)
    
    # Visibility based on weather
    visibility = "Good"
    if "Snow" in condition or "Rain" in condition:
        visibility = "Limited"
    elif "Cloudy" in condition:
        visibility = "Moderate"
    
    # Best visit time based on weather and season
    if current_month in [4, 5, 6, 9, 10]:
        best_visit_time = "6:00 AM - 6:00 PM (Peak season)"
    elif current_month in [7, 8]:
        best_visit_time = "7:00 AM - 5:00 PM (Monsoon - check conditions)"
    else:
        best_visit_time = "Closed (Winter season)"
    
    return WeatherInfo(
        shrine=shrine.title(),
        temperature=temp,
        condition=condition,
        humidity=humidity,
        visibility=visibility,
        best_visit_time=best_visit_time
    )

@router.get("/route-info/{from_shrine}/{to_shrine}")
async def get_route_info(from_shrine: str, to_shrine: str):
    """
    Get route information between two shrines.
    
    TODO: Integrate with Google Maps API or similar for real route data.
    """
    
    valid_shrines = ["kedarnath", "badrinath", "gangotri", "yamunotri", "rishikesh", "haridwar"]
    
    if from_shrine.lower() not in valid_shrines or to_shrine.lower() not in valid_shrines:
        raise HTTPException(status_code=404, detail="Invalid shrine names")
    
    if from_shrine.lower() == to_shrine.lower():
        raise HTTPException(status_code=400, detail="Source and destination cannot be the same")
    
    # Mock route data (distances in km, time in hours)
    route_matrix = {
        ("rishikesh", "kedarnath"): {"distance": 223, "time": 8.5, "difficulty": "Moderate"},
        ("rishikesh", "badrinath"): {"distance": 301, "time": 10.0, "difficulty": "Moderate"},
        ("rishikesh", "gangotri"): {"distance": 249, "time": 9.0, "difficulty": "Easy"},
        ("rishikesh", "yamunotri"): {"distance": 209, "time": 8.0, "difficulty": "Easy"},
        ("kedarnath", "badrinath"): {"distance": 233, "time": 9.5, "difficulty": "Difficult"},
        ("gangotri", "yamunotri"): {"distance": 61, "time": 3.0, "difficulty": "Easy"},
    }
    
    # Create route key (normalize order)
    route_key = tuple(sorted([from_shrine.lower(), to_shrine.lower()]))
    
    if route_key not in route_matrix:
        # Generate approximate data for missing routes
        base_distance = random.randint(150, 400)
        base_time = base_distance / 25  # Approximate mountain driving speed
        difficulty = random.choice(["Easy", "Moderate", "Difficult"])
    else:
        route_data = route_matrix[route_key]
        base_distance = route_data["distance"]
        base_time = route_data["time"]
        difficulty = route_data["difficulty"]
    
    # Add weather-based adjustments
    current_month = datetime.now().month
    weather_factor = 1.0
    
    if current_month in [7, 8]:  # Monsoon
        weather_factor = 1.3
        difficulty = "Difficult" if difficulty != "Difficult" else "Very Difficult"
    elif current_month in [12, 1, 2]:  # Winter
        weather_factor = 1.2
    
    adjusted_time = base_time * weather_factor
    
    return {
        "from": from_shrine.title(),
        "to": to_shrine.title(),
        "distance_km": base_distance,
        "estimated_time_hours": round(adjusted_time, 1),
        "difficulty": difficulty,
        "best_travel_time": "Early morning (6-8 AM)",
        "warnings": [
            "Check weather conditions before travel",
            "Carry warm clothing and rain gear",
            "Keep vehicle in good condition",
            "Inform someone about your travel plans"
        ] if difficulty in ["Difficult", "Very Difficult"] else [
            "Check weather conditions before travel",
            "Carry basic emergency supplies"
        ],
        "fuel_stops": ["Rishikesh", "Rudraprayag", "Guptkashi"] if base_distance > 200 else ["Rishikesh"],
        "estimated_fuel_cost": round(base_distance * 6.5, 0)  # ₹6.5 per km average
    }