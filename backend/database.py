
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
import os
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

SQLALCHEMY_DATABASE_URL = os.getenv('DATABASE_URL')
print(SQLALCHEMY_DATABASE_URL)

# Check if we are running in Alembic context, which does not support async engine
if 'alembic' not in os.environ:
    engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)
    # create a configured "Session" class
    AsyncSessionLocal = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    # then use it in FastAPI dependencies
    from fastapi import Depends, FastAPI

    async def get_db():
        async with AsyncSessionLocal() as session:
            yield session
