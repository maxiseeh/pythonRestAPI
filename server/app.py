from flask import Flask
from server.routes.inventory import inventory_bp

def create_app():
    app = Flask(__name__)
    app.register_blueprint(inventory_bp)
    return app
