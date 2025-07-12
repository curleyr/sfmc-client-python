# --- manager/base_manager.py ---
from __future__ import annotations
from src.sfmc_client.client.base_client import BaseClient
from xml.etree.ElementTree import Element
from typing import Optional


class BaseManager:
    """
    Base class for all Salesforce Marketing Cloud object managers.

    Provides shared access to the SFMCAPIClient and utilities for parsing SOAP responses.
    """
    
    def __init__(self, client: BaseClient) -> None:
        """
        Initialize the manager with a reference to the SFMC API client.

        :param sfmc_client: An instance of SFMCAPIClient used for executing API requests.
        """
        self.client = client
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
