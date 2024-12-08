from base_manager import BaseManager
from typing import Any, Dict, Optional

class QueryManager(BaseManager):

  def get(self):
    print("got query")