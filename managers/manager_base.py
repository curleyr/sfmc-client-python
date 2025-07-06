# --- manager_base.py ---
from typing import Optional, TYPE_CHECKING
from xml.etree.ElementTree import Element

# Import for type hints only to avoid circular imports.
# `TYPE_CHECKING` ensures this is ignored at runtime and instead, only evaluated at type checking time.
if TYPE_CHECKING:
    from core.sfmc_api_client import SFMCAPIClient


class BaseManager:
    """
    Base class for all Salesforce Marketing Cloud object managers.

    Provides shared access to the SFMCAPIClient and utilities for parsing SOAP responses.
    """
    
    def __init__(self, sfmc_client: 'SFMCAPIClient') -> None:
        """
        Initialize the manager with a reference to the SFMC API client.

        :param sfmc_client: An instance of SFMCAPIClient used for executing API requests.
        """
        self._sfmc_client = sfmc_client
        self.soap_xml_namespaces = {"s": "http://www.w3.org/2003/05/soap-envelope", "default": "http://exacttarget.com/wsdl/partnerAPI"}


    def _get_soap_text(self, parent: Element, tag: str) -> Optional[str]:
        """
        Safely retrieve the text content of a child element from a SOAP XML node.

        :param parent: The parent XML element to search within.
        :param tag: The tag name (without prefix) to search for.
        :return: The text content of the element, or None if not found.
        """
        element = parent.find(f"default:{tag}", namespaces=self.soap_xml_namespaces)
        return element.text if element is not None else None
