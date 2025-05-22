#!/usr/bin/env python3
"""
Start the DCS Lua Analyzer API server
"""
import sys
import os

# Add the dcs-lua-analyzer directory to Python path
sys.path.insert(0, os.path.expanduser('~/Dev/dcs-lua-analyzer'))

# Import and run the API server
from api_server import app
import uvicorn

if __name__ == "__main__":
    # Get port from environment variable or use default
    port = int(os.environ.get("DCS_ANALYZER_PORT", 8001))
    
    print(f"Starting DCS Lua Analyzer API on port {port}...")
    
    # Run the application
    uvicorn.run(app, host="0.0.0.0", port=port)