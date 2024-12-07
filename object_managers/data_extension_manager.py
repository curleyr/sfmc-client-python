class DataExtensionManager:
  def __init__(self, sfmc_client):
    """
    TODO
    """
    self._sfmc_client: sfmc_client

  #def perform_rest_request(self, request_type, ):
  #  """
  #  Helper function that calls the make_rest_request method of the SFMCAPIClient class.
  #  """  

  def get(self):
    print("called get()")