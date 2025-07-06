# --- sfmc_api_client.py ---
import requests
from time import time
import os
import json
import threading
import xml.etree.ElementTree as ET
from typing import Optional, Dict, Any, Callable, MutableMapping
from exceptions import AuthenticationError, RequestError

from dotenv import load_dotenv
load_dotenv()


class SFMCAPIClient:
    def __init__(
        self,
        account_name: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        account_id: Optional[str] = None,
        tenant_subdomain: Optional[str] = None,
        http_client: Optional[Callable[..., Any]] = None,
        environment: Optional[MutableMapping[str, str]] = None,
        http_success_codes: Optional[list[int]] = None
    ):
        """
        Initialize the Salesforce Marketing Cloud API client.

        Loads credentials and endpoint URLs from environment variables if not provided.
        Initializes authentication token storage and thread lock for token refresh.

        :param account_name: Logical account name used to select account ID. If None, defaults to the first key in the `SFMC_ACCOUNT_IDS` env var JSON.
        :param client_id: OAuth client ID. Defaults to environment variable `SFMC_CLIENT_ID`.
        :param client_secret: OAuth client secret. Defaults to environment variable `SFMC_CLIENT_SECRET`.
        :param account_id: Specific account ID (MID). Overrides `account_name`.
        :param tenant_subdomain: Assigned tenant specific subdomain. Used in API endpoint URLs. Defaults to env `SFMC_TENANT_SUBDOMAIN`.
        :param http_client: HTTP client function, defaults to `requests.request`.
        :param http_success_codes: HTTP status codes considered successful. Defaults to [200, 201, 202].

        :raises ValueError: If account_name is invalid or missing in environment configuration.
        """

        environment = environment or os.environ

        self.client_id = client_id or environment.get("SFMC_CLIENT_ID")
        """ :type : str """
        self.client_secret = client_secret or environment.get("SFMC_CLIENT_SECRET")
        """ :type : str """

        account_ids = json.loads(environment.get("SFMC_ACCOUNT_IDS", "{}"))
        if not account_name:
            # Default to first key if available
            account_name = next(iter(account_ids), None)
        self.account_id = account_id or account_ids.get(account_name)
        """ :type : str """
        
        self.tenant_subdomain = tenant_subdomain or environment.get("SFMC_TENANT_SUBDOMAIN")
        """ :type : str """
        self.access_token = None
        """ :type : str """
        self.token_expiration = None
        """ :type : Optional[float] """
        self.http_client = http_client or requests.request
        """ :type : HttpClient """
        self.http_success_codes = http_success_codes or [200, 201, 202]
        """ :type : list[int] """
        self.auth_lock: threading.Lock = threading.Lock()
        """ :type : threading.Lock """

        if not self.account_id:
            raise ValueError(f"Account name '{account_name}' is not a valid account or is not configured properly in the environment.")
        
        # Managers lazy init
        self._data_extensions = None
        self._automations = None
        self._queries = None
        self._subscribers = None

        
    def authenticate(self) -> None:
        """
        Authenticate with Salesforce Marketing Cloud using OAuth client credentials flow.

        Obtains a Bearer token by POSTing client credentials to the authentication endpoint.
        Stores the access token and expiration time (with a 60-second buffer).

        :raises AuthenticationError: If the authentication request fails or token info is missing.
        """

        with self.auth_lock:
            if not self.is_token_expired():
                return
      
        auth_data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "account_id": self.account_id
        }
        response = requests.post(f"https://{self.tenant_subdomain}.auth.marketingcloudapis.com", data=auth_data)
        if response.status_code not in self.http_success_codes:
            raise AuthenticationError("Authentication failed: " + response.text)

        self.access_token = response.json().get("access_token")
        self.token_expiration = time() + response.json().get("expires_in") - 60  # Set expiration 60s before actual expiration
        
        if not self.access_token or not self.token_expiration:
            raise AuthenticationError("Access token or expiration missing in auth response.")


    def is_token_expired(self) -> bool:
        """
        Check if the current OAuth token is missing or expired.

        :return: True if no valid token exists or token has expired, else False.
        :rtype: bool
        """

        return not self.access_token or time() >= (self.token_expiration or 0)


    def make_rest_request(
        self, 
        endpoint: str, 
        method: Optional[str] = "GET", 
        data: Optional[Dict] = None
    ) -> Optional[Dict]:
        """
        Make a REST API request to the Salesforce Marketing Cloud endpoint.

        Automatically authenticates if the token is expired.

        :param endpoint: REST API endpoint path (appended to base URL).
        :param method: HTTP method to use (GET, POST, PUT, DELETE). Defaults to "GET".
        :param data: JSON body for POST/PUT requests. Defaults to None.

        :return: JSON-decoded response body.
        :rtype: dict

        :raises ValueError: If an unsupported HTTP method is provided.
        :raises RequestError: If the HTTP response is unsuccessful.
        """

        if method not in ["GET", "POST", "PUT", "DELETE"]:
            raise ValueError(f"Unsupported HTTP method: {method}")
      
        # Check if have valid token before making REST call
        if self.is_token_expired():
            self.authenticate()

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        url = f"https://{self.tenant_subdomain}.rest.marketingcloudapis.com/{endpoint}"
        response = self.http_client(method, url, headers=headers, json=data)
      
        if response.status_code not in self.http_success_codes:
            raise RequestError(f"REST API Error {response.status_code}: {response.text}")
        
        return response.json()
        

    def make_soap_request(
        self, action: str, 
        body: str
    ) -> ET.Element:
        """
        Send a SOAP API request to Salesforce Marketing Cloud.

        Automatically authenticates if the token is expired.

        :param action: SOAPAction header specifying the operation.
        :param body: XML body content of the SOAP request.

        :return: Parsed XML element of the SOAP response.
        :rtype: xml.etree.ElementTree.Element

        :raises RequestError: If the SOAP request fails or response cannot be parsed.
        """

        # Check if have valid token before making SOAP call
        if self.is_token_expired():
            self.authenticate()

        headers = {
            "Content-Type": "text/xml",
            "SOAPAction": action
        }

        envelope = "\n".join([
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope" xmlns:a="http://schemas.xmlsoap.org/ws/2004/08/addressing" xmlns:u="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd">',
            '   <s:Header>',
            f'      <fueloauth>{self.access_token}</fueloauth>',
            '   </s:Header>',
            '   <s:Body xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">',
            f'      {body}',
            '   </s:Body>',
            '</s:Envelope>'
        ])

        response = self.http_client(
            method="POST",
            url=f"https://{self.tenant_subdomain}.soap.marketingcloudapis.com",
            headers=headers,
            data=envelope
        )
      
        if response.status_code not in self.http_success_codes:
            raise RequestError(f"SOAP API Error {response.status_code}: {response.text}")
      
        try:
            return ET.fromstring(response.content)
        except ET.ParseError as e:
            raise RequestError(f"Failed to parse SOAP response: {e}") from e


    def __repr__(self) -> str:
        """
        Provide a friendly representation

        :returns: String with identifying details
        """
        return f"<SFMC API {self.account_id}>"
    

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
            from managers.manager_data_extensions import DataExtensionManager
            self._data_extensions = DataExtensionManager(self)
        return self._data_extensions


    @property
    def automations(self):
        """
        Lazy-load and return the AutomationManager instance.

        :return: Manager for automation operations.
        """
        if self._automations is None:
            from managers.manager_automations import AutomationManager
            self._automations = AutomationManager(self)
        return self._automations


    @property
    def queries(self):
        """
        Lazy-load and return the QueryManager instance.

        :return: Manager for query operations.
        """
        if self._queries is None:
            from managers.manager_queries import QueryManager
            self._queries = QueryManager(self)
        return self._queries


    @property
    def subscribers(self):
        """
        Lazy-load and return the QueryManager instance.

        :return: Manager for query operations.
        """
        if self._subscribers is None:
            from managers.manager_subscribers import SubscriberManager
            self._subscribers = SubscriberManager(self)
        return self._subscribers
