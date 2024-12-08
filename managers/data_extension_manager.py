from base_manager import BaseManager
from typing import Any, Dict, Optional

class DataExtensionManager(BaseManager):
    
  def get_by_key(self, de_key: str) -> dict:
    """
    Retrieves a Data Extension object by its CustomerKey.

    This method sends a SOAP request to retrieve a Data Extension with specific 
    properties and filters by the CustomerKey.

    Arguments:
      - de_key (str): The CustomerKey of the Data Extension to retrieve.

    Returns:
      - dict: A dictionary representation of the Data Extension's properties.
    """
    body = f"""
      <RetrieveRequest>
        <ObjectType>DataExtension</ObjectType>
        <Properties>ObjectID</Properties>
        <Properties>CustomerKey</Properties>
        <Properties>Name</Properties>
        <Properties>IsSendable</Properties>
        <Properties>SendableSubscriberField.Name</Properties>
        <Filter xsi:type="SimpleFilterPart">
        <Property>CustomerKey</Property>
        <SimpleOperator>equals</SimpleOperator>
        <Value>{de_key}</Value>
        </Filter>
      </RetrieveRequest>
    """
    response_xml = self._sfmc_client.make_soap_request("Retrieve", body)
    result = {
      "ObjectID": response_xml.find(".//ObjectID").text,
      "CustomerKey": response_xml.find(".//CustomerKey").text,
      "Name": response_xml.find(".//Name").text,
      "IsSendable": response_xml.find(".//IsSendable").text,
      "SendableSubscriberFieldName": response_xml.find(".//SendableSubscriberField.Name").text,
    }
    return result

  def get_by_name(self, de_name: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves a list of Data Extensions matching the search string.

    Arguments:
      - de_name (str): The name or part of the name of the Data Extension to search for.

    Returns:
      - dict: The response data containing Data Extensions, or None if no results are found.
    """
    response = self._sfmc_client.make_rest_request(endpoint = f"data/v1/customobjects?$search={de_name}")
    
    # Check if the response contains items and return the result
    if response and response.get("items"):
      return response["items"]
    
    return None
  
  def get_by_id(self, de_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves a Data Extension by its unique ID.

    Arguments:
      - de_id (str): The unique ID of the Data Extension.

    Returns:
      - dict: The response data containing the Data Extension details, or None if not found.
    """
    return self._sfmc_client.make_rest_request(endpoint = f"data/v1/customobjects/{de_id}")
 
  def get_fields(self, de_name) -> Optional[Dict[str, Any]]:
    """
    Retrieves the fields of a Data Extension by its name.

    Arguments:
      - de_name (str): The name of the Data Extension.

    Returns:
      - dict: The response data containing fields, or None if the Data Extension is not found.
    """
    de_list = self.get_by_name(de_name)

    if not de_list:
      return None 
    
    de_id = de_list.items[0].id
    return self._sfmc_client.make_rest_request(endpoint = f"data/v1/customobjects/{de_id}/fields")
  
  def create(self, de_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Creates a new Data Extension in Salesforce Marketing Cloud.

    Arguments:
      - de_data (dict): A dictionary containing the data for the new Data Extension.

    Returns:
      - dict: The response data from the API, typically containing the created Data Extension.
    """
    return self._sfmc_client.make_rest_request(endpoint = "data/v1/customobjects", method = "POST", data = de_data)