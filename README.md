# Inventory Management System — Flask REST API

A Flask-based REST API with CRUD operations, OpenFoodFacts integration, a CLI frontend, and a pytest test suite.

---

## Project Structure

```
pythonRestAPI/
├── server/
│   ├── app.py                  # Flask app factory
│   ├── data/
│   │   └── database.py         # In-memory mock database (seed data)
│   ├── routes/
│   │   └── inventory.py        # All inventory API endpoints
│   └── services/
│       └── openfoodfacts.py    # OpenFoodFacts API integration
├── cli/
│   └── main.py                 # Interactive CLI tool
├── tests/
│   ├── conftest.py             # Shared pytest fixtures
│   ├── test_inventory_routes.py
│   ├── test_openfoodfacts.py
│   └── test_cli.py
├── run.py                      # Development server entry point
├── Pipfile
├── requirements.txt
└── README.md
```

---

## Installation & Setup

### Prerequisites
- Python 3.9+
- `pipenv` (`pip install pipenv`)

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd pythonRestAPI
```

### 2. Install dependencies
```bash
pipenv install --dev
```

### 3. Activate the virtual environment
```bash
pipenv shell
```

---

## Running the API Server

```bash
python run.py
```

The server starts at **http://localhost:5000** with Flask debug mode enabled.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/inventory` | Fetch all inventory items |
| `GET` | `/inventory/<id>` | Fetch a single item by ID |
| `POST` | `/inventory` | Add a new inventory item |
| `PATCH` | `/inventory/<id>` | Update an existing item |
| `DELETE` | `/inventory/<id>` | Remove an item |
| `GET` | `/inventory/search/barcode/<barcode>` | Search OpenFoodFacts by barcode |
| `GET` | `/inventory/search/name/<name>` | Search OpenFoodFacts by product name |

### Request / Response Examples

#### GET /inventory
```json
[
  {
    "id": 1,
    "product_name": "Organic Almond Milk",
    "brands": "Silk",
    "barcode": "025293003628",
    "category": "Plant-based milks",
    "quantity": 50,
    "price": 4.99,
    "ingredients_text": "Filtered water, almonds, ...",
    "nutriments": { "energy_kcal": 30, "proteins": 1.0, ... },
    "image_url": ""
  }
]
```

#### POST /inventory — Required fields
```json
{
  "product_name": "Granola Bar",
  "quantity": 25,
  "price": 1.49,
  "brands": "Kind",
  "barcode": "602652179512",
  "category": "Snacks"
}
```

#### PATCH /inventory/1
```json
{ "quantity": 30, "price": 3.99 }
```

---

## CLI Tool

Start the Flask server first, then in a separate terminal run:

```bash
python cli/main.py
```

### Available Commands

| Option | Action |
|--------|--------|
| `1` | View all inventory items |
| `2` | View a single item by ID |
| `3` | Add a new item (manual entry) |
| `4` | Update item quantity, price, name or brand |
| `5` | Delete an item (with confirmation) |
| `6` | Search OpenFoodFacts by barcode or name and optionally add to inventory |
| `0` | Exit |

### Example CLI Session

```
  Select an option: 6

  Search OpenFoodFacts API
  1. Search by Barcode
  2. Search by Product Name

  Select search method: 1
  Enter barcode: 025293003628

  Searching for barcode: 025293003628...

  Found product:
  Product:      Organic Almond Milk
  Brand:        Silk
  Barcode:      025293003628
  Category:     Plant-based milks

  Add this product to inventory? (yes/no): yes
  Enter quantity to stock: 40
  Enter price: 4.99

  Product added to inventory! (ID: 6)
```

---

## Running Tests

```bash
# Run all tests
pipenv run pytest

# Run with verbose output
pipenv run pytest -v

# Run a specific test file
pipenv run pytest tests/test_inventory_routes.py -v
```

### Test Coverage

| File | What is tested |
|------|----------------|
| `test_inventory_routes.py` | All CRUD endpoints (GET, POST, PATCH, DELETE), validation, edge cases |
| `test_openfoodfacts.py` | Barcode/name search, response parsing, timeout & network error handling |
| `test_cli.py` | All CLI functions with mocked HTTP calls and user inputs |

---

## External API — OpenFoodFacts

- **Base URL:** `https://world.openfoodfacts.org`
- **Barcode lookup:** `GET /api/v2/product/<barcode>`
- **Name search:** `GET /cgi/search.pl?search_terms=<name>&json=1`
- No API key required.
- Docs: https://world.openfoodfacts.org/data

---

## Git Workflow

```bash
# Create a feature branch
git checkout -b feature/add-search-endpoint

# After making changes
git add .
git commit -m "feat: add barcode search endpoint"
git push origin feature/add-search-endpoint

# Open a pull request, merge, then delete the branch
git checkout main
git merge feature/add-search-endpoint
git branch -d feature/add-search-endpoint
```
