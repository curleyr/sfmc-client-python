import requests
from time import time
import os
import json
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
from typing import Optional, Dict

# Load environment variables from the .env file
load_dotenv()

class SFMCAPIClient:
  def __init__(self, account_name: str = "Transactional"):
    """
    Initializes the Salesforce Marketing Cloud API client with credentials and endpoint URLs.

    This method retrieves the client ID, client secret, account ID, and endpoint URLs
    (authentication, SOAP, and REST) from environment variables. It also initializes 
    the access token and token expiration time as `None`, as they are obtained after 
    authentication.

    Arguments:
      - account_name (str, optional): The name of the SFMC mid, defaults to 'Transactional'.
        Valid options are 'Transactional', 'Customer Retention', and 'Safeco'.

    Attributes:
      - _client_id: The client ID for the Salesforce Marketing Cloud account.
      - _client_secret: The client secret for the Salesforce Marketing Cloud account.
      - _account_id: The account ID (MID) for the Salesforce Marketing Cloud account.
      - _auth_endpoint: The endpoint for the authentication API.
      - _rest_endpoint: The endpoint for the REST API.
      - _soap_endpoint: The endpoint for the SOAP API.
      - _access_token: Initially set to None, will store the access token after authentication.
      - _token_expiration: Initially set to None, will store the expiration time of the access token.
      - _http_success: Successful HTTP response statis codes.
    
    Raises:
      - ValueError: If an invalid account_name is provided or it's not configured propertly in the environment variables.
    """
    self._client_id = os.environ.get("client_id")
    self._client_secret = os.environ.get("client_secret")
    self._account_id = json.loads(os.environ.get("account_ids", "{}")).get(account_name)
    self._auth_endpoint = os.environ.get("auth_endpoint")
    self._rest_endpoint = os.environ.get("rest_endpoint")
    self._soap_endpoint = os.environ.get("soap_endpoint")
    self._access_token = None
    self._token_expiration = None
    self._http_success = [200, 201, 202]

    if not self._account_id:
      raise ValueError(f"Account name '{account_name}' is not a valid account or is not configured properly in the environment variables.")
        
  def authenticate(self) -> None:
    """
    Authenticates the user using the OAuth client credentials flow to obtain a Bearer token.

    This method sends a POST request to the authentication endpoint with the client 
    credentials (client_id, client_secret, and account_id) to retrieve an access token. 
    The method stores the access token and the token expiration time (60 seconds before actual expiration).

    Updates:
      - Sets _access_token with the obtained Bearer token.
      - Sets _token_expiration with the expiration time of the token.

    Returns:
      - None
    
    Raises:
      - Exception: If authentication fails or the response is not successful.
    """
    auth_data = {
      'grant_type': 'client_credentials',
      'client_id': self._client_id,
      'client_secret': self._client_secret,
      'account_id': self._account_id
    }
    response = requests.post(self._auth_endpoint, data=auth_data)
    
    if response.status_code in self._http_success:
      self._access_token = response.json().get('access_token')
      self._token_expiration = time() + response.json().get('expires_in') - 60  # Set expiration 60s before actual expiration
      print("Authenticated successfully. Token will expire in", round(response.json().get('expires_in') / 60), "minutes.")
    else:
      raise Exception("Authentication failed: " + response.text)

  def is_token_expired(self) -> bool:
    """
    Checks whether the Bearer token is missing or has expired.

    This method verifies if the access token is present and whether it has 
    expired based on the stored expiration time. If no token exists or the 
    token has expired, it returns `True`, otherwise `False`.

    Arguments: 
      - None

    Returns:
      - bool: True if the access token is either missing or has expired, otherwise False.
    """
    return self._access_token is None or time() >= self._token_expiration

  def make_rest_request(self, endpoint: str, method: Optional[str] = 'GET', data: Optional[Dict] = None) -> Optional[Dict]:
    """
    Makes a REST request to the specified Salesforce Marketing Cloud REST API endpoint using the given HTTP method.

    This method handles GET, POST, PUT, and DELETE requests and ensures the access token 
    is valid before making the request.
    
    Arguments:
      - endpoint (str): The URL endpoint for the request.
      - method (str, optional): The HTTP method to use (GET, POST, PUT, DELETE). Defaults to 'GET'.
      - data (dict, optional): The body of the request, for POST/PUT requests. Defaults to None.

   Returns:
      - dict: The JSON response data from the REST API if the request is successful.

    Raises:
      - ValueError: If an unsupported HTTP method is provided.
      - Exception: If the REST API request fails (non-200/201 status code) or returns an error response.
    """
    if method not in ['GET', 'POST', 'PUT', 'DELETE']:
      raise ValueError(f"Unsupported HTTP method: {method}")
    
    # Check if have valid token before making REST call
    if self.is_token_expired():
      self.authenticate()

    headers = {
      'Authorization': f'Bearer {self._access_token}',
      'Content-Type': 'application/json'
    }
    url = f'{self._rest_endpoint}/{endpoint}'
    response = requests.request(method, url, headers=headers, json=data)
    
    if response.status_code in self._http_success:
      return response.json()
    else:
      raise Exception(f'REST API request failed: {response.text}')

  def make_soap_request(self, action: str, body: str) -> ET.Element:
    """
    Sends a SOAP request to the Salesforce Marketing Cloud SOAP API.

    This method sends a POST request to the SOAP endpoint with the specified SOAP action 
    and request body. It ensures that a valid access token is used by checking the token's 
    expiration before making the request.

    Keyword arguments:
      - action (str) -- The SOAPAction header value that specifies the operation to be invoked.
      - body (str) -- The XML body of the SOAP request, containing the parameters for the operation.

    Returns:
      - ET.Element: The parsed XML response from the SOAP API, or raises an exception if the request fails.

    Raises:
      - Exception: If the SOAP request fails (non-200 status code) or if there is an issue parsing the response.
    """
    # Check if have valid token before making SOAP call
    if self.is_token_expired():
      self.authenticate()

    headers = {
      'Authorization': f'Bearer {self._access_token}',
      'Content-Type': 'text/xml',
      'SOAPAction': action
    }
    response = requests.post(self._soap_endpoint, headers=headers, data=body)
    
    if response.status_code in self._http_success:
      return ET.fromstring(response.content)
    else:
      raise Exception(f'SOAP API request failed: {response.text}')