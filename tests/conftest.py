import os
import pytest
from pathlib import Path
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from ailabel.db.models import Topic, Label, LabeledPayload


@pytest.fixture(name="session")
def session_fixture():
    """Create an in-memory database session for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="mock_gemini_api_key", autouse=True)
def mock_gemini_api_key_fixture(monkeypatch):
    """Mock the GEMINI_API_KEY environment variable."""
    monkeypatch.setenv("GEMINI_API_KEY", "fake-api-key")


@pytest.fixture
def sample_topic():
    """Sample topic fixture."""
    return "test_topic"


@pytest.fixture
def sample_label():
    """Sample label fixture."""
    return "test_label"


@pytest.fixture
def sample_payload():
    """Sample payload fixture."""
    return "This is a test payload for testing purposes."