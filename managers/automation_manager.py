from base_manager import BaseManager
from typing import Any, Dict, Optional

class AutomationManager(BaseManager):

  def get(self):
    print("got automation")