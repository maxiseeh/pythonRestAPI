"""
Inventory REST API routes.

Endpoints:
    GET    /inventory             — Fetch all items
    GET    /inventory/<id>        — Fetch a single item
    POST   /inventory             — Add a new item
    PATCH  /inventory/<id>        — Update an item
    DELETE /inventory/<id>        — Remove an item
    GET    /inventory/search/barcode/<barcode> — Search OpenFoodFacts by barcode
    GET    /inventory/search/name/<name>       — Search OpenFoodFacts by name
"""
from flask import Blueprint, request, jsonify
from server.data.database import inventory, get_next_id
from server.services.openfoodfacts import fetch_product_by_barcode, fetch_product_by_name

inventory_bp = Blueprint("inventory", __name__, url_prefix="/inventory")

# Fields that must be present when creating a new item
REQUIRED_FIELDS = ["product_name", "quantity", "price"]


# ─────────────────────────────────────────────────────────────────────────────
# GET /inventory
# ─────────────────────────────────────────────────────────────────────────────
@inventory_bp.route("", methods=["GET"], strict_slashes=False)
def get_all_inventory():
    """Return all inventory items."""
    return jsonify(inventory), 200


# ─────────────────────────────────────────────────────────────────────────────
# GET /inventory/<id>
# ─────────────────────────────────────────────────────────────────────────────
@inventory_bp.route("/<int:item_id>", methods=["GET"])
def get_inventory_item(item_id):
    """Return a single inventory item by ID."""
    item = next((i for i in inventory if i["id"] == item_id), None)
    if not item:
        return jsonify({"error": f"Item with ID {item_id} not found"}), 404
    return jsonify(item), 200


# ─────────────────────────────────────────────────────────────────────────────
# POST /inventory
# ─────────────────────────────────────────────────────────────────────────────
@inventory_bp.route("", methods=["POST"], strict_slashes=False)
def add_inventory_item():
    """Add a new item to inventory."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    missing = [f for f in REQUIRED_FIELDS if f not in data]
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    # Validate types
    try:
        quantity = int(data["quantity"])
        price = float(data["price"])
        if quantity < 0 or price < 0:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify(
            {"error": "quantity must be a non-negative integer and price must be a non-negative number"}
        ), 400

    new_item = {
        "id": get_next_id(),
        "product_name": data["product_name"],
        "brands": data.get("brands", ""),
        "barcode": data.get("barcode", ""),
        "ingredients_text": data.get("ingredients_text", ""),
        "category": data.get("category", ""),
        "quantity": quantity,
        "price": price,
        "nutriments": data.get("nutriments", {}),
        "image_url": data.get("image_url", ""),
    }
    inventory.append(new_item)
    return jsonify(new_item), 201


# ─────────────────────────────────────────────────────────────────────────────
# PATCH /inventory/<id>
# ─────────────────────────────────────────────────────────────────────────────
@inventory_bp.route("/<int:item_id>", methods=["PATCH"])
def update_inventory_item(item_id):
    """Partially update an existing inventory item."""
    item = next((i for i in inventory if i["id"] == item_id), None)
    if not item:
        return jsonify({"error": f"Item with ID {item_id} not found"}), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    # Validate numeric fields if provided
    if "quantity" in data:
        try:
            data["quantity"] = int(data["quantity"])
            if data["quantity"] < 0:
                raise ValueError
        except (ValueError, TypeError):
            return jsonify({"error": "quantity must be a non-negative integer"}), 400

    if "price" in data:
        try:
            data["price"] = float(data["price"])
            if data["price"] < 0:
                raise ValueError
        except (ValueError, TypeError):
            return jsonify({"error": "price must be a non-negative number"}), 400

    # Apply updates — ID cannot be changed
    for key, value in data.items():
        if key != "id":
            item[key] = value

    return jsonify(item), 200


# ─────────────────────────────────────────────────────────────────────────────
# DELETE /inventory/<id>
# ─────────────────────────────────────────────────────────────────────────────
@inventory_bp.route("/<int:item_id>", methods=["DELETE"])
def delete_inventory_item(item_id):
    """Remove an item from inventory."""
    item = next((i for i in inventory if i["id"] == item_id), None)
    if not item:
        return jsonify({"error": f"Item with ID {item_id} not found"}), 404

    inventory.remove(item)
    return jsonify(
        {"message": f"Item '{item['product_name']}' (ID: {item_id}) deleted successfully"}
    ), 200


# ─────────────────────────────────────────────────────────────────────────────
# GET /inventory/search/barcode/<barcode>
# ─────────────────────────────────────────────────────────────────────────────
@inventory_bp.route("/search/barcode/<barcode>", methods=["GET"])
def search_by_barcode(barcode):
    """Fetch product details from OpenFoodFacts by barcode."""
    try:
        product = fetch_product_by_barcode(barcode)
        if not product:
            return jsonify({"error": f"No product found for barcode: {barcode}"}), 404
        return jsonify(product), 200
    except ConnectionError as e:
        return jsonify({"error": str(e)}), 503


# ─────────────────────────────────────────────────────────────────────────────
# GET /inventory/search/name/<name>
# ─────────────────────────────────────────────────────────────────────────────
@inventory_bp.route("/search/name/<path:name>", methods=["GET"])
def search_by_name(name):
    """Search OpenFoodFacts for products by name."""
    try:
        products = fetch_product_by_name(name)
        return jsonify(products), 200
    except ConnectionError as e:
        return jsonify({"error": str(e)}), 503
