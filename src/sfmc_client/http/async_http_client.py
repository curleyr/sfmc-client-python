# --- http/async_http_client.py ---
from __future__ import annotations
import aiohttp
import xml.etree.ElementTree as ET
from typing import Optional, Dict, Any
from src.sfmc_client.http.base_http_client import BaseHTTPClient
from src.sfmc_client.core.exceptions import RequestError

from src.sfmc_client.core.config import Config
from src.sfmc_client.auth.auth_manager import AuthManager


class AsyncHTTPClient(BaseHTTPClient):
    """
    Asynchronous HTTP client for Salesforce Marketing Cloud APIs.

    Uses `aiohttp` to make non-blocking REST, SOAP, and auth requests.
    Intended to be used with an async client and async auth manager.
    """
    def __init__(
        self,
        config: Config,
        auth_manager: Optional[AuthManager] = None
    ) -> None:
        """
        Initialize AsyncHTTPClient.

        :param config: Config instance with API credentials and base domain info.
        :param auth_manager: Optional AuthManager instance. If not set, use `set_auth_manager()` later.
        """
        self.config = config
        self.auth_manager = auth_manager
    
    def set_auth_manager(self, auth_manager: AuthManager) -> None:
        """
        Inject or override the auth manager instance.

        :param auth_manager: AuthManager that provides access tokens.
        """
        self.auth_manager = auth_manager

    async def auth_request(
        self, 
        method: str, 
        url: str, 
        data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make an async request to the SFMC auth endpoint.

        :param method: HTTP method (typically "POST").
        :param url: Full URL to auth endpoint.
        :param data: JSON payload to send.
        :return: Parsed JSON response from the server.
        :raises RequestError: On non-2xx response.
        """
        url = f"https://{self.config.tenant_subdomain}.auth.marketingcloudapis.com"
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, json=data) as response:
                if response.status < 200 or response.status >= 300:
                    text = await response.text()
                    raise RequestError(f"Auth request failed: {response.status_code} - {response.text}")
                return await response.json()

    async def rest_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make an async REST API request to SFMC.

        :param method: HTTP method (e.g., "GET", "POST").
        :param endpoint: API path after domain root (e.g., "/data/v1/customobject").
        :param data: Request body for POST/PUT methods.
        :return: Parsed JSON response.
        :raises RequestError: On non-2xx response.
        """
        url = f"{self.config.tenant_subdomain}/{endpoint.lstrip('/')}"
        headers = {
            "Authorization": f"Bearer {await self.auth_manager.get_token_async()}",
            "Content-Type": "application/json"
        }

        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, json=data, headers=headers) as response:
                if response.status < 200 or response.status >= 300:
                    text = await response.text()
                    raise RequestError(f"REST request failed: {response.status} - {text}")
                return await response.json()

    async def soap_request(
        self,
        action: str,
        body: str
    ) -> ET.Element:
        """
        Make an async SOAP API request to SFMC.

        :param action: SOAPAction header string.
        :param body: XML request body.
        :return: Parsed ElementTree XML response.
        :raises RequestError: On non-2xx response or XML parsing failure.
        """
        url = f"{self.config.tenant_subdomain}"
        headers = {
            "Content-Type": "text/xml",
            "SOAPAction": action
        }

        envelope = "\n".join([
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope" '
            'xmlns:a="http://schemas.xmlsoap.org/ws/2004/08/addressing" '
            'xmlns:u="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd">',
            '   <s:Header>',
            f'      <fueloauth>{await self.auth_manager.get_token_async()}</fueloauth>',
            '   </s:Header>',
            '   <s:Body xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            'xmlns:xsd="http://www.w3.org/2001/XMLSchema">',
            f'      {body}',
            '   </s:Body>',
            '</s:Envelope>'
        ])

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=envelope) as response:
                if response.status < 200 or response.status >= 300:
                    text = await response.text()
                    raise RequestError(f"SOAP request failed: {response.status} - {text}")
                try:
                    return ET.fromstring(await response.text())
                except ET.ParseError as e:
                    raise RequestError(f"SOAP response parsing failed: {e}") from e
