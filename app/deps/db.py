from app.db.database import AsyncSessionLocal
from sqlalchemy.ext.asyncio import AsyncSession


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
