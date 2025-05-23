#!/usr/bin/env python3
"""
Test Ollama API directly to see response format
"""

import requests
import json
import time

OLLAMA_URL = "http://10.0.0.130:11434/api/chat"

def test_ollama_chat():
    """Test Ollama chat API directly"""
    
    payload = {
        "model": "codellama:latest",
        "messages": [
            {
                "role": "user",
                "content": "What is a Python list?"
            }
        ],
        "stream": False,
        "options": {
            "temperature": 0.7
        }
    }
    
    print(f"Testing Ollama at: {OLLAMA_URL}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        start_time = time.time()
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        end_time = time.time()
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response Time: {end_time - start_time:.2f} seconds")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\nResponse JSON structure:")
            print(f"Keys: {list(result.keys())}")
            print(f"\nFull Response:")
            print(json.dumps(result, indent=2))
            
            # Check for expected fields
            if 'message' in result:
                print(f"\nMessage content: {result['message'].get('content', 'No content')[:200]}...")
            if 'response' in result:
                print(f"\nResponse content: {result['response'][:200]}...")
                
        else:
            print(f"Error: {response.text}")
            
    except requests.exceptions.Timeout:
        print("Error: Request timed out")
    except Exception as e:
        print(f"Error: {str(e)}")

def test_ollama_generate():
    """Test Ollama generate API for comparison"""
    
    url = "http://10.0.0.130:11434/api/generate"
    payload = {
        "model": "codellama:latest",
        "prompt": "What is a Python list?",
        "stream": False
    }
    
    print(f"\n\nTesting Ollama generate endpoint at: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\nGenerate Response structure:")
            print(f"Keys: {list(result.keys())}")
            if 'response' in result:
                print(f"Response: {result['response'][:200]}...")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_ollama_chat()
    test_ollama_generate()