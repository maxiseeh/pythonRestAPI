#!/usr/bin/env python3
"""
CLI interface for the Inventory Management System.

Requires the Flask server to be running at http://localhost:5000.
Start the server with: python run.py
"""

import sys
import requests

BASE_URL = "http://localhost:5000"
HEADERS = {"Content-Type": "application/json"}


# ─────────────────────────────────────────────────────────────────────────────
# Low-level HTTP helpers
# ─────────────────────────────────────────────────────────────────────────────

def api_get(endpoint):
    """Perform a GET request and return (data, status_code)."""
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
        return response.json(), response.status_code
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to server. Is the Flask server running?"}, 503
    except requests.exceptions.RequestException as exc:
        return {"error": str(exc)}, 500


def api_post(endpoint, payload):
    """Perform a POST request and return (data, status_code)."""
    try:
        response = requests.post(
            f"{BASE_URL}{endpoint}", headers=HEADERS, json=payload, timeout=10
        )
        return response.json(), response.status_code
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to server. Is the Flask server running?"}, 503
    except requests.exceptions.RequestException as exc:
        return {"error": str(exc)}, 500


def api_patch(endpoint, payload):
    """Perform a PATCH request and return (data, status_code)."""
    try:
        response = requests.patch(
            f"{BASE_URL}{endpoint}", headers=HEADERS, json=payload, timeout=10
        )
        return response.json(), response.status_code
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to server. Is the Flask server running?"}, 503
    except requests.exceptions.RequestException as exc:
        return {"error": str(exc)}, 500


def api_delete(endpoint):
    """Perform a DELETE request and return (data, status_code)."""
    try:
        response = requests.delete(f"{BASE_URL}{endpoint}", timeout=10)
        return response.json(), response.status_code
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to server. Is the Flask server running?"}, 503
    except requests.exceptions.RequestException as exc:
        return {"error": str(exc)}, 500


# ─────────────────────────────────────────────────────────────────────────────
# Display helpers
# ─────────────────────────────────────────────────────────────────────────────

def _sep(char="-", width=72):
    print(char * width)


def _print_item(item):
    print(f"\n  ID:           {item.get('id')}")
    print(f"  Product:      {item.get('product_name')}")
    print(f"  Brand:        {item.get('brands') or 'N/A'}")
    print(f"  Barcode:      {item.get('barcode') or 'N/A'}")
    print(f"  Category:     {item.get('category') or 'N/A'}")
    print(f"  Quantity:     {item.get('quantity')} units")
    print(f"  Price:        ${item.get('price', 0):.2f}")
    ing = item.get("ingredients_text", "")
    if ing:
        print(f"  Ingredients:  {ing[:67] + '...' if len(ing) > 67 else ing}")
    nut = item.get("nutriments", {})
    if nut:
        print(
            f"  Nutrition:    {nut.get('energy_kcal', 0)} kcal | "
            f"Protein {nut.get('proteins', 0)}g | "
            f"Fat {nut.get('fat', 0)}g | "
            f"Carbs {nut.get('carbohydrates', 0)}g"
        )


def _print_table(items):
    print(
        f"\n  {'ID':<5} {'Product Name':<26} {'Brand':<18} "
        f"{'Category':<15} {'Qty':<6} {'Price':>7}"
    )
    _sep()
    for item in items:
        print(
            f"  {item.get('id'):<5} "
            f"{str(item.get('product_name', ''))[:25]:<26} "
            f"{str(item.get('brands', ''))[:17]:<18} "
            f"{str(item.get('category', ''))[:14]:<15} "
            f"{item.get('quantity', 0):<6} "
            f"${item.get('price', 0):>6.2f}"
        )


def _print_api_product(product):
    print(f"  Product:      {product.get('product_name', 'N/A')}")
    print(f"  Brand:        {product.get('brands') or 'N/A'}")
    print(f"  Barcode:      {product.get('barcode') or 'N/A'}")
    print(f"  Category:     {product.get('category') or 'N/A'}")
    ing = product.get("ingredients_text", "")
    print(f"  Ingredients:  {ing[:67] + '...' if len(ing) > 67 else ing or 'N/A'}")


# ─────────────────────────────────────────────────────────────────────────────
# Feature functions
# ─────────────────────────────────────────────────────────────────────────────

def view_all_inventory():
    """Fetch and display all inventory items in a table."""
    print("\n  Fetching all inventory items...\n")
    data, status = api_get("/inventory")
    if "error" in data:
        print(f"  Error: {data['error']}")
        return
    if not data:
        print("  Inventory is empty.")
        return
    print(f"  Total items: {len(data)}")
    _print_table(data)


def view_single_item():
    """Fetch and display a single inventory item by ID."""
    item_id = input("\n  Enter item ID: ").strip()
    if not item_id.isdigit():
        print("  Invalid ID. Please enter a positive integer.")
        return
    data, status = api_get(f"/inventory/{item_id}")
    if "error" in data:
        print(f"  Error: {data['error']}")
        return
    _sep()
    _print_item(data)


def add_item_manually():
    """Prompt the user for item details and POST to inventory."""
    print("\n  Add New Inventory Item  (* = required, Enter to skip optional fields)")
    _sep()

    product_name = input("  Product Name *: ").strip()
    if not product_name:
        print("  Error: product name is required.")
        return

    brands = input("  Brand: ").strip()
    barcode = input("  Barcode: ").strip()
    category = input("  Category: ").strip()
    ingredients = input("  Ingredients: ").strip()

    quantity_raw = input("  Quantity *: ").strip()
    if not quantity_raw.isdigit() or int(quantity_raw) < 0:
        print("  Error: quantity must be a non-negative integer.")
        return

    price_raw = input("  Price * (e.g. 4.99): ").strip()
    try:
        price = float(price_raw)
        if price < 0:
            raise ValueError
    except ValueError:
        print("  Error: price must be a non-negative number.")
        return

    payload = {
        "product_name": product_name,
        "brands": brands,
        "barcode": barcode,
        "category": category,
        "ingredients_text": ingredients,
        "quantity": int(quantity_raw),
        "price": price,
    }

    data, status = api_post("/inventory", payload)
    if status == 201:
        print(f"\n  Item added successfully! (ID: {data.get('id')})")
        _print_item(data)
    else:
        print(f"  Error: {data.get('error', 'Unknown error')}")


def update_item():
    """Partially update an inventory item (quantity, price, name, brand)."""
    item_id = input("\n  Enter item ID to update: ").strip()
    if not item_id.isdigit():
        print("  Invalid ID. Please enter a positive integer.")
        return

    data, status = api_get(f"/inventory/{item_id}")
    if "error" in data:
        print(f"  Error: {data['error']}")
        return

    print(f"\n  Updating: {data.get('product_name')} (ID: {item_id})")
    print("  Leave a field blank to keep its current value.\n")

    updates = {}

    new_qty = input(f"  New Quantity [{data.get('quantity')}]: ").strip()
    if new_qty:
        if not new_qty.isdigit() or int(new_qty) < 0:
            print("  Error: quantity must be a non-negative integer.")
            return
        updates["quantity"] = int(new_qty)

    new_price = input(f"  New Price [${data.get('price', 0):.2f}]: ").strip()
    if new_price:
        try:
            new_price_f = float(new_price)
            if new_price_f < 0:
                raise ValueError
            updates["price"] = new_price_f
        except ValueError:
            print("  Error: price must be a non-negative number.")
            return

    new_name = input(f"  New Product Name [{data.get('product_name')}]: ").strip()
    if new_name:
        updates["product_name"] = new_name

    new_brand = input(f"  New Brand [{data.get('brands', '')}]: ").strip()
    if new_brand:
        updates["brands"] = new_brand

    if not updates:
        print("  No changes made.")
        return

    result, status = api_patch(f"/inventory/{item_id}", updates)
    if status == 200:
        print("\n  Item updated successfully!")
        _print_item(result)
    else:
        print(f"  Error: {result.get('error', 'Unknown error')}")


def delete_item():
    """Delete an inventory item after confirmation."""
    item_id = input("\n  Enter item ID to delete: ").strip()
    if not item_id.isdigit():
        print("  Invalid ID. Please enter a positive integer.")
        return

    data, status = api_get(f"/inventory/{item_id}")
    if "error" in data:
        print(f"  Error: {data['error']}")
        return

    print(f"\n  About to delete: {data.get('product_name')} (ID: {item_id})")
    confirm = input("  Are you sure? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("  Deletion cancelled.")
        return

    result, status = api_delete(f"/inventory/{item_id}")
    if status == 200:
        print(f"\n  {result.get('message', 'Item deleted.')}")
    else:
        print(f"  Error: {result.get('error', 'Unknown error')}")


def search_and_add_from_api():
    """Search OpenFoodFacts by barcode or name, then optionally add to inventory."""
    print("\n  Search OpenFoodFacts API")
    print("  1. Search by Barcode")
    print("  2. Search by Product Name")

    choice = input("\n  Select search method: ").strip()
    product_data = None

    if choice == "1":
        barcode = input("  Enter barcode: ").strip()
        if not barcode:
            print("  Error: barcode cannot be empty.")
            return
        print(f"\n  Searching for barcode: {barcode}...")
        data, status = api_get(f"/inventory/search/barcode/{barcode}")
        if "error" in data:
            print(f"  Error: {data['error']}")
            return
        product_data = data
        print("\n  Found product:")
        _sep()
        _print_api_product(product_data)

    elif choice == "2":
        name = input("  Enter product name: ").strip()
        if not name:
            print("  Error: product name cannot be empty.")
            return
        print(f"\n  Searching for '{name}'...")
        data, status = api_get(f"/inventory/search/name/{name}")
        if "error" in data:
            print(f"  Error: {data['error']}")
            return
        if not data:
            print("  No products found.")
            return
        print(f"\n  Found {len(data)} product(s):\n")
        for i, product in enumerate(data, 1):
            print(
                f"  {i:>2}. {product.get('product_name', 'Unknown')}"
                f"  —  {product.get('brands', 'N/A')}"
            )
        pick = input("\n  Select product number to add (0 to cancel): ").strip()
        if not pick.isdigit() or int(pick) == 0 or int(pick) > len(data):
            print("  Cancelled.")
            return
        product_data = data[int(pick) - 1]
        print("\n  Selected product:")
        _sep()
        _print_api_product(product_data)

    else:
        print("  Invalid option.")
        return

    add = input("\n  Add this product to inventory? (yes/no): ").strip().lower()
    if add != "yes":
        print("  Product not added.")
        return

    quantity_raw = input("  Enter quantity to stock: ").strip()
    if not quantity_raw.isdigit() or int(quantity_raw) < 0:
        print("  Error: invalid quantity.")
        return

    price_raw = input("  Enter price: ").strip()
    try:
        price = float(price_raw)
        if price < 0:
            raise ValueError
    except ValueError:
        print("  Error: invalid price.")
        return

    payload = {
        "product_name": product_data.get("product_name", "Unknown"),
        "brands": product_data.get("brands", ""),
        "barcode": product_data.get("barcode", ""),
        "category": product_data.get("category", ""),
        "ingredients_text": product_data.get("ingredients_text", ""),
        "nutriments": product_data.get("nutriments", {}),
        "image_url": product_data.get("image_url", ""),
        "quantity": int(quantity_raw),
        "price": price,
    }

    result, status = api_post("/inventory", payload)
    if status == 201:
        print(f"\n  Product added to inventory! (ID: {result.get('id')})")
    else:
        print(f"  Error: {result.get('error', 'Unknown error')}")


# ─────────────────────────────────────────────────────────────────────────────
# Main menu
# ─────────────────────────────────────────────────────────────────────────────

MENU = """
+------------------------------------------+
|   Inventory Management System — CLI       |
+------------------------------------------+
|  1. View all inventory                   |
|  2. View single item                     |
|  3. Add new item (manual entry)          |
|  4. Update item                          |
|  5. Delete item                          |
|  6. Search & add from OpenFoodFacts      |
|  0. Exit                                 |
+------------------------------------------+
"""

ACTIONS = {
    "1": view_all_inventory,
    "2": view_single_item,
    "3": add_item_manually,
    "4": update_item,
    "5": delete_item,
    "6": search_and_add_from_api,
}


def main():
    print("\n  Welcome to the Inventory Management System!")
    print("  Ensure the Flask server is running: python run.py\n")

    while True:
        print(MENU)
        choice = input("  Select an option: ").strip()

        if choice == "0":
            print("\n  Goodbye!\n")
            sys.exit(0)

        action = ACTIONS.get(choice)
        if action:
            action()
        else:
            print("  Invalid option. Please choose from the menu.")

        input("\n  Press Enter to continue...")


if __name__ == "__main__":
    main()
