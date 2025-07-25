from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.api.routes import school, auth, student, invoice
from app.db.database import engine
from app.db.base import Base
from app.core.exceptions import register_exception_handlers


app = FastAPI()


@app.on_event("startup")
async def startup_event():
    """Handles application startup events."""
    pass
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)


register_exception_handlers(app)


app.include_router(school.router)
app.include_router(auth.router)
app.include_router(student.router)
app.include_router(invoice.router)


@app.get("/")
async def root():
    """Root endpoint for the API."""
    return {"message": "Mattilda API en local!"}
