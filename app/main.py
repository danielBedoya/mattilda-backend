from fastapi import FastAPI
from app.api.routes import school
from app.db.database import engine
from app.db.base import Base

app = FastAPI()


app.include_router(school.router)


@app.get("/")
async def root():
    return {"message": "Mattilda API en local!"}
