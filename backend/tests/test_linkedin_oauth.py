"""
Tests for LinkedIn OAuth integration.

This module contains tests for the LinkedIn OAuth functionality
including URL generation and authentication flow.
"""

from urllib.parse import urlparse, parse_qs
from pathlib import Path
import sys

from fastapi.testclient import TestClient
from fastapi import FastAPI

# Ensure 'backend' is in sys.path so 'app' package can be imported
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.api.v1.integrations_linkedin import (  # noqa: E402
    router,
    LinkedInSettings,
    get_li_settings,
)


def get_settings_override() -> LinkedInSettings:
    """Provide test settings for LinkedIn integration."""
    return LinkedInSettings(
        client_id="test_client_id",
        client_secret="test_client_secret",
        redirect_uri="https://example.com/callback",
        api_version=None,
    )


def create_app() -> FastAPI:
    """Create a test FastAPI application with LinkedIn router."""
    app = FastAPI()
    # Override the Depends(get_li_settings) provider
    app.dependency_overrides[get_li_settings] = get_settings_override
    app.include_router(router, prefix="/api/v1/integrations/linkedin")
    return app


def test_oauth_url_generation() -> None:
    """Test that OAuth URL generation works correctly with proper parameters."""
    app = create_app()
    client = TestClient(app)
    r = client.get(
        "/api/v1/integrations/linkedin/oauth/url",
        params={
            "scopes": "r_liteprofile,r_ads,r_marketing_leadgen_automation",
            "state": "abc",
        },
    )
    assert r.status_code == 200
    url = r.json()["auth_url"]
    parsed = urlparse(url)
    assert parsed.netloc == "www.linkedin.com"
    assert parsed.path.endswith("/oauth/v2/authorization")
    q = parse_qs(parsed.query)
    assert q.get("response_type") == ["code"]
    assert q.get("client_id") == ["test_client_id"]
    assert q.get("redirect_uri") == ["https://example.com/callback"]
    # Space-delimited in URL; parse_qs returns as a single value
    scope_val = (q.get("scope") or [""])[0]
    assert "r_liteprofile r_ads r_marketing_leadgen_automation" in scope_val
    assert q.get("state") == ["abc"]
