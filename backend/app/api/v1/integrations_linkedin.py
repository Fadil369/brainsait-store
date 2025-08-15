"""
LinkedIn Integration Endpoints

Implements OAuth flows and basic Lead Forms access using direct HTTP
requests (no third-party SDK dependency).

Notes:
- Do not hardcode secrets. Use environment variables or a secrets
    manager.
- Ensure your LinkedIn app has been approved for the required products
    and scopes.
- For Lead Sync API, you must be in the Lead Sync program and use
    r_marketing_leadgen_automation.
"""

import os
import re
import urllib.parse
from typing import Any, Dict, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

AUTH_BASE = "https://www.linkedin.com/oauth/v2/authorization"
TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
REST_BASE = "https://api.linkedin.com/rest"


def _first_redirect_uri() -> str:
    raw = os.getenv("LINKEDIN_REDIRECT_URI", "")
    if not raw:
        return ""
    # Split on comma, whitespace, or newlines, keep order
    parts = [p.strip().strip(",") for p in re.split(r"[\s,]+", raw) if p.strip()]
    return parts[0] if parts else ""


class LinkedInSettings(BaseModel):
    client_id: str = Field(default_factory=lambda: os.getenv("LINKEDIN_CLIENT_ID", ""))
    client_secret: str = Field(
        default_factory=lambda: os.getenv("LINKEDIN_CLIENT_SECRET", "")
    )
    redirect_uri: str = Field(default_factory=_first_redirect_uri)
    api_version: Optional[str] = Field(
        default_factory=lambda: os.getenv("LINKEDIN_API_VERSION", None)
    )


def get_li_settings() -> LinkedInSettings:
    settings = LinkedInSettings()
    if not settings.client_id or not settings.client_secret:
        raise HTTPException(
            status_code=500, detail="LinkedIn credentials not configured"
        )
    return settings


router = APIRouter()


@router.get("/oauth/url")
def get_oauth_url(
    scopes: str,
    state: Optional[str] = None,
    li: LinkedInSettings = Depends(get_li_settings),
):
    """Generate the member authorization URL for 3-legged OAuth.

    Query params:
        - scopes: comma-separated list of scopes (e.g.,
            r_liteprofile,r_ads,r_marketing_leadgen_automation)
    - state: optional CSRF token
    """
    if not li.redirect_uri:
        raise HTTPException(
            status_code=500, detail="LINKEDIN_REDIRECT_URI not configured"
        )

    scope_list = [s.strip() for s in scopes.split(",") if s.strip()]
    params = {
        "response_type": "code",
        "client_id": li.client_id,
        "redirect_uri": li.redirect_uri,
        "scope": " ".join(scope_list),  # LinkedIn expects space-delimited
    }
    if state:
        params["state"] = state
    url = f"{AUTH_BASE}?{urllib.parse.urlencode(params)}"
    return {"auth_url": url}


class OAuthCallback(BaseModel):
    code: str


@router.post("/oauth/callback")
def oauth_callback(
    payload: OAuthCallback, li: LinkedInSettings = Depends(get_li_settings)
):
    """Exchange authorization code for a 3-legged access token."""
    if not li.redirect_uri:
        raise HTTPException(
            status_code=500, detail="LINKEDIN_REDIRECT_URI not configured"
        )
    form = {
        "grant_type": "authorization_code",
        "code": payload.code,
        "redirect_uri": li.redirect_uri,
        "client_id": li.client_id,
        "client_secret": li.client_secret,
    }
    try:
        with httpx.Client(timeout=20.0) as client:
            r = client.post(
                TOKEN_URL,
                data=form,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                },
            )
        r.raise_for_status()
        data = r.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=e.response.text,
        )
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(e))
    return {
        "access_token": data.get("access_token"),
        "expires_in": data.get("expires_in"),
        "refresh_token": data.get("refresh_token"),
        "scope": data.get("scope"),
        "token_type": data.get("token_type", "Bearer"),
    }


class OAuthRefresh(BaseModel):
    refresh_token: str


@router.post("/oauth/refresh")
def oauth_refresh(
    payload: OAuthRefresh, li: LinkedInSettings = Depends(get_li_settings)
):
    """Exchange a refresh token for a new access token."""
    form = {
        "grant_type": "refresh_token",
        "refresh_token": payload.refresh_token,
        "client_id": li.client_id,
        "client_secret": li.client_secret,
    }
    try:
        with httpx.Client(timeout=20.0) as client:
            r = client.post(
                TOKEN_URL,
                data=form,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                },
            )
        r.raise_for_status()
        data = r.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=e.response.text,
        )
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(e))
    return {
        "access_token": data.get("access_token"),
        "expires_in": data.get("expires_in"),
        "refresh_token": data.get("refresh_token"),
        "scope": data.get("scope"),
        "token_type": data.get("token_type", "Bearer"),
    }


class LeadFormsQuery(BaseModel):
    access_token: str
    # e.g., urn:li:sponsoredAccount:123 or organization URN for organic
    account_urn: Optional[str] = None
    fields: Optional[str] = None  # comma-separated fields


@router.post("/lead-forms")
def list_lead_forms(
    query: LeadFormsQuery, li: LinkedInSettings = Depends(get_li_settings)
):
    """List Lead Forms accessible by the token.

    Requires appropriate scopes and roles as per LinkedIn docs.
    """
    q_params: Dict[str, Any] = {}
    if query.fields:
        q_params["fields"] = query.fields
    if query.account_urn:
        # Some endpoints filter by account/organization URN; this is
        # illustrative and may vary by API.
        q_params["account"] = query.account_urn

    headers = {
        "Authorization": f"Bearer {query.access_token}",
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json",
    }
    if li.api_version:
        headers["LinkedIn-Version"] = li.api_version
    url = f"{REST_BASE}/leadForms"
    try:
        with httpx.Client(timeout=20.0) as client:
            r = client.get(url, params=q_params or None, headers=headers)
        r.raise_for_status()
        data = r.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=e.response.text,
        )
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(e))
    return data


class LeadFormResponsesQuery(BaseModel):
    access_token: str
    # Provide one of these depending on your access context
    lead_gen_form_urn: Optional[str] = None  # urn:li:leadGenForm:...
    account_urn: Optional[str] = None  # urn:li:sponsoredAccount:...
    # Optional filters
    created_after: Optional[int] = None  # epoch millis
    created_before: Optional[int] = None  # epoch millis
    count: Optional[int] = None
    start: Optional[int] = None


@router.post("/lead-form-responses")
def list_lead_form_responses(
    query: LeadFormResponsesQuery,
    li: LinkedInSettings = Depends(get_li_settings),
):
    """List Lead Form Responses via LinkedIn REST API.

    Note: Exact query params may vary by API version and program. This
    endpoint covers the common pattern using q=leadGenForm and optional
    time range.
    """
    headers = {
        "Authorization": f"Bearer {query.access_token}",
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json",
    }
    if li.api_version:
        headers["LinkedIn-Version"] = li.api_version

    params: Dict[str, Any] = {}
    # Default query per docs
    if query.lead_gen_form_urn:
        params["q"] = "leadGenForm"
        params["leadGenForm"] = query.lead_gen_form_urn
    elif query.account_urn:
        params["q"] = "account"
        params["account"] = query.account_urn
    if query.created_after is not None:
        params["createdAfter"] = query.created_after
    if query.created_before is not None:
        params["createdBefore"] = query.created_before
    if query.count is not None:
        params["count"] = query.count
    if query.start is not None:
        params["start"] = query.start

    url = f"{REST_BASE}/leadFormResponses"
    try:
        with httpx.Client(timeout=30.0) as client:
            r = client.get(url, params=params or None, headers=headers)
        r.raise_for_status()
        data = r.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=e.response.text,
        )
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(e))
    return data


@router.post("/webhooks/lead-notifications")
async def lead_notifications_webhook(request: Request):
    """Receiver for LinkedIn leadNotifications webhook (proxied by
    Cloudflare Worker).

    LinkedIn delivers events to the configured webhook URL. Cloudflare
    Worker should validate signature and forward JSON to this endpoint.
    Here we accept payload and return 200.
    """
    try:
        payload = await request.json()
    except Exception:
        payload = None
    return {"ok": True, "received": payload is not None}
