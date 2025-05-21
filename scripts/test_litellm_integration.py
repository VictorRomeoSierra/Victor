#!/usr/bin/env python3
"""
Test script for LiteLLM + Victor RAG integration.
This script tests the complete pipeline from query to enhanced response.
"""

import asyncio
import httpx
import json
import logging
import time
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("victor-litellm-test")

class LiteLLMTester:
    """
    Test suite for LiteLLM + Victor integration.
    """
    
    def __init__(self, 
                 litellm_url: str = "http://localhost:4000",
                 victor_url: str = "http://localhost:8000"):
        self.litellm_url = litellm_url
        self.victor_url = victor_url
        
    async def test_victor_api(self) -> bool:
        """Test Victor API endpoints."""
        logger.info("🧪 Testing Victor API...")
        
        try:
            async with httpx.AsyncClient() as client:
                # Test health endpoint
                response = await client.get(f"{self.victor_url}/health")
                if response.status_code != 200:
                    logger.error(f"❌ Victor health check failed: {response.status_code}")
                    return False
                    
                # Test enhance_prompt endpoint
                test_prompt = "How do I create a DCS mission trigger?"
                response = await client.post(
                    f"{self.victor_url}/enhance_prompt",
                    json={"prompt": test_prompt, "model": "codellama"}
                )
                
                if response.status_code != 200:
                    logger.error(f"❌ Victor enhance_prompt failed: {response.status_code}")
                    return False
                    
                result = response.json()
                enhanced = result.get("enhanced_prompt", "")
                
                if enhanced and enhanced != test_prompt:
                    logger.info("✅ Victor API enhancement working")
                    logger.info(f"   Original: {test_prompt}")
                    logger.info(f"   Enhanced: {enhanced[:100]}...")
                    return True
                else:
                    logger.warning("⚠️ Victor API returned unchanged prompt")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Victor API test failed: {e}")
            return False
    
    async def test_litellm_api(self) -> bool:
        """Test LiteLLM API endpoints."""
        logger.info("🧪 Testing LiteLLM API...")
        
        try:
            async with httpx.AsyncClient() as client:
                # Test health endpoint
                response = await client.get(f"{self.litellm_url}/health")
                if response.status_code != 200:
                    logger.error(f"❌ LiteLLM health check failed: {response.status_code}")
                    return False
                    
                # Test models endpoint
                response = await client.get(f"{self.litellm_url}/models")
                if response.status_code != 200:
                    logger.error(f"❌ LiteLLM models endpoint failed: {response.status_code}")
                    return False
                    
                models = response.json()
                model_names = [model["id"] for model in models.get("data", [])]
                logger.info(f"✅ LiteLLM models available: {model_names}")
                
                return True
                
        except Exception as e:
            logger.error(f"❌ LiteLLM API test failed: {e}")
            return False
    
    async def test_rag_integration(self) -> bool:
        """Test the complete RAG integration."""
        logger.info("🧪 Testing RAG integration...")
        
        test_cases = [
            {
                "name": "DCS-related query",
                "message": "How do I create a waypoint for an F-16 in DCS using Lua?",
                "should_enhance": True
            },
            {
                "name": "Non-DCS query", 
                "message": "What's the weather like today?",
                "should_enhance": False
            },
            {
                "name": "Code-related DCS query",
                "message": "Show me how to write a Lua script for DCS mission triggers",
                "should_enhance": True
            }
        ]
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                for test_case in test_cases:
                    logger.info(f"   Testing: {test_case['name']}")
                    
                    # Test with a DCS-optimized model
                    payload = {
                        "model": "dcs-codellama",
                        "messages": [
                            {"role": "user", "content": test_case["message"]}
                        ],
                        "max_tokens": 50,
                        "stream": False
                    }
                    
                    start_time = time.time()
                    response = await client.post(
                        f"{self.litellm_url}/v1/chat/completions",
                        json=payload
                    )
                    end_time = time.time()
                    
                    if response.status_code == 200:
                        result = response.json()
                        response_content = result["choices"][0]["message"]["content"]
                        logger.info(f"   ✅ Response received ({end_time - start_time:.2f}s)")
                        logger.info(f"      Content preview: {response_content[:100]}...")
                    else:
                        logger.error(f"   ❌ Request failed: {response.status_code} - {response.text}")
                        return False
                        
            return True
            
        except Exception as e:
            logger.error(f"❌ RAG integration test failed: {e}")
            return False
    
    async def test_model_routing(self) -> bool:
        """Test automatic model routing based on query type."""
        logger.info("🧪 Testing model routing...")
        
        # This would require implementing model selection logic
        # For now, just verify different models are accessible
        
        models_to_test = ["dcs-codellama", "dcs-llama3"]
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                for model in models_to_test:
                    payload = {
                        "model": model,
                        "messages": [
                            {"role": "user", "content": "Hello, are you working?"}
                        ],
                        "max_tokens": 10,
                        "stream": False
                    }
                    
                    response = await client.post(
                        f"{self.litellm_url}/v1/chat/completions",
                        json=payload
                    )
                    
                    if response.status_code == 200:
                        logger.info(f"   ✅ Model {model} is accessible")
                    else:
                        logger.error(f"   ❌ Model {model} failed: {response.status_code}")
                        return False
                        
            return True
            
        except Exception as e:
            logger.error(f"❌ Model routing test failed: {e}")
            return False
    
    async def run_all_tests(self) -> Dict[str, bool]:
        """Run all tests and return results."""
        logger.info("🚀 Starting LiteLLM + Victor integration tests...")
        
        results = {}
        
        # Test individual components
        results["victor_api"] = await self.test_victor_api()
        results["litellm_api"] = await self.test_litellm_api()
        
        # Test integration features
        if results["victor_api"] and results["litellm_api"]:
            results["rag_integration"] = await self.test_rag_integration()
            results["model_routing"] = await self.test_model_routing()
        else:
            logger.warning("⚠️ Skipping integration tests due to API failures")
            results["rag_integration"] = False
            results["model_routing"] = False
        
        # Print summary
        logger.info("\n📊 Test Results Summary:")
        for test_name, passed in results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            logger.info(f"   {test_name}: {status}")
        
        overall_success = all(results.values())
        overall_status = "✅ ALL TESTS PASSED" if overall_success else "❌ SOME TESTS FAILED"
        logger.info(f"\n{overall_status}")
        
        return results

async def main():
    """Main test function."""
    tester = LiteLLMTester()
    results = await tester.run_all_tests()
    
    # Exit with appropriate code
    if all(results.values()):
        exit(0)
    else:
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())