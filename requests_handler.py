from sfmc_api_client import SFMCAPIClient
from object_managers.data_extension_manager import DataExtensionManager
from object_managers.automation_manager import AutomationManager
from object_managers.query_manager import QueryManager

class RequestsHandler:
  """
  Provides a centralized interface for interacting with the various SFMC object managers.

  The RequestsHandler acts as a bridge between the SFMC API client and specific object 
  managers such as DataExtensionManager, AutomationManager, and QueryManager. 
  It encapsulates the initialization and management of these objects.

  Attributes:
    - _sfmc_client (SFMCAPIClient): An instance of the SFMCAPIClient class used for 
      managing authentication and executing API requests.
    - _data_extension (DataExtensionManager): Manages interactions with Data Extensions.
    - _automation (AutomationManager): Manages interactions with Automations.
    - _query (QueryManager): Manages interactions with Queries.
  """
      
  def __init__(self, sfmc_client: SFMCAPIClient):
    """
    Initializes the RequestsHandler instance and instantanializes the individual object manager classes.

    Arguments:
      - sfmc_client (SFMCAPIClient): An instance of the SFMCAPIClient class that manages the SFMC connection/authentication and execution of requests.
    """
    self._sfmc_client = sfmc_client
    self._data_extension = DataExtensionManager(self._sfmc_client)
    self._automation = AutomationManager(self._sfmc_client)
    self._query = QueryManager(self._sfmc_client)