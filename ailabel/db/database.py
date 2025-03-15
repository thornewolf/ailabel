# ruff: noqa: F401
from typing import Callable, Concatenate
from sqlmodel import SQLModel, create_engine, Session
from ailabel.db import models  # intentional to have models for metadata.create_all
from pathlib import Path

data_dir = Path.home() / ".local" / "share" / "ailabel"
data_dir.mkdir(parents=True, exist_ok=True)
sqlite_url = f"sqlite:///{data_dir}/labels.db"
engine = create_engine(sqlite_url)

SQLModel.metadata.create_all(engine)


def with_session[T, **P](func: Callable[Concatenate[Session, P], T]) -> Callable[P, T]:
    def wrapper(*args: P.args, session=None, **kwargs: P.kwargs):
        if session is not None:
            return func(session, *args, **kwargs)
        with Session(engine) as s:
            return func(s, *args, **kwargs)

    return wrapper


@with_session
def test_fn(session: Session):
    print(session)


# still expects session arg
if __name__ == "__main__":
    test_fn()
