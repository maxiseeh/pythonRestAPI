"""
In-memory mock database for the inventory management system.
Data structure mirrors the OpenFoodFacts API response format.
"""
import copy

_INITIAL_INVENTORY = [
    {
        "id": 1,
        "product_name": "Organic Almond Milk",
        "brands": "Silk",
        "barcode": "025293003628",
        "ingredients_text": (
            "Filtered water, almonds, cane sugar, sea salt, "
            "sunflower lecithin, locust bean gum, gellan gum"
        ),
        "category": "Plant-based milks",
        "quantity": 50,
        "price": 4.99,
        "nutriments": {
            "energy_kcal": 30,
            "proteins": 1.0,
            "fat": 2.5,
            "carbohydrates": 1.0,
            "fiber": 0.0,
            "sugars": 0.0,
        },
        "image_url": "",
    },
    {
        "id": 2,
        "product_name": "Whole Grain Bread",
        "brands": "Nature's Own",
        "barcode": "040000487579",
        "ingredients_text": (
            "Whole grain wheat flour, water, yeast, sugar, salt, soybean oil"
        ),
        "category": "Breads",
        "quantity": 30,
        "price": 3.49,
        "nutriments": {
            "energy_kcal": 70,
            "proteins": 4.0,
            "fat": 1.0,
            "carbohydrates": 13.0,
            "fiber": 2.0,
            "sugars": 2.0,
        },
        "image_url": "",
    },
    {
        "id": 3,
        "product_name": "Greek Yogurt",
        "brands": "Chobani",
        "barcode": "818290011242",
        "ingredients_text": (
            "Cultured nonfat milk, cane sugar, water, fruit pectin, "
            "locust bean gum, natural flavors"
        ),
        "category": "Dairy",
        "quantity": 45,
        "price": 1.79,
        "nutriments": {
            "energy_kcal": 90,
            "proteins": 12.0,
            "fat": 0.0,
            "carbohydrates": 10.0,
            "fiber": 0.0,
            "sugars": 9.0,
        },
        "image_url": "",
    },
    {
        "id": 4,
        "product_name": "Orange Juice",
        "brands": "Tropicana",
        "barcode": "048500204528",
        "ingredients_text": "100% pure squeezed pasteurized orange juice",
        "category": "Juices",
        "quantity": 20,
        "price": 5.99,
        "nutriments": {
            "energy_kcal": 110,
            "proteins": 2.0,
            "fat": 0.0,
            "carbohydrates": 26.0,
            "fiber": 0.0,
            "sugars": 22.0,
        },
        "image_url": "",
    },
    {
        "id": 5,
        "product_name": "Sparkling Water",
        "brands": "LaCroix",
        "barcode": "096619872046",
        "ingredients_text": "Carbonated water, natural flavor",
        "category": "Water",
        "quantity": 100,
        "price": 5.49,
        "nutriments": {
            "energy_kcal": 0,
            "proteins": 0.0,
            "fat": 0.0,
            "carbohydrates": 0.0,
            "fiber": 0.0,
            "sugars": 0.0,
        },
        "image_url": "",
    },
]

# Live inventory list — mutated by CRUD operations
inventory = copy.deepcopy(_INITIAL_INVENTORY)

# Auto-incrementing ID counter
_id_counter = {"value": len(_INITIAL_INVENTORY) + 1}


def get_next_id():
    """Return the next available unique ID and increment the counter."""
    current = _id_counter["value"]
    _id_counter["value"] += 1
    return current


def reset_database():
    """Reset inventory to the initial seed data. Intended for use in tests."""
    inventory.clear()
    inventory.extend(copy.deepcopy(_INITIAL_INVENTORY))
    _id_counter["value"] = len(_INITIAL_INVENTORY) + 1
