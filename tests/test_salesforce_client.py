from unittest.mock import MagicMock, patch

import pytest

from src.crm import salesforce_client


@pytest.fixture(autouse=True)
def _reset_token_cache():
    salesforce_client._access_token = None
    salesforce_client._instance_url = None
    yield
    salesforce_client._access_token = None
    salesforce_client._instance_url = None


def _response(status_code: int = 200, json_data: dict | None = None) -> MagicMock:
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = json_data or {}
    return response


AUTH_RESPONSE = _response(
    json_data={"access_token": "token123", "instance_url": "https://example.my.salesforce.com"}
)


@patch("src.crm.salesforce_client.httpx.request")
@patch("src.crm.salesforce_client.httpx.post", return_value=AUTH_RESPONSE)
def test_create_lead_authenticates_then_posts(mock_post, mock_request):
    mock_request.return_value = _response(json_data={"id": "00Q123"})

    record_id = salesforce_client.create_lead({"LastName": "Doe", "Company": "Acme"})

    assert record_id == "00Q123"
    mock_post.assert_called_once()
    called_url = mock_request.call_args.args[1]
    assert called_url == "https://example.my.salesforce.com/services/data/v59.0/sobjects/Lead"


@patch("src.crm.salesforce_client.httpx.request")
@patch("src.crm.salesforce_client.httpx.post", return_value=AUTH_RESPONSE)
def test_create_case_reuses_cached_token(mock_post, mock_request):
    mock_request.return_value = _response(json_data={"id": "500123"})

    salesforce_client.create_case({"Subject": "complaint", "Description": "issue"})
    salesforce_client.create_case({"Subject": "another", "Description": "issue2"})

    assert mock_post.call_count == 1
    assert mock_request.call_count == 2


@patch("src.crm.salesforce_client.httpx.request")
@patch("src.crm.salesforce_client.httpx.post", return_value=AUTH_RESPONSE)
def test_reauthenticates_on_401(mock_post, mock_request):
    mock_request.side_effect = [
        _response(status_code=401),
        _response(json_data={"id": "00Q999"}),
    ]

    record_id = salesforce_client.create_lead({"LastName": "Smith"})

    assert record_id == "00Q999"
    assert mock_post.call_count == 2
    assert mock_request.call_count == 2
