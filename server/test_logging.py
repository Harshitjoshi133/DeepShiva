#!/usr/bin/env python3
"""
Test script for Deep-Shiva API logging system
Run this to verify that logging is working correctly
"""

import requests
import json
import time
from pathlib import Path

def test_logging_system():
    """Test the logging system by making API calls and checking logs"""
    
    base_url = "http://localhost:8000"
    
    print("🔍 Testing Deep-Shiva API Logging System")
    print("=" * 50)
    
    # Test 1: Basic API call
    print("\n1. Testing basic API call...")
    try:
        response = requests.get(f"{base_url}/")
        print(f"   ✅ Root endpoint: {response.status_code}")
        request_id = response.headers.get('X-Request-ID')
        print(f"   📝 Request ID: {request_id}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # Test 2: Health check
    print("\n2. Testing health check...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"   ✅ Health check: {response.status_code}")
        health_data = response.json()
        print(f"   📊 Status: {health_data.get('status')}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # Test 3: Chat endpoint
    print("\n3. Testing chat endpoint...")
    try:
        chat_data = {
            "message": "Tell me about Kedarnath temple",
            "user_id": "test_user_123",
            "language": "en"
        }
        response = requests.post(f"{base_url}/api/v1/chat/query", json=chat_data)
        print(f"   ✅ Chat query: {response.status_code}")
        if response.status_code == 200:
            chat_response = response.json()
            print(f"   💬 Message ID: {chat_response.get('message_id')}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # Test 4: Tourism endpoint
    print("\n4. Testing tourism endpoint...")
    try:
        response = requests.get(f"{base_url}/api/v1/tourism/crowd-status")
        print(f"   ✅ Crowd status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # Test 5: Error handling
    print("\n5. Testing error handling...")
    try:
        # Send invalid data to trigger validation error
        invalid_data = {
            "message": "",  # Empty message should cause error
            "user_id": "test_user"
        }
        response = requests.post(f"{base_url}/api/v1/chat/query", json=invalid_data)
        print(f"   ✅ Error handling: {response.status_code}")
        if response.status_code == 400:
            print("   📝 Validation error logged correctly")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # Test 6: Monitoring endpoints
    print("\n6. Testing monitoring endpoints...")
    try:
        # Get recent logs
        response = requests.get(f"{base_url}/api/v1/monitoring/logs?limit=5")
        print(f"   ✅ Recent logs: {response.status_code}")
        
        # Get statistics
        response = requests.get(f"{base_url}/api/v1/monitoring/stats")
        print(f"   ✅ Statistics: {response.status_code}")
        
        # Get system health
        response = requests.get(f"{base_url}/api/v1/monitoring/health-detailed")
        print(f"   ✅ System health: {response.status_code}")
        
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # Test 7: Check log files
    print("\n7. Checking log files...")
    logs_dir = Path("logs")
    
    if logs_dir.exists():
        print("   📁 Log directory exists")
        
        log_files = ["app.log", "error.log", "access.log"]
        for log_file in log_files:
            log_path = logs_dir / log_file
            if log_path.exists():
                size = log_path.stat().st_size
                print(f"   📄 {log_file}: {size} bytes")
                
                # Show last few lines
                try:
                    with open(log_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        if lines:
                            print(f"      Last entry: {lines[-1].strip()[:100]}...")
                except Exception as e:
                    print(f"      Error reading file: {e}")
            else:
                print(f"   ❌ {log_file}: Not found")
    else:
        print("   ❌ Log directory not found")
    
    print("\n" + "=" * 50)
    print("🎉 Logging system test completed!")
    print("\nTo view logs in real-time, run:")
    print("   tail -f logs/app.log")
    print("   tail -f logs/access.log")
    print("\nTo view monitoring dashboard:")
    print(f"   {base_url}/api/v1/monitoring/stats")

if __name__ == "__main__":
    test_logging_system()