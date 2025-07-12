# --- client/async_client.py ---
from __future__ import annotations
from typing import Optional
from src.sfmc_client.client.base_client import BaseClient
from src.sfmc_client.core.config import Config
from src.sfmc_client.auth.auth_manager import AuthManager
from src.sfmc_client.http.async_http_client import AsyncHTTPClient
import xml.etree.ElementTree as ET


class AsyncClient(BaseClient):
    def __init__(
        self, 
        config: Optional[Config] = None, 
        http_client: Optional[AsyncHTTPClient] = None, 
        auth_manager: Optional[AuthManager] = None
    ) ->None:
        """
        Asynchronous API client for Salesforce Marketing Cloud.

        This client uses asynchronous transport and auth layers and provides
        high-level access to REST and SOAP API calls.

        :param config: Optional Config instance. If None, will auto-load from environment.
        :param http_client: Optional custom AsyncHTTPClient instance.
        :param auth_manager: Optional custom AuthManager instance.
        """
        self.config = config or Config()
        self.http_client = http_client or AsyncHTTPClient(self.config)
        self.auth_manager = auth_manager or AuthManager(config=self.config, http_client=self.http_client, is_async=True)
        self.http_client.set_auth_manager(self.auth_manager)

        super().__init__(self.config, self.http_client, self.auth_manager)

        self._data_extensions = None
        self._automations = None
        self._queries = None
        self._subscribers = None

    async def make_rest_request(
        self, 
        endpoint: str, 
        method: str = "GET", 
        data: Optional[dict] = None
    ) -> dict :
        """
        Make an authenticated async REST request.

        :param endpoint: REST API endpoint path.
        :param method: HTTP method (e.g., "GET", "POST").
        :param data: Optional JSON payload.
        :return: JSON response as dictionary.
        :raises RequestError: On non-2xx response.
        """
        await self.auth_manager.ensure_authenticated_async()
        return await self.http_client.rest_request(method, endpoint, data)

    async def make_soap_request(
        self,
        action: str,
        body: str
    ) -> ET:
        """
        Make an authenticated async SOAP request.

        :param action: SOAPAction string.
        :param body: Raw XML string payload.
        :return: Parsed XML Element from response.
        :raises RequestError: On SOAP failure or malformed response.
        """
        await self.auth_manager.ensure_authenticated()
        return await self.http_client.soap_request(action, body)
    
    # Object managers as lazy-loaded properties
    #
    # These properties provide access to high-level abstractions for interacting with
    # specific Salesforce Marketing Cloud objects (e.g., Data Extensions, Automations).
    #
    # They are implemented as lazy-loaded properties, meaning their corresponding manager
    # classes are only instantiated when first accessed, not during client initialization.
    #
    # This approach has several benefits:
    # - Improves performance by avoiding unnecessary imports and object creation unless needed.
    # - Reduces startup time and memory usage, especially if the client only interacts with a subset of SFMC objects.
    # - Avoids circular import issues by deferring imports to runtime within the property body.
    #
    # Accessing one of these properties (e.g., `client.data_extensions`) will dynamically load
    # and cache the associated manager for subsequent calls.

    @property
    def data_extensions(self):
        """
        Lazy-load and return the DataExtensionManager instance.

        :return: Manager for data extension operations.
        """
        if self._data_extensions is None:
            from src.sfmc_client.manager.data_extensions import DataExtensionManager
            self._data_extensions = DataExtensionManager(self)
        return self._data_extensions


    @property
    def automations(self):
        """
        Lazy-load and return the AutomationManager instance.

        :return: Manager for automation operations.
        """
        if self._automations is None:
            from src.sfmc_client.manager.automations import AutomationManager
            self._automations = AutomationManager(self)
        return self._automations


    @property
    def queries(self):
        """
        Lazy-load and return the QueryManager instance.

        :return: Manager for query operations.
        """
        if self._queries is None:
            from src.sfmc_client.manager.queries import QueryManager
            self._queries = QueryManager(self)
        return self._queries


    @property
    def subscribers(self):
        """
        Lazy-load and return the QueryManager instance.

        :return: Manager for query operations.
        """
        if self._subscribers is None:
            from src.sfmc_client.manager.subscribers import SubscriberManager
            self._subscribers = SubscriberManager(self)
        return self._subscribers
