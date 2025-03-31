"""Database connection and session handling.

This module provides the database connection, session management,
and a decorator for handling database sessions in CRUD operations.

The module:
1. Sets up the SQLite database in a user-specific location
2. Initializes the database schema based on the models
3. Provides a `with_session` decorator that automatically creates and manages database sessions

Usage:
    @with_session
    def my_db_function(session: Session, arg1: str, arg2: int) -> Result:
        # Use the session here
        return result

    # Call without specifying a session (one will be created automatically)
    result = my_db_function("value1", 42)

    # Or provide an existing session
    with Session(engine) as session:
        result = my_db_function("value1", 42, session=session)
"""

# ruff: noqa: F401
from typing import Callable, Concatenate
from sqlmodel import SQLModel, create_engine, Session
from pathlib import Path

from ailabel.db import models  # intentional to have models for metadata.create_all

data_dir = Path.home() / ".local" / "share" / "ailabel"
data_dir.mkdir(parents=True, exist_ok=True)
sqlite_url = f"sqlite:///{data_dir}/labels.db"
engine = create_engine(sqlite_url)

SQLModel.metadata.create_all(engine)


def with_session[T, **P](func: Callable[Concatenate[Session, P], T]) -> Callable[P, T]:
    """Decorator to automatically handle database sessions.

    This decorator wraps a function that requires a database session.
    If a session is provided when calling the function, it will be used.
    Otherwise, a new session will be created and automatically closed when done.

    Args:
        func: The function to wrap, which should take a Session as its first parameter

    Returns:
        A wrapped function that doesn't require a session parameter to be passed

    Example:
        @with_session
        def get_user(session: Session, user_id: int) -> User:
            return session.get(User, user_id)

        # Call without session (one will be created)
        user = get_user(42)
    """

    def wrapper(*args: P.args, session=None, **kwargs: P.kwargs) -> T:
        if session is not None:
            return func(session, *args, **kwargs)
        with Session(engine) as s:
            return func(s, *args, **kwargs)

    return wrapper


# Example usage (not used in production)
if __name__ == "__main__":

    @with_session
    def test_fn(session: Session) -> None:
        """Test function to demonstrate session usage."""
        print(f"Using session: {session}")
