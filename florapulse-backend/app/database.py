from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database_models import Base, User
from app.utils.auth import hash_password

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

def seed_admin_user():
    """Create default admin user if it doesn't exist"""

    db = SessionLocal()
    
    # Check if admin exists
    admin = db.query(User).filter(User.username == "admin").first()
    
    if not admin:
        admin_user = User(
            username="admin",
            email="admin@florapulse.local",
            password_hash=hash_password("admin123"),
            full_name="Administrator",
            is_admin=True
        )
        db.add(admin_user)
        db.commit()
        print("✅ Admin user created: admin / admin123")
    else:
        # Make sure is_admin is True
        if not admin.is_admin:
            admin.is_admin = True
            db.commit()
    
    db.close()
seed_admin_user()
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
