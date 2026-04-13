"""Flask application factory."""
from flask import Flask
from server.routes.inventory import inventory_bp


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.register_blueprint(inventory_bp)
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
