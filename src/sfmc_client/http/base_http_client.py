# --- http/base_http_client.py ---
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Optional


class BaseHTTPClient(ABC):
    """
    Abstract base class for HTTP client implementations (sync and async).
    Defines the interface for REST and SOAP request methods.
    """

    def __init__(self, base_url: str, auth_token_getter: Optional[callable] = None):
        """
        :param base_url: Base URL for REST or SOAP endpoints (e.g., "https://YOUR_SUBDOMAIN.rest.marketingcloudapis.com")
        :param auth_token_getter: Callable to retrieve the latest access token
        """
        self.base_url = base_url.rstrip("/")
        self.get_auth_token = auth_token_getter

    @abstractmethod
    def rest_request(self, method: str, endpoint: str, data: Optional[dict] = None) -> Any:
        """
        Perform a REST request.

        :param method: HTTP method (GET, POST, etc.)
        :param endpoint: Path after base_url (e.g., "/data/v1/customobject")
        :param data: Request body for POST/PUT
        :return: Response payload (usually JSON-decoded dict)
        """
        raise NotImplementedError

    @abstractmethod
    def soap_request(self, action: str, body: str) -> Any:
        """
        Perform a SOAP request.

        :param action: SOAPAction header
        :param body: Full SOAP XML body
        :return: Parsed XML response (ElementTree or similar)
        """
        raise NotImplementedError
