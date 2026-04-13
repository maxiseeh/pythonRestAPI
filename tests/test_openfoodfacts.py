"""
Unit tests for the OpenFoodFacts service layer.

All HTTP calls are mocked so these tests run without network access.
"""
import pytest
import requests as requests_lib
from unittest.mock import patch, Mock

from server.services.openfoodfacts import (
    fetch_product_by_barcode,
    fetch_product_by_name,
    _parse_product,
)

# ─────────────────────────────────────────────────────────────────────────────
# Shared fixtures / helpers
# ─────────────────────────────────────────────────────────────────────────────

MOCK_RAW_PRODUCT = {
    "product_name": "Test Almond Milk",
    "brands": "Test Brand",
    "code": "123456789012",
    "ingredients_text": "Filtered water, almonds, sugar",
    "categories": "Plant-based milks",
    "nutriments": {
        "energy-kcal_100g": 30,
        "proteins_100g": 1.0,
        "fat_100g": 2.5,
        "carbohydrates_100g": 2.0,
        "fiber_100g": 0.5,
        "sugars_100g": 1.5,
    },
    "image_url": "https://example.com/image.jpg",
}


def _mock_response(json_data, status_code=200):
    """Build a minimal mock requests.Response."""
    mock = Mock()
    mock.json.return_value = json_data
    mock.status_code = status_code
    mock.raise_for_status.return_value = None
    return mock


# ─────────────────────────────────────────────────────────────────────────────
# fetch_product_by_barcode
# ─────────────────────────────────────────────────────────────────────────────

class TestFetchProductByBarcode:
    def test_returns_parsed_product_on_success(self):
        resp = _mock_response({"status": 1, "product": MOCK_RAW_PRODUCT})
        with patch("server.services.openfoodfacts.requests.get", return_value=resp):
            result = fetch_product_by_barcode("123456789012")
        assert result is not None
        assert result["product_name"] == "Test Almond Milk"
        assert result["brands"] == "Test Brand"
        assert result["barcode"] == "123456789012"

    def test_returns_none_when_status_is_0(self):
        resp = _mock_response({"status": 0})
        with patch("server.services.openfoodfacts.requests.get", return_value=resp):
            result = fetch_product_by_barcode("000000000000")
        assert result is None

    def test_returns_none_when_product_key_missing(self):
        resp = _mock_response({"status": 1})
        with patch("server.services.openfoodfacts.requests.get", return_value=resp):
            result = fetch_product_by_barcode("000000000000")
        assert result is None

    def test_raises_connection_error_on_timeout(self):
        with patch(
            "server.services.openfoodfacts.requests.get",
            side_effect=requests_lib.exceptions.Timeout,
        ):
            with pytest.raises(ConnectionError, match="timed out"):
                fetch_product_by_barcode("123456789012")

    def test_raises_connection_error_on_network_failure(self):
        with patch(
            "server.services.openfoodfacts.requests.get",
            side_effect=requests_lib.exceptions.ConnectionError,
        ):
            with pytest.raises(ConnectionError):
                fetch_product_by_barcode("123456789012")

    def test_nutriments_parsed_correctly(self):
        resp = _mock_response({"status": 1, "product": MOCK_RAW_PRODUCT})
        with patch("server.services.openfoodfacts.requests.get", return_value=resp):
            result = fetch_product_by_barcode("123456789012")
        nut = result["nutriments"]
        assert nut["energy_kcal"] == 30
        assert nut["proteins"] == 1.0
        assert nut["fat"] == 2.5
        assert nut["carbohydrates"] == 2.0
        assert nut["fiber"] == 0.5
        assert nut["sugars"] == 1.5

    def test_image_url_is_included(self):
        resp = _mock_response({"status": 1, "product": MOCK_RAW_PRODUCT})
        with patch("server.services.openfoodfacts.requests.get", return_value=resp):
            result = fetch_product_by_barcode("123456789012")
        assert result["image_url"] == "https://example.com/image.jpg"


# ─────────────────────────────────────────────────────────────────────────────
# fetch_product_by_name
# ─────────────────────────────────────────────────────────────────────────────

class TestFetchProductByName:
    def test_returns_list_of_products(self):
        second = {**MOCK_RAW_PRODUCT, "product_name": "Oat Milk"}
        resp = _mock_response({"products": [MOCK_RAW_PRODUCT, second]})
        with patch("server.services.openfoodfacts.requests.get", return_value=resp):
            results = fetch_product_by_name("almond milk")
        assert len(results) == 2
        assert results[0]["product_name"] == "Test Almond Milk"
        assert results[1]["product_name"] == "Oat Milk"

    def test_returns_empty_list_when_no_products(self):
        resp = _mock_response({"products": []})
        with patch("server.services.openfoodfacts.requests.get", return_value=resp):
            results = fetch_product_by_name("xyzunknown999")
        assert results == []

    def test_filters_out_products_without_name(self):
        unnamed = {"brands": "Ghost Brand", "code": "111"}
        resp = _mock_response({"products": [MOCK_RAW_PRODUCT, unnamed]})
        with patch("server.services.openfoodfacts.requests.get", return_value=resp):
            results = fetch_product_by_name("milk")
        # Only the named product should be returned
        assert len(results) == 1
        assert results[0]["product_name"] == "Test Almond Milk"

    def test_raises_connection_error_on_timeout(self):
        with patch(
            "server.services.openfoodfacts.requests.get",
            side_effect=requests_lib.exceptions.Timeout,
        ):
            with pytest.raises(ConnectionError, match="timed out"):
                fetch_product_by_name("milk")

    def test_raises_connection_error_on_network_failure(self):
        with patch(
            "server.services.openfoodfacts.requests.get",
            side_effect=requests_lib.exceptions.ConnectionError,
        ):
            with pytest.raises(ConnectionError):
                fetch_product_by_name("milk")


# ─────────────────────────────────────────────────────────────────────────────
# _parse_product (internal helper)
# ─────────────────────────────────────────────────────────────────────────────

class TestParseProduct:
    def test_all_known_fields_are_mapped(self):
        result = _parse_product(MOCK_RAW_PRODUCT)
        assert result["product_name"] == "Test Almond Milk"
        assert result["brands"] == "Test Brand"
        assert result["barcode"] == "123456789012"
        assert result["ingredients_text"] == "Filtered water, almonds, sugar"
        assert result["category"] == "Plant-based milks"
        assert result["image_url"] == "https://example.com/image.jpg"

    def test_empty_product_uses_defaults(self):
        result = _parse_product({})
        assert result["product_name"] == "Unknown"
        assert result["brands"] == ""
        assert result["barcode"] == ""
        assert result["ingredients_text"] == ""
        assert result["category"] == ""
        assert result["image_url"] == ""

    def test_nutriments_default_to_zero(self):
        result = _parse_product({})
        for key in ("energy_kcal", "proteins", "fat", "carbohydrates", "fiber", "sugars"):
            assert result["nutriments"][key] == 0

    def test_fallback_barcode_uses_underscore_id(self):
        product = {**MOCK_RAW_PRODUCT}
        del product["code"]
        product["_id"] = "fallback-id"
        result = _parse_product(product)
        assert result["barcode"] == "fallback-id"
