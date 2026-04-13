# Inventory Management System

A Flask REST API for managing store inventory with CLI and OpenFoodFacts integration.

---

## Setup

```bash
pipenv install --dev
pipenv shell
```

## Run the Server

```bash
python run.py
```

Server runs at `http://localhost:5000`

## Run the CLI

Open a second terminal and run:

```bash
python cli/main.py
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/inventory` | Get all items |
| GET | `/inventory/<id>` | Get one item |
| POST | `/inventory` | Add an item |
| PATCH | `/inventory/<id>` | Update an item |
| DELETE | `/inventory/<id>` | Delete an item |
| GET | `/inventory/search/barcode/<barcode>` | Search by barcode |
| GET | `/inventory/search/name/<name>` | Search by name |

### POST required fields
```json
{ "product_name": "Granola Bar", "quantity": 10, "price": 1.99 }
```

---

## CLI Menu

| Option | Action |
|--------|--------|
| 1 | View all inventory |
| 2 | View item by ID |
| 3 | Add new item |
| 4 | Update item |
| 5 | Delete item |
| 6 | Search OpenFoodFacts and add to inventory |
| 0 | Exit |

---

## Tests

```bash
pipenv run pytest -v
```
