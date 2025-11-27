import yaml
import os
import sys
from loguru import logger
from dotenv import load_dotenv
from .proxy import apply_proxy
from .log_config import setup_logging

#====================== Determine project path and set sys.path =======================
# append project path to sys.path
script_path = os.path.abspath(__file__)
project_path = os.path.dirname(os.path.dirname(os.path.dirname(script_path)))

print("project_path is {}".format(project_path))

# append project path to sys.path
sys.path.append(project_path)


#================= Load environment variables from .env file =======================
load_dotenv(override=True)

# Get the application environment, default to 'dev' if not set
app_env = os.getenv("APP_ENVIRONMENT", "dev")


# Configure logging
setup_logging(app_env)


# Debug: Print content of .env file before loading
try:
    with open(".env") as f:
        #logger.debug(f".env file content:\n{f.read()}")
        pass
except FileNotFoundError:
    logger.debug(".env file not found.")

logger.info(f"Application Environment (APP_ENVIRONMENT) is set to: '{app_env}'")



#================= Load YAML configuration based on config.yaml =======================
yaml_configs = None
# Dynamically load config file based on the environment
config_file_name = f"config_{app_env}.yaml"
config_file_path = os.path.join(project_path, "src", "configs", config_file_name)

logger.info(f"Attempting to load configuration from: {config_file_path}")

try:
    with open(config_file_path) as f:
        yaml_configs = yaml.load(f, Loader=yaml.FullLoader)
    logger.info(f"Successfully loaded configuration from {config_file_name}")
except FileNotFoundError:
    logger.error(f"Configuration file '{config_file_name}' not found. Please ensure it exists.")
    # Exit or handle the error appropriately
    sys.exit(1)

logger.info("all configs loaded")


# =================proxy settings apply here =======================
if app_env == "local" and yaml_configs and "proxy" in yaml_configs:
    proxy_settings = yaml_configs["proxy"]
    apply_proxy(
        http_proxy=proxy_settings.get("http"),
        https_proxy=proxy_settings.get("https")
    )