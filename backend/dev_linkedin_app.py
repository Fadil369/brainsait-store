"""
Standalone FastAPI app for testing the LinkedIn integration router.

Usage:
  uvicorn dev_linkedin_app:app --app-dir backend --reload --port 8000

Environment:
  Use account.env at repo root or set LINKEDIN_* vars before running.
"""

import os
import re
from pathlib import Path

from fastapi import FastAPI

from app.api.v1 import integrations_linkedin as linkedin


app = FastAPI(title="BrainSAIT LinkedIn Dev")


def _load_account_env() -> None:
    root = Path(__file__).resolve().parents[1]
    env_file = root / "account.env"
    if not env_file.exists():
        return
    data = env_file.read_text()
    env: dict[str, str] = {}
    for line in data.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        if s.startswith("export "):
            s = s[len("export "):]
        if "=" in s:
            k, v = s.split("=", 1)
            env[k.strip()] = v.strip()
    # Normalize redirect URI to first URL only
    redir = env.get("LINKEDIN_REDIRECT_URI", "")
    if redir:
        parts = [
            p.strip().strip(",")
            for p in re.split(r"[\s,]+", redir)
            if p.strip()
        ]
        if parts:
            env["LINKEDIN_REDIRECT_URI"] = parts[0]
    for k, v in env.items():
        if k.startswith("LINKEDIN_"):
            os.environ.setdefault(k, v)


_load_account_env()

app.include_router(
    linkedin.router,
    prefix="/api/v1/integrations/linkedin",
    tags=["LinkedIn"],
)


@app.get("/")
def root():
    return {
        "service": "LinkedIn Dev",
        "routes": [
            "/api/v1/integrations/linkedin/oauth/url",
            "/api/v1/integrations/linkedin/oauth/callback",
            "/api/v1/integrations/linkedin/lead-forms",
            "/api/v1/integrations/linkedin/webhooks/lead-notifications",
        ],
    }
