# Victor Project Summary

## Project Overview
Victor is an AI-powered coding assistant designed specifically for the VRS community to understand and work with the large Lua codebase inherited from XSAF. The system provides contextual code understanding, execution flow analysis, and development assistance while running entirely locally on a Mac Mini.

## Core Objectives
1. **Code Understanding**: Help developers quickly grasp how different parts of the codebase work
2. **Execution Flow**: Identify which files are being loaded and executed
3. **Purpose Clarification**: Explain why specific code is being run
4. **Local Operation**: Run entirely on local hardware without cloud dependencies

## Technical Architecture

### Current Infrastructure
- **Mac Mini** hosting most components
- **Ollama** for local model execution (already installed, listening on port 11434)
- **PostgreSQL** with pgvector for vector storage (already running in Docker, port 5433)
- **LiteLLM** for model management (already running in Docker, port 4000)
- **Open-WebUI** for user interface (already running in Docker, port 3000)
- **Nginx** reverse proxy on a separate machine (already configured)

### Components to Develop
1. **RAG Middleware Service**: 
   - Intercepts and enhances LiteLLM requests with code context
   - Manages retrieval from vector database
   - Formats code examples and explanations

2. **Vector Database Implementation**:
   - Database schema for code storage
   - Embedding generation and storage
   - Efficient retrieval mechanisms

3. **Code Processing Pipeline**:
   - Lua code parser for semantic understanding
   - Code chunking for efficient storage
   - Metadata extraction for enhanced context

4. **UI Enhancements**:
   - Code-specific display components
   - File browser and visualization tools
   - Specialized chat templates

5. **Integration Components**:
   - GitHub webhook handler for automatic updates
   - VSCode integration through Roo Code or Cline
   - Automation workflows for maintenance

## Implementation Approach
The implementation follows a phased approach, focusing first on core functionality and progressively adding enhanced features:

### Phase 0: Planning and Analysis
- Project specifications and requirements
- Analysis of XSAF codebase
- Test dataset creation

### Phase 1: Model Selection and Database Setup
- Evaluate and select Ollama models for Lua
- Implement vector database schema
- Create database migration toolkit

### Phase 2: Embedding Service
- Develop Lua parser and chunking strategy
- Build embedding generation service
- Implement retrieval system

### Phase 3-4: Integration
- Configure LiteLLM for RAG workflow
- Enhance Open-WebUI for code interactions
- Develop VSCode extension

### Phase 5-8: Refinement and Deployment
- Testing and optimization
- Documentation and training
- Final deployment and launch

## Unique Selling Points
1. **Domain-Specific Understanding**: Tailored for DCS Lua codebase
2. **Local Execution**: No reliance on cloud infrastructure
3. **Multi-Interface Access**: Web UI and IDE integration
4. **Contextual Awareness**: Understanding of code relationships
5. **Execution Tracing**: Ability to follow function calls and data flow

## Success Criteria
1. Developers can quickly understand unfamiliar parts of the codebase
2. Reduction in time spent tracing execution flow manually
3. Accurate responses about code purpose and functionality
4. System runs with acceptable performance on Mac Mini hardware
5. Seamless integration with existing development workflow

## Target Timeline
- **Planning Phase**: 2 weeks
- **Core Development**: 12 weeks
- **Integration and Enhancement**: 5 weeks
- **Testing and Deployment**: 3 weeks
- **Total Project Duration**: Approximately 22 weeks

## Key Technical Decisions

### Model Selection Strategy
- Start with CodeLlama variants optimized for Lua
- Evaluate based on code understanding, accuracy, and performance
- Configure LiteLLM to route queries between Claude and local models

### Retrieval Approach
- Semantic chunking based on code structures
- Hybrid vector and keyword search
- Context enhancement with dependency information

### User Experience Philosophy
- Focus on developer workflow integration
- Minimize context switching between tools
- Provide both high-level understanding and detailed explanations

## Resource Requirements
- Computing: Mac Mini with GPU acceleration
- Storage: Approximately 50GB for models and database
- Network: Standard connectivity for GitHub integration
- Development: 1-2 developers for core implementation

## Next Steps
1. Detailed analysis of XSAF codebase structure
2. Model evaluation and selection
3. Database schema implementation
4. RAG middleware prototype development