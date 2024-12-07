from sfmc_api_client import SFMCAPIClient
from requests_handler import RequestsHandler

client = SFMCAPIClient()
req = RequestsHandler(client)

req._data_extension.get()
req._automation.get()
req._query.get()