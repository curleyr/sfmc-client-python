# --- manager/subscribers.py ---
from __future__ import annotations
from src.sfmc_client.manager.base_manager import BaseManager
from typing import Any, Dict


class SubscriberManager(BaseManager):
    """Manager class for interacting with Subsriber objects in Salesforce Marketing Cloud."""

    def get_by_key(self, subscriber_key: str) -> Dict[str, Any]:
        """
        Retrieve a Subscriber by its CustomerKey via SOAP.

        :param subscriber_key: The CustomerKey of the Subscriber.
        :return: Dictionary of key properties for the Subscriber.
        """
        body = "\n".join([
            '<RetrieveRequestMsg xmlns="http://exacttarget.com/wsdl/partnerAPI">',
            '   <RetrieveRequest>',
            '       <ObjectType>Subscriber</ObjectType>',
            '       <Properties>ID</Properties>',
            '       <Properties>CreatedDate</Properties>',
            '       <Properties>EmailAddress</Properties>',
            '       <Properties>SubscriberKey</Properties>',
            '       <Properties>UnsubscribedDate</Properties>',
            '       <Properties>Status</Properties>',
            '       <Filter xsi:type="SimpleFilterPart">',
            '           <Property>SubscriberKey</Property>',
            '           <SimpleOperator>equals</SimpleOperator>',
            f'          <Value>{subscriber_key}</Value>',
            '       </Filter>',
            '   </RetrieveRequest>',
            '</RetrieveRequestMsg>'
        ])
        response_xml = self.client.make_soap_request(action="Retrieve", body=body)
        results = response_xml.find(".//s:Body/default:RetrieveResponseMsg/default:Results", namespaces=self.soap_xml_namespaces)

        if results is None:
            return None
        
        return {
          "ID": self._get_soap_text(results, "ID"),
          "CreatedDate": self._get_soap_text(results, "CreatedDate"),
          "EmailAddress": self._get_soap_text(results, "EmailAddress"),
          "SubscriberKey": self._get_soap_text(results, "SubscriberKey"),
          "UnsubscribedDate": self._get_soap_text(results, "UnsubscribedDate"),
          "Status": self._get_soap_text(results, "Status")
        }
