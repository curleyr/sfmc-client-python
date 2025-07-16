# --- manager/data_extensions.py ---
from __future__ import annotations
from src.sfmc_client.manager.base_manager import BaseManager
from typing import Any, Dict, Optional, List


class DataExtensionManager(BaseManager):
    """Manager class for interacting with Data Extension objects in Salesforce Marketing Cloud."""

    def get_by_key(self, de_key: str) -> Dict[str, Any]:
        """
        Retrieve a Data Extension by its CustomerKey via SOAP.

        :param de_key: The CustomerKey of the Data Extension.
        :return: Dictionary of key properties for the Data Extension.
        """
        body = "\n".join([
            '<RetrieveRequestMsg xmlns="http://exacttarget.com/wsdl/partnerAPI">',
            '    <RetrieveRequest>',
            '        <ObjectType>DataExtension</ObjectType>',
            '        <Properties>ObjectID</Properties>',
            '        <Properties>CustomerKey</Properties>',
            '        <Properties>Name</Properties>',
            '        <Properties>IsSendable</Properties>',
            '        <Properties>SendableSubscriberField.Name</Properties>',
            '        <Filter xsi:type="SimpleFilterPart">',
            '            <Property>CustomerKey</Property>',
            '            <SimpleOperator>equals</SimpleOperator>',
            f'           <Value>{de_key}</Value>',
            '        </Filter>',
            '    </RetrieveRequest>',
            '</RetrieveRequestMsg>'
        ])
        response_xml = self.client.make_soap_request("Retrieve", body)
        results = response_xml.find(".//s:Body/default:RetrieveResponseMsg/default:Results", namespaces=self.soap_xml_namespaces)
        
        if results is None:
            return None
                
        return {
            "ObjectID": self._get_soap_text(results, "ObjectID"),
            "CustomerKey": self._get_soap_text(results, "CustomerKey"),
            "Name": self._get_soap_text(results, "Name"),
            "IsSendable": self._get_soap_text(results, "IsSendable"),
            "SendableSubscriberFieldName": self._get_soap_text(results, "SendableSubscriberField.Name")
        }


    def get_by_name(self, de_name: str) -> Optional[List[Dict[str, Any]]]:
        """
        Retrieve Data Extensions whose names match or contain the given string.

        :param de_name: Full or partial Data Extension name.
        :return: List of matching Data Extensions, or None if none found.
        """
        response = self.client.make_rest_request(
            endpoint = f"data/v1/customobjects?$search={de_name}"
        )
        return response.get("items") if response and "items" in response else None


    def get_by_id(self, de_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a Data Extension by its unique ID.

        :param de_id: The unique identifier of the Data Extension.
        :return: Data Extension details or None if not found.
        """
        return self.client.make_rest_request(
            endpoint = f"data/v1/customobjects/{de_id}"
        )


    def get_fields(self, de_name) -> Optional[Dict[str, Any]]:
        """
        Retrieve the fields of the first Data Extension matching the given name.

        :param de_name: The name of the Data Extension.
        :return: Fields of the Data Extension or None if not found.
        """
        matches = self.get_by_name(de_name)
        if not matches:
            return None

        first_de = matches[0]
        de_id = first_de.get("id")
        if not de_id:
            return None

        return self.client.make_rest_request(
            endpoint=f"data/v1/customobjects/{de_id}/fields"
        )


    def create(self, de_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new Data Extension.

        :param de_data: Data structure for the new Data Extension.
        :return: API response containing the created object.
        """
        return self.client.make_rest_request(
            endpoint = "data/v1/customobjects",
            method = "POST",
            data = de_data
        )
