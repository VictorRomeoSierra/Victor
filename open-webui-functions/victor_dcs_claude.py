"""
title: Victor DCS - Claude 3.7
author: VictorRomeoSierra
version: 1.0.0
license: MIT
description: Victor DCS Assistant using Claude API via N8N
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
        self.id = "victor_claude"
        self.name = "Victor DCS - Claude"
        self.valves = self.Valves()
        
        # N8N Webhook Configuration for Claude workflow
        self.api_url = "https://n8n.victorromeosierra.com/webhook/victor-chat"
        self.verify_ssl = True

    def pipe(self, body: dict) -> str:
        """Routes requests through N8N webhook for DCS-enhanced responses using Claude."""
        
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
                print(f"[Victor-Claude] Processing: {user_message[:50]}...")
                print(f"[Victor-Claude] Timeout: {self.valves.timeout}s")
            
            # Prepare payload for N8N webhook
            # This webhook expects a different format for Claude
            payload = {
                "messages": messages,
                "model": "claude-3-7-sonnet-latest",  # Claude model identifier - must match N8N config
                "stream": False,  # TODO: Implement streaming support
                "temperature": body.get("temperature", 0.7),
                "max_tokens": body.get("max_tokens"),
                "user": user_message
            }
            
            # Send request to N8N webhook
            if self.valves.debug:
                print(f"[Victor-Claude] Sending request to N8N Claude webhook...")
            
            response = requests.post(
                self.api_url,
                headers={'Content-Type': 'application/json'},
                json=payload,
                timeout=self.valves.timeout,
                verify=self.verify_ssl
            )
            
            if self.valves.debug:
                print(f"[Victor-Claude] Received response: {response.status_code}")
            
            if response.status_code != 200:
                return f"Error: N8N returned status {response.status_code}"
            
            if not response.text:
                return "Error: N8N returned empty response"
            
            # Parse response
            try:
                response_data = response.json()
                
                # Handle various response formats
                if isinstance(response_data, dict):
                    # Claude API response format
                    if "content" in response_data:
                        # Direct Claude response
                        if isinstance(response_data["content"], list):
                            # Claude v3 format with content blocks
                            for block in response_data["content"]:
                                if block.get("type") == "text":
                                    return block.get("text", "")
                        else:
                            return response_data["content"]
                    
                    # OpenAI-compatible format
                    if "choices" in response_data and isinstance(response_data["choices"], list):
                        if len(response_data["choices"]) > 0:
                            choice = response_data["choices"][0]
                            if "message" in choice and "content" in choice["message"]:
                                return choice["message"]["content"]
                    
                    # Try other common response fields
                    for field in ["response", "message", "output", "text"]:
                        if field in response_data:
                            return response_data[field]
                    
                    # If no recognized field, return error with available keys
                    return f"Unexpected response format from N8N: {list(response_data.keys())}"
                else:
                    return str(response_data)
                    
            except json.JSONDecodeError:
                return response.text
                
        except requests.exceptions.Timeout:
            return (
                f"Error: Request timed out after {self.valves.timeout} seconds. "
                "Claude responses can take time for complex queries. Try increasing the timeout."
            )
        except requests.exceptions.ConnectionError:
            return "Error: Failed to connect to Victor Claude service. Please try again."
        except Exception as e:
            return f"Error: {str(e)}"