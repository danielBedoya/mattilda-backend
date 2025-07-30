from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.school import controller as school_controller
from app.user import controller as user_controller
from app.student import controller as student_controller
from app.invoice import controller as invoice_controller
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


app.include_router(school_controller.router)
app.include_router(user_controller.router)
app.include_router(student_controller.router)
app.include_router(invoice_controller.router)


@app.get("/")
async def root():
    """Root endpoint for the API."""
    return {"message": "Mattilda API en local!"}
