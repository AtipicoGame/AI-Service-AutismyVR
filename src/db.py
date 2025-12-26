import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

# Default to local postgres if not set (for docker)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/autismyvr")

engine = create_engine(DATABASE_URL)
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Initialize database: run SQL migrations first, then create SQLAlchemy tables.
    """
    from src.db_migrations import run_migrations, check_migrations_table
    
    try:
        print("Initializing database...")
        
        check_migrations_table()
        run_migrations()
        
        from src.models.chat_models import ChatSession, Interaction
        Base.metadata.create_all(bind=engine)
        
        print("Database initialization completed successfully")
    except Exception as e:
        print(f"Database initialization error: {e}")
        raise
