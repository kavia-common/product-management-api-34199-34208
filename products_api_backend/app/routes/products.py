from flask_smorest import Blueprint, abort
from flask.views import MethodView
from marshmallow import ValidationError

from ..db import get_connection
from ..schemas import ProductCreateSchema, ProductUpdateSchema, ProductSchema
from ..schemas import BalanceSchema  # new schema for balance response

# PUBLIC_INTERFACE
blp = Blueprint(
    "Products",
    "products",
    url_prefix="/products",
    description="CRUD operations for products",
)


def _row_to_product(row) -> dict:
    """Convert a sqlite3.Row to a product dict."""
    return {
        "id": row["id"],
        "name": row["name"],
        "price": row["price"],
        "quantity": row["quantity"],
    }


@blp.route("")
class ProductsList(MethodView):
    """
    PUBLIC_INTERFACE
    get:
      summary: List all products
      description: Returns an array of products.
    post:
      summary: Create a product
      description: Creates a new product with name, price, and quantity.
    """

    @blp.response(200, ProductSchema(many=True))
    def get(self):
        """List all products."""
        with get_connection() as conn:
            cur = conn.execute("SELECT id, name, price, quantity FROM products ORDER BY id ASC")
            rows = cur.fetchall()
            return [_row_to_product(r) for r in rows]

    @blp.arguments(ProductCreateSchema)
    @blp.response(201, ProductSchema)
    def post(self, data):
        """Create a new product."""
        with get_connection() as conn:
            cur = conn.execute(
                "INSERT INTO products (name, price, quantity) VALUES (?, ?, ?)",
                (data["name"], float(data["price"]), int(data["quantity"])),
            )
            new_id = cur.lastrowid
            cur = conn.execute("SELECT id, name, price, quantity FROM products WHERE id = ?", (new_id,))
            row = cur.fetchone()
            return _row_to_product(row)


@blp.route("/balance")
class ProductsBalance(MethodView):
    """
    PUBLIC_INTERFACE
    get:
      summary: Get total inventory value
      description: Returns the total balance as sum of price * quantity across all products.
    """

    @blp.response(200, BalanceSchema)
    def get(self):
        """Calculate and return total inventory value."""
        try:
            with get_connection() as conn:
                # SUM over price * quantity; COALESCE to 0.0 when table empty
                cur = conn.execute("SELECT COALESCE(SUM(price * quantity), 0.0) AS total FROM products")
                row = cur.fetchone()
                total = float(row["total"]) if row and row["total"] is not None else 0.0
                # Ensure non-negative due to DB constraints, but clamp just in case
                if total < 0:
                    total = 0.0
                return {"total_balance": total}
        except Exception:
            # Unexpected error path: surface a 500 with safe message
            abort(500, message="Failed to compute total balance")


@blp.route("/<int:id>")
class ProductDetail(MethodView):
    """
    PUBLIC_INTERFACE
    get:
      summary: Get product by id
      description: Returns a product by its identifier.
    put:
      summary: Update product
      description: Updates an existing product with provided fields.
    delete:
      summary: Delete product
      description: Deletes a product by id.
    """

    @blp.response(200, ProductSchema)
    def get(self, id: int):
        """Get a product by id."""
        with get_connection() as conn:
            cur = conn.execute("SELECT id, name, price, quantity FROM products WHERE id = ?", (id,))
            row = cur.fetchone()
            if not row:
                abort(404, message="Product not found")
            return _row_to_product(row)

    @blp.arguments(ProductUpdateSchema)
    @blp.response(200, ProductSchema)
    def put(self, data, id: int):
        """Update a product by id with partial or full data."""
        if not data:
            # Validate empty payload
            raise ValidationError("No fields provided to update.")

        with get_connection() as conn:
            # Check existence
            cur = conn.execute("SELECT id FROM products WHERE id = ?", (id,))
            if cur.fetchone() is None:
                abort(404, message="Product not found")

            # Build dynamic update
            fields = []
            values = []
            if "name" in data and data["name"] is not None:
                fields.append("name = ?")
                values.append(data["name"])
            if "price" in data and data["price"] is not None:
                fields.append("price = ?")
                values.append(float(data["price"]))
            if "quantity" in data and data["quantity"] is not None:
                fields.append("quantity = ?")
                values.append(int(data["quantity"]))

            if not fields:
                # nothing to update
                cur = conn.execute("SELECT id, name, price, quantity FROM products WHERE id = ?", (id,))
                row = cur.fetchone()
                return _row_to_product(row)

            values.append(id)
            sql = f"UPDATE products SET {', '.join(fields)} WHERE id = ?"
            conn.execute(sql, tuple(values))

            # Return updated record
            cur = conn.execute("SELECT id, name, price, quantity FROM products WHERE id = ?", (id,))
            row = cur.fetchone()
            return _row_to_product(row)

    @blp.response(204)
    def delete(self, id: int):
        """Delete a product by id."""
        with get_connection() as conn:
            cur = conn.execute("DELETE FROM products WHERE id = ?", (id,))
            if cur.rowcount == 0:
                abort(404, message="Product not found")
            return "", 204
