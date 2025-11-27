import sys
import json
import os
from loguru import logger

def setup_logging(app_env_variable: str = "local"):
    """
    Configures the Loguru logger based on the application environment.
    """
    logger.remove()


    if app_env_variable != "local":
        # For GCP, use a custom formatter to produce structured JSON logs
        # that are compatible with Google Cloud Logging.
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
            # The sink's format must only contain {message} to output the raw JSON string
            record["extra"]["json_message"] = json.dumps(log_entry)
            return "{extra[json_message]}\n"

        logger.add(sys.stdout, format=gcp_formatter, level="DEBUG")
        logger.info("Loguru configured for custom JSON output to stdout for GCP.")
    else:
        # For local development, use standard colorized logging to stderr.
        logger.add(sys.stderr, level="DEBUG")
        logger.info("Loguru configured for standard terminal output.")
