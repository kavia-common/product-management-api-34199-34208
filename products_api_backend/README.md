# Product Management API (Flask)

A simple Flask REST API that provides CRUD operations on products with fields:
- id (auto-increment)
- name (string)
- price (float >= 0)
- quantity (integer >= 0)

The service exposes OpenAPI documentation via flask-smorest at /docs and runs on port 3001.

## Quick start

1) Install dependencies (Python 3.10+ recommended):
```
pip install -r requirements.txt
```

2) (Optional) Create a .env to configure DB path:
```
cp .env.example .env
# Edit DB_PATH if needed
```

3) Run the server:
```
python run.py
```

The API will be available at:
- OpenAPI UI: http://localhost:3001/docs
- OpenAPI JSON: http://localhost:3001/openapi.json
- Health: http://localhost:3001/

On first run, the SQLite DB is initialized automatically.

## Environment variables

- DB_PATH: Filesystem path to the SQLite database. Defaults to `instance/products.db` if not set.
- PORT: Informational. The app binds to 0.0.0.0:3001 via run.py.

## Routes organization

- Health blueprint: `app/routes/health.py` exports `blp`
- Products blueprint: `app/routes/products.py` exports `blp`
- Both are registered in `app/__init__.py` via flask-smorest Api.

## Endpoints

- GET `/` — Health check
- GET `/products` — List all products
- POST `/products` — Create a product
  - Body: `{ "name": "Widget", "price": 19.99, "quantity": 5 }`
- GET `/products/<id>` — Get product by id
- PUT `/products/<id>` — Update product (partial or full)
  - Body: Any of `name`, `price`, `quantity`
- DELETE `/products/<id>` — Delete product
- GET `/products/balance` — Get total inventory value (sum of price * quantity)

## Request/Response Schemas

- ProductCreate: `{ name: string, price: number>=0, quantity: integer>=0 }`
- ProductUpdate: Partial of ProductCreate
- Product: `{ id: integer, name: string, price: number, quantity: integer }`

Validation and error handling are performed via marshmallow and flask-smorest; typical errors:
- 400 for invalid input
- 404 when a product id is not found

### Example: Total inventory value
Request:
```
GET http://localhost:3001/products/balance
```

Response:
```
Status: 200 OK
Body: { "total_balance": 199.9 }
```

## Lightweight persistence

The API uses SQLite as a lightweight persistent store. The database is initialized on app startup if not present. No migrations are required; the schema is created with `CREATE TABLE IF NOT EXISTS`.

## Notes

- CORS is enabled for all origins.
- OpenAPI docs served under `/docs`.
