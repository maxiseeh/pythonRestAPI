"""
OpenFoodFacts API integration.

Provides functions to search products by barcode or name and normalise
the response into the inventory item schema.

API docs: https://world.openfoodfacts.org/data
"""
import requests

OPENFOODFACTS_BASE_URL = "https://world.openfoodfacts.org"
REQUEST_TIMEOUT = 10  # seconds


def fetch_product_by_barcode(barcode):
    """
    Fetch a single product from OpenFoodFacts using its barcode.

    Args:
        barcode (str): The product barcode (EAN-13 / UPC-A, etc.)

    Returns:
        dict | None: Parsed product dict, or None if not found.

    Raises:
        ConnectionError: On network or API failure.
    """
    try:
        url = f"{OPENFOODFACTS_BASE_URL}/api/v2/product/{barcode}"
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        if data.get("status") == 1 and "product" in data:
            return _parse_product(data["product"])
        return None
    except requests.exceptions.Timeout:
        raise ConnectionError("Request to OpenFoodFacts API timed out.")
    except requests.exceptions.RequestException as exc:
        raise ConnectionError(f"Failed to fetch product from OpenFoodFacts: {exc}")


def fetch_product_by_name(name):
    """
    Search OpenFoodFacts for products matching a name string.

    Args:
        name (str): Product name or keyword to search for.

    Returns:
        list[dict]: List of parsed product dicts (may be empty).

    Raises:
        ConnectionError: On network or API failure.
    """
    try:
        url = f"{OPENFOODFACTS_BASE_URL}/cgi/search.pl"
        params = {
            "search_terms": name,
            "search_simple": 1,
            "action": "process",
            "json": 1,
            "page_size": 10,
        }
        response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        products = data.get("products", [])
        # Filter out items without a product name
        return [_parse_product(p) for p in products if p.get("product_name")]
    except requests.exceptions.Timeout:
        raise ConnectionError("Request to OpenFoodFacts API timed out.")
    except requests.exceptions.RequestException as exc:
        raise ConnectionError(f"Failed to search products on OpenFoodFacts: {exc}")


def _parse_product(product):
    """
    Normalise a raw OpenFoodFacts product dict into the inventory schema.

    Args:
        product (dict): Raw product data from OpenFoodFacts.

    Returns:
        dict: Normalised product dict.
    """
    nutriments = product.get("nutriments", {})
    return {
        "product_name": product.get("product_name", "Unknown"),
        "brands": product.get("brands", ""),
        "barcode": product.get("code", product.get("_id", "")),
        "ingredients_text": product.get("ingredients_text", ""),
        "category": product.get("categories", ""),
        "nutriments": {
            "energy_kcal": nutriments.get("energy-kcal_100g", 0),
            "proteins": nutriments.get("proteins_100g", 0),
            "fat": nutriments.get("fat_100g", 0),
            "carbohydrates": nutriments.get("carbohydrates_100g", 0),
            "fiber": nutriments.get("fiber_100g", 0),
            "sugars": nutriments.get("sugars_100g", 0),
        },
        "image_url": product.get("image_url", product.get("image_front_url", "")),
    }
