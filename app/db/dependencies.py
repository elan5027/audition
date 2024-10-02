from typing import Generator
from app.db.session import session


def get_db() -> Generator:
    db = session()
    try:
        yield db
    finally:
        db.close()
