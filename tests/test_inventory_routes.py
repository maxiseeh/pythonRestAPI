"""
Unit tests for inventory CRUD API endpoints.

Covers: GET all, GET single, POST, PATCH, DELETE.
"""
import json
import pytest


# ─────────────────────────────────────────────────────────────────────────────
# GET /inventory
# ─────────────────────────────────────────────────────────────────────────────

class TestGetAllInventory:
    def test_returns_200(self, client):
        response = client.get("/inventory")
        assert response.status_code == 200

    def test_returns_list(self, client):
        data = json.loads(client.get("/inventory").data)
        assert isinstance(data, list)

    def test_returns_seeded_items(self, client):
        data = json.loads(client.get("/inventory").data)
        assert len(data) == 5  # five seed items

    def test_items_have_required_fields(self, client):
        data = json.loads(client.get("/inventory").data)
        for item in data:
            for field in ("id", "product_name", "quantity", "price"):
                assert field in item, f"Field '{field}' missing from item"

    def test_trailing_slash_also_works(self, client):
        response = client.get("/inventory/")
        assert response.status_code == 200


# ─────────────────────────────────────────────────────────────────────────────
# GET /inventory/<id>
# ─────────────────────────────────────────────────────────────────────────────

class TestGetSingleItem:
    def test_returns_200_for_existing_item(self, client):
        assert client.get("/inventory/1").status_code == 200

    def test_returns_correct_item(self, client):
        data = json.loads(client.get("/inventory/1").data)
        assert data["id"] == 1
        assert data["product_name"] == "Organic Almond Milk"

    def test_returns_404_for_missing_item(self, client):
        assert client.get("/inventory/9999").status_code == 404

    def test_error_body_on_missing_item(self, client):
        data = json.loads(client.get("/inventory/9999").data)
        assert "error" in data

    def test_returns_404_for_non_integer_id(self, client):
        # Flask itself returns 404 when the converter type doesn't match
        assert client.get("/inventory/abc").status_code == 404


# ─────────────────────────────────────────────────────────────────────────────
# POST /inventory
# ─────────────────────────────────────────────────────────────────────────────

class TestAddInventoryItem:
    _valid_payload = {"product_name": "Test Product", "quantity": 10, "price": 2.99}

    def test_returns_201_on_success(self, client):
        response = client.post("/inventory", json=self._valid_payload)
        assert response.status_code == 201

    def test_response_contains_new_item(self, client):
        data = json.loads(client.post("/inventory", json=self._valid_payload).data)
        assert data["product_name"] == "Test Product"
        assert data["quantity"] == 10
        assert data["price"] == 2.99

    def test_new_item_is_assigned_an_id(self, client):
        data = json.loads(client.post("/inventory", json=self._valid_payload).data)
        assert "id" in data
        assert isinstance(data["id"], int)

    def test_item_appears_in_get_all(self, client):
        client.post("/inventory", json=self._valid_payload)
        all_items = json.loads(client.get("/inventory").data)
        assert any(i["product_name"] == "Test Product" for i in all_items)

    def test_returns_400_when_body_missing(self, client):
        assert client.post("/inventory").status_code == 400

    def test_returns_400_for_missing_product_name(self, client):
        response = client.post("/inventory", json={"quantity": 5, "price": 1.0})
        assert response.status_code == 400

    def test_returns_400_for_missing_quantity(self, client):
        response = client.post("/inventory", json={"product_name": "X", "price": 1.0})
        assert response.status_code == 400

    def test_returns_400_for_missing_price(self, client):
        response = client.post("/inventory", json={"product_name": "X", "quantity": 1})
        assert response.status_code == 400

    def test_returns_400_for_negative_quantity(self, client):
        payload = {**self._valid_payload, "quantity": -1}
        assert client.post("/inventory", json=payload).status_code == 400

    def test_returns_400_for_negative_price(self, client):
        payload = {**self._valid_payload, "price": -0.01}
        assert client.post("/inventory", json=payload).status_code == 400

    def test_returns_400_for_non_numeric_price(self, client):
        payload = {**self._valid_payload, "price": "not_a_number"}
        assert client.post("/inventory", json=payload).status_code == 400

    def test_optional_fields_default_to_empty(self, client):
        data = json.loads(client.post("/inventory", json=self._valid_payload).data)
        assert data.get("brands") == ""
        assert data.get("barcode") == ""


# ─────────────────────────────────────────────────────────────────────────────
# PATCH /inventory/<id>
# ─────────────────────────────────────────────────────────────────────────────

class TestUpdateInventoryItem:
    def test_returns_200_on_success(self, client):
        assert client.patch("/inventory/1", json={"quantity": 99}).status_code == 200

    def test_quantity_is_updated(self, client):
        data = json.loads(client.patch("/inventory/1", json={"quantity": 99}).data)
        assert data["quantity"] == 99

    def test_price_is_updated(self, client):
        data = json.loads(client.patch("/inventory/1", json={"price": 9.99}).data)
        assert data["price"] == 9.99

    def test_product_name_is_updated(self, client):
        data = json.loads(client.patch("/inventory/1", json={"product_name": "New Name"}).data)
        assert data["product_name"] == "New Name"

    def test_id_cannot_be_changed(self, client):
        data = json.loads(client.patch("/inventory/1", json={"id": 999}).data)
        assert data["id"] == 1

    def test_update_persists_in_get(self, client):
        client.patch("/inventory/1", json={"quantity": 77})
        data = json.loads(client.get("/inventory/1").data)
        assert data["quantity"] == 77

    def test_returns_404_for_missing_item(self, client):
        assert client.patch("/inventory/9999", json={"quantity": 1}).status_code == 404

    def test_returns_400_when_body_missing(self, client):
        assert client.patch("/inventory/1").status_code == 400

    def test_returns_400_for_negative_quantity(self, client):
        assert client.patch("/inventory/1", json={"quantity": -5}).status_code == 400

    def test_returns_400_for_negative_price(self, client):
        assert client.patch("/inventory/1", json={"price": -1.0}).status_code == 400


# ─────────────────────────────────────────────────────────────────────────────
# DELETE /inventory/<id>
# ─────────────────────────────────────────────────────────────────────────────

class TestDeleteInventoryItem:
    def test_returns_200_on_success(self, client):
        assert client.delete("/inventory/1").status_code == 200

    def test_response_contains_message(self, client):
        data = json.loads(client.delete("/inventory/1").data)
        assert "message" in data

    def test_item_no_longer_in_inventory(self, client):
        client.delete("/inventory/1")
        assert client.get("/inventory/1").status_code == 404

    def test_inventory_count_decreases(self, client):
        before = len(json.loads(client.get("/inventory").data))
        client.delete("/inventory/1")
        after = len(json.loads(client.get("/inventory").data))
        assert after == before - 1

    def test_returns_404_for_missing_item(self, client):
        assert client.delete("/inventory/9999").status_code == 404

    def test_error_body_on_missing_item(self, client):
        data = json.loads(client.delete("/inventory/9999").data)
        assert "error" in data
