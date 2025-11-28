import sys
import json
import os
import logging
from loguru import logger

class EndpointFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return record.getMessage().find("GET / HTTP/1.1") == -1

def health_check_filter(record):
    """
    Filters out uvicorn access logs for health check endpoints.
    """
    is_access_log = record["name"] == "uvicorn.access"
    if is_access_log:
        message = record["message"]
        if '"GET / HTTP/1.1"' in message or '"GET /webhook/ HTTP/1.1"' in message:
            return False
    return True

def setup_logging(app_env_variable: str = "local"):
    """
    Configures the Loguru logger based on the application environment.
    """
    # Filter uvicorn access logs
    logging.getLogger("uvicorn.access").addFilter(EndpointFilter())

    logger.remove()

    if app_env_variable != "local":
        def gcp_formatter(record):
            log_entry = {
                "severity": record["level"].name,
                "message": record["message"],
                "timestamp": record["time"].isoformat(),
                "logging.googleapis.com/sourceLocation": {
                    "file": record["file"].path,
                    "line": record["line"],
                    "function": record["function"],
                },
            }
            record["extra"]["json_message"] = json.dumps(log_entry)
            return "{extra[json_message]}\n"

        logger.add(sys.stdout, format=gcp_formatter, level="DEBUG", filter=health_check_filter)
        logger.info("Loguru configured for custom JSON output to stdout for GCP.")
    else:
        logger.add(sys.stderr, level="DEBUG", filter=health_check_filter)
        logger.info("Loguru configured for standard terminal output.")