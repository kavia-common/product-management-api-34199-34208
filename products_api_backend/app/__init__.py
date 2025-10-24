from flask import Flask
from flask_cors import CORS
from flask_smorest import Api

from .routes.health import blp as health_blp
from .routes.products import blp as products_blp
from .db import init_db

# Initialize Flask app and API
app = Flask(__name__)
app.url_map.strict_slashes = False
CORS(app, resources={r"/*": {"origins": "*"}})

# OpenAPI / Swagger config
app.config["API_TITLE"] = "Product Management API"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.3"
app.config["OPENAPI_URL_PREFIX"] = "/docs"
app.config["OPENAPI_SWAGGER_UI_PATH"] = ""
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

# Initialize DB (idempotent) on app start
with app.app_context():
    init_db()

# Register blueprints to expose routes
api = Api(app)
api.register_blueprint(health_blp)
api.register_blueprint(products_blp)
