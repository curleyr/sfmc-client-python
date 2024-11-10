import requests
from time import time
import os
import xml.etree.ElementTree as ET
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

class SFMCClient:
  def __init__(self):
    self._client_id = os.environ.get("client_id")
    self._client_secret = os.environ.get("client_secret")
    self._account_id = os.environ.get("account_id")
    self._auth_endpoint = os.environ.get("auth_endpoint")
    self._soap_endpoint = os.environ.get("soap_endpoint")
    self._rest_endpoint = os.environ.get("rest_endpoint")
    self._access_token = None
    self._token_expiration = None

  def authenticate(self):
    """Authenticates using the OAuth flow to obtain bearer token. 
    Sets self._access_token and self._token_expiration
    
    Keyword arguments: None
    Return: None
    """
    auth_data = {
      'grant_type': 'client_credentials',
      'client_id': self._client_id,
      'client_secret': self._client_secret,
      'account_id': self._account_id
    }
    response = requests.post(self._auth_endpoint, data=auth_data)
    if response.status_code == 200:
      self._access_token = response.json().get('access_token')
      self._token_expiration = time() + response.json().get('expires_in') - 60  # Set expiration 60s before actual expiration
      print("Authenticated successfully. Token will expire in", response.json().get('expires_in'), "seconds.")
    else:
      raise Exception("Authentication failed: " + response.text)

  def is_token_expired(self):
    """Checks if the token has expired
    Keyword arguments: None
    Return: True if token has expired, otherwise False
    """
    return self._access_token is None or time() >= self._token_expiration

  def make_rest_request(self, endpoint, method='GET', data=None):
    """sumary_line
    
    Keyword arguments:
    argument -- description
    Return: return_description
    """
    
    # Check if have valid token before making REST call
    if self.is_token_expired():
      self.authenticate()
    headers = {
      'Authorization': f'Bearer {self._access_token}',
      'Content-Type': 'application/json'
    }
    url = f"{self._rest_endpoint}/{endpoint}"
    response = requests.request(method, url, headers=headers, json=data)
    if response.status_code in [200, 201]:
      return response.json()
    else:
      raise Exception(f"REST API request failed: {response.text}")

  def make_soap_request(self, soap_action, body):
    """sumary_line
    
    Keyword arguments:
    argument -- description
    Return: return_description
    """
    
    # Check if have valid token before making SOAP call
    if self.is_token_expired():
      self.authenticate()
    headers = {
      'Authorization': f'Bearer {self._access_token}',
      'Content-Type': 'text/xml',
      'SOAPAction': soap_action
    }
    response = requests.post(self._soap_endpoint, headers=headers, data=body)
    if response.status_code == 200:
      return ET.fromstring(response.content)
    else:
      raise Exception(f"SOAP API request failed: {response.text}")