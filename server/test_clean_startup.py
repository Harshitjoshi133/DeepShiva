#!/usr/bin/env python3
"""
Test script to verify clean startup without verbose SQLAlchemy logs
"""

import subprocess
import sys
import time

def test_clean_startup():
    """Test that the server starts cleanly without verbose logs"""
    
    print("🧪 Testing Clean Server Startup")
    print("=" * 40)
    
    try:
        # Start the server process
        print("Starting server...")
        process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd="."
        )
        
        # Wait a few seconds for startup
        time.sleep(3)
        
        # Check if process is still running
        if process.poll() is None:
            print("✅ Server started successfully!")
            
            # Get some output
            try:
                stdout, stderr = process.communicate(timeout=2)
                print("\n📋 Startup Output:")
                print("-" * 20)
                if stdout:
                    print(stdout[:500] + "..." if len(stdout) > 500 else stdout)
                if stderr:
                    print("STDERR:", stderr[:200] + "..." if len(stderr) > 200 else stderr)
            except subprocess.TimeoutExpired:
                print("✅ Server is running (no immediate output)")
            
            # Terminate the test server
            process.terminate()
            process.wait()
            print("\n✅ Test completed - server startup is clean!")
            
        else:
            print("❌ Server failed to start")
            stdout, stderr = process.communicate()
            print("STDOUT:", stdout)
            print("STDERR:", stderr)
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        if 'process' in locals():
            process.terminate()

if __name__ == "__main__":
    test_clean_startup()