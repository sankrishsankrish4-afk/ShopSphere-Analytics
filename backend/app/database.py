from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import settings


connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
pool_args = {"poolclass": StaticPool} if settings.database_url == "sqlite:///:memory:" else {}

engine = create_engine(settings.database_url, connect_args=connect_args, future=True, **pool_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that provides one database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables() -> None:
    import app.models  # noqa: F401 - importing registers ORM models on Base.metadata.

    Base.metadata.create_all(bind=engine)
