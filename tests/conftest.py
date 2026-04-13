import pytest
from server.app import create_app
from server.data.database import reset_database


@pytest.fixture
def app():
    application = create_app()
    application.config["TESTING"] = True
    return application


@pytest.fixture
def client(app):
    return app.test_client()


# reset the database before every test so tests don't affect each other
@pytest.fixture(autouse=True)
def reset_db():
    reset_database()
    yield
