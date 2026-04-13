import requests

# base url for the OpenFoodFacts API
BASE_URL = "https://world.openfoodfacts.org"


def fetch_product_by_barcode(barcode):
    # look up a product using its barcode number
    try:
        url = f"{BASE_URL}/api/v2/product/{barcode}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("status") == 1 and "product" in data:
            return parse_product(data["product"])

        return None

    except requests.exceptions.Timeout:
        raise ConnectionError("Request to OpenFoodFacts API timed out.")
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Failed to fetch product from OpenFoodFacts: {e}")


def fetch_product_by_name(name):
    # search for products by name
    try:
        url = f"{BASE_URL}/cgi/search.pl"
        params = {
            "search_terms": name,
            "search_simple": 1,
            "action": "process",
            "json": 1,
            "page_size": 10
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        products = data.get("products", [])

        # only return products that have a name
        result = []
        for p in products:
            if p.get("product_name"):
                result.append(parse_product(p))

        return result

    except requests.exceptions.Timeout:
        raise ConnectionError("Request to OpenFoodFacts API timed out.")
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Failed to search products on OpenFoodFacts: {e}")


def parse_product(product):
    # pull out the fields we care about from the API response
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
            "sugars": nutriments.get("sugars_100g", 0)
        },
        "image_url": product.get("image_url", product.get("image_front_url", ""))
    }


# keep _parse_product as an alias so existing tests still work
_parse_product = parse_product
