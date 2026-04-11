import os
from dotenv import load_dotenv

load_dotenv()

def _require(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise EnvironmentError(f"Missing required environment variable: {key}")
    return value

# Required
CAPTURE_TOKEN = _require("CAPTURE_TOKEN")
CAPTURE_WALLET = _require("CAPTURE_WALLET")

# Optional — agent identity (may be empty on first run)
AGENT_NID = os.getenv("AGENT_NID", "").strip()

# API Endpoints
PYRO_API_URL = os.getenv(
    "PYRO_API_URL",
    "https://us-central1-pyroimage-x402.cloudfunctions.net/fetchPyroAssets"
)
PYRO_ORG_ID = os.getenv("PYRO_ORG_ID", "f3bdb752-cd59-43f3-ace9-ec7b021fa772")
DIA_BACKEND_URL = os.getenv(
    "DIA_BACKEND_URL",
    "https://dia-backend.numbersprotocol.io/api/v3"
)
COMMIT_API_URL = os.getenv(
    "COMMIT_API_URL",
    "https://us-central1-numbers-protocol-api.cloudfunctions.net/nit-commit-to-jade"
)
REGISTRATION_API_URL = os.getenv(
    "REGISTRATION_API_URL",
    "https://api.numbersprotocol.io/api/v3/assets/"
)

# Agent Config
AGENT_NAME = os.getenv("AGENT_NAME", "Numbers Audit Agent")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Fixed Numbers Protocol action Nid for commits
ACTION_COMMIT_NID = "bafkreicptxn6f752c4pvb6gqwro7s7wb336idkzr6wmolkifj3aafhvwii"