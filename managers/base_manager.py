class BaseManager:
  def __init__(self, sfmc_client):
    """
    Initializes the base manager instance with a Salesforce Marketing Cloud API client.

    Arguments:
      - sfmc_client (SFMCAPIClient): The SFMC API client that manages the connection
        and execution of requests.
    """
    self._sfmc_client = sfmc_client