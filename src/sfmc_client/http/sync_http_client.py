# --- http/sync_http_client.py ---
from __future__ import annotations
import requests
import xml.etree.ElementTree as ET
from typing import Optional, Dict, Any
from src.sfmc_client.http.base_http_client import BaseHTTPClient
from src.sfmc_client.core.exceptions import RequestError

from src.sfmc_client.core.config import Config
from src.sfmc_client.auth.auth_manager import AuthManager


class SyncHTTPClient(BaseHTTPClient):
    """
    Ssynchronous HTTP client for Salesforce Marketing Cloud APIs.

    Uses requests to make REST, SOAP, and auth requests.
    Intended to be used with a sync client and sync auth manager.
    """
    def __init__(
        self, 
        config: Config,
        auth_manager: Optional[AuthManager] = None
    ):
        """
        Initialize SyncHTTPClient.

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

    def auth_request(
        self, 
        method: str, 
        url: str, 
        data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make a sync request to the SFMC auth endpoint.

        :param method: HTTP method (typically "POST").
        :param url: Full URL to auth endpoint.
        :param data: JSON payload to send.
        :return: Parsed JSON response from the server.
        :raises RequestError: On non-2xx response.
        """
        response = requests.request(method, url, json=data)
        if not response.ok:
            raise RequestError(f"Auth request failed: {response.status_code} - {response.text}")

        return response.json()

    def rest_request(
        self, 
        method: str, 
        endpoint: str,
        data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make an sync REST API request to SFMC.

        :param method: HTTP method (e.g., "GET", "POST").
        :param endpoint: API path after domain root (e.g., "/data/v1/customobject").
        :param data: Request body for POST/PUT methods.
        :return: Parsed JSON response.
        :raises RequestError: On non-2xx response.
        """
        url = f"{self.config.tenant_subdomain}/{endpoint.lstrip('/')}"
        headers = {
            "Authorization": f"Bearer {self.auth_manager.get_token()}",
            "Content-Type": "application/json"
        }

        response = requests.request(method, url, json=data, headers=headers)
        if not response.ok:
            raise RequestError(f"REST request failed: {response.status_code} - {response.text}")

        return response.json()

    def soap_request(
        self, 
        action: str, 
        body: str
    ) -> ET.Element:
        """
        Make a sync SOAP API request to SFMC.

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
            f'      <fueloauth>{self.auth_manager.get_token()}</fueloauth>',
            '   </s:Header>',
            '   <s:Body xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            'xmlns:xsd="http://www.w3.org/2001/XMLSchema">',
            f'      {body}',
            '   </s:Body>',
            '</s:Envelope>'
        ])

        response = requests.post(url, headers=headers, data=envelope)

        if not response.ok:
            raise RequestError(f"SOAP request failed: {response.status_code} - {response.text}")

        try:
            return ET.fromstring(response.content)
        except ET.ParseError as e:
            raise RequestError(f"SOAP response parsing failed: {e}") from e
