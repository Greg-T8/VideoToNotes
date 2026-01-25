import os
from pathlib import Path

def load_token() -> str:
    """Load token from environment or .env file."""
    
    # 1. Check environment variable first
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        return token
    
    # 2. Try .env file in current directory
    env_file = Path(".env")
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if line.startswith("GITHUB_TOKEN="):
                return line.split("=", 1)[1].strip().strip('"\'')
    
    # 3. Try ~/.config/gh-models/.env
    config_file = Path.home() / ".config" / "gh-models" / ".env"
    if config_file.exists():
        for line in config_file.read_text().splitlines():
            if line.startswith("GITHUB_TOKEN="):
                return line.split("=", 1)[1].strip().strip('"\'')
    
    raise ValueError(
        "GITHUB_TOKEN not found.\n"
        "Options:\n"
        "  1. export GITHUB_TOKEN='ghp_xxx'\n"
        "  2. Create .env file with: GITHUB_TOKEN=ghp_xxx\n"
        "  3. Create ~/.config/gh-models/.env"
    )