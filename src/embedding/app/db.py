import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "victor")
DB_USER = os.getenv("POSTGRES_USER", "victor")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "changeThisPassword")

# Create async engine
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_async_engine(DATABASE_URL, echo=False)

# Create async session factory
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Logger
logger = logging.getLogger("victor-db")

async def init_db():
    """
    Initialize the database connection and verify the schema exists.
    """
    try:
        async with engine.begin() as conn:
            # Check if the victor schema exists
            result = await conn.execute(text(
                "SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'victor'"
            ))
            schema_exists = result.scalar_one_or_none()
            
            if not schema_exists:
                logger.warning("Victor schema does not exist. Please run the initialization scripts.")
            else:
                logger.info("Victor schema exists.")
                
            # Check if pgvector extension is installed
            result = await conn.execute(text(
                "SELECT extname FROM pg_extension WHERE extname = 'vector'"
            ))
            vector_exists = result.scalar_one_or_none()
            
            if not vector_exists:
                logger.warning("pgvector extension is not installed. Please install it.")
            else:
                logger.info("pgvector extension is installed.")
                
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        raise

async def get_db():
    """
    Dependency to get DB session for FastAPI endpoints
    """
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()