import pytest
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from ailabel.db.database import with_session


def test_with_session_decorator():
    """Test the with_session decorator behavior."""
    # Create an in-memory test database
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    
    # Test function to be decorated
    @with_session
    def test_function(session: Session, value: str):
        # This function would normally do database operations
        return f"Got session and value: {value}"
    
    # Test without providing a session (decorator should create one)
    result = test_function("test")
    assert result == "Got session and value: test"
    
    # Test with explicit session
    with Session(engine) as session:
        result = test_function("explicit", session=session)
        assert result == "Got session and value: explicit"


def test_with_session_error_handling():
    """Test error handling in the with_session decorator."""
    # Create an in-memory test database
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    
    # Test function that raises an exception
    @with_session
    def failing_function(session: Session):
        raise ValueError("Test exception")
    
    # Verify that the exception is propagated
    with pytest.raises(ValueError, match="Test exception"):
        failing_function()
    
    # With explicit session
    with pytest.raises(ValueError, match="Test exception"):
        with Session(engine) as session:
            failing_function(session=session)