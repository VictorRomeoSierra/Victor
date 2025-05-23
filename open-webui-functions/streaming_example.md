# Streaming Response Implementation Guide

## Overview
Streaming responses would provide a better user experience by showing text as it's generated rather than waiting for the complete response.

## Technical Challenges

### 1. N8N Limitations
N8N webhooks typically return complete responses, not streams. To implement streaming:

**Option A: Server-Sent Events (SSE)**
```javascript
// N8N Code node example
const response = $response;
response.setHeader('Content-Type', 'text/event-stream');
response.setHeader('Cache-Control', 'no-cache');
response.setHeader('Connection', 'keep-alive');

// Stream chunks as they arrive
for (const chunk of responseChunks) {
  response.write(`data: ${JSON.stringify({content: chunk})}\n\n`);
}
response.end();
```

**Option B: WebSocket Connection**
- More complex but bidirectional
- Requires N8N WebSocket nodes

### 2. Open-WebUI Pipe Function Changes

```python
def pipe(self, body: dict) -> Generator:
    """Stream responses from N8N webhook."""
    
    # Check if streaming is requested
    if body.get("stream", False):
        # Make streaming request
        response = requests.post(
            self.api_url,
            json=payload,
            stream=True,  # Enable streaming
            timeout=self.valves.timeout
        )
        
        # Yield chunks as they arrive
        def stream_generator():
            for line in response.iter_lines():
                if line:
                    # Parse SSE format
                    if line.startswith(b'data: '):
                        data = line[6:]  # Remove 'data: ' prefix
                        try:
                            chunk = json.loads(data)
                            yield chunk.get('content', '')
                        except:
                            continue
        
        return stream_generator()
    else:
        # Non-streaming response (current implementation)
        return complete_response
```

### 3. Ollama Streaming Support

Ollama already supports streaming via its API:

```python
# Ollama streaming request
response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "codellama",
        "prompt": enhanced_prompt,
        "stream": True
    },
    stream=True
)

# Process stream
for line in response.iter_lines():
    if line:
        chunk = json.loads(line)
        yield chunk['response']
```

### 4. Claude Streaming Support

Claude API also supports streaming:

```python
# Claude streaming with Anthropic SDK
stream = anthropic.messages.create(
    model="claude-3-opus-20240229",
    messages=messages,
    stream=True,
    max_tokens=1000
)

for chunk in stream:
    if chunk.type == "content_block_delta":
        yield chunk.delta.text
```

## Implementation Plan

1. **Phase 1: Research**
   - Test N8N's ability to handle streaming responses
   - Verify Open-WebUI properly handles generator functions
   - Check if current webhook setup supports keep-alive connections

2. **Phase 2: N8N Workflow Updates**
   - Modify Ollama workflow to support streaming
   - Update Claude workflow for streaming
   - Implement proper error handling for disconnections

3. **Phase 3: Open-WebUI Function Updates**
   - Update pipe functions to detect stream parameter
   - Implement generator functions for streaming
   - Add fallback to non-streaming mode

4. **Phase 4: Testing**
   - Test with various query lengths
   - Verify proper chunk handling
   - Ensure error recovery works

## Benefits
- Immediate feedback for users
- Better perceived performance
- Ability to stop generation mid-stream
- More engaging user experience

## Considerations
- Increased complexity
- Potential for partial responses on errors
- Need to handle connection drops gracefully
- May require nginx configuration updates for SSE