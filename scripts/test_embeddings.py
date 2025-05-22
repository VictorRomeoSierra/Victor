#!/usr/bin/env python3
"""
Test script to verify embedding generation is working
"""

import requests
import json
import sys

API_URL = "http://localhost:8000"
if len(sys.argv) > 1:
    API_URL = sys.argv[1]

print(f"Testing embeddings at: {API_URL}")
print()

# Test 1: Check embedding provider info
print("1. Checking embedding provider configuration...")
try:
    response = requests.get(f"{API_URL}/stats")
    if response.status_code == 200:
        stats = response.json()
        provider_info = stats.get("embedding_provider", {})
        print(f"   Provider: {provider_info.get('provider', 'unknown')}")
        print(f"   Model: {provider_info.get('model', 'unknown')}")
        print(f"   Dimension: {provider_info.get('dimension', 'unknown')}")
        if provider_info.get('base_url'):
            print(f"   Base URL: {provider_info['base_url']}")
    else:
        print(f"   Error: {response.status_code}")
except Exception as e:
    print(f"   Error: {e}")

# Test 2: Test vector search (requires embeddings)
print("\n2. Testing vector search...")
try:
    response = requests.post(
        f"{API_URL}/search",
        json={
            "query": "spawn aircraft",
            "limit": 3,
            "search_type": "vector"
        }
    )
    if response.status_code == 200:
        result = response.json()
        print(f"   ✓ Vector search successful")
        print(f"   Found {result.get('count', 0)} results")
        if result.get('count', 0) == 0:
            print("   ⚠️  No results found - embeddings may not be generated yet")
    else:
        print(f"   ✗ Error: {response.status_code}")
        print(f"   {response.text}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 3: Test hybrid search
print("\n3. Testing hybrid search...")
try:
    response = requests.post(
        f"{API_URL}/search",
        json={
            "query": "create waypoints for aircraft",
            "limit": 3,
            "search_type": "hybrid"
        }
    )
    if response.status_code == 200:
        result = response.json()
        print(f"   ✓ Hybrid search successful")
        print(f"   Found {result.get('count', 0)} results")
        
        # Show a sample result if available
        results = result.get('results', [])
        if results:
            first = results[0]
            print(f"\n   Sample result:")
            print(f"   File: {first.get('file_path', 'unknown')}")
            print(f"   Type: {first.get('chunk_type', 'unknown')}")
            print(f"   Lines: {first.get('line_start', '?')}-{first.get('line_end', '?')}")
            print(f"   Score: {first.get('score', 0):.3f}")
    else:
        print(f"   ✗ Error: {response.status_code}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 4: Test Ollama connectivity through API
print("\n4. Testing Ollama embedding generation...")
try:
    # This tests if the API can actually generate embeddings
    response = requests.post(
        f"{API_URL}/search",
        json={
            "query": "test embedding generation",
            "limit": 1,
            "search_type": "vector"
        }
    )
    if response.status_code == 200:
        print("   ✓ API can process embedding requests")
    else:
        print("   ✗ API cannot process embedding requests")
        print(f"   Status: {response.status_code}")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n" + "="*50)
print("Embedding Test Complete")
print("\nIf vector searches return no results, you may need to:")
print("1. Check that the lua_chunks table has data")
print("2. Regenerate embeddings for existing chunks")
print("3. Verify Ollama is running with the correct model")