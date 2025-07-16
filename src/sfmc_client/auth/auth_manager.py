# --- auth/auth_manager.py ---
from __future__ import annotations
from time import time
import threading
from src.sfmc_client.core.exceptions import AuthenticationError
from src.sfmc_client.core.config import Config
from src.sfmc_client.http.base_http_client import BaseHTTPClient


class AuthManager:
    def __init__(
        self, 
        config: Config,
        http_client: BaseHTTPClient, 
        is_async: bool = False
    ) -> None:
        """
        Manages OAuth authentication for Salesforce Marketing Cloud API.

        :param config: Config object with client_id, client_secret, tenant_subdomain, account_id.
        :param http_client: HTTP client to make requests (sync or async).
        :param is_async: Whether using async context (affects method behavior).
        """
        self.config = config
        self.http_client = http_client
        self.is_async = is_async

        self.access_token = None
        self.token_expiration = None
        self.http_success_codes = [200, 201, 202]
        self.auth_lock = threading.Lock()

    def get_token(self) -> str:
        """
        Retrieves token for sync clients.
        :returns: Token
        :trype: str
        :raises RuntimeError: If called in async mode
        """
        if self.is_async:
            raise RuntimeError("Use 'await get_token_async()' in async context.")
        if self.is_token_expired():
            self.authenticate()
        return self.access_token
    
    async def get_token_async(self) -> str:
        """
        Retrieves token for async clients.
        :returns: Token
        :trype: str
        :raises RuntimeError: If called in async mode
        """
        if not self.is_async:
            raise RuntimeError("Use 'get_token()' in sync context.")
        if self.is_token_expired():
            await self.authenticate_async()
        return self.access_token

    def is_token_expired(self) -> bool:
        """
        Check if the current OAuth token is missing or expired.

        :return: True if no valid token exists or token has expired, else False.
        :rtype: bool
        """
        return not self.access_token or time() >= (self.token_expiration or 0)

    def ensure_authenticated(self) -> None:
        """
        Ensure there is a valid token for sync clients.

        :raises RuntimeError: If called in async mode
        """
        if self.is_async:
            raise RuntimeError("Use 'await ensure_authenticated()' in async context.")
        if self.is_token_expired():
            self.authenticate()

    async def ensure_authenticated_async(self) -> None:
        """
        Ensure there is a valid token for async clients.

        :raises RuntimeError: If called in sync mode
        """
        if not self.is_async:
            raise RuntimeError("Use 'ensure_authenticated()' in sync context.")
        if self.is_token_expired():
            await self.authenticate_async()

    def authenticate(self):
        """
        Authenticate syncronously with Salesforce Marketing Cloud using OAuth client credentials flow.

        Obtains a Bearer token by POSTing client credentials to the authentication endpoint.
        Stores the access token and expiration time (with a 60-second buffer).

        :raises AuthenticationError: If the authentication request fails or token info is missing.
        """
        with self.auth_lock:
            if not self.is_token_expired():
                return

            url = f"https://{self.config.tenant_subdomain}.auth.marketingcloudapis.com/v2/token"
            payload = {
                "grant_type": "client_credentials",
                "client_id": self.config.client_id,
                "client_secret": self.config.client_secret,
                "account_id": self.config.account_id
            }
            response = self.http_client.auth_request("POST", url, data=payload)
            self.access_token = response.get("access_token")
            self.token_expiration = time() + response.get("expires_in") - 60  # Set expiration 60s before actual expiration
            
            if not self.access_token or not self.token_expiration:
                raise AuthenticationError("Access token or expiration missing in auth response.")

    async def authenticate_async(self):
        """
        Authenticate asyncronously with Salesforce Marketing Cloud using OAuth client credentials flow.

        Obtains a Bearer token by POSTing client credentials to the authentication endpoint.
        Stores the access token and expiration time (with a 60-second buffer).

        :raises AuthenticationError: If the authentication request fails or token info is missing.
        """
        with self.auth_lock:
            if not self.is_token_expired():
                return
            
            url = f"https://{self.config.tenant_subdomain}.auth.marketingcloudapis.com/v2/token"
            payload = {
                "grant_type": "client_credentials",
                "client_id": self.config.client_id,
                "client_secret": self.config.client_secret,
                "account_id": self.config.account_id
            }
            response = await self.http_client.rest_request("POST", url, data=payload)
            if response.status_code not in self.http_success_codes:
                raise AuthenticationError(f"Auth failed: {response.status_code} {response.text}")

            self.access_token = await response.json().get("access_token")
            self.token_expiration = await time() + response.json().get("expires_in") - 60  # Set expiration 60s before actual expiration
            
            if not self.access_token or not self.token_expiration:
                raise AuthenticationError("Access token or expiration missing in auth response.")
