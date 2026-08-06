import os
from dotenv import load_dotenv

load_dotenv()


def get_required_env(name):
    require_env = os.getenv(name)
    if require_env is None:
        raise ValueError(f"Environment variable '{name}' is required but not set.")
    return require_env