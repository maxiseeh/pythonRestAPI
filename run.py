"""Entry point to run the Flask development server."""
from server.app import create_app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
