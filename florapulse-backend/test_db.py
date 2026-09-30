from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys, os

# Add app to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from app.database import Base, get_db
from app.database_models import User

engine = create_engine("sqlite:///florapulse.db")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

testuser = db.query(User).filter(User.username == "testuser").first()
if testuser:
    print(f"testuser exists: id={testuser.id}, username={testuser.username}")
else:
    print("testuser not found!")
