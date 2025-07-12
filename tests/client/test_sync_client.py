# --- tests/client/test_sync_client.py ---
import pytest
from unittest.mock import Mock
from src.sfmc_client.client.sync_client import SyncClient


@pytest.fixture
def mock_auth():
    auth = Mock()
    auth.ensure_authenticated.return_value = None
    return auth


@pytest.fixture
def mock_http():
    return Mock()


@pytest.fixture
def client(mock_auth, mock_http):
    return SyncClient(config=Mock(), http_client=mock_http, auth_manager=mock_auth)


def test_rest_request_calls_http(client, mock_http):
    mock_http.rest_request.return_value = {"ok": True}
    result = client.make_rest_request("endpoint", method="POST", data={"test": 123})
    assert result == {"ok": True}
    mock_http.rest_request.assert_called_once_with("POST", "endpoint", {"test": 123})


def test_soap_request_calls_http(client, mock_http):
    mock_http.soap_request.return_value = "<xml></xml>"
    result = client.make_soap_request("SomeAction", "<Body/>")
    assert result == "<xml></xml>"
    mock_http.soap_request.assert_called_once_with("SomeAction", "<Body/>")