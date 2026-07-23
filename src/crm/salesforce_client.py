"""
Salesforce CRM client.

Authenticates via the OAuth2 username-password flow and pushes records to
Salesforce: Lead for inquiries/leads/compliments, Case for complaints (kept
separate so complaints never pass through the LLM before reaching a human).
"""
from __future__ import annotations

from typing import Any

import httpx

from src.config import settings
from src.logging.trace import get_logger

logger = get_logger("crm.salesforce")

_access_token: str | None = None
_instance_url: str | None = None


def _authenticate() -> None:
    global _access_token, _instance_url

    response = httpx.post(
        f"{settings.salesforce_login_url}/services/oauth2/token",
        data={
            "grant_type": "password",
            "client_id": settings.salesforce_client_id,
            "client_secret": settings.salesforce_client_secret,
            "username": settings.salesforce_username,
            "password": f"{settings.salesforce_password}{settings.salesforce_security_token}",
        },
        timeout=settings.crm_webhook_timeout_seconds,
    )
    response.raise_for_status()
    body = response.json()
    _access_token = body["access_token"]
    _instance_url = body["instance_url"]
    logger.info("authenticated with salesforce")


def _request(method: str, path: str, json: dict[str, Any]) -> httpx.Response:
    if _access_token is None or _instance_url is None:
        _authenticate()

    def _send() -> httpx.Response:
        return httpx.request(
            method,
            f"{_instance_url}{path}",
            json=json,
            headers={"Authorization": f"Bearer {_access_token}"},
            timeout=settings.crm_webhook_timeout_seconds,
        )

    response = _send()
    if response.status_code == 401:
        _authenticate()
        response = _send()

    response.raise_for_status()
    return response


def create_lead(payload: dict[str, Any]) -> str:
    """Push a lead/inquiry/compliment to Salesforce as a Lead record. Returns the new record ID."""
    path = f"/services/data/{settings.salesforce_api_version}/sobjects/Lead"
    record_id: str = _request("POST", path, payload).json()["id"]
    logger.info("lead created in salesforce")
    return record_id


def create_case(payload: dict[str, Any]) -> str:
    """Push a complaint to Salesforce as a Case record. Returns the new record ID."""
    path = f"/services/data/{settings.salesforce_api_version}/sobjects/Case"
    record_id: str = _request("POST", path, payload).json()["id"]
    logger.info("case created in salesforce")
    return record_id
