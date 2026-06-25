from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# This creates a local file named 'plant_doctor.db' in your project folder
SQLALCHEMY_DATABASE_URL = "sqlite:///./plant_doctor.db"

# connect_args={"check_same_thread": False} is required for SQLite in FastAPI
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# This creates database sessions for our app to use
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# This is the base class our database tables will inherit from
Base = declarative_base()