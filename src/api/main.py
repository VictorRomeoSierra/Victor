from fastapi import FastAPI, Body, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import os

app = FastAPI(title="Victor API", description="API for Victor DCS Lua coding assistant")

class EnhancePromptRequest(BaseModel):
    prompt: str
    model: Optional[str] = "codellama"

class EnhancePromptResponse(BaseModel):
    enhanced_prompt: str

@app.get("/")
async def root():
    return {"message": "Welcome to Victor API", "status": "operational"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/enhance_prompt", response_model=EnhancePromptResponse)
async def enhance_prompt(request: EnhancePromptRequest):
    """
    Enhance a prompt with context for LiteLLM.
    """
    query = request.prompt
    model = request.model
    
    # TODO: Implement actual context retrieval
    # This is a placeholder implementation
    
    # Check if query is DCS-related
    if is_dcs_related(query):
        # Get relevant code snippets (placeholder)
        snippets = [{"content": "-- Example DCS code snippet", "path": "example.lua"}]
        
        # Format context based on model
        context = format_context_for_model(snippets, model)
        
        # Enhance the prompt
        enhanced_prompt = f"""You are an expert in DCS World Lua programming.
        Use the following code snippets to help answer the question.
        
        {context}
        
        Question: {query}
        """
        
        return {"enhanced_prompt": enhanced_prompt}
    
    # Return original prompt if not DCS-related
    return {"enhanced_prompt": query}

def is_dcs_related(query: str) -> bool:
    """
    Check if a query is related to DCS World.
    """
    dcs_keywords = ["dcs", "lua", "mission", "script", "trigger", "event", "xsaf"]
    return any(keyword in query.lower() for keyword in dcs_keywords)

def format_context_for_model(snippets: List[Dict[str, Any]], model: str) -> str:
    """
    Format code snippets as context based on the model.
    """
    formatted_snippets = []
    
    for snippet in snippets:
        formatted_snippets.append(f"File: {snippet['path']}\n```lua\n{snippet['content']}\n```\n")
    
    return "\n".join(formatted_snippets)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)