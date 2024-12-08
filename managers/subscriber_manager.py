from typing import Any, Dict, Optional

class SubscriberManager:
  def __init__(self, sfmc_client):
    """
    Initializes the SubscriberManager instance, which provides methods to interact
    with Salesforce Marketing Cloud's subscribers.

    Arguments:
      - sfmc_client (SFMCAPIClient): The SFMC API client that manages the connection
        and execution of requests.
    """
    self._sfmc_client = sfmc_client
  
  def get_by_key(self, subscriber_key: str) -> dict:
    """
    Retrieves a Subscriber object by its SubscriberKey.

    This method sends a SOAP request to retrieve a Subscriber with specific 
    properties and filters by the SubscriberKey.

    Arguments:
      - subscriber_key (str): The SubscriberKey of the Subscriber to retrieve.

    Returns:
      - dict: A dictionary representation of the Subscriber's properties.
    """
    body = f"""
      <s:Body xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
        <RetrieveRequestMsg xmlns="http://exacttarget.com/wsdl/partnerAPI">
          <RetrieveRequest>
            <ObjectType>Subscriber</ObjectType>
            <Properties>ID</Properties>
            <Properties>CreatedDate</Properties>
            <Properties>EmailAddress</Properties>
            <Properties>SubscriberKey</Properties>
            <Properties>UnsubscribedDate</Properties>
            <Properties>Status</Properties>
            <Filter xmlns:q1="http://exacttarget.com/wsdl/partnerAPI" xsi:type="q1:SimpleFilterPart">
              <q1:Property>SubscriberKey</q1:Property>
              <q1:SimpleOperator>equals</q1:SimpleOperator>
              <q1:Value>{subscriber_key}</q1:Value>
            </Filter>
          </RetrieveRequest>
        </RetrieveRequestMsg>
      </s:Body>
    """
    response_xml = self._sfmc_client.make_soap_request("Retrieve", body = body)
    result = {
      "ID": response_xml.find(".//ID").text,
      "CreatedDate": response_xml.find(".//CreatedDate").text,
      "EmailAddress": response_xml.find(".//EmailAddress").text,
      "SubscriberKey": response_xml.find(".//SubscriberKey").text,
      "UnsubscribedDate": response_xml.find(".//UnsubscribedDate").text,
      "Status": response_xml.find(".//Status").text
    }
    return result