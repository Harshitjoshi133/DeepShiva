#!/usr/bin/env python3
"""
Test script to verify all imports work correctly
"""

try:
    print("Testing imports...")
    
    # Test individual routers
    from app.routers import chat
    print("✅ Chat router imported successfully")
    
    from app.routers import vision  
    print("✅ Vision router imported successfully")
    
    from app.routers import tourism
    print("✅ Tourism router imported successfully")
    
    from app.routers import culture
    print("✅ Culture router imported successfully")
    
    # Test main app
    from app.main import app
    print("✅ Main FastAPI app imported successfully")
    
    print("\n🎉 All imports successful! Server should start without errors.")
    
except Exception as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()