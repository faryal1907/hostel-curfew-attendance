from fastapi import FastAPI
from backend.models.database import Base, engine
from backend.app.routes import router

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(router)