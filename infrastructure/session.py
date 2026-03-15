from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

from infrastructure.database import get_engine

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())


@contextmanager
def get_session():
    session = SessionLocal()

    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# EXAMPLE USAGE
# from infrastructure.session import get_session

# with get_session() as session:
#     ...
