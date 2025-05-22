# LiteLLM Web Interface Configuration for Victor RAG

## Overview
Configure LiteLLM running on the Mac Mini to integrate with Victor's RAG system through the web interface.

## Access Points
- **LiteLLM API Documentation**: http://10.0.0.130:4000/
- **Admin Interface**: http://10.0.0.130:4000/ui (if enabled)
- **Public Access**: https://ai.victorromeosierra.com/ (will need routing setup)

## Current Status
✅ LiteLLM is running on Mac Mini port 4000  
⚠️ Authentication is enabled (requires API key)  
✅ Swagger UI is available for API documentation  

## Configuration Steps

### 1. Access the Web Interface
Navigate to: http://10.0.0.130:4000/

This will show the Swagger UI where you can:
- View available endpoints
- Test API calls
- Configure models
- Set up authentication

### 2. Enable Victor RAG Integration

#### Option A: Through Configuration File
If LiteLLM is using a config file, update it with:

```yaml
# litellm_config.yaml
model_list:
  - model_name: dcs-codellama
    litellm_params:
      model: ollama/codellama  
      api_base: http://localhost:11434
    model_info:
      description: "CodeLlama with DCS RAG context"

# Add pre-request hooks for Victor integration
general_settings:
  callbacks: ["victor_rag"]
  
environment_variables:
  VICTOR_API_URL: "http://localhost:8000"
```

#### Option B: Through API Calls
Use the LiteLLM API to configure models and hooks:

```bash
# Add a new model with Victor RAG
curl -X POST http://10.0.0.130:4000/model/new \
  -H "Authorization: Bearer YOUR_ADMIN_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "dcs-codellama",
    "litellm_params": {
      "model": "ollama/codellama",
      "api_base": "http://localhost:11434"
    },
    "model_info": {
      "description": "CodeLlama with DCS RAG enhancement"
    }
  }'
```

### 3. Configure Pre-Request Hooks

To enable automatic RAG enhancement, we need to set up pre-request hooks that call Victor API:

```python
# This would be added to LiteLLM's callback system
async def victor_rag_callback(kwargs, completion_response=None, start_time=None):
    if completion_response is None:  # Pre-request
        messages = kwargs.get("messages", [])
        if messages and messages[-1].get("role") == "user":
            # Call Victor API to enhance prompt
            victor_response = await call_victor_api(messages[-1]["content"])
            if victor_response:
                kwargs["messages"][-1]["content"] = victor_response
    return kwargs
```

### 4. Test the Integration

#### Test Basic LiteLLM Functionality:
```bash
curl -X POST http://10.0.0.130:4000/v1/chat/completions \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "codellama",
    "messages": [{"role": "user", "content": "Hello"}],
    "max_tokens": 50
  }'
```

#### Test DCS RAG Enhancement:
```bash
curl -X POST http://10.0.0.130:4000/v1/chat/completions \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "dcs-codellama", 
    "messages": [{"role": "user", "content": "How do I create a DCS mission trigger?"}],
    "max_tokens": 100
  }'
```

## Authentication Setup

### Find/Set Admin Key
LiteLLM requires authentication. Check the Mac Mini for:

1. **Environment Variables**:
   ```bash
   # Check for existing keys
   env | grep -i litellm
   env | grep -i master
   ```

2. **Configuration Files**:
   ```bash
   # Look for config files
   find /path/to/litellm -name "*.yaml" -o -name "*.yml" -o -name "*.env"
   ```

3. **Docker Logs**:
   ```bash
   # Check Docker logs for the admin key
   docker logs litellm-container-name
   ```

### Set Up API Keys for Victor Integration
Once you have admin access, create an API key specifically for Victor:

```bash
curl -X POST http://10.0.0.130:4000/key/generate \
  -H "Authorization: Bearer ADMIN_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "key_alias": "victor-rag",
    "duration": null,
    "models": ["dcs-codellama", "dcs-llama3"],
    "metadata": {"description": "Victor RAG integration key"}
  }'
```

## Nginx Routing for External Access

Add to your nginx configuration to make LiteLLM accessible externally:

```nginx
# Add to ai.victorromeosierra.com server block
location /llm/ {
    proxy_pass http://10.0.0.130:4000/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # WebSocket support
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

## Verification Steps

### 1. Check Model Availability
```bash
curl -H "Authorization: Bearer YOUR_KEY" http://10.0.0.130:4000/models
```

### 2. Test Victor API Integration
```bash
# This should return enhanced prompt for DCS queries
curl -X POST https://ai.victorromeosierra.com/victor/enhance_prompt \
  -H "Content-Type: application/json" \
  -d '{"prompt": "How do I create DCS waypoints?", "model": "codellama"}'
```

### 3. Test End-to-End Flow
1. Open Open-WebUI: https://ai.victorromeosierra.com/
2. Select a DCS-optimized model
3. Ask a DCS-related question
4. Verify the response includes code context

## Troubleshooting

### Common Issues:
1. **401 Authentication Error**: Missing or invalid API key
2. **Model Not Found**: Model not properly configured in LiteLLM
3. **Victor API Timeout**: Victor API not responding or wrong URL
4. **No RAG Enhancement**: Pre-request hooks not configured

### Debug Commands:
```bash
# Check LiteLLM status
curl http://10.0.0.130:4000/health

# Check Victor API status  
curl https://ai.victorromeosierra.com/victor/health

# Check available models
curl -H "Authorization: Bearer KEY" http://10.0.0.130:4000/models
```

## Next Steps

1. **Access LiteLLM web interface** to get admin credentials
2. **Configure DCS-specific models** with RAG enhancement
3. **Set up pre-request hooks** for automatic context injection
4. **Test the complete pipeline** with Open-WebUI
5. **Add nginx routing** for external access (optional)