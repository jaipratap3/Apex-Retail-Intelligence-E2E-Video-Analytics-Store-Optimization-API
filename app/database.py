from sqlalchemy import create_engine, Column, String, Integer, Boolean, Float, DateTime, JSON
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./store_intelligence.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class EventRecord(Base):
    __tablename__ = "events"

    # We use event_id as primary key to ensure idempotency naturally
    event_id = Column(String, primary_key=True, index=True)
    store_id = Column(String, index=True)
    camera_id = Column(String)
    visitor_id = Column(String, index=True)
    event_type = Column(String, index=True)
    timestamp = Column(DateTime, index=True)
    zone_id = Column(String, nullable=True)
    dwell_ms = Column(Integer, default=0)
    is_staff = Column(Boolean, default=False)
    confidence = Column(Float)
    metadata_json = Column(JSON, nullable=True)

# Create tables
Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
