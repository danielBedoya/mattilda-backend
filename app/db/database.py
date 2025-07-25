from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker as sessionMarker
from app.core.config import settings

DATABASE_URL = settings.DATABASE_URL
engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal = sessionMarker(
    bind=engine, expire_on_commit=False, class_=AsyncSession
)
