# --- tests/http/test_sync_http_client.py ---
import pytest
from unittest.mock import Mock, patch
from requests.models import Response
from src.sfmc_client.http.sync_http_client import SyncHTTPClient
from src.sfmc_client.core.config import Config
from src.sfmc_client.core.exceptions import RequestError


@pytest.fixture
def mock_config():
    mock = Mock(spec=Config)
    mock.tenant_subdomain = "https://example.com"
    return mock


@pytest.fixture
def mock_auth_manager():
    mock = Mock()
    mock.get_token.return_value = "abc123"
    return mock


@patch("requests.request")
def test_rest_request_success(mock_request, mock_config, mock_auth_manager):
    client = SyncHTTPClient(config=mock_config, auth_manager=mock_auth_manager)

    response = Mock(spec=Response)
    response.ok = True
    response.json.return_value = {"status": "ok"}
    mock_request.return_value = response

    result = client.rest_request("GET", "/test")
    assert result == {"status": "ok"}
    mock_auth_manager.get_token.assert_called_once()


@patch("requests.request")
def test_rest_request_failure(mock_request, mock_config, mock_auth_manager):
    client = SyncHTTPClient(config=mock_config, auth_manager=mock_auth_manager)

    response = Mock(spec=Response)
    response.ok = False
    response.status_code = 403
    response.text = "Forbidden"
    mock_request.return_value = response

    with pytest.raises(RequestError, match="REST request failed: 403 - Forbidden"):
        client.rest_request("GET", "/fail")

# TODO add soap_request tests