#!/usr/bin/env python3
"""
Test the N8N debug workflow
"""

import requests
import json
import time

# Debug webhook URL - update this based on your N8N setup
WEBHOOK_URL = "https://n8n.victorromeosierra.com/webhook/victor-debug"

def test_debug_workflow():
    """Test the debug workflow"""
    
    print(f"Testing N8N Debug Workflow")
    print(f"Webhook URL: {WEBHOOK_URL}")
    print("This will test basic Ollama connectivity through N8N\n")
    
    # Simple test payload
    payload = {
        "test": "debug",
        "timestamp": time.time()
    }
    
    try:
        print("Sending request...")
        start_time = time.time()
        
        response = requests.post(WEBHOOK_URL, json=payload, timeout=30)
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response Time: {elapsed:.2f} seconds")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print("\nResponse received!")
                print(json.dumps(result, indent=2))
                
                # Check what we got
                if 'extracted_content' in result:
                    print(f"\nExtracted content preview: {result['extracted_content'][:200]}...")
                
                if 'has_message' in result:
                    print(f"\nOllama returned message format: {result['has_message']}")
                    
                if 'model' in result:
                    print(f"Model used: {result['model']}")
                    
            except json.JSONDecodeError:
                print(f"\nRaw response: {response.text}")
        else:
            print(f"\nError response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("\nError: Request timed out after 30 seconds")
        print("This might mean Ollama is taking too long to respond")
    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to N8N webhook")
        print("Make sure the workflow is active and the webhook URL is correct")
    except Exception as e:
        print(f"\nError: {str(e)}")

if __name__ == "__main__":
    test_debug_workflow()
    print("\n" + "="*60)
    print("Debug tips:")
    print("1. If timeout: Check N8N execution logs for the workflow")
    print("2. If 404: Make sure the workflow is activated in N8N")
    print("3. If empty response: Check N8N logs for errors in nodes")
    print("4. Expected response time: 15-20 seconds (Ollama processing)")