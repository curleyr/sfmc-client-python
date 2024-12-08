from core.sfmc_api_client import SFMCAPIClient
from core.requests_handler import RequestsHandler

client = SFMCAPIClient()
req = RequestsHandler(client)

req._data_extension.get_by_key("key")
req._automation.get()
req._query.get()