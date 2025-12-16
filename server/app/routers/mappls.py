"""
MapmyIndia (Mappls) API integration router
Handles REST API requests for the Mappls mapping service using direct access token
"""

import os
import httpx
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Request, Query
from fastapi.responses import JSONResponse
from app.logging_config import get_logger

logger = get_logger("mappls")

router = APIRouter()

def get_mappls_access_token() -> str:
    """Get Mappls access token from environment variables"""
    access_token = os.getenv("MAPPLS_ACCESS_TOKEN")
    
    if not access_token:
        logger.error("Mappls access token not found in environment variables")
        raise HTTPException(
            status_code=500, 
            detail="Mappls access token not configured"
        )
    
    return access_token

@router.get("/token")
async def get_mappls_token(request: Request):
    """
    Get the Mappls access token for frontend use
    Returns the configured access token from environment
    """
    request_id = getattr(request.state, 'request_id', 'unknown')
    logger.info(f"Token request received - Request ID: {request_id}")
    
    try:
        access_token = get_mappls_access_token()
        
        logger.info(f"Token provided successfully - Request ID: {request_id}")
        return {
            "access_token": access_token,
            "token_type": "Bearer",
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in token endpoint - Request ID: {request_id}, Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@router.get("/autosuggest")
async def autosuggest_places(
    request: Request,
    query: str = Query(..., description="Search query for places"),
    location: Optional[str] = Query(None, description="Bias location as lat,lng"),
    region: Optional[str] = Query("IND", description="Country/region code"),
    tokenizeAddress: Optional[bool] = Query(True, description="Tokenize address"),
    pod: Optional[str] = Query(None, description="Place type filter"),
    filter: Optional[str] = Query(None, description="Additional filters")
):
    """
    Auto-suggest places using Mappls API
    Based on: https://developer.mappls.com/documentation/sdk/rest-apis/mappls-maps-auto-suggest-api-example/
    """
    request_id = getattr(request.state, 'request_id', 'unknown')
    logger.info(f"Autosuggest request - Query: {query}, Request ID: {request_id}")
    
    try:
        access_token = get_mappls_access_token()
        
        # Mappls Autosuggest API endpoint
        autosuggest_url = "https://atlas.mappls.com/api/places/search/json"
        
        # Build query parameters
        params = {
            "query": query,
            "region": region,
            "tokenizeAddress": str(tokenizeAddress).lower()
        }
        
        if location:
            params["location"] = location
        if pod:
            params["pod"] = pod
        if filter:
            params["filter"] = filter
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                autosuggest_url,
                params=params,
                headers=headers,
                timeout=30.0
            )
            
            if response.status_code != 200:
                logger.error(f"Mappls Autosuggest API error: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Autosuggest API request failed"
                )
            
            result = response.json()
            logger.info(f"Autosuggest successful - Found {len(result.get('suggestedLocations', []))} suggestions - Request ID: {request_id}")
            return result
            
    except HTTPException:
        raise
    except httpx.RequestError as e:
        logger.error(f"Network error in autosuggest - Request ID: {request_id}, Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Network error connecting to autosuggest API"
        )
    except Exception as e:
        logger.error(f"Unexpected error in autosuggest - Request ID: {request_id}, Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@router.get("/geocode")
async def geocode_address(
    request: Request,
    address: str = Query(..., description="Address to geocode"),
    itemCount: Optional[int] = Query(1, description="Number of results to return"),
    bias: Optional[int] = Query(0, description="Bias towards India")
):
    """
    Geocode an address using Mappls API
    """
    request_id = getattr(request.state, 'request_id', 'unknown')
    logger.info(f"Geocode request - Address: {address}, Request ID: {request_id}")
    
    try:
        access_token = get_mappls_access_token()
        
        # Mappls Geocoding API endpoint
        geocode_url = "https://atlas.mappls.com/api/places/geocode"
        
        params = {
            "address": address,
            "itemCount": itemCount,
            "bias": bias
        }
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                geocode_url,
                params=params,
                headers=headers,
                timeout=30.0
            )
            
            if response.status_code != 200:
                logger.error(f"Mappls Geocode API error: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Geocode API request failed"
                )
            
            result = response.json()
            logger.info(f"Geocode successful - Request ID: {request_id}")
            return result
            
    except HTTPException:
        raise
    except httpx.RequestError as e:
        logger.error(f"Network error in geocode - Request ID: {request_id}, Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Network error connecting to geocode API"
        )
    except Exception as e:
        logger.error(f"Unexpected error in geocode - Request ID: {request_id}, Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@router.get("/route")
async def get_route(
    request: Request,
    start: str = Query(..., description="Start coordinates as lat,lng"),
    end: str = Query(..., description="End coordinates as lat,lng"),
    profile: Optional[str] = Query("driving", description="Routing profile: driving, walking, biking"),
    alternatives: Optional[bool] = Query(False, description="Return alternative routes"),
    steps: Optional[bool] = Query(True, description="Include turn-by-turn directions"),
    overview: Optional[str] = Query("full", description="Route geometry detail level")
):
    """
    Get route between two points using Mappls API
    """
    request_id = getattr(request.state, 'request_id', 'unknown')
    logger.info(f"Route request - Start: {start}, End: {end}, Request ID: {request_id}")
    
    try:
        access_token = get_mappls_access_token()
        
        # Mappls Route API endpoint
        route_url = "https://apis.mappls.com/advancedmaps/v1/route"
        
        params = {
            "start": start,
            "end": end,
            "profile": profile,
            "alternatives": str(alternatives).lower(),
            "steps": str(steps).lower(),
            "overview": overview
        }
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                route_url,
                params=params,
                headers=headers,
                timeout=30.0
            )
            
            if response.status_code != 200:
                logger.error(f"Mappls Route API error: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Route API request failed"
                )
            
            result = response.json()
            logger.info(f"Route calculation successful - Request ID: {request_id}")
            return result
            
    except HTTPException:
        raise
    except httpx.RequestError as e:
        logger.error(f"Network error in route - Request ID: {request_id}, Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Network error connecting to route API"
        )
    except Exception as e:
        logger.error(f"Unexpected error in route - Request ID: {request_id}, Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@router.get("/traffic")
async def get_traffic_data(
    request: Request,
    bbox: Optional[str] = Query(None, description="Bounding box as minLon,minLat,maxLon,maxLat"),
    zoom: Optional[int] = Query(10, description="Zoom level for traffic data")
):
    """
    Get traffic data using Mappls API
    
    Args:
        bbox: Bounding box coordinates (format: "minLon,minLat,maxLon,maxLat")
        zoom: Zoom level for traffic data
    """
    request_id = getattr(request.state, 'request_id', 'unknown')
    logger.info(f"Traffic API request - Request ID: {request_id}")
    
    try:
        access_token = get_mappls_access_token()
        
        # Mappls Traffic API endpoint
        traffic_url = "https://apis.mappls.com/advancedmaps/v1/traffic"
        
        # Build query parameters
        params = {
            "zoom": zoom
        }
        
        if bbox:
            params["bbox"] = bbox
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                traffic_url,
                params=params,
                headers=headers,
                timeout=30.0
            )
            
            if response.status_code != 200:
                logger.error(f"Mappls Traffic API error: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Traffic API request failed"
                )
            
            logger.info(f"Traffic data retrieved successfully - Request ID: {request_id}")
            return response.json()
            
    except HTTPException:
        raise
    except httpx.RequestError as e:
        logger.error(f"Network error in traffic API - Request ID: {request_id}, Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Network error connecting to traffic API"
        )
    except Exception as e:
        logger.error(f"Unexpected error in traffic API - Request ID: {request_id}, Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@router.get("/health")
async def mappls_health_check(request: Request):
    """Health check endpoint for Mappls integration"""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    try:
        # Test if we can get access token
        access_token = get_mappls_access_token()
        
        # Test a simple API call to verify token works
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            # Test with a simple autosuggest call
            response = await client.get(
                "https://atlas.mappls.com/api/places/search/json",
                params={"query": "Delhi", "region": "IND"},
                headers=headers,
                timeout=10.0
            )
            
            token_valid = response.status_code == 200
        
        logger.info(f"Mappls health check passed - Request ID: {request_id}")
        return {
            "status": "healthy" if token_valid else "degraded",
            "service": "mappls",
            "token_configured": True,
            "token_valid": token_valid,
            "api_accessible": token_valid
        }
        
    except Exception as e:
        logger.error(f"Mappls health check failed - Request ID: {request_id}, Error: {str(e)}")
        return {
            "status": "unhealthy",
            "service": "mappls",
            "error": str(e),
            "token_configured": False,
            "token_valid": False,
            "api_accessible": False
        }