"""
Deployment environment verifier for BazaarBrain-Pro.

Reads environment variables and prints their presence with masked values.
Use: `python deploy/check_env.py` (ensure the correct .env is loaded).

Priority:
- If DOTENV_FILE is set, it will load that file.
- Else if ENVIRONMENT=production and .env.production exists, it will load that.
- Else falls back to .env.
"""
import os
from pathlib import Path
from dotenv import load_dotenv


def load_env():
    env = os.getenv("ENVIRONMENT", "development").lower()
    dotenv_file = os.getenv("DOTENV_FILE")
    if not dotenv_file:
        if env == "production" and Path(".env.production").exists():
            dotenv_file = ".env.production"
        elif Path(".env").exists():
            dotenv_file = ".env"
    if dotenv_file:
        load_dotenv(dotenv_file)
    else:
        load_dotenv()
    return env, dotenv_file


def mask(value: str, visible: int = 4) -> str:
    if not value:
        return "<missing>"
    if len(value) <= visible:
        return "*" * len(value)
    return value[:visible] + "*" * (len(value) - visible)


def main():
    env, dotenv_file = load_env()
    keys = [
        "SUPABASE_URL",
        "SUPABASE_KEY",
        "SUPABASE_ANON_KEY",
        "SUPABASE_SERVICE_ROLE_KEY",
        "OPENAI_API_KEY",
        "GOOGLE_API_KEY",
        "ENVIRONMENT",
        "LOG_LEVEL",
        "FRONTEND_ORIGIN",
        "ALLOWED_ORIGINS",
    ]
    print(f"Environment: {env}")
    print(f"Loaded dotenv file: {dotenv_file or '<auto/default>'}")
    print("\nVariables:")
    for k in keys:
        v = os.getenv(k)
        print(f"- {k}: {mask(v)}")


if __name__ == "__main__":
    main()
