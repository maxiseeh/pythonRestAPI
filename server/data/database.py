import copy

# This is our fake database stored in memory as a list
# Each item has an id and product info similar to OpenFoodFacts
inventory = [
    {
        "id": 1,
        "product_name": "Organic Almond Milk",
        "brands": "Silk",
        "barcode": "025293003628",
        "ingredients_text": "Filtered water, almonds, cane sugar, sea salt, sunflower lecithin, locust bean gum, gellan gum",
        "category": "Plant-based milks",
        "quantity": 50,
        "price": 4.99,
        "nutriments": {
            "energy_kcal": 30,
            "proteins": 1.0,
            "fat": 2.5,
            "carbohydrates": 1.0,
            "fiber": 0.0,
            "sugars": 0.0
        },
        "image_url": ""
    },
    {
        "id": 2,
        "product_name": "Whole Grain Bread",
        "brands": "Nature's Own",
        "barcode": "040000487579",
        "ingredients_text": "Whole grain wheat flour, water, yeast, sugar, salt, soybean oil",
        "category": "Breads",
        "quantity": 30,
        "price": 3.49,
        "nutriments": {
            "energy_kcal": 70,
            "proteins": 4.0,
            "fat": 1.0,
            "carbohydrates": 13.0,
            "fiber": 2.0,
            "sugars": 2.0
        },
        "image_url": ""
    },
    {
        "id": 3,
        "product_name": "Greek Yogurt",
        "brands": "Chobani",
        "barcode": "818290011242",
        "ingredients_text": "Cultured nonfat milk, cane sugar, water, fruit pectin, locust bean gum, natural flavors",
        "category": "Dairy",
        "quantity": 45,
        "price": 1.79,
        "nutriments": {
            "energy_kcal": 90,
            "proteins": 12.0,
            "fat": 0.0,
            "carbohydrates": 10.0,
            "fiber": 0.0,
            "sugars": 9.0
        },
        "image_url": ""
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
            "sugars": 22.0
        },
        "image_url": ""
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
            "sugars": 0.0
        },
        "image_url": ""
    }
]

# keep a copy of the original data so we can reset during tests
_original_inventory = copy.deepcopy(inventory)

# track the next id to use
next_id = len(inventory) + 1


def get_next_id():
    global next_id
    id_to_use = next_id
    next_id += 1
    return id_to_use


def reset_database():
    global next_id
    inventory.clear()
    inventory.extend(copy.deepcopy(_original_inventory))
    next_id = len(_original_inventory) + 1
