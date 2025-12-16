"""
External API integration services
Handles weather data from OpenWeatherMap and crowd data from various sources
"""

import os
import httpx
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
from ..logging_config import get_logger

logger = get_logger("external_apis")

class WeatherService:
    """OpenWeatherMap API integration for real weather data"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENWEATHER_API_KEY")
        self.base_url = "https://api.openweathermap.org/data/2.5"
        
    async def get_weather_data(self, lat: float, lon: float) -> Dict[str, Any]:
        """Get current weather data for coordinates"""
        if not self.api_key:
            logger.warning("OpenWeather API key not configured, using mock data")
            return self._get_mock_weather(lat, lon)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/weather",
                    params={
                        "lat": lat,
                        "lon": lon,
                        "appid": self.api_key,
                        "units": "metric"
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "temperature": round(data["main"]["temp"]),
                        "condition": data["weather"][0]["main"],
                        "description": data["weather"][0]["description"],
                        "humidity": data["main"]["humidity"],
                        "visibility": data.get("visibility", 10000) / 1000,  # Convert to km
                        "wind_speed": data["wind"]["speed"]
                    }
                else:
                    logger.error(f"OpenWeather API error: {response.status_code}")
                    return self._get_mock_weather(lat, lon)
                    
        except Exception as e:
            logger.error(f"Weather API request failed: {e}")
            return self._get_mock_weather(lat, lon)
    
    def _get_mock_weather(self, lat: float, lon: float) -> Dict[str, Any]:
        """Generate realistic mock weather data based on location and season"""
        import random
        
        # Altitude-based temperature adjustment
        if lat > 30.5:  # Higher altitude shrines
            base_temp = -2 if datetime.now().month in [11, 12, 1, 2, 3] else 8
        else:
            base_temp = 5 if datetime.now().month in [11, 12, 1, 2, 3] else 15
        
        conditions = ["Clear", "Cloudy", "Light Snow", "Sunny", "Light Rain"]
        condition = random.choice(conditions)
        
        return {
            "temperature": base_temp + random.randint(-8, 12),
            "condition": condition,
            "description": condition.lower(),
            "humidity": random.randint(40, 80),
            "visibility": random.randint(5, 15),
            "wind_speed": random.randint(2, 15)
        }

class CrowdDataService:
    """Service for aggregating crowd data from multiple sources"""
    
    def __init__(self):
        self.weather_service = WeatherService()
        
    async def get_enhanced_crowd_data(self, shrine_name: str, coordinates: tuple) -> Dict[str, Any]:
        """Get enhanced crowd data with weather integration"""
        
        # Get weather data for the shrine
        weather_data = await self.weather_service.get_weather_data(
            coordinates[1], coordinates[0]  # lat, lon
        )
        
        # Calculate crowd level based on multiple factors
        crowd_level = await self._calculate_crowd_level(shrine_name, weather_data)
        
        # Determine accessibility based on weather and season
        accessibility = self._determine_accessibility(shrine_name, weather_data, crowd_level)
        
        return {
            "shrine": shrine_name,
            "crowd_level": crowd_level,
            "weather": weather_data,
            "accessibility": accessibility,
            "last_updated": datetime.now().strftime("%H:%M"),
            "data_sources": ["weather_api", "historical_patterns", "seasonal_analysis"]
        }
    
    async def _calculate_crowd_level(self, shrine_name: str, weather_data: Dict) -> int:
        """Calculate crowd level using weather and other factors"""
        import random
        
        now = datetime.now()
        
        # Base levels by shrine
        base_levels = {
            "Kedarnath": 65,
            "Badrinath": 55,
            "Gangotri": 40,
            "Yamunotri": 45
        }
        
        base_level = base_levels.get(shrine_name, 50)
        
        # Weather impact
        weather_multiplier = 1.0
        condition = weather_data.get("condition", "Clear")
        temperature = weather_data.get("temperature", 10)
        
        if condition in ["Light Snow", "Light Rain"]:
            weather_multiplier = 0.7
        elif condition == "Clear" and temperature > 5:
            weather_multiplier = 1.2
        elif temperature < -5:
            weather_multiplier = 0.5
        
        # Seasonal impact
        seasonal_multiplier = 1.8 if now.month in [4, 5, 6, 9, 10] else 0.8
        
        # Time of day impact
        hour = now.hour
        if 6 <= hour <= 10:
            time_multiplier = 1.5
        elif 11 <= hour <= 16:
            time_multiplier = 1.8
        elif 17 <= hour <= 19:
            time_multiplier = 1.2
        else:
            time_multiplier = 0.6
        
        # Calculate final level
        final_level = base_level * seasonal_multiplier * time_multiplier * weather_multiplier
        final_level *= random.uniform(0.8, 1.2)  # Add some randomness
        
        return max(0, min(100, int(final_level)))
    
    def _determine_accessibility(self, shrine_name: str, weather_data: Dict, crowd_level: int) -> str:
        """Determine shrine accessibility based on conditions"""
        
        now = datetime.now()
        condition = weather_data.get("condition", "Clear")
        temperature = weather_data.get("temperature", 10)
        
        # Winter closure for high altitude shrines
        if now.month in [12, 1, 2, 3] and shrine_name in ["Kedarnath", "Badrinath"]:
            return "Closed (Winter)"
        
        # Weather-based restrictions
        if condition in ["Heavy Snow", "Heavy Rain"]:
            return "Closed (Weather)"
        elif condition in ["Light Snow", "Light Rain"] and crowd_level > 80:
            return "Limited"
        elif crowd_level > 95:
            return "Restricted (Overcrowded)"
        else:
            return "Open"

# Global service instances
weather_service = WeatherService()
crowd_service = CrowdDataService()