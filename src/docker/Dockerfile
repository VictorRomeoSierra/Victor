FROM python:3.11-slim

# Build arguments
ARG INSTALL_ML_PACKAGES=true

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

# Install essential ML packages one by one to better control dependencies
RUN if [ "$INSTALL_ML_PACKAGES" = "true" ] ; then \
    pip install numpy==1.26.1 && \
    pip install asyncpg==0.28.0 && \
    # Try to install torch with fallback to CPU-only version
    (pip install torch==2.1.0 || pip install --index-url https://download.pytorch.org/whl/cpu torch==2.1.0 || echo "torch could not be installed") && \
    # Install remaining ML packages with careful error handling
    (pip install tokenizers==0.14.1 || echo "tokenizers could not be installed") && \
    (pip install transformers==4.35.0 || echo "transformers could not be installed") && \
    (pip install sentence-transformers==2.2.2 || echo "sentence-transformers could not be installed") && \
    # These have more complex dependency trees, so install them last
    (pip install langchain==0.0.325 || echo "langchain could not be installed") && \
    (pip install llama-index==0.9.3 || echo "llama-index could not be installed") && \
    # Try to install lua-ast (likely to fail on some platforms)
    (pip install lua-ast==0.1.7 || echo "lua-ast could not be installed") \
    ; fi

# Copy source code
COPY . /app/src

# Install the package
WORKDIR /app
RUN pip install -e src

# Run the application
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]