# Configuring Open-WebUI to Use N8N Victor Webhook

This guide explains how to configure Open-WebUI to use the N8N webhook endpoint that provides Victor-enhanced responses with XSAF code context.

## Overview

The N8N webhook acts as an OpenAI-compatible API endpoint that:
1. Receives chat requests from Open-WebUI
2. Detects DCS-related queries
3. Enhances them with XSAF code snippets via Victor API
4. Routes to Ollama for generation
5. Returns OpenAI-compatible responses

## Configuration Steps

### 1. Access Open-WebUI Settings

Navigate to Open-WebUI and access the settings/admin panel. This is typically done by:
- Clicking on your profile/avatar
- Selecting "Settings" or "Admin Panel"

### 2. Add Custom Model

In the Models or Connections section:

1. **Add New OpenAI API Connection**:
   - Name: `Victor-Enhanced Ollama`
   - API Base URL: `https://n8n.victorromeosierra.com/webhook`
   - API Key: `victor-local-chat` (or any placeholder, as N8N doesn't validate keys)
   - Model: `victor-local-chat`

2. **Alternative: Environment Variables**:
   If Open-WebUI uses environment variables, add:
   ```bash
   OPENAI_API_BASE=https://n8n.victorromeosierra.com/webhook
   OPENAI_API_KEY=victor-local-chat
   DEFAULT_MODELS=victor-local-chat
   ```

### 3. Model Configuration

Configure the model settings:
- Display Name: `Victor DCS Assistant`
- Description: `Ollama with XSAF code context for DCS Lua programming`
- Context Length: 4096
- Default Temperature: 0.7

### 4. Testing

1. Select the "Victor DCS Assistant" model in the chat interface
2. Test with a DCS-related query:
   ```
   How do I create waypoints in DCS?
   ```
3. Verify the response includes XSAF code examples

## Webhook Details

- **Endpoint**: `https://n8n.victorromeosierra.com/webhook/victor-local-chat`
- **Method**: POST
- **Request Format**: OpenAI Chat Completion API
- **Response Format**: OpenAI Chat Completion API

### Request Example:
```json
{
  "model": "codellama:latest",
  "messages": [
    {
      "role": "user",
      "content": "How do I spawn units in DCS?"
    }
  ],
  "stream": false
}
```

### Response Example:
```json
{
  "id": "chatcmpl-xxxxx",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "codellama:latest",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "To spawn units in DCS... [includes XSAF code examples]"
    },
    "finish_reason": "stop"
  }],
  "usage": {
    "prompt_tokens": 100,
    "completion_tokens": 200,
    "total_tokens": 300
  }
}
```

## Troubleshooting

### Issue: Connection Failed
- Verify the webhook URL is accessible: `curl https://n8n.victorromeosierra.com/webhook/victor-local-chat`
- Check N8N workflow is active
- Ensure CORS is properly configured if needed

### Issue: No Code Context in Responses
- Verify Victor API is running: `http://localhost:8000/health`
- Check vector database has embeddings: `http://localhost:8000/stats`
- Ensure DCS keywords are in the query

### Issue: Timeout Errors
- Ollama generation can take 15-30 seconds
- Increase timeout in Open-WebUI settings if possible
- Check N8N workflow timeout settings (currently 60s)

## Advanced Configuration

### Multiple Models
You can add multiple endpoints for different use cases:
- `victor-local-chat` - For DCS/XSAF queries
- Direct Ollama endpoint - For general queries
- LiteLLM endpoint - For other models

### Streaming Support
The webhook currently has `stream: false`. For streaming support:
1. Update N8N workflow to handle streaming
2. Enable streaming in Open-WebUI model settings

## Architecture

```
Open-WebUI → N8N Webhook → Is DCS Query?
                              ├─ Yes → Victor API (RAG) → Ollama
                              └─ No → Ollama Direct
```

This setup ensures DCS-related queries get enhanced with relevant XSAF code snippets while general queries go directly to Ollama.