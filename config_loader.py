import yaml
import os

# Load configuration from config.yaml
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config/config.yaml")

with open(CONFIG_FILE, "r") as file:
    config = yaml.safe_load(file)

# Constants
DATA_API = config["alpaca"]["data_api"]
PAPER_API = config["alpaca"]["paper_api"]
ALPACA_API_KEY = config["alpaca"]["api_key"]
ALPACA_SECRET_KEY = config["alpaca"]["secret_key"]
