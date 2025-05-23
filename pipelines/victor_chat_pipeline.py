"""
title: Victor DCS Chat Pipeline
author: VictorRomeoSierra
date: 2025-05-23
version: 1.0
license: MIT
description: Routes chat requests through N8N webhook for DCS-enhanced responses using Victor RAG system
requirements: requests
"""

from typing import List, Union, Generator, Iterator, Optional
from pydantic import BaseModel
import requests
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Pipeline:
    """
    Victor DCS Chat Pipeline
    
    This pipeline routes chat requests through the N8N webhook at n8n.victorromeosierra.com
    which detects DCS-related queries and enhances them with XSAF code context from the
    Victor RAG system before sending to Ollama for response generation.
    """
    
    class Valves(BaseModel):
        webhook_url: str = "https://n8n.victorromeosierra.com/webhook/victor-local-chat"
        timeout: int = 30
        verify_ssl: bool = True
        debug: bool = False
        description: str = "Webhook URL for N8N Victor integration"

    def __init__(self):
        self.name = "Victor DCS Assistant"
        self.id = "victor-dcs-chat"
        self.valves = self.Valves()

    async def on_startup(self):
        """Called when the server starts."""
        logger.info(f"Starting {self.name} pipeline")
        logger.info(f"Webhook URL: {self.valves.webhook_url}")

    async def on_shutdown(self):
        """Called when the server stops."""
        logger.info(f"Shutting down {self.name} pipeline")

    async def inlet(self, body: dict, user: Optional[dict] = None) -> dict:
        """Pre-process the request before sending to the pipeline."""
        if self.valves.debug:
            logger.debug(f"Inlet - Body: {json.dumps(body, indent=2)}")
            logger.debug(f"Inlet - User: {user}")
        
        # Ensure we have the required fields
        if "messages" not in body:
            body["messages"] = []
        
        return body

    async def outlet(self, body: dict, user: Optional[dict] = None) -> dict:
        """Post-process the response after receiving from the pipeline."""
        if self.valves.debug:
            logger.debug(f"Outlet - Body: {json.dumps(body, indent=2)}")
        
        return body

    def pipe(
        self,
        user_message: str,
        model_id: str,
        messages: List[dict],
        body: dict
    ) -> Union[str, Generator, Iterator]:
        """
        Main pipeline logic that routes requests through N8N webhook.
        
        The N8N workflow will:
        1. Detect if the query is DCS-related
        2. If DCS: Route through Victor API to get XSAF code context
        3. Send enhanced prompt to Ollama (codellama model)
        4. If not DCS: Send directly to Ollama
        """
        try:
            if self.valves.debug:
                logger.debug(f"Pipe - User message: {user_message}")
                logger.debug(f"Pipe - Model ID: {model_id}")
                logger.debug(f"Pipe - Messages count: {len(messages)}")
                logger.debug(f"Pipe - Stream: {body.get('stream', False)}")

            # Prepare headers
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            # Prepare payload for N8N webhook
            # N8N expects the data in a specific format based on the workflow
            payload = {
                "messages": messages,
                "model": model_id,
                "stream": body.get("stream", False),
                "temperature": body.get("temperature", 0.7),
                "max_tokens": body.get("max_tokens"),
                "user": user_message  # Include the latest message for easy access
            }
            
            if self.valves.debug:
                logger.debug(f"Sending request to: {self.valves.webhook_url}")
                logger.debug(f"Payload: {json.dumps(payload, indent=2)}")
            
            # Send request to N8N webhook
            response = requests.post(
                self.valves.webhook_url,
                headers=headers,
                json=payload,
                timeout=self.valves.timeout,
                verify=self.valves.verify_ssl,
                stream=body.get("stream", False)
            )
            
            response.raise_for_status()
            
            # Handle streaming response
            if body.get("stream", False):
                def stream_response():
                    """Generator for streaming responses."""
                    for line in response.iter_lines():
                        if line:
                            try:
                                decoded_line = line.decode('utf-8')
                                if self.valves.debug:
                                    logger.debug(f"Stream chunk: {decoded_line}")
                                yield decoded_line
                            except Exception as e:
                                logger.error(f"Stream decode error: {e}")
                                if self.valves.debug:
                                    yield f"data: {json.dumps({'error': str(e)})}\n\n"
                
                return stream_response()
            else:
                # Non-streaming response
                response_data = response.json()
                
                if self.valves.debug:
                    logger.debug(f"Response data: {json.dumps(response_data, indent=2)}")
                
                # Extract the actual response from N8N
                # N8N should return a response in the format we expect
                if isinstance(response_data, dict):
                    # Try different possible response formats
                    if "response" in response_data:
                        return response_data["response"]
                    elif "message" in response_data:
                        return response_data["message"]
                    elif "content" in response_data:
                        return response_data["content"]
                    elif "choices" in response_data and len(response_data["choices"]) > 0:
                        # OpenAI-style response format
                        return response_data["choices"][0].get("message", {}).get("content", str(response_data))
                    else:
                        # Return the whole response if we can't find a specific field
                        return json.dumps(response_data)
                else:
                    # If response is a string, return it directly
                    return str(response_data)
                
        except requests.exceptions.Timeout:
            error_msg = f"Request to N8N webhook timed out after {self.valves.timeout} seconds"
            logger.error(error_msg)
            return f"Error: {error_msg}"
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Failed to connect to N8N webhook: {str(e)}"
            logger.error(error_msg)
            return f"Error: {error_msg}"
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP error from N8N webhook: {e.response.status_code} - {e.response.text}"
            logger.error(error_msg)
            return f"Error: {error_msg}"
        except json.JSONDecodeError as e:
            error_msg = f"Failed to parse JSON response from N8N: {str(e)}"
            logger.error(error_msg)
            return f"Error: {error_msg}"
        except Exception as e:
            error_msg = f"Unexpected error in Victor pipeline: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return f"Error: {error_msg}"

    async def on_valves_updated(self):
        """Called when valves are updated via the UI."""
        logger.info(f"Valves updated - Webhook URL: {self.valves.webhook_url}")
        logger.info(f"Debug mode: {self.valves.debug}")