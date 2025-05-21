#!/usr/bin/env python3
"""
Startup script for LiteLLM with Victor RAG integration.
This script configures and starts LiteLLM with the Victor RAG hooks.
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.litellm_config import configure_litellm, VICTOR_MODELS, victor_pre_call_hook
import litellm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("victor-litellm-startup")

def setup_environment():
    """
    Set up environment variables for LiteLLM with Victor integration.
    """
    # Set default values if not already set
    env_defaults = {
        "VICTOR_API_URL": "http://localhost:8000",
        "VICTOR_TIMEOUT": "10.0", 
        "VICTOR_RAG_ENABLED": "true",
        "OLLAMA_BASE_URL": "http://localhost:11434",
        "LITELLM_PORT": "4000",
        "LITELLM_HOST": "0.0.0.0"
    }
    
    for key, default_value in env_defaults.items():
        if key not in os.environ:
            os.environ[key] = default_value
            logger.info(f"Set {key}={default_value}")

async def test_victor_connection():
    """
    Test connection to Victor API before starting LiteLLM.
    """
    import httpx
    
    victor_url = os.getenv("VICTOR_API_URL", "http://localhost:8000")
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{victor_url}/health")
            if response.status_code == 200:
                logger.info("✅ Victor API connection successful")
                return True
            else:
                logger.warning(f"⚠️ Victor API returned status {response.status_code}")
                return False
    except Exception as e:
        logger.error(f"❌ Failed to connect to Victor API: {e}")
        return False

def start_litellm():
    """
    Start LiteLLM with Victor configuration.
    """
    try:
        # Configure LiteLLM with Victor settings
        configure_litellm()
        
        # Set up model configurations
        for model_config in VICTOR_MODELS:
            logger.info(f"Configured model: {model_config['model_name']}")
        
        # Import and start LiteLLM proxy
        from litellm.proxy.proxy_server import app
        import uvicorn
        
        # Get host and port from environment
        host = os.getenv("LITELLM_HOST", "0.0.0.0")
        port = int(os.getenv("LITELLM_PORT", "4000"))
        
        logger.info(f"Starting LiteLLM with Victor RAG integration on {host}:{port}")
        logger.info("Available endpoints:")
        logger.info(f"  - Health check: http://{host}:{port}/health")
        logger.info(f"  - Models: http://{host}:{port}/models")
        logger.info(f"  - Chat completions: http://{host}:{port}/v1/chat/completions")
        
        # Start the server
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info",
            reload=False
        )
        
    except Exception as e:
        logger.error(f"Failed to start LiteLLM: {e}")
        sys.exit(1)

async def main():
    """
    Main startup function.
    """
    logger.info("🚀 Starting LiteLLM with Victor RAG integration...")
    
    # Set up environment
    setup_environment()
    
    # Test Victor API connection
    victor_connected = await test_victor_connection()
    if not victor_connected:
        logger.warning("⚠️ Victor API not available - RAG enhancement will be disabled")
        os.environ["VICTOR_RAG_ENABLED"] = "false"
    
    # Start LiteLLM
    start_litellm()

if __name__ == "__main__":
    asyncio.run(main())