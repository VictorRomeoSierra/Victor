# Victor DCS Assistant for Open-WebUI

This directory contains Open-WebUI function implementations for the Victor DCS Assistant, supporting multiple Ollama models.

## Available Functions

Each function routes DCS-related queries through the N8N webhook for XSAF code enhancement before sending to the respective Ollama model:

### Premium Model
- **victor_dcs_claude.py** - Victor DCS - Claude (Uses Claude API via N8N)

### Coding-Focused Models
- **victor_dcs_codellama.py** - Victor DCS - CodeLlama (Best for DCS Lua coding)
- **victor_dcs_qwen25_coder.py** - Victor DCS - Qwen2.5 Coder
- **victor_dcs_codestral.py** - Victor DCS - Codestral
- **victor_dcs_deepseek_coder_v2.py** - Victor DCS - DeepSeek Coder v2
- **victor_dcs_codegemma.py** - Victor DCS - CodeGemma

### General Purpose Models
- **victor_dcs_llama32.py** - Victor DCS - Llama 3.2
- **victor_dcs_mistral.py** - Victor DCS - Mistral
- **victor_dcs_deepseek_r1.py** - Victor DCS - DeepSeek R1
- **victor_dcs_gemma2.py** - Victor DCS - Gemma 2

## Features

All functions include:
- Configurable timeout (default: 120 seconds)
- Debug mode for troubleshooting
- Routes through N8N webhook for intelligent query handling
- Automatic detection of DCS-related queries
- XSAF code context enhancement from 37k+ indexed code chunks

## Installation

1. In Open-WebUI, go to **Workspace** → **Functions**
2. Click **"+ Create Function"**
3. Copy and paste the content from your chosen model file
4. Click **Save**

## Usage

Once installed, each function will appear as a model option with the prefix "Victor DCS -":
- Select "Victor DCS - CodeLlama" for the best DCS Lua coding assistance
- Other models offer different strengths and response styles

## How It Works

1. **User asks a question** in Open-WebUI
2. **Function receives the message** and sends it to N8N webhook
3. **N8N workflow**:
   - Detects if query is DCS-related (keywords: dcs, lua, mission, script, trigger, xsaf, waypoint, aircraft, helicopter, miz, coalitions)
   - If DCS: Routes to Victor API to get relevant XSAF code context
   - If not DCS: Routes directly to Ollama
4. **Enhanced prompt** is sent to the selected Ollama model
5. **Response** is returned to the user with relevant code examples

## Configuration

Each function supports configuration via Valves:
- **timeout**: Request timeout in seconds (default: 120)
- **debug**: Enable debug logging (default: false)

## Troubleshooting

### Function not appearing
- Make sure you saved the function
- Refresh the Open-WebUI page
- Check for syntax errors in the function code

### Connection errors
- Verify N8N is running and accessible
- Check if the webhook URL is correct
- Ensure Victor API is running on the Mac Mini

### No DCS context in responses
- Check if the embedding database has indexed content
- Verify Victor API is connecting to the database
- Test the N8N workflow directly

### Timeout errors
- Increase the timeout value in function settings
- Try a more specific query
- Consider using a faster model

## Testing

Test with DCS-related queries:
- "How do I create waypoints in DCS?"
- "Show me how to spawn units with XSAF"
- "What's the best way to handle triggers in a mission?"

Non-DCS queries will go directly to Ollama:
- "What is 2+2?"
- "Explain Python decorators"