"""
Shared pytest fixtures for the test suite.
"""
import pytest
from server.app import create_app
from server.data.database import reset_database


@pytest.fixture
def app():
    """Create a testing instance of the Flask app."""
    application = create_app()
    application.config["TESTING"] = True
    return application


@pytest.fixture
def client(app):
    """Return a test client for the Flask app."""
    return app.test_client()


@pytest.fixture(autouse=True)
def reset_db():
    """Reset the in-memory database before every test."""
    reset_database()
    yield
