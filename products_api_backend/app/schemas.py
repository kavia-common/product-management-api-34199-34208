from marshmallow import Schema, fields, validate, validates, ValidationError

class ProductBaseSchema(Schema):
    """Base schema with shared fields and validation."""
    name = fields.String(required=True, validate=validate.Length(min=1), metadata={"description": "Product name"})
    price = fields.Float(required=True, metadata={"description": "Unit price (>= 0)"})
    quantity = fields.Integer(required=True, metadata={"description": "Quantity in stock (>= 0)"})

    @validates("price")
    def validate_price(self, value):
        """Ensure price is non-negative."""
        if value < 0:
            raise ValidationError("Price must be greater than or equal to 0.")

    @validates("quantity")
    def validate_quantity(self, value):
        """Ensure quantity is non-negative."""
        if value < 0:
            raise ValidationError("Quantity must be greater than or equal to 0.")

# PUBLIC_INTERFACE
class ProductCreateSchema(ProductBaseSchema):
    """Schema for creating a product (no id in payload)."""
    # No extra fields; inherits validation from ProductBaseSchema
    pass

# PUBLIC_INTERFACE
class ProductUpdateSchema(Schema):
    """Schema for updating a product; all fields optional but if present must be valid."""
    name = fields.String(required=False, validate=validate.Length(min=1), metadata={"description": "Product name"})
    price = fields.Float(required=False, metadata={"description": "Unit price (>= 0)"})
    quantity = fields.Integer(required=False, metadata={"description": "Quantity in stock (>= 0)"})

    @validates("price")
    def validate_price(self, value):
        """Ensure price is non-negative when provided."""
        if value < 0:
            raise ValidationError("Price must be greater than or equal to 0.")

    @validates("quantity")
    def validate_quantity(self, value):
        """Ensure quantity is non-negative when provided."""
        if value < 0:
            raise ValidationError("Quantity must be greater than or equal to 0.")

# PUBLIC_INTERFACE
class ProductSchema(ProductBaseSchema):
    """Schema for returning a product with id."""
    id = fields.Integer(required=True, metadata={"description": "Product identifier"})


# PUBLIC_INTERFACE
class BalanceSchema(Schema):
    """Schema for returning total inventory value."""
    total_balance = fields.Float(required=True, metadata={"description": "Sum of price * quantity across all products"})
