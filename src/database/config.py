import os

from dotenv import load_dotenv

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker


load_dotenv()

DATABASE_URL = os.getenv("DB_URL")

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
