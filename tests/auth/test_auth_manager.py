# --- tests/auth/test_auth_manager.py ---
import pytest
from unittest.mock import Mock
from src.sfmc_client.auth.auth_manager import AuthManager
from src.sfmc_client.core.exceptions import AuthenticationError


def test_auth_success():
    mock_config = Mock(client_id="abc", client_secret="xyz", tenant_subdomain="test", account_id="acct")

    mock_http = Mock()
    mock_http.auth_request.return_value = {
        "access_token": "token123",
        "expires_in": 3600
    }

    auth = AuthManager(mock_config, mock_http)
    auth.authenticate()

    assert auth.access_token == "token123"
    assert auth.token_expiration is not None


def test_auth_failure():
    mock_config = Mock(client_id="abc", client_secret="xyz", tenant_subdomain="test", account_id="acct")
    
    mock_http = Mock()
    mock_http.auth_request.side_effect = AuthenticationError("Auth failed: 401 - Unauthorized")

    auth = AuthManager(mock_config, mock_http)
    with pytest.raises(AuthenticationError, match="Auth failed: 401"):
        auth.authenticate()
