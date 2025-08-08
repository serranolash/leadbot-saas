from sqlmodel import SQLModel, Session, create_engine
from .settings import settings

engine = create_engine(settings.DATABASE_URL, echo=False)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
