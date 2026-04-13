from flask import Blueprint, request, jsonify
from server.data.database import inventory, get_next_id
from server.services.openfoodfacts import fetch_product_by_barcode, fetch_product_by_name

inventory_bp = Blueprint("inventory", __name__, url_prefix="/inventory")


# GET /inventory - return all items
@inventory_bp.route("", methods=["GET"], strict_slashes=False)
def get_all_inventory():
    return jsonify(inventory), 200


# GET /inventory/<id> - return one item by id
@inventory_bp.route("/<int:item_id>", methods=["GET"])
def get_inventory_item(item_id):
    item = None
    for i in inventory:
        if i["id"] == item_id:
            item = i
            break

    if item is None:
        return jsonify({"error": f"Item with ID {item_id} not found"}), 404

    return jsonify(item), 200


# POST /inventory - add a new item
@inventory_bp.route("", methods=["POST"], strict_slashes=False)
def add_inventory_item():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    # check required fields
    required = ["product_name", "quantity", "price"]
    missing = []
    for field in required:
        if field not in data:
            missing.append(field)

    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    # validate quantity and price
    try:
        quantity = int(data["quantity"])
        price = float(data["price"])
        if quantity < 0 or price < 0:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({"error": "quantity must be a non-negative integer and price must be a non-negative number"}), 400

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
        "image_url": data.get("image_url", "")
    }

    inventory.append(new_item)
    return jsonify(new_item), 201


# PATCH /inventory/<id> - update an existing item
@inventory_bp.route("/<int:item_id>", methods=["PATCH"])
def update_inventory_item(item_id):
    item = None
    for i in inventory:
        if i["id"] == item_id:
            item = i
            break

    if item is None:
        return jsonify({"error": f"Item with ID {item_id} not found"}), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be valid JSON"}), 400

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

    for key, value in data.items():
        if key != "id":
            item[key] = value

    return jsonify(item), 200


# DELETE /inventory/<id> - remove an item
@inventory_bp.route("/<int:item_id>", methods=["DELETE"])
def delete_inventory_item(item_id):
    item = None
    for i in inventory:
        if i["id"] == item_id:
            item = i
            break

    if item is None:
        return jsonify({"error": f"Item with ID {item_id} not found"}), 404

    inventory.remove(item)
    return jsonify({"message": f"Item '{item['product_name']}' (ID: {item_id}) deleted successfully"}), 200


# GET /inventory/search/barcode/<barcode> - search OpenFoodFacts by barcode
@inventory_bp.route("/search/barcode/<barcode>", methods=["GET"])
def search_by_barcode(barcode):
    try:
        product = fetch_product_by_barcode(barcode)
        if not product:
            return jsonify({"error": f"No product found for barcode: {barcode}"}), 404
        return jsonify(product), 200
    except ConnectionError as e:
        return jsonify({"error": str(e)}), 503


# GET /inventory/search/name/<name> - search OpenFoodFacts by name
@inventory_bp.route("/search/name/<path:name>", methods=["GET"])
def search_by_name(name):
    try:
        products = fetch_product_by_name(name)
        return jsonify(products), 200
    except ConnectionError as e:
        return jsonify({"error": str(e)}), 503
