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
            "image": "https://placehold.co/400x400/FF9933/FFFFFF?text=Aipan+Art"
        },
        {
            "id": 2,
            "name": "Woolen Shawl",
            "description": "Pure wool shawl with traditional Garhwali patterns",
            "price": 2500,
            "artisan": "Ram Singh",
            "image": "https://placehold.co/400x400/228B22/FFFFFF?text=Woolen+Shawl"
        },
        {
            "id": 3,
            "name": "Ringal Basket",
            "description": "Eco-friendly basket made from Himalayan bamboo",
            "price": 800,
            "artisan": "Kamla Bisht",
            "image": "https://placehold.co/400x400/FF9933/FFFFFF?text=Ringal+Basket"
        },
        {
            "id": 4,
            "name": "Copper Water Bottle",
            "description": "Handcrafted copper bottle with traditional engravings",
            "price": 1200,
            "artisan": "Mohan Lal",
            "image": "https://placehold.co/400x400/228B22/FFFFFF?text=Copper+Bottle"
        },
        {
            "id": 5,
            "name": "Himalayan Honey",
            "description": "Pure organic honey from high-altitude flowers",
            "price": 600,
            "artisan": "Uttarakhand Bee Cooperative",
            "image": "https://placehold.co/400x400/FF9933/FFFFFF?text=Honey"
        }
    ]
    
    return [Product(**item) for item in mock_products]
