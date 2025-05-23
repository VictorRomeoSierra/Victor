#!/usr/bin/env python3
"""
Debug Victor API embedding issues
"""

import requests
import json

API_URL = "http://10.0.0.130:8000"

# First, let's check what the Victor API thinks about its embedding service
print("Testing Victor API embedding service...")

# Test the /debug endpoint if it exists, or check logs
# Let's test with a very simple query
response = requests.post(
    f"{API_URL}/search",
    json={
        "query": "function",  # Very common word that should match many things
        "limit": 2,
        "search_type": "text"  # Start with text search
    }
)

print(f"\nText search for 'function':")
print(f"Status: {response.status_code}")
if response.status_code == 200:
    result = response.json()
    print(f"Found {result['count']} results")

# Now try vector search with the same query
response = requests.post(
    f"{API_URL}/search",
    json={
        "query": "function",
        "limit": 2,
        "search_type": "vector"
    }
)

print(f"\nVector search for 'function':")
print(f"Status: {response.status_code}")
if response.status_code == 200:
    result = response.json()
    print(f"Found {result['count']} results")
    if result['count'] == 0:
        print("\n⚠️  Vector search returned 0 results!")
        print("This suggests the embedding generation for queries is failing")
else:
    print(f"Error: {response.text}")