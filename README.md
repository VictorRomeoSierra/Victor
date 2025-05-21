# Victor - AI Coding Assistant for DCS Lua Development

## Overview
Victor is an AI-powered coding assistant designed to help VRS community developers understand and work with the large Lua codebase inherited from XSAF. It provides contextual code understanding, execution flow analysis, and development assistance while running entirely locally on a Mac Mini.

## Repository Structure

```
Victor/
├── .claude/               # Claude reference files
├── ai_docs/               # AI-specific documentation
│   ├── model_selection/   # Model evaluation and selection docs
│   ├── architecture/      # AI architecture documentation
│   └── examples/          # Example prompts and responses
├── specs/                 # Project specifications
├── src/                   # Source code
│   ├── api/               # API endpoints
│   ├── docker/            # Docker configuration
│   ├── database/          # Database schemas and scripts
│   ├── embedding/         # Embedding and retrieval code
│   ├── ui/                # Web UI customization
│   ├── ide/               # IDE integration code
│   └── automation/        # N8N workflows and scripts
```

## Getting Started

### Prerequisites
- Docker and Docker Compose
- Mac Mini with macOS (recommended)
- Git

### Setup Instructions
1. Clone this repository
2. Run the setup script: `./setup.sh`
3. Follow the configuration wizard

## Technical Stack
- **Ollama**: Local LLM execution
- **PostgreSQL/pgvector**: Vector database
- **Open-WebUI**: Web interface
- **N8N**: Automation workflows
- **Docker**: Containerization
- **Nginx**: Reverse proxy

## Development

### Local Development
Instructions for local development setup will be added here.

### Testing
Testing procedures and frameworks will be documented here.

## Contributing
Guidelines for contributing to the project will be added here.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments
- VRS Discord community
- XSAF for the original codebase