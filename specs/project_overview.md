# Victor - AI Coding Assistant for DCS Lua Development

## Overview
Victor is an AI-powered coding assistant designed to help VRS community developers understand and work with the large Lua codebase inherited from XSAF. It provides contextual code understanding, execution flow analysis, and development assistance while running entirely locally on a Mac Mini.

## Core Objectives
1. **Code Understanding**: Help developers quickly grasp how different parts of the codebase work
2. **Execution Flow**: Identify which files are being loaded and executed
3. **Purpose Clarification**: Explain why specific code is being run
4. **Local Operation**: Run entirely on local hardware without cloud dependencies

## Technical Requirements

### Infrastructure
- **Hardware**: Mac Mini
- **Containerization**: Docker for component isolation
- **Database**: PostgreSQL for vector storage and metadata
- **Automation**: N8N for workflow automation

### AI Components
- **LLM Runtime**: Ollama for local model execution
- **Models**: To be evaluated based on Lua understanding capabilities
- **Context Methods**: 
  - Retrieval-Augmented Generation (RAG)
  - Multi-Context Programming (MCP)

### User Interface
- **Web Interface**: Open-WebUI for browser-based interaction
- **IDE Integration**: 
  - VSCode extension compatibility
  - Support for Roo Code or Cline
- **Network**: Nginx reverse proxy for secure internet exposure

### Integrations
- **Version Control**: Automatic updates when changes are pushed to private GitHub repo
- **Contextual Awareness**: Automatic updating of vector database when codebase changes

## Success Criteria
1. Developers can quickly understand unfamiliar parts of the codebase
2. Reduction in time spent tracing execution flow manually
3. Accurate responses about code purpose and functionality
4. System runs with acceptable performance on Mac Mini hardware
5. Seamless integration with existing development workflow

## Future Considerations
- Expansion to additional DCS modules
- Support for collaborative coding sessions
- Integration with CI/CD workflows
- Performance optimizations for larger codebases