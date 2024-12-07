class QueryManager:
  def __init__(self, sfmc_client):
    """
    TODO
    """
    self._sfmc_client: sfmc_client

  def get(self):
    print("got query")