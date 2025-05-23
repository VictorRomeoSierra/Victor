"""
title: Victor DCS - Llama 3.2
author: VictorRomeoSierra
version: 1.0.0
license: MIT
description: Victor DCS Assistant using Llama 3.2 model
requirements: requests, pydantic
"""

import requests
import json
from pydantic import BaseModel, Field

class Pipe:
    class Valves(BaseModel):
        timeout: int = Field(
            default=120,
            description="Request timeout in seconds (default: 120)"
        )
        debug: bool = Field(
            default=False,
            description="Enable debug logging"
        )
    
    def __init__(self):
        self.type = "pipe"
        self.id = "victor_llama32"
        self.name = "Victor DCS - Llama 3.2"
        self.valves = self.Valves()
        
        # Model configuration
        self.ollama_model = "llama3.2:latest"
        
        # N8N Webhook Configuration
        self.api_url = "https://n8n.victorromeosierra.com/webhook/victor-local-chat"
        self.verify_ssl = True

    def pipe(self, body: dict) -> str:
        """Routes requests through N8N webhook for DCS-enhanced responses using Llama 3.2."""
        
        try:
            # Extract user message
            messages = body.get("messages", [])
            user_message = None
            for msg in reversed(messages):
                if msg.get("role") == "user":
                    user_message = msg.get("content", "")
                    break
            
            if not user_message:
                return "Error: No user message found"
            
            if self.valves.debug:
                print(f"[Victor-Llama 3.2] Processing: {user_message[:50]}...")
                print(f"[Victor-Llama 3.2] Timeout: {self.valves.timeout}s, Model: {self.ollama_model}")
            
            # Prepare payload for N8N webhook
            payload = {
                "messages": messages,
                "model": self.ollama_model,
                "stream": False,
                "temperature": body.get("temperature", 0.7),
                "max_tokens": body.get("max_tokens"),
                "user": user_message
            }
            
            # Send request to N8N webhook
            if self.valves.debug:
                print(f"[Victor-Llama 3.2] Sending request to N8N...")
            
            response = requests.post(
                self.api_url,
                headers={'Content-Type': 'application/json'},
                json=payload,
                timeout=self.valves.timeout,
                verify=self.verify_ssl
            )
            
            if self.valves.debug:
                print(f"[Victor-Llama 3.2] Received response: {response.status_code}")
            
            if response.status_code != 200:
                return f"Error: N8N returned status {response.status_code}"
            
            if not response.text:
                return "Error: N8N returned empty response"
            
            # Parse response
            try:
                response_data = response.json()
                
                # Handle OpenAI-style response format
                if isinstance(response_data, dict):
                    # Check for OpenAI chat completion format
                    if "choices" in response_data and isinstance(response_data["choices"], list):
                        if len(response_data["choices"]) > 0:
                            choice = response_data["choices"][0]
                            if "message" in choice and "content" in choice["message"]:
                                return choice["message"]["content"]
                    
                    # Try other common response fields
                    for field in ["response", "message", "content", "output"]:
                        if field in response_data:
                            return response_data[field]
                    
                    # If no recognized field, return error
                    return f"Unexpected response format from N8N: {list(response_data.keys())}"
                else:
                    return str(response_data)
                    
            except json.JSONDecodeError:
                return response.text
                
        except requests.exceptions.Timeout:
            return (
                f"Error: Request timed out after {self.valves.timeout} seconds. "
                "Try increasing the timeout in the function settings or use a more specific query."
            )
        except requests.exceptions.ConnectionError:
            return "Error: Failed to connect to Victor service. Please try again."
        except Exception as e:
            return f"Error: {str(e)}"
