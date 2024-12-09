 # inventory/app/database.py

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Fetch DATABASE_URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://ecommerce_user:ecommerce_pass@database:5432/ecommerce_db")

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative models
Base = declarative_base()
