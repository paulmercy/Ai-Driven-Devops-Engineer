#!/usr/bin/env python3
"""
Test script to verify Makefile functionality
"""

import subprocess
import sys
import time

def run_command(command, timeout=30):
    """Run a command and return success status"""
    try:
        print(f"🧪 Testing: {command}")
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True,
            timeout=timeout
        )
        
        if result.returncode == 0:
            print(f"✅ Success: {command}")
            return True
        else:
            print(f"❌ Failed: {command}")
            print(f"   Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ Timeout: {command}")
        return False
    except Exception as e:
        print(f"💥 Exception: {command} - {e}")
        return False

def main():
    print("🛡️  Testing DevSecOps Dashboard Makefile")
    print("=" * 50)
    
    tests = [
        ("make check", 60),
        ("make validate-compose", 30),
        ("make help", 10),
        ("make status", 10),
        ("make ports", 10),
    ]
    
    passed = 0
    total = len(tests)
    
    for command, timeout in tests:
        if run_command(command, timeout):
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! Makefile is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
