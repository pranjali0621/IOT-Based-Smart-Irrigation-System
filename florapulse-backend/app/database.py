from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database_models import Base

DATABASE_URL = "sqlite:///./florapulse.db"

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine
)

# CREATE ALL TABLES ON STARTUP
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
