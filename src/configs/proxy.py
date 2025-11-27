import os
from loguru import logger

def apply_proxy(http_proxy=None, https_proxy=None):
    """
    Applies proxy settings to environment variables only if APP_ENVIRONMENT
    is 'LOCAL' or not set.
    """
    app_env = os.getenv("APP_ENVIRONMENT", "LOCAL").upper()

    if app_env == "LOCAL":
        if http_proxy:
            os.environ["HTTP_PROXY"] = http_proxy
            logger.info(f"HTTP_PROXY set to: {http_proxy} for LOCAL environment.")
        
        if https_proxy:
            os.environ["HTTPS_PROXY"] = https_proxy
            logger.info(f"HTTPS_PROXY set to: {https_proxy} for LOCAL environment.")
        
        if not http_proxy and not https_proxy:
            logger.info("No proxy settings provided, but in LOCAL environment.")
    else:
        logger.info(f"APP_ENVIRONMENT is '{app_env}', skipping proxy setup.")
