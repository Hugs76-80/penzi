import pytest
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

import app.models  # noqa: F401
from app.config import settings
from app.database import Base


@pytest.fixture(scope="session")
def engine():
    url = settings.test_database_url
    if not url:
        pytest.fail("TEST_DATABASE_URL is empty. Add it to your .env file.")
    database_name = make_url(url).database or ""
    if url == settings.database_url or not database_name.endswith("_test"):
        pytest.exit(
            "Refusing to run: the test database name must end in _test.",
            returncode=2,
        )
    test_engine = create_engine(url)
    Base.metadata.create_all(test_engine)
    yield test_engine
    Base.metadata.drop_all(test_engine)
    test_engine.dispose()


@pytest.fixture
def db(engine):
    connection = engine.connect()
    outer = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint")
    try:
        yield session
    finally:
        session.close()
        outer.rollback()
        connection.close()