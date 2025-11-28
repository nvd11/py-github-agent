import src.configs.config
from src.configs.log_config import setup_logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import os
import sys

# Import the routers
# from src.routers import chat_router, user_router, conversation_router

# Get root_path from an environment variable. Defaults to "/python-template-app" if not set.
root_path = os.getenv("ROOT_PATH", "/py-github-agent")

# Initialize the FastAPI app
app = FastAPI(
    title="py-github-agent API",
    description="ai agent for checking github info",
    version="1.0.0",
    root_path=root_path,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include the routers
# app.include_router(chat_router.router)


@app.get("/")
def read_root():
    """A simple root endpoint to confirm the server is running."""
    # logger.debug("Root endpoint was hit.")
    return {"message": "Welcome to the demo API. See /docs for details.this version after 0.0.6"}


@app.get("/getcallinfo")
def endpoint1(request: Request):
    client_ip = getattr(request, "client", None)
    client_ip = client_ip.host if client_ip else None
    headers = dict(request.headers)
    data = {
        "endpoint": "webhook/getcallinfo",
        "client_ip": client_ip,
        "host": headers.get("host"),
        "method": request.method,
        "path": request.url.path,
        "query": request.url.query,
        "headers": headers,
    }
    logger.info(f"Request data: {data}")
    return data


if __name__ == "__main__":
    import uvicorn
    
    # Debug: Print current environment
    current_env = os.getenv("APP_ENVIRONMENT", "unknown")
    print(f"DEBUG: Server starting. APP_ENVIRONMENT={current_env}", file=sys.stderr)
    
    # Force re-setup logging just to be sure
    setup_logging(current_env)
    
    logger.info("Starting Uvicorn server...")
    # Disable Uvicorn's default logging to let Loguru take full control
    uvicorn.run(app, host="0.0.0.0", port=8000, log_config=None)
