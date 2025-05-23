#!/usr/bin/env python3
"""
Test Ollama embedding generation
"""

import requests
import json
# import numpy as np

OLLAMA_URL = "http://10.0.0.130:11434"

def test_embedding():
    """Test embedding generation with Ollama"""
    
    print("Testing Ollama embedding generation")
    print(f"URL: {OLLAMA_URL}/api/embeddings")
    print(f"Model: nomic-embed-text")
    
    payload = {
        "model": "nomic-embed-text",
        "prompt": "How do I create waypoints in DCS?"
    }
    
    print(f"\nPayload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/embeddings",
            json=payload
        )
        
        print(f"\nStatus: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            embedding = result.get('embedding', [])
            
            print(f"Embedding dimension: {len(embedding)}")
            print(f"First 10 values: {embedding[:10]}")
            
            # Check if it's a valid embedding
            if len(embedding) == 768:
                print("\n✅ Valid 768-dimensional embedding generated")
                
                # Test vector magnitude
                magnitude = sum(x*x for x in embedding) ** 0.5
                print(f"Vector magnitude: {magnitude:.4f}")
            else:
                print(f"\n❌ Unexpected embedding dimension: {len(embedding)}")
                
        else:
            print(f"Error response: {response.text}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_embedding()