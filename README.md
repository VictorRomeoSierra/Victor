# Victor - AI Coding Assistant for DCS Lua Development

## Overview
Victor is an AI-powered coding assistant designed to help VRS community developers understand and work with the large Lua codebase inherited from XSAF. It provides contextual code understanding, execution flow analysis, and development assistance while running entirely locally on a Mac Mini.

## Repository Structure

```
Victor/
├── config/               # Configuration files
│   └── .env.example      # Example environment variables
├── docs/                 # Documentation
│   ├── nginx-config.md   # Nginx configuration guide
│   └── troubleshooting.md # Troubleshooting guide
├── scripts/              # Deployment and utility scripts
│   ├── deploy.sh         # Deployment script
│   └── run.sh            # Service management script
├── specs/                # Project specifications
├── src/                  # Source code
│   ├── api/              # API endpoints
│   ├── database/         # Database schemas and scripts
│   ├── docker/           # Docker configuration
│   ├── embedding/        # Embedding and retrieval code
│   ├── requirements.txt  # Python dependencies
│   └── setup.py          # Package setup
└── .env                  # Environment variables (created from .env.example)
```

## Getting Started

### Prerequisites
- Docker and Docker Compose
- Mac Mini with macOS (recommended)
- Git

### Setup Instructions
1. Clone this repository:
   ```bash
   git clone git@github.com:VictorRomeoSierra/Victor.git
   cd Victor
   ```

2. Run the deployment script:
   ```bash
   ./scripts/deploy.sh
   ```

3. The script will:
   - Create a .env file from config/.env.example if none exists
   - Build and start the necessary Docker containers
   - Show service status

## Service Management

Use the run.sh script to manage services:

```bash
# Start all services
./scripts/run.sh up

# Stop all services
./scripts/run.sh down

# View logs
./scripts/run.sh logs

# Check service status
./scripts/run.sh status
```

## Technical Stack
- **Ollama**: Local LLM execution
- **PostgreSQL/pgvector**: Vector database
- **Open-WebUI**: Web interface
- **N8N**: Automation workflows
- **Docker**: Containerization
- **FastAPI**: API framework

## Development

See [docs/](docs/) for more detailed documentation, including:
- Nginx configuration
- Troubleshooting
- Environment setup

## Project Specifications

See [specs/](specs/) for detailed specifications, including:
- Architecture design
- Implementation plans
- Integration details

## Contributing
Guidelines for contributing to the project will be added soon.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments
- VRS Discord community
- XSAF for the original codebase