# --- manager_subscribers.py ---
from managers.manager_base import BaseManager
from typing import Any, Dict, Optional, List


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
            '       <Filter xmlns:q1="http://exacttarget.com/wsdl/partnerAPI" xsi:type="q1:SimpleFilterPart">',
            '           <q1:Property>SubscriberKey</q1:Property>',
            '           <q1:SimpleOperator>equals</q1:SimpleOperator>',
            f'          <q1:Value>{subscriber_key}</q1:Value>',
            '       </Filter>',
            '   </RetrieveRequest>',
            '<RetrieveRequestMsg>'
        ])
        response_xml = self._sfmc_client.make_soap_request("Retrieve", body = body)
        results = response_xml.find(".//s:Body/default:RetrieveResponseMsg/default:Results", namespace=self.soap_xml_namespaces)

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
