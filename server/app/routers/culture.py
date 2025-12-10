from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional
import random

router = APIRouter()

class Product(BaseModel):
    id: int
    name: str
    description: str
    price: int
    artisan: str
    image: str
    category: str
    rating: float
    reviews_count: int
    in_stock: bool
    materials: List[str]
    origin_village: str
    crafting_time_days: int
    eco_friendly: bool

class ProductFilter(BaseModel):
    category: Optional[str] = None
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    eco_friendly: Optional[bool] = None
    in_stock: Optional[bool] = None

class ArtisanProfile(BaseModel):
    name: str
    village: str
    specialization: str
    experience_years: int
    products_count: int
    rating: float
    story: str
    contact_available: bool

@router.get("/products", response_model=List[Product])
async def get_products(
    category: Optional[str] = Query(None, description="Filter by category"),
    min_price: Optional[int] = Query(None, ge=0, description="Minimum price filter"),
    max_price: Optional[int] = Query(None, ge=0, description="Maximum price filter"),
    eco_friendly: Optional[bool] = Query(None, description="Filter eco-friendly products"),
    in_stock: Optional[bool] = Query(True, description="Show only in-stock products"),
    sort_by: Optional[str] = Query("name", description="Sort by: name, price, rating"),
    limit: Optional[int] = Query(20, ge=1, le=100, description="Number of products to return")
):
    """
    Returns filtered and sorted list of local artisan products.
    
    TODO: Connect to actual product database.
    TODO: Add full-text search functionality.
    TODO: Add user favorites and recommendations.
    """
    
    # Enhanced mock product data
    mock_products = [
        {
            "id": 1,
            "name": "Aipan Art Canvas",
            "description": "Traditional Kumaoni floor art on canvas, handmade by local artists using natural pigments",
            "price": 1500,
            "artisan": "Meera Devi",
            "image": "/images/products/aipan-art.jpg",
            "category": "Art & Paintings",
            "rating": 4.8,
            "reviews_count": 23,
            "in_stock": True,
            "materials": ["Canvas", "Natural Pigments", "Traditional Brushes"],
            "origin_village": "Almora",
            "crafting_time_days": 3,
            "eco_friendly": True
        },
        {
            "id": 2,
            "name": "Woolen Shawl",
            "description": "Pure wool shawl with traditional Garhwali patterns, hand-woven on traditional looms",
            "price": 2500,
            "artisan": "Ram Singh",
            "image": "/images/products/woolen-shawl.jpg",
            "category": "Textiles",
            "rating": 4.6,
            "reviews_count": 18,
            "in_stock": True,
            "materials": ["Pure Wool", "Natural Dyes"],
            "origin_village": "Chamoli",
            "crafting_time_days": 7,
            "eco_friendly": True
        },
        {
            "id": 3,
            "name": "Ringal Basket",
            "description": "Eco-friendly basket made from Himalayan bamboo, perfect for storage and decoration",
            "price": 800,
            "artisan": "Kamla Bisht",
            "image": "/images/products/ringal-basket.png",
            "category": "Home & Decor",
            "rating": 4.7,
            "reviews_count": 31,
            "in_stock": True,
            "materials": ["Ringal Bamboo", "Natural Fiber"],
            "origin_village": "Pithoragarh",
            "crafting_time_days": 2,
            "eco_friendly": True
        },
        {
            "id": 4,
            "name": "Copper Water Bottle",
            "description": "Handcrafted copper bottle with traditional engravings, known for health benefits",
            "price": 1200,
            "artisan": "Mohan Lal",
            "image": "/images/products/copper-bottle.png",
            "category": "Utensils",
            "rating": 4.5,
            "reviews_count": 42,
            "in_stock": True,
            "materials": ["Pure Copper", "Traditional Tools"],
            "origin_village": "Bageshwar",
            "crafting_time_days": 1,
            "eco_friendly": True
        },
        {
            "id": 5,
            "name": "Himalayan Honey",
            "description": "Pure organic honey from high-altitude flowers, collected by traditional beekeepers",
            "price": 600,
            "artisan": "Uttarakhand Bee Cooperative",
            "image": "/images/products/himalayan-honey.png",
            "category": "Food & Beverages",
            "rating": 4.9,
            "reviews_count": 67,
            "in_stock": True,
            "materials": ["Wild Flower Nectar", "Traditional Hives"],
            "origin_village": "Munsiyari",
            "crafting_time_days": 30,
            "eco_friendly": True
        },
        {
            "id": 6,
            "name": "Wooden Prayer Beads",
            "description": "Handcrafted prayer beads from sacred Rudraksha seeds",
            "price": 450,
            "artisan": "Pandit Govind",
            "image": "/images/products/prayer-beads.jpg",
            "category": "Spiritual Items",
            "rating": 4.8,
            "reviews_count": 29,
            "in_stock": False,
            "materials": ["Rudraksha Seeds", "Cotton Thread"],
            "origin_village": "Kedarnath Valley",
            "crafting_time_days": 1,
            "eco_friendly": True
        },
        {
            "id": 7,
            "name": "Pashmina Scarf",
            "description": "Luxurious pashmina scarf made from finest Himalayan goat wool",
            "price": 3500,
            "artisan": "Sunita Rawat",
            "image": "/images/products/pashmina-scarf.jpg",
            "category": "Textiles",
            "rating": 4.9,
            "reviews_count": 15,
            "in_stock": True,
            "materials": ["Pashmina Wool", "Silk Thread"],
            "origin_village": "Nanda Devi Region",
            "crafting_time_days": 10,
            "eco_friendly": True
        }
    ]
    
    # Apply filters
    filtered_products = mock_products
    
    if category:
        filtered_products = [p for p in filtered_products if p["category"].lower() == category.lower()]
    
    if min_price is not None:
        filtered_products = [p for p in filtered_products if p["price"] >= min_price]
    
    if max_price is not None:
        filtered_products = [p for p in filtered_products if p["price"] <= max_price]
    
    if eco_friendly is not None:
        filtered_products = [p for p in filtered_products if p["eco_friendly"] == eco_friendly]
    
    if in_stock is not None:
        filtered_products = [p for p in filtered_products if p["in_stock"] == in_stock]
    
    # Apply sorting
    if sort_by == "price":
        filtered_products.sort(key=lambda x: x["price"])
    elif sort_by == "rating":
        filtered_products.sort(key=lambda x: x["rating"], reverse=True)
    elif sort_by == "name":
        filtered_products.sort(key=lambda x: x["name"])
    
    # Apply limit
    filtered_products = filtered_products[:limit]
    
    return [Product(**item) for item in filtered_products]

@router.get("/products/{product_id}", response_model=Product)
async def get_product_details(product_id: int):
    """
    Get detailed information about a specific product.
    
    TODO: Connect to actual product database.
    """
    
    # This would normally query the database
    # For now, we'll simulate it by calling get_products and filtering
    products = await get_products()
    
    for product in products:
        if product.id == product_id:
            return product
    
    raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found")

@router.get("/categories")
async def get_categories():
    """
    Get all available product categories.
    
    TODO: Connect to actual database for dynamic categories.
    """
    
    categories = [
        {"name": "Art & Paintings", "count": 15, "description": "Traditional Kumaoni and Garhwali art"},
        {"name": "Textiles", "count": 23, "description": "Handwoven fabrics and clothing"},
        {"name": "Home & Decor", "count": 18, "description": "Decorative items for home"},
        {"name": "Utensils", "count": 12, "description": "Traditional cooking and storage items"},
        {"name": "Food & Beverages", "count": 8, "description": "Organic local produce"},
        {"name": "Spiritual Items", "count": 10, "description": "Religious and meditation items"},
        {"name": "Jewelry", "count": 7, "description": "Traditional silver and bead jewelry"}
    ]
    
    return categories

@router.get("/artisans/{artisan_name}", response_model=ArtisanProfile)
async def get_artisan_profile(artisan_name: str):
    """
    Get detailed profile of an artisan.
    
    TODO: Connect to artisan database.
    TODO: Add artisan verification system.
    """
    
    # Mock artisan profiles
    artisan_profiles = {
        "meera-devi": {
            "name": "Meera Devi",
            "village": "Almora",
            "specialization": "Aipan Art & Traditional Paintings",
            "experience_years": 25,
            "products_count": 15,
            "rating": 4.8,
            "story": "Meera Devi learned the ancient art of Aipan from her grandmother. She has been preserving this traditional Kumaoni floor art for over 25 years, teaching it to younger generations while creating beautiful canvas pieces for art lovers worldwide.",
            "contact_available": True
        },
        "ram-singh": {
            "name": "Ram Singh",
            "village": "Chamoli",
            "specialization": "Traditional Weaving & Textiles",
            "experience_years": 30,
            "products_count": 23,
            "rating": 4.6,
            "story": "Ram Singh comes from a family of traditional weavers. Using age-old techniques passed down through generations, he creates beautiful woolen shawls and blankets that keep the Garhwali textile tradition alive.",
            "contact_available": True
        },
        "kamla-bisht": {
            "name": "Kamla Bisht",
            "village": "Pithoragarh",
            "specialization": "Ringal Bamboo Crafts",
            "experience_years": 20,
            "products_count": 18,
            "rating": 4.7,
            "story": "Kamla Bisht is an expert in Ringal bamboo crafting, a sustainable art form native to Uttarakhand. Her eco-friendly baskets and containers are not just functional but also help preserve the environment.",
            "contact_available": True
        },
        "mohan-lal": {
            "name": "Mohan Lal",
            "village": "Bageshwar",
            "specialization": "Copper & Brass Work",
            "experience_years": 35,
            "products_count": 12,
            "rating": 4.5,
            "story": "Mohan Lal is a master craftsman specializing in traditional copper and brass work. His handcrafted utensils are not only beautiful but also promote healthy living through Ayurvedic principles.",
            "contact_available": False
        }
    }
    
    artisan_key = artisan_name.lower().replace(" ", "-")
    
    if artisan_key not in artisan_profiles:
        raise HTTPException(status_code=404, detail=f"Artisan '{artisan_name}' not found")
    
    return ArtisanProfile(**artisan_profiles[artisan_key])

@router.get("/featured-products", response_model=List[Product])
async def get_featured_products():
    """
    Get featured/recommended products.
    
    TODO: Implement recommendation algorithm based on user preferences.
    TODO: Add seasonal and trending product features.
    """
    
    # Get all products and return top-rated ones
    all_products = await get_products(limit=100)
    
    # Sort by rating and return top 5
    featured = sorted(all_products, key=lambda x: x.rating, reverse=True)[:5]
    
    return featured

class ProductReviewRequest(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    comment: str = Field(..., min_length=10, max_length=500, description="Review comment")
    reviewer_name: str = Field(..., min_length=2, max_length=50, description="Reviewer name")

@router.post("/products/{product_id}/review")
async def add_product_review(product_id: int, request: ProductReviewRequest):
    """
    Add a review for a product.
    
    TODO: Implement user authentication.
    TODO: Store reviews in database.
    TODO: Add review moderation system.
    """
    
    # Verify product exists
    try:
        await get_product_details(product_id)
    except HTTPException:
        raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found")
    
    # In a real system, this would save to database
    review_data = {
        "product_id": product_id,
        "rating": request.rating,
        "comment": request.comment,
        "reviewer_name": request.reviewer_name,
        "review_date": "2024-12-10",  # Would use datetime.now()
        "verified_purchase": False,  # Would check against orders
        "helpful_votes": 0
    }
    
    return {
        "message": "Review added successfully",
        "review_id": random.randint(1000, 9999),
        "status": "pending_moderation"
    }

@router.get("/search")
async def search_products(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Number of results")
):
    """
    Search products by name, description, or artisan.
    
    TODO: Implement full-text search with Elasticsearch or similar.
    TODO: Add search analytics and suggestions.
    """
    
    all_products = await get_products(limit=100)
    query_lower = q.lower()
    
    # Simple text search in name, description, and artisan
    matching_products = []
    for product in all_products:
        if (query_lower in product.name.lower() or 
            query_lower in product.description.lower() or 
            query_lower in product.artisan.lower() or
            query_lower in product.category.lower()):
            matching_products.append(product)
    
    return {
        "query": q,
        "total_results": len(matching_products),
        "results": matching_products[:limit]
    }