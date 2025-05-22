#!/bin/bash

# Setup script for LiteLLM + Victor integration environment
# This script sets up the Python environment and dependencies

set -e

echo "🚀 Setting up LiteLLM + Victor integration environment..."

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "📁 Project root: $PROJECT_ROOT"

# Check if python3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ python3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "🐍 Python version: $(python3 --version)"

# Create virtual environment if it doesn't exist
VENV_DIR="$PROJECT_ROOT/venv-litellm"
if [ ! -d "$VENV_DIR" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install LiteLLM requirements
echo "📦 Installing LiteLLM requirements..."
pip install -r requirements-litellm.txt

# Install Victor API requirements (if exists)
if [ -f "src/requirements.txt" ]; then
    echo "📦 Installing Victor API requirements..."
    pip install -r src/requirements.txt
fi

# Set up environment variables
echo "⚙️ Setting up environment variables..."
cat > "$PROJECT_ROOT/.env.litellm" << EOF
# LiteLLM + Victor Integration Environment Variables

# Victor API Configuration
VICTOR_API_URL=http://localhost:8000
VICTOR_TIMEOUT=10.0
VICTOR_RAG_ENABLED=true

# LiteLLM Configuration  
LITELLM_PORT=4000
LITELLM_HOST=0.0.0.0

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434

# Optional: Anthropic API Key for Claude integration
# ANTHROPIC_API_KEY=your_key_here

# Optional: Observability
# LANGFUSE_PUBLIC_KEY=your_key_here
# LANGFUSE_SECRET_KEY=your_key_here
# LANGFUSE_HOST=https://cloud.langfuse.com
EOF

echo "✅ Environment setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Activate the environment: source venv-litellm/bin/activate"
echo "2. Load environment variables: source .env.litellm"
echo "3. Start Victor API on the Mac Mini"
echo "4. Run the test script: python scripts/test_litellm_integration.py"
echo "5. Start LiteLLM with Victor: python scripts/start_litellm_with_victor.py"
echo ""
echo "🔧 Configuration files:"
echo "  - LiteLLM Config: config/litellm_config.yaml"
echo "  - Environment: .env.litellm"
echo "  - Python Config: config/litellm_config.py"