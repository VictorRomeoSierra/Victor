"""
LiteLLM Configuration with Victor RAG Integration
This module provides the configuration and hooks for integrating
Victor's RAG system with LiteLLM.
"""

import litellm
import httpx
import os
import logging
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("victor-litellm")

class VictorRAGIntegration:
    """
    Victor RAG integration for LiteLLM.
    Handles automatic prompt enhancement with DCS code context.
    """
    
    def __init__(self):
        self.victor_api_url = os.getenv("VICTOR_API_URL", "http://localhost:8000")
        self.timeout = float(os.getenv("VICTOR_TIMEOUT", "10.0"))
        self.enabled = os.getenv("VICTOR_RAG_ENABLED", "true").lower() == "true"
        
        logger.info(f"Victor RAG Integration initialized:")
        logger.info(f"  API URL: {self.victor_api_url}")
        logger.info(f"  Timeout: {self.timeout}s")
        logger.info(f"  Enabled: {self.enabled}")
    
    async def enhance_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enhance the last user message with Victor RAG context.
        """
        if not self.enabled or not messages:
            return messages
            
        # Find the last user message
        last_user_msg = None
        last_user_idx = None
        
        for i in range(len(messages) - 1, -1, -1):
            if messages[i].get("role") == "user":
                last_user_msg = messages[i]
                last_user_idx = i
                break
        
        if not last_user_msg:
            return messages
            
        try:
            # Call Victor API to enhance the prompt
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.victor_api_url}/enhance_prompt",
                    json={
                        "prompt": last_user_msg["content"],
                        "model": "codellama"
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    enhanced_prompt = result.get("enhanced_prompt")
                    
                    if enhanced_prompt and enhanced_prompt != last_user_msg["content"]:
                        # Create a copy of messages and update the last user message
                        enhanced_messages = messages.copy()
                        enhanced_messages[last_user_idx] = {
                            **last_user_msg,
                            "content": enhanced_prompt
                        }
                        
                        logger.info("Successfully enhanced prompt with Victor RAG context")
                        return enhanced_messages
                    else:
                        logger.info("Prompt was not enhanced (not DCS-related or unchanged)")
                else:
                    logger.warning(f"Victor API returned status {response.status_code}: {response.text}")
                    
        except Exception as e:
            logger.error(f"Victor RAG enhancement failed: {e}")
            
        return messages
    
    def should_use_code_model(self, messages: List[Dict[str, Any]]) -> bool:
        """
        Determine if we should route to a code-specialized model.
        """
        if not messages:
            return False
            
        # Check if any message contains DCS/code keywords
        dcs_keywords = ["dcs", "lua", "mission", "script", "trigger", "event", "xsaf", "function", "code"]
        
        for message in messages:
            if message.get("role") == "user":
                content = message.get("content", "").lower()
                if any(keyword in content for keyword in dcs_keywords):
                    return True
                    
        return False

# Global instance
victor_rag = VictorRAGIntegration()

async def victor_pre_call_hook(user_api_key_dict, cache, data, call_type):
    """
    Pre-call hook for LiteLLM to enhance prompts with Victor RAG.
    """
    try:
        if "messages" in data:
            # Enhance messages with Victor RAG
            data["messages"] = await victor_rag.enhance_messages(data["messages"])
            
            # Optionally route to code model for DCS queries
            if victor_rag.should_use_code_model(data["messages"]):
                original_model = data.get("model", "")
                if "codellama" not in original_model.lower():
                    # Switch to CodeLlama if available
                    if "ollama/" in original_model:
                        data["model"] = "ollama/codellama"
                        logger.info(f"Routed DCS query from {original_model} to ollama/codellama")
                    
    except Exception as e:
        logger.error(f"Error in Victor pre-call hook: {e}")
        # Don't fail the request if enhancement fails
        
    return data

# Register the pre-call hook with LiteLLM
litellm.pre_call_hooks = [victor_pre_call_hook]

# Model configurations
VICTOR_MODELS = [
    {
        "model_name": "dcs-codellama",
        "litellm_params": {
            "model": "ollama/codellama",
            "api_base": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        },
        "model_info": {
            "description": "CodeLlama optimized for DCS Lua development with RAG context",
            "mode": "chat"
        }
    },
    {
        "model_name": "dcs-llama3",
        "litellm_params": {
            "model": "ollama/llama3",
            "api_base": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        },
        "model_info": {
            "description": "Llama3 with DCS RAG context for general assistance", 
            "mode": "chat"
        }
    }
]

# Additional Claude integration if API key available
if os.getenv("ANTHROPIC_API_KEY"):
    VICTOR_MODELS.append({
        "model_name": "dcs-claude",
        "litellm_params": {
            "model": "claude-3-sonnet-20240229",
            "api_key": os.getenv("ANTHROPIC_API_KEY")
        },
        "model_info": {
            "description": "Claude Sonnet with DCS RAG context for advanced analysis",
            "mode": "chat"
        }
    })

# Test configuration with provided API key
VICTOR_MODELS.append({
    "model_name": "claude-test",
    "litellm_params": {
        "model": "claude-3-sonnet-20240229", 
        "api_key": "sk-GvsVf6xdqB0eSMtPxitTsQ"
    },
    "model_info": {
        "description": "Claude Sonnet test configuration",
        "mode": "chat"
    }
})

def configure_litellm():
    """
    Configure LiteLLM with Victor settings.
    """
    # Set global configurations
    litellm.success_callback = ["langfuse"]  # Add observability if needed
    litellm.failure_callback = ["langfuse"]
    
    # Configure timeouts
    litellm.request_timeout = 300  # 5 minutes for code generation
    
    logger.info("LiteLLM configured with Victor RAG integration")
    logger.info(f"Available models: {[model['model_name'] for model in VICTOR_MODELS]}")

if __name__ == "__main__":
    configure_litellm()
    print("Victor LiteLLM configuration loaded successfully")