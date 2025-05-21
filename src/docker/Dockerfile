FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install tree-sitter dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Try to install platform-specific packages separately
RUN pip install lua-ast==0.1.7 || echo "lua-ast could not be installed, will be handled manually if needed"
RUN pip install torch==2.1.0 || pip install --index-url https://download.pytorch.org/whl/cpu torch==2.1.0 || echo "torch could not be installed, will be handled manually if needed"
RUN pip install sentence-transformers==2.2.2 || echo "sentence-transformers could not be installed, will be handled manually if needed"

# Copy source code
COPY . /app/src

# Install the package
WORKDIR /app
RUN pip install -e src

# Run the application
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]