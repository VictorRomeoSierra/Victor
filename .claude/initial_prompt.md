# Victor: AI Coding Assistant for Lua Development in DCS

## Project Overview
- Created for the Victor Romeo Sierra (VRS) discord community
- Goal: Help developers understand the large codebase inherited from XSAF
- Focus on:
  - Understanding how code works
  - Which files are loaded/executed
  - Purpose of execution

## Technical Stack
- Runs locally on Mac Mini
- Components:
  - Open-WebUI
  - LiteLLM
  - Postgres
  - Ollama
  - Docker
  - N8N
- GitHub integration for auto-updates
- Nginx reverse proxy
- VSCode integration via Roo Code or Cline

## Key Requirements
- Model: Evaluate Ollama models for Lua development
- Context methods: RAG and MCP
- Codebase location: ~/Dev/XSAF/

## Project Plan
1. Create specifications in specs directory
2. Evaluate different Ollama models
3. Design and implement the system architecture
4. Setup integration with VSCode
5. Configure GitHub webhook for auto-updates