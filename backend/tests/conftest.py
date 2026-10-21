import pytest
from app.db.session import engine, Base
from app.db import models

@pytest.fixture(autouse=True, scope="session")
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    yield
