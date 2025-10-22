#!/usr/bin/env python3
"""
Telegram Contact Manager Backend - Startup Script
This script properly configures the Python path and starts the FastAPI server
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
backend_dir = Path(__file__).parent
src_dir = backend_dir / "src"
sys.path.insert(0, str(src_dir))

# Now import and run the application
if __name__ == "__main__":
    import uvicorn
    from dotenv import load_dotenv

    # Load environment variables
    env_file = backend_dir / ".env"
    if env_file.exists():
        load_dotenv(env_file)

    # Get configuration from environment
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))

    print(f"Starting Telegram Contact Manager API on {host}:{port}")
    print(f"API Documentation: http://localhost:{port}/docs")
    print(f"Press CTRL+C to stop the server\n")

    # Run the application
    uvicorn.run("main:app", host=host, port=port, reload=True, log_level="info")
