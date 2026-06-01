import os

os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("CELERY_BROKER_URL", "memory://")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from db.database import Base
from api.deps import get_db
import main
from services.tasks import process_image_task


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def _setup_database():

    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def delay_calls(monkeypatch):

    calls = []

    def fake_delay(*args, **kwargs):
        calls.append((args, kwargs))
        return None

    monkeypatch.setattr(process_image_task, "delay", fake_delay)
    return calls


@pytest.fixture
def client(delay_calls):
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    main.app.dependency_overrides[get_db] = override_get_db
    with TestClient(main.app) as test_client:
        yield test_client
    main.app.dependency_overrides.clear()


DEFAULT_PASSWORD = "supersecret123"


def register(client, username="alice", email="alice@example.com", password=DEFAULT_PASSWORD):
    return client.post(
        "/auth/signup",
        json={"username": username, "email": email, "password": password},
    )


def login(client, username="alice", password=DEFAULT_PASSWORD):
    return client.post(
        "/auth/login",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )


@pytest.fixture
def auth_headers(client):

    register(client)
    token = login(client).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
