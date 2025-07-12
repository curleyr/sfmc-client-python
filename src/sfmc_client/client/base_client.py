# --- client/base_client.py ---
from abc import ABC, abstractmethod
from typing import Any

class BaseClient(ABC):
    def __init__(
        self,
        config,
        http_client,
        auth_manager
    ):
        self.config = config
        self.http_client = http_client
        self.auth_manager = auth_manager

    @abstractmethod
    def make_rest_request(
        self, 
        endpoint: str, 
        method: str = "GET", 
        data: Any = None
    ) -> Any:
        pass

    @abstractmethod
    def make_soap_request(
        self, 
        action: str, 
        body: str
    ) -> Any:
        pass