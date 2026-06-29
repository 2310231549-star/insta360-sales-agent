"""Configuration — edit LLM endpoint / model here."""

# LLM (OpenAI-compatible API — defaults to Agnes AI proxy)
LLM_BASE_URL = "http://localhost:8899/v1"
LLM_API_KEY = "sk-yz9OvG7uJR747nZP94ch4Z3gO3kTvBQPona3wOJxFZRUEeZz"
LLM_MODEL = "agnes-2.0-flash"
LLM_MAX_TOKENS = 1200

# Data files
DATA_DIR = "data"
AMAZON_FILE = f"{DATA_DIR}/amazon_sales.csv"
SHOPIFY_FILE = f"{DATA_DIR}/shopify_sales.csv"
