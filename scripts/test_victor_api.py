#!/usr/bin/env python3
"""
Test script for Victor API functionality
"""

import requests
import json
import sys
from typing import Dict, Any

# API URL - change this if testing remotely
API_URL = "http://localhost:8000"
if len(sys.argv) > 1:
    API_URL = sys.argv[1]

def test_endpoint(name: str, method: str, endpoint: str, data: Dict[str, Any] = None) -> bool:
    """Test a single API endpoint"""
    print(f"\n{'='*50}")
    print(f"Testing: {name}")
    print(f"Endpoint: {method} {endpoint}")
    
    try:
        if method == "GET":
            response = requests.get(f"{API_URL}{endpoint}")
        else:  # POST
            response = requests.post(f"{API_URL}{endpoint}", json=data)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)[:500]}...")  # First 500 chars
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def main():
    print(f"Testing Victor API at: {API_URL}")
    
    # Test 1: Health check
    test_endpoint("Health Check", "GET", "/health")
    
    # Test 2: Stats
    test_endpoint("Index Statistics", "GET", "/stats")
    
    # Test 3: Text search
    test_endpoint(
        "Text Search",
        "POST",
        "/search",
        {
            "query": "waypoint",
            "limit": 3,
            "search_type": "text"
        }
    )
    
    # Test 4: Context generation
    test_endpoint(
        "Context Generation",
        "POST",
        "/context",
        {
            "query": "How do I create waypoints in DCS?",
            "limit": 3,
            "detailed": False
        }
    )
    
    # Test 5: Prompt enhancement
    test_endpoint(
        "Prompt Enhancement",
        "POST",
        "/enhance_prompt",
        {
            "prompt": "How do I spawn aircraft in DCS?",
            "model": "codellama"
        }
    )
    
    print(f"\n{'='*50}")
    print("Testing complete!")

if __name__ == "__main__":
    main()