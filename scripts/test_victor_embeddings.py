#!/usr/bin/env python3
"""
Test Victor API embedding and search functionality
"""

import requests
import json
import sys

# API URL
API_URL = "http://localhost:8000"
if len(sys.argv) > 1:
    API_URL = sys.argv[1]

def test_search_endpoints():
    """Test all search endpoints"""
    
    print(f"Testing Victor API at: {API_URL}")
    
    # Test 1: Vector search
    print("\n" + "="*60)
    print("Test 1: Vector Search")
    print("="*60)
    
    try:
        response = requests.post(
            f"{API_URL}/search",
            json={
                "query": "waypoint",
                "limit": 2,
                "search_type": "vector"
            }
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Found {result['count']} results")
            for idx, res in enumerate(result.get('results', [])):
                print(f"\nResult {idx+1}:")
                print(f"  File: {res['file_path']}")
                print(f"  Type: {res['chunk_type']}")
                print(f"  Score: {res.get('score', 'N/A')}")
                print(f"  Lines: {res['line_start']}-{res['line_end']}")
                print(f"  Content preview: {res['content'][:100]}...")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {str(e)}")
    
    # Test 2: Hybrid search
    print("\n" + "="*60)
    print("Test 2: Hybrid Search")
    print("="*60)
    
    try:
        response = requests.post(
            f"{API_URL}/search",
            json={
                "query": "spawn aircraft",
                "limit": 2,
                "search_type": "hybrid"
            }
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Found {result['count']} results")
            for idx, res in enumerate(result.get('results', [])):
                print(f"\nResult {idx+1}:")
                print(f"  File: {res['file_path']}")
                print(f"  Type: {res['chunk_type']}")
                print(f"  Score: {res.get('score', 'N/A')}")
                print(f"  Content preview: {res['content'][:100]}...")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {str(e)}")
    
    # Test 3: Context generation
    print("\n" + "="*60)
    print("Test 3: Context Generation")
    print("="*60)
    
    try:
        response = requests.post(
            f"{API_URL}/context",
            json={
                "query": "How do I create waypoints in DCS?",
                "limit": 3,
                "detailed": True
            }
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Found {result['snippet_count']} snippets")
            print(f"\nFormatted context preview:")
            print(result['context'][:500] + "...")
            
            if 'results' in result:
                print(f"\nFirst result detail:")
                first = result['results'][0]
                print(f"  File: {first['file_path']}")
                print(f"  Type: {first['chunk_type']}")
                print(f"  Lines: {first['line_start']}-{first['line_end']}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {str(e)}")
    
    # Test 4: Enhance prompt
    print("\n" + "="*60)
    print("Test 4: Enhance Prompt")
    print("="*60)
    
    try:
        response = requests.post(
            f"{API_URL}/enhance_prompt",
            json={
                "prompt": "How do I spawn units in DCS?",
                "model": "codellama"
            }
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            enhanced = result['enhanced_prompt']
            
            # Check if actual code snippets are included
            has_code = "```" in enhanced or "function" in enhanced or ".lua" in enhanced
            print(f"Enhanced prompt includes code snippets: {has_code}")
            print(f"\nEnhanced prompt preview:")
            print(enhanced[:500] + "...")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_search_endpoints()