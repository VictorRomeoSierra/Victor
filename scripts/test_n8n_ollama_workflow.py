#!/usr/bin/env python3
"""
Test script for N8N Ollama workflow
Tests the webhook endpoint with both DCS and non-DCS queries
"""

import requests
import json
import sys
from typing import Dict, Any

# N8N webhook URL
WEBHOOK_URL = "https://n8n.victorromeosierra.com/webhook/victor-local-chat"
if len(sys.argv) > 1:
    WEBHOOK_URL = sys.argv[1]

def test_query(name: str, query: str, is_dcs: bool = False) -> bool:
    """Test a single query through the N8N workflow"""
    print(f"\n{'='*60}")
    print(f"Test: {name}")
    print(f"Query: {query}")
    print(f"Expected DCS routing: {is_dcs}")
    
    payload = {
        "model": "codellama:latest",
        "messages": [
            {
                "role": "user",
                "content": query
            }
        ],
        "stream": False
    }
    
    try:
        print(f"\nSending request to: {WEBHOOK_URL}")
        response = requests.post(WEBHOOK_URL, json=payload, timeout=120)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            # Try to parse JSON response
            try:
                result = response.json()
            except json.JSONDecodeError:
                # Handle non-JSON response
                print(f"Raw response: {response.text[:500]}...")
                return False
            
            # Check if we got an expected response format
            if "choices" in result:
                content = result["choices"][0]["message"]["content"]
                print(f"\nResponse preview: {content[:200]}...")
                
                # Check if DCS context was added (look for file paths)
                has_context = "xsaf" in content.lower() or ".lua:" in content
                print(f"\nDCS context detected: {has_context}")
                
                if is_dcs and not has_context:
                    print("WARNING: Expected DCS context but none found!")
                elif not is_dcs and has_context:
                    print("WARNING: Unexpected DCS context found!")
                    
                return True
            else:
                print(f"Unexpected response format: {json.dumps(result, indent=2)[:500]}...")
                return False
        else:
            print(f"Error: {response.text[:500]}...")
            return False
    except requests.exceptions.Timeout:
        print("Error: Request timed out (60s)")
        return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def main():
    print(f"Testing N8N Ollama Workflow")
    print(f"Webhook URL: {WEBHOOK_URL}")
    
    # Test 1: Non-DCS query
    test_query(
        "General Programming Query",
        "What is a Python list comprehension?",
        is_dcs=False
    )
    
    # Test 2: DCS query with 'waypoint' keyword
    test_query(
        "DCS Waypoint Query",
        "How do I create waypoints in DCS?",
        is_dcs=True
    )
    
    # Test 3: DCS query with 'lua' keyword
    test_query(
        "DCS Lua Query", 
        "How can I spawn aircraft using Lua scripts?",
        is_dcs=True
    )
    
    # Test 4: DCS query with 'xsaf' keyword
    test_query(
        "XSAF Query",
        "What XSAF functions are available for mission scripting?",
        is_dcs=True
    )
    
    # Test 5: Edge case - contains 'script' but not DCS
    test_query(
        "Non-DCS Script Query",
        "How do I write a bash script to backup files?",
        is_dcs=False  # Should be routed to DCS due to 'script' keyword
    )
    
    print(f"\n{'='*60}")
    print("Testing complete!")
    print("\nNOTE: For these tests to work:")
    print("1. N8N must be running and the workflow must be active")
    print("2. Victor API must be running on http://10.0.0.130:8000")
    print("3. Ollama must be running on http://10.0.0.130:11434")

if __name__ == "__main__":
    main()