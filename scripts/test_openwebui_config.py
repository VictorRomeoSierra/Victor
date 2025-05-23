#!/usr/bin/env python3
"""
Test script to verify Open-WebUI can connect to N8N webhook
This simulates what Open-WebUI sends to verify the configuration
"""

import requests
import json
import sys

# N8N webhook endpoint that Open-WebUI should use
WEBHOOK_URL = "https://n8n.victorromeosierra.com/webhook/victor-local-chat"

def test_openai_compatibility():
    """Test if the webhook responds like an OpenAI API"""
    
    print("Testing N8N Webhook for OpenAI Compatibility")
    print(f"Endpoint: {WEBHOOK_URL}")
    print("=" * 60)
    
    # Test 1: Basic chat completion request
    print("\nTest 1: Basic Chat Completion")
    payload = {
        "model": "victor-local-chat",  # Model name Open-WebUI will send
        "messages": [
            {
                "role": "user",
                "content": "Hello, can you help me?"
            }
        ],
        "stream": False,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            # Check for OpenAI response structure
            if all(key in data for key in ["id", "object", "choices"]):
                print("✅ Valid OpenAI response structure")
                if data["choices"] and "message" in data["choices"][0]:
                    print(f"Response preview: {data['choices'][0]['message']['content'][:100]}...")
            else:
                print("❌ Invalid response structure")
                print(f"Keys found: {list(data.keys())}")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Connection error: {str(e)}")
    
    # Test 2: DCS-specific query
    print("\n" + "=" * 60)
    print("Test 2: DCS Query with Context")
    
    dcs_payload = {
        "model": "victor-local-chat",
        "messages": [
            {
                "role": "user",
                "content": "How do I create waypoints in DCS Lua?"
            }
        ],
        "stream": False
    }
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            json=dcs_payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # Check if response includes XSAF context
            has_context = any(keyword in content.lower() for keyword in ["xsaf", ".lua", "file:", "line:"])
            print(f"Contains XSAF context: {'✅ Yes' if has_context else '❌ No'}")
            
            # Check token usage
            if "usage" in data:
                print(f"Token usage: {data['usage']}")
                
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Test 3: Model listing (some Open-WebUI versions check this)
    print("\n" + "=" * 60)
    print("Test 3: Model List Request (Optional)")
    
    try:
        # Try the models endpoint (may not be implemented)
        models_url = WEBHOOK_URL.replace("/victor-local-chat", "/models")
        response = requests.get(models_url, timeout=5)
        
        if response.status_code == 200:
            print("✅ Models endpoint exists")
        else:
            print("ℹ️ Models endpoint not implemented (this is okay)")
            
    except:
        print("ℹ️ Models endpoint not available (this is okay)")
    
    print("\n" + "=" * 60)
    print("Configuration for Open-WebUI:")
    print(f"API Base URL: https://n8n.victorromeosierra.com/webhook")
    print(f"API Key: any-key-will-work")
    print(f"Model Name: victor-local-chat")

if __name__ == "__main__":
    test_openai_compatibility()