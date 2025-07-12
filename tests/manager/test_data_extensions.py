# --- tests/manager/test_data_extensions.py ---
import unittest
from unittest.mock import MagicMock
from src.sfmc_client.manager.data_extensions import DataExtensionManager

class TestDataExtensionManager(unittest.TestCase):
    def setUp(self):
        self.mock_client = MagicMock()
        self.manager = DataExtensionManager(self.mock_client)

    def test_get_by_key_success(self):
        self.mock_client.make_soap_request.return_value.find.return_value = MagicMock(text="123")
        result = self.manager.get_by_key("my_key")
        self.assertIn("ObjectID", result)

    def test_get_by_name_success(self):
        self.mock_client.make_rest_request.return_value = {"items": ["item1", "item2"]}
        result = self.manager.get_by_name("my_name")
        self.assertEqual(result, ["item1", "item2"])

    def test_get_by_id_success(self):
        self.mock_client.make_rest_request.return_value = {"id": "de123"}
        result = self.manager.get_by_id("de123")
        self.assertEqual(result["id"], "de123")

    def test_get_fields_no_match(self):
        self.mock_client.make_rest_request.return_value = {"items": []}
        result = self.manager.get_fields("no_match")
        self.assertIsNone(result)

    def test_create_success(self):
        self.mock_client.make_rest_request.return_value = {"status": "created"}
        result = self.manager.create({"Name": "TestDE"})
        self.assertEqual(result["status"], "created")