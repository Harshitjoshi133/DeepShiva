from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter()

class Product(BaseModel):
    id: int
    name: str
    description: str
    price: int
    artisan: str
    image: str

@router.get("/products", response_model=List[Product])
async def get_products():
    """
    Returns list of local artisan products.
    
    TODO: Connect to actual product database.
    TODO: Add filtering, sorting, and pagination.
    """
    
    # Mock product data
    mock_products = [
        {
            "id": 1,
            "name": "Aipan Art Canvas",
            "description": "Traditional Kumaoni floor art on canvas, handmade by local artists",
            "price": 1500,
            "artisan": "Meera Devi",
            "image": "/images/products/aipan-art.jpg"
        },
        {
            "id": 3,
            "name": "Ringal Basket",
            "description": "Eco-friendly basket made from Himalayan bamboo",
            "price": 800,
            "artisan": "Kamla Bisht",
            "image": "/images/products/ringal-basket.png"
        },
        {
            "id": 4,
            "name": "Copper Water Bottle",
            "description": "Handcrafted copper bottle with traditional engravings",
            "price": 1200,
            "artisan": "Mohan Lal",
            "image": "/images/products/copper-bottle.png"
        },
        {
            "id": 5,
            "name": "Himalayan Honey",
            "description": "Pure organic honey from high-altitude flowers",
            "price": 600,
            "artisan": "Uttarakhand Bee Cooperative",
            "image": "/images/products/himalayan-honey.png"
        }
    ]
    
    return [Product(**item) for item in mock_products]
