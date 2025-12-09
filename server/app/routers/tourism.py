from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter()

class CrowdStatus(BaseModel):
    shrine: str
    crowd_level: int
    status: str

class CarbonRequest(BaseModel):
    distance: float
    vehicle_type: str

class CarbonResponse(BaseModel):
    co2_kg: float
    saved_vs_suv: float
    vehicle_type: str
    distance: float

@router.get("/crowd-status", response_model=List[CrowdStatus])
async def get_crowd_status():
    """
    Returns live crowd status at major shrines.
    
    TODO: Integrate with real-time crowd monitoring system.
    TODO: Add historical data and prediction models.
    """
    
    # Mock crowd data
    mock_data = [
        {"shrine": "Kedarnath", "crowd_level": 85, "status": "Heavy"},
        {"shrine": "Badrinath", "crowd_level": 40, "status": "Moderate"},
        {"shrine": "Gangotri", "crowd_level": 25, "status": "Light"},
        {"shrine": "Yamunotri", "crowd_level": 60, "status": "Moderate"}
    ]
    
    return [CrowdStatus(**item) for item in mock_data]

@router.post("/calculate-carbon", response_model=CarbonResponse)
async def calculate_carbon(request: CarbonRequest):
    """
    Calculates carbon footprint based on distance and vehicle type.
    
    Emission factors (kg CO2 per km):
    - Car: 0.21
    - Bike: 0.10
    - Bus: 0.08
    - EV: 0.05
    - SUV (baseline): 0.30
    """
    
    emission_factors = {
        "car": 0.21,
        "bike": 0.10,
        "bus": 0.08,
        "ev": 0.05,
        "suv": 0.30
    }
    
    # Calculate CO2 emissions
    factor = emission_factors.get(request.vehicle_type.lower(), 0.21)
    co2_kg = request.distance * factor
    
    # Calculate savings vs SUV
    suv_emissions = request.distance * emission_factors["suv"]
    saved_vs_suv = suv_emissions - co2_kg
    
    return CarbonResponse(
        co2_kg=co2_kg,
        saved_vs_suv=saved_vs_suv,
        vehicle_type=request.vehicle_type,
        distance=request.distance
    )
