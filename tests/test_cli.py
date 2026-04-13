"""
Unit tests for the CLI interface (cli/main.py).

All HTTP requests and user inputs are mocked so the Flask server does
not need to be running.
"""
import pytest
import requests as requests_lib
from unittest.mock import patch, Mock

import cli.main as cli


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

MOCK_ITEMS = [
    {
        "id": 1,
        "product_name": "Almond Milk",
        "brands": "Silk",
        "category": "Beverages",
        "quantity": 50,
        "price": 4.99,
        "barcode": "12345",
        "ingredients_text": "water, almonds",
        "nutriments": {"energy_kcal": 30, "proteins": 1, "fat": 2.5, "carbohydrates": 1,
                       "fiber": 0, "sugars": 0},
        "image_url": "",
    },
    {
        "id": 2,
        "product_name": "Orange Juice",
        "brands": "Tropicana",
        "category": "Juices",
        "quantity": 20,
        "price": 5.99,
        "barcode": "67890",
        "ingredients_text": "100% OJ",
        "nutriments": {"energy_kcal": 110, "proteins": 2, "fat": 0, "carbohydrates": 26,
                       "fiber": 0, "sugars": 22},
        "image_url": "",
    },
]
MOCK_ITEM = MOCK_ITEMS[0]

API_PRODUCT = {
    "product_name": "Found Product",
    "brands": "Found Brand",
    "barcode": "9876543210",
    "category": "Foods",
    "ingredients_text": "water, sugar",
    "nutriments": {},
    "image_url": "",
}


# ─────────────────────────────────────────────────────────────────────────────
# view_all_inventory
# ─────────────────────────────────────────────────────────────────────────────

class TestViewAllInventory:
    def test_displays_product_names(self, capsys):
        with patch("cli.main.api_get", return_value=(MOCK_ITEMS, 200)):
            cli.view_all_inventory()
        out = capsys.readouterr().out
        assert "Almond Milk" in out
        assert "Orange Juice" in out

    def test_shows_total_count(self, capsys):
        with patch("cli.main.api_get", return_value=(MOCK_ITEMS, 200)):
            cli.view_all_inventory()
        assert "2" in capsys.readouterr().out

    def test_empty_inventory_message(self, capsys):
        with patch("cli.main.api_get", return_value=([], 200)):
            cli.view_all_inventory()
        assert "empty" in capsys.readouterr().out.lower()

    def test_displays_error_on_connection_failure(self, capsys):
        with patch("cli.main.api_get", return_value=({"error": "Cannot connect to server."}, 503)):
            cli.view_all_inventory()
        assert "error" in capsys.readouterr().out.lower()


# ─────────────────────────────────────────────────────────────────────────────
# view_single_item
# ─────────────────────────────────────────────────────────────────────────────

class TestViewSingleItem:
    def test_displays_item_details(self, capsys):
        with patch("cli.main.api_get", return_value=(MOCK_ITEM, 200)), \
             patch("builtins.input", return_value="1"):
            cli.view_single_item()
        assert "Almond Milk" in capsys.readouterr().out

    def test_rejects_non_numeric_id(self, capsys):
        with patch("builtins.input", return_value="abc"):
            cli.view_single_item()
        assert "invalid" in capsys.readouterr().out.lower()

    def test_shows_error_for_missing_item(self, capsys):
        with patch("cli.main.api_get", return_value=({"error": "Item not found"}, 404)), \
             patch("builtins.input", return_value="9999"):
            cli.view_single_item()
        out = capsys.readouterr().out
        assert "error" in out.lower() or "not found" in out.lower()


# ─────────────────────────────────────────────────────────────────────────────
# add_item_manually
# ─────────────────────────────────────────────────────────────────────────────

class TestAddItemManually:
    _good_inputs = ["Test Product", "Test Brand", "123", "Foods", "water", "10", "5.99"]

    def test_successful_add_prints_confirmation(self, capsys):
        added = {**MOCK_ITEM, "id": 6, "product_name": "Test Product",
                 "quantity": 10, "price": 5.99}
        with patch("builtins.input", side_effect=self._good_inputs), \
             patch("cli.main.api_post", return_value=(added, 201)):
            cli.add_item_manually()
        out = capsys.readouterr().out
        assert "success" in out.lower() or "added" in out.lower()

    def test_rejects_empty_product_name(self, capsys):
        with patch("builtins.input", return_value=""):
            cli.add_item_manually()
        assert "required" in capsys.readouterr().out.lower() or \
               "error" in capsys.readouterr().out.lower()

    def test_rejects_non_numeric_quantity(self, capsys):
        inputs = ["Product", "Brand", "bar", "cat", "ing", "abc"]
        with patch("builtins.input", side_effect=inputs):
            cli.add_item_manually()
        assert "error" in capsys.readouterr().out.lower() or \
               "integer" in capsys.readouterr().out.lower()

    def test_rejects_non_numeric_price(self, capsys):
        inputs = ["Product", "Brand", "bar", "cat", "ing", "5", "notprice"]
        with patch("builtins.input", side_effect=inputs):
            cli.add_item_manually()
        assert "error" in capsys.readouterr().out.lower()


# ─────────────────────────────────────────────────────────────────────────────
# update_item
# ─────────────────────────────────────────────────────────────────────────────

class TestUpdateItem:
    def test_successful_update_prints_confirmation(self, capsys):
        updated = {**MOCK_ITEM, "quantity": 99, "price": 9.99}
        with patch("cli.main.api_get", return_value=(MOCK_ITEM, 200)), \
             patch("cli.main.api_patch", return_value=(updated, 200)), \
             patch("builtins.input", side_effect=["1", "99", "9.99", "", ""]):
            cli.update_item()
        out = capsys.readouterr().out
        assert "success" in out.lower() or "updated" in out.lower()

    def test_rejects_non_numeric_id(self, capsys):
        with patch("builtins.input", return_value="xyz"):
            cli.update_item()
        assert "invalid" in capsys.readouterr().out.lower()

    def test_no_changes_when_all_fields_skipped(self, capsys):
        with patch("cli.main.api_get", return_value=(MOCK_ITEM, 200)), \
             patch("builtins.input", side_effect=["1", "", "", "", ""]):
            cli.update_item()
        assert "no changes" in capsys.readouterr().out.lower()

    def test_shows_error_for_missing_item(self, capsys):
        with patch("cli.main.api_get", return_value=({"error": "Item not found"}, 404)), \
             patch("builtins.input", return_value="9999"):
            cli.update_item()
        assert "error" in capsys.readouterr().out.lower()


# ─────────────────────────────────────────────────────────────────────────────
# delete_item
# ─────────────────────────────────────────────────────────────────────────────

class TestDeleteItem:
    def test_successful_delete_prints_confirmation(self, capsys):
        with patch("cli.main.api_get", return_value=(MOCK_ITEM, 200)), \
             patch("cli.main.api_delete", return_value=({"message": "Item deleted."}, 200)), \
             patch("builtins.input", side_effect=["1", "yes"]):
            cli.delete_item()
        out = capsys.readouterr().out
        assert "deleted" in out.lower() or "success" in out.lower()

    def test_cancellation_aborts_delete(self, capsys):
        with patch("cli.main.api_get", return_value=(MOCK_ITEM, 200)), \
             patch("builtins.input", side_effect=["1", "no"]):
            cli.delete_item()
        assert "cancelled" in capsys.readouterr().out.lower()

    def test_rejects_non_numeric_id(self, capsys):
        with patch("builtins.input", return_value="abc"):
            cli.delete_item()
        assert "invalid" in capsys.readouterr().out.lower()

    def test_shows_error_for_missing_item(self, capsys):
        with patch("cli.main.api_get", return_value=({"error": "Item not found"}, 404)), \
             patch("builtins.input", return_value="9999"):
            cli.delete_item()
        assert "error" in capsys.readouterr().out.lower()


# ─────────────────────────────────────────────────────────────────────────────
# search_and_add_from_api
# ─────────────────────────────────────────────────────────────────────────────

class TestSearchAndAddFromApi:
    def test_barcode_search_displays_product(self, capsys):
        with patch("cli.main.api_get", return_value=(API_PRODUCT, 200)), \
             patch("cli.main.api_post", return_value=({**API_PRODUCT, "id": 10,
                                                        "quantity": 5, "price": 2.99}, 201)), \
             patch("builtins.input", side_effect=["1", "9876543210", "yes", "5", "2.99"]):
            cli.search_and_add_from_api()
        assert "Found Product" in capsys.readouterr().out

    def test_name_search_shows_no_products_message(self, capsys):
        with patch("cli.main.api_get", return_value=([], 200)), \
             patch("builtins.input", side_effect=["2", "unknownxyz123"]):
            cli.search_and_add_from_api()
        assert "no products" in capsys.readouterr().out.lower()

    def test_invalid_search_method_shows_error(self, capsys):
        with patch("builtins.input", return_value="9"):
            cli.search_and_add_from_api()
        assert "invalid" in capsys.readouterr().out.lower()

    def test_empty_barcode_shows_error(self, capsys):
        with patch("builtins.input", side_effect=["1", ""]):
            cli.search_and_add_from_api()
        assert "error" in capsys.readouterr().out.lower()

    def test_cancel_add_does_not_post(self, capsys):
        with patch("cli.main.api_get", return_value=(API_PRODUCT, 200)), \
             patch("cli.main.api_post") as mock_post, \
             patch("builtins.input", side_effect=["1", "9876543210", "no"]):
            cli.search_and_add_from_api()
        mock_post.assert_not_called()

    def test_name_search_cancel_selection(self, capsys):
        products = [API_PRODUCT]
        with patch("cli.main.api_get", return_value=(products, 200)), \
             patch("builtins.input", side_effect=["2", "milk", "0"]):
            cli.search_and_add_from_api()
        assert "cancelled" in capsys.readouterr().out.lower()
