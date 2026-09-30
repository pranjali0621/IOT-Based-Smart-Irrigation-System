from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database_models import Base, User, Plant, Sensor
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
    """Create default admin user if it doesn't exist."""
    db = SessionLocal()
    
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
        if not admin.is_admin:
            admin.is_admin = True
            db.commit()
    
    db.close()


def seed_demo_data():
    """
    Seed demo user + plant + sensor so simulate_esp32.py always works,
    even after a DB reset.  Uses 'upsert-style' checks so it's safe to
    call on every startup.
    """
    db = SessionLocal()

    # --- demo user ---
    demo_user = db.query(User).filter(User.username == "demo").first()
    if not demo_user:
        demo_user = User(
            username="demo",
            email="demo@florapulse.local",
            password_hash=hash_password("demo123"),
            full_name="Demo User",
        )
        db.add(demo_user)
        db.commit()
        db.refresh(demo_user)
        print("✅ Demo user seeded: demo / demo123")

    # --- demo plant (owned by demo user) ---
    demo_plant = (
        db.query(Plant)
        .filter(Plant.user_id == demo_user.id, Plant.name == "Demo Plant")
        .first()
    )
    if not demo_plant:
        demo_plant = Plant(
            user_id=demo_user.id,
            name="Demo Plant",
            description="Automatically seeded demo plant",
        )
        db.add(demo_plant)
        db.commit()
        db.refresh(demo_plant)
        print(f"✅ Demo plant seeded: '{demo_plant.name}' (id={demo_plant.id})")

    # --- demo sensor (ESP32_DEMO_001) ---
    demo_sensor = (
        db.query(Sensor)
        .filter(Sensor.sensor_id == "ESP32_DEMO_001")
        .first()
    )
    if not demo_sensor:
        demo_sensor = Sensor(
            plant_id=demo_plant.id,
            sensor_id="ESP32_DEMO_001",
            sensor_name="Demo Moisture Sensor",
            is_connected=False,
        )
        db.add(demo_sensor)
        db.commit()
        print("✅ Demo sensor seeded: ESP32_DEMO_001")
    elif demo_sensor.plant_id != demo_plant.id:
        # Re-link if plant was re-created
        demo_sensor.plant_id = demo_plant.id
        db.commit()

    db.close()


seed_admin_user()
seed_demo_data()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
